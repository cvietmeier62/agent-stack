"""
Universal Agent Harness Server

FastAPI server that wraps the Claude Agent SDK to serve any collection of
SKILL.md files as HTTP endpoints. Loads configuration from agent.config.json
in the same directory as this file.

Environment variables:
    ANTHROPIC_API_KEY  — Required. Anthropic API key for Claude Agent SDK.
    AGENT_DIR          — Optional. Overrides config's agent_dir field.
"""

import asyncio
import json
import logging
import os
import time
from pathlib import Path
from typing import Optional

import yaml
from fastapi import FastAPI, HTTPException, Request, Security
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel

from claude_agent_sdk import query, ClaudeAgentOptions

# ---------------------------------------------------------------------------
# Paths & config
# ---------------------------------------------------------------------------

HARNESS_DIR = Path(os.path.dirname(os.path.abspath(__file__)))
CONFIG_PATH = HARNESS_DIR / "agent.config.json"

with open(CONFIG_PATH) as f:
    CONFIG = json.load(f)

# Resolve agent_dir: env var overrides config, config is relative to harness/
AGENT_DIR = os.environ.get("AGENT_DIR") or os.path.abspath(
    os.path.join(str(HARNESS_DIR), CONFIG.get("agent_dir", ".."))
)

# Warn if API key is missing (will error on actual agent calls, but /health and /skills still work)
if not os.environ.get("ANTHROPIC_API_KEY"):
    import warnings
    warnings.warn("ANTHROPIC_API_KEY not set — /chat and /trigger will fail, but /health and /skills work")

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S",
)
logger = logging.getLogger("harness")

# ---------------------------------------------------------------------------
# FastAPI app
# ---------------------------------------------------------------------------

START_TIME = time.time()

