"""
AWS Bedrock AgentCore entry point for the Financial Engine agent.

Thin wrapper that makes the Claude Agent SDK-based agent deployable
to AgentCore. Reads the same agent.config.json used by the local
FastAPI server so behaviour stays consistent across runtimes.
"""

import asyncio
import json
import os
import time
from pathlib import Path

from bedrock_agentcore import BedrockAgentCoreApp
from claude_agent_sdk import query

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

AGENT_DIR = Path(os.environ.get("AGENT_DIR", "/app/agent"))
CONFIG_PATH = Path(__file__).parent / "agent.config.json"

def _load_config() -> dict:
    """Load agent.config.json, falling back to sensible defaults."""
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH) as f:
            return json.load(f)
    return {
        "agent_dir": "..",
        "timeout_seconds": 600,
        "max_turns": 50,
        "allowed_tools": [
            "Skill", "Read", "Write", "Bash", "Glob",
            "Grep", "WebSearch", "WebFetch", "Agent",
        ],
        "metadata": {
            "name": "Financial Engine",
            "version": "1.0.0",
        },
    }

CONFIG = _load_config()

# Resolve the working directory the agent sessions should use.
# In a container AGENT_DIR points at the repo root; locally the
# config stores a relative path from harness/ to the repo root.
_configured_dir = CONFIG.get("agent_dir", "..")
if AGENT_DIR.exists():
    WORKING_DIR = str(AGENT_DIR)
else:
    WORKING_DIR = str((Path(__file__).parent / _configured_dir).resolve())

# Skill name → default prompt when the caller omits one.
_DEFAULT_PROMPTS: dict[str, str] = {
    "daily-advisor": "/daily-advisor",
    "morning-brief": "/morning-brief",
    "portfolio-status": "/portfolio-status",
    "risk-monitor": "/risk-monitor",
    "regime-detector": "/regime-detector",
    "catalyst-calendar": "/catalyst-calendar",
    "weekly-review": "/weekly-review",
    "capital-efficiency": "/capital-efficiency",
    "conviction-sizer": "/conviction-sizer",
    "rebalance-triggers": "/rebalance-triggers",
    "factor-engine": "/factor-engine",
    "find-shorts": "/find-shorts",
    "options-toolkit": "/options-toolkit",
    "backtest": "/backtest",
    "analyze-opportunity": "/analyze-opportunity",
}

# ---------------------------------------------------------------------------
# Async agent execution
# ---------------------------------------------------------------------------

async def _run_agent(prompt: str) -> list[dict]:
    """
    Run the Claude Agent SDK query() and collect the result messages.

    Returns a list of content blocks from the agent's response.
    """
    options = {
        "cwd": WORKING_DIR,
        "max_turns": CONFIG.get("max_turns", 50),
        "timeout_seconds": CONFIG.get("timeout_seconds", 600),
        "allowed_tools": CONFIG.get("allowed_tools", []),
    }

    # The SDK respects ANTHROPIC_API_KEY from the environment.
    results: list[dict] = []
    async for event in query(prompt=prompt, options=options):
        # Collect assistant text messages from the stream.
        if hasattr(event, "type"):
            if event.type == "assistant" and hasattr(event, "content"):
                for block in event.content:
                    if hasattr(block, "text"):
                        results.append({"type": "text", "text": block.text})
            elif event.type == "result" and hasattr(event, "content"):
                for block in event.content:
                    if hasattr(block, "text"):
                        results.append({"type": "text", "text": block.text})

    return results

# ---------------------------------------------------------------------------
# AgentCore application
# ---------------------------------------------------------------------------

app = BedrockAgentCoreApp()


@app.entrypoint
def invoke(payload: dict) -> dict:
    """
    AgentCore invocation entry point.

    Payload options:
        {"prompt": "..."}                         — let model route
        {"prompt": "...", "skill": "daily-advisor"} — skill with custom prompt
        {"skill": "daily-advisor"}                — skill with default prompt
    """
    start = time.time()

    try:
        prompt = payload.get("prompt")
        skill = payload.get("skill")

        # Build the effective prompt.
        if skill and prompt:
            # Prefix with the slash-command so the agent activates the skill.
            effective_prompt = f"/{skill} {prompt}"
        elif skill:
            effective_prompt = _DEFAULT_PROMPTS.get(skill, f"/{skill}")
        elif prompt:
            effective_prompt = prompt
        else:
            return {
                "error": "Payload must include 'prompt', 'skill', or both.",
                "duration_seconds": round(time.time() - start, 2),
                "skill": None,
            }

        # Bridge async → sync.  AgentCore's invoke is synchronous but the
        # Claude Agent SDK query() is async.
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = None

        if loop and loop.is_running():
            # If we're already inside an event loop (unlikely in AgentCore
            # but defensive), create a new loop in a thread.
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
                results = pool.submit(
                    asyncio.run, _run_agent(effective_prompt)
                ).result()
        else:
            results = asyncio.run(_run_agent(effective_prompt))

        return {
            "results": results,
            "duration_seconds": round(time.time() - start, 2),
            "skill": skill,
        }

    except Exception as exc:
        return {
            "error": str(exc),
            "duration_seconds": round(time.time() - start, 2),
            "skill": payload.get("skill"),
        }