app = FastAPI(
    title=CONFIG.get("metadata", {}).get("name", "Agent Harness"),
    version=CONFIG.get("metadata", {}).get("version", "0.0.1"),
    description=CONFIG.get("metadata", {}).get("description", ""),
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=CONFIG.get("cors_origins", ["*"]),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Auth
# ---------------------------------------------------------------------------

security = HTTPBearer(auto_error=False)
API_KEYS: list[str] = CONFIG.get("api_keys", [])


async def verify_auth(
    credentials: Optional[HTTPAuthorizationCredentials] = Security(security),
) -> None:
    """Enforce bearer token auth when api_keys is non-empty."""
    if not API_KEYS:
        return  # dev mode — no auth required
    if credentials is None or credentials.credentials not in API_KEYS:
        raise HTTPException(status_code=401, detail="Invalid or missing API key")


# ---------------------------------------------------------------------------
# Request logging middleware
# ---------------------------------------------------------------------------

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    duration = time.time() - start
    logger.info(
        "%s %s — %d (%.2fs)",
        request.method,
        request.url.path,
        response.status_code,
        duration,
    )
    return response


# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------

class ChatRequest(BaseModel):
    message: str


class TriggerRequest(BaseModel):
    prompt: Optional[str] = None


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _build_options(**overrides) -> ClaudeAgentOptions:
    """Construct ClaudeAgentOptions from config with optional overrides."""
    opts = ClaudeAgentOptions(
        cwd=AGENT_DIR,
        setting_sources=["project"],
        allowed_tools=CONFIG.get("allowed_tools", []),
        max_turns=overrides.get("max_turns", CONFIG.get("max_turns", 50)),
    )
    return opts


def _extract_skill_frontmatter(skill_path: Path) -> dict:
    """Read a SKILL.md and extract name + description from YAML frontmatter."""
    try:
        text = skill_path.read_text(encoding="utf-8")
    except Exception:
        return {}

    if not text.startswith("---"):
        return {"name": skill_path.parent.name, "description": ""}

    parts = text.split("---", 2)
    if len(parts) < 3:
        return {"name": skill_path.parent.name, "description": ""}

    try:
        fm = yaml.safe_load(parts[1])
        if not isinstance(fm, dict):
            fm = {}
    except Exception:
        fm = {}

    return {
        "name": fm.get("name", skill_path.parent.name),
        "description": fm.get("description", ""),
    }


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@app.get("/health")
async def health():
    """Health check with uptime and agent directory."""
    return {
        "status": "ok",
        "agent_dir": AGENT_DIR,
        "uptime_seconds": round(time.time() - START_TIME, 2),
    }


@app.get("/skills", dependencies=[Security(verify_auth)])
async def list_skills():
    """Discover available skills by scanning .claude/skills/*/SKILL.md."""
    skills_dir = Path(AGENT_DIR) / ".claude" / "skills"
    skills = []

    if skills_dir.is_dir():
        for skill_md in sorted(skills_dir.glob("*/SKILL.md")):
            info = _extract_skill_frontmatter(skill_md)
            if info:
                skills.append(info)

    return {"skills": skills}


@app.post("/chat", dependencies=[Security(verify_auth)])
async def chat(req: ChatRequest):
    """
    Stream a chat response as Server-Sent Events.

    SSE event types:
      - content  : incremental text from the agent
      - result   : final complete response
      - error    : something went wrong
      - done     : stream is finished
    """

    async def event_stream():
        try:
            options = _build_options()
            full_response = []

            async for event in query(prompt=req.message, options=options):
                # Log event structure for debugging
                event_type = getattr(event, "type", None)
                event_subtype = getattr(event, "subtype", None)
                has_result = hasattr(event, "result")
                has_content = hasattr(event, "content")
                logger.debug("SDK event: type=%s subtype=%s has_result=%s has_content=%s keys=%s",
                    event_type, event_subtype, has_result, has_content,
                    list(event.__dict__.keys()) if hasattr(event, "__dict__") else "N/A")

                # The SDK yields Message objects with various types
                if has_result:
                    # Final result message
                    result_text = str(event.result)
                    full_response.append(result_text)
                    yield f"data: {json.dumps({'type': 'result', 'content': result_text})}\n\n"
                elif event_type == "assistant" and has_content:
                    # Assistant content (text response)
                    content = str(event.content) if not isinstance(event.content, str) else event.content
                    full_response.append(content)
                    yield f"data: {json.dumps({'type': 'content', 'content': content})}\n\n"
                elif event_type == "error":
                    msg = getattr(event, "content", str(event))
                    yield f"data: {json.dumps({'type': 'error', 'content': str(msg)})}\n\n"
                elif has_content:
                    # Any other event with content
                    content = str(event.content) if not isinstance(event.content, str) else event.content
                    if content:
                        full_response.append(content)
                        yield f"data: {json.dumps({'type': 'content', 'content': content})}\n\n"

            # If we accumulated text without an explicit result, send it
            if full_response:
                combined = "\n".join(full_response)
                yield f"data: {json.dumps({'type': 'result', 'content': combined})}\n\n"

            yield f"data: {json.dumps({'type': 'done'})}\n\n"

        except Exception as exc:
            logger.exception("Error in /chat stream")
            yield f"data: {json.dumps({'type': 'error', 'content': str(exc)})}\n\n"
            yield f"data: {json.dumps({'type': 'done'})}\n\n"

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@app.post("/trigger/{skill_name}", dependencies=[Security(verify_auth)])
async def trigger_skill(skill_name: str, req: TriggerRequest = TriggerRequest()):
    """
    Synchronously execute a skill and return the collected results.

    Uses the default prompt unless overridden in the request body.
    """
    # Verify the skill exists
    skill_path = Path(AGENT_DIR) / ".claude" / "skills" / skill_name / "SKILL.md"
    if not skill_path.is_file():
        raise HTTPException(
            status_code=404,
            detail=f"Skill '{skill_name}' not found at {skill_path}",
        )

    prompt = req.prompt or (
        f"Run the /{skill_name} skill now. Follow all instructions in the SKILL.md."
    )

    start = time.time()
    results: list[str] = []

    try:
        options = _build_options()

        async for event in query(prompt=prompt, options=options):
            if hasattr(event, "type"):
                if event.type in ("content", "result"):
                    text = event.content if hasattr(event, "content") else str(event)
                    results.append(text)
                elif event.type == "error":
                    text = event.content if hasattr(event, "content") else str(event)
                    results.append(f"[ERROR] {text}")
            elif isinstance(event, str):
                results.append(event)

    except Exception as exc:
        logger.exception("Error triggering skill %s", skill_name)
        raise HTTPException(
            status_code=500,
            detail=f"Skill execution failed: {str(exc)}",
        )

    duration = round(time.time() - start, 2)
    logger.info("Skill /%s completed in %.2fs", skill_name, duration)

    return {
        "skill": skill_name,
        "results": results,
        "duration_seconds": duration,
    }


# ---------------------------------------------------------------------------
# Global error handler
# ---------------------------------------------------------------------------

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled exception on %s %s", request.method, request.url.path)
    return JSONResponse(
        status_code=500,
        content={"error": str(exc), "path": str(request.url.path)},
    )


# ---------------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import uvicorn

    port = CONFIG.get("port", 8000)
    logger.info("Starting harness on port %d — agent_dir=%s", port, AGENT_DIR)
    uvicorn.run(app, host="0.0.0.0", port=port)
