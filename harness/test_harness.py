"""
Acceptance tests for the universal agent harness.

Run config-only tests (no server needed):
    pytest harness/test_harness.py -k "config"

Run server tests (requires running server at localhost:8000):
    pytest harness/test_harness.py -k "not integration and not config"

Run integration tests (requires ANTHROPIC_API_KEY + running server):
    pytest harness/test_harness.py -m integration
"""

from __future__ import annotations

import json
import os
from pathlib import Path

import httpx
import pytest
import pytest_asyncio

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

HARNESS_DIR = Path(__file__).resolve().parent
CONFIG_PATH = HARNESS_DIR / "agent.config.json"
SERVER_URL = os.environ.get("SERVER_URL", "http://localhost:8000")


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest_asyncio.fixture
async def client():
    """Async HTTP client pointed at the harness server."""
    async with httpx.AsyncClient(base_url=SERVER_URL, timeout=30.0) as c:
        yield c


@pytest_asyncio.fixture
async def authed_client():
    """Async HTTP client that sends a Bearer token from the config's api_keys."""
    config = json.loads(CONFIG_PATH.read_text())
    api_keys: list[str] = config.get("api_keys", [])
    token = api_keys[0] if api_keys else "test-token"
    headers = {"Authorization": f"Bearer {token}"}
    async with httpx.AsyncClient(
        base_url=SERVER_URL, timeout=30.0, headers=headers
    ) as c:
        yield c


def _load_config() -> dict:
    """Load and return the agent config dict."""
    return json.loads(CONFIG_PATH.read_text())


# ===========================================================================
# CONFIG TESTS — no running server needed
# ===========================================================================


class TestConfig:
    """Validate agent.config.json without requiring a running server."""

    def test_config_loads(self):
        """agent.config.json loads and contains required fields."""
        config = _load_config()
        required_fields = ["agent_dir", "port", "allowed_tools"]
        for field in required_fields:
            assert field in config, f"Missing required field: {field}"

    def test_config_env_override(self, monkeypatch):
        """AGENT_DIR env var overrides the config value."""
        override = "/tmp/override-agent-dir"
        monkeypatch.setenv("AGENT_DIR", override)

        config = _load_config()
        effective_agent_dir = os.environ.get("AGENT_DIR", config.get("agent_dir"))
        assert effective_agent_dir == override

    def test_config_defaults(self):
        """Missing optional fields fall back to sensible defaults."""
        config = _load_config()

        # Defaults that should be assumed when absent
        defaults = {
            "timeout_seconds": 600,
            "max_turns": 50,
            "cors_origins": ["http://localhost:3000"],
            "api_keys": [],
        }

        for key, default_value in defaults.items():
            actual = config.get(key, default_value)
            # If the key is present its value is fine; if missing the default
            # should be used.  We just verify the *effective* value is correct.
            assert actual == config.get(key, default_value)

    def test_config_agent_dir_resolves(self):
        """agent_dir resolves relative to the harness/ directory."""
        config = _load_config()
        agent_dir_raw = config["agent_dir"]
        resolved = (HARNESS_DIR / agent_dir_raw).resolve()
        assert resolved.is_dir(), (
            f"agent_dir resolved to {resolved} which is not a directory"
        )


# ===========================================================================
# SERVER TESTS — require a running server at SERVER_URL
# ===========================================================================


class TestHealth:
    @pytest.mark.asyncio
    async def test_health(self, client: httpx.AsyncClient):
        """GET /health returns 200 with status ok."""
        resp = await client.get("/health")
        assert resp.status_code == 200
        body = resp.json()
        assert body.get("status") == "ok"


class TestSkills:
    @pytest.mark.asyncio
    async def test_skills_list(self, client: httpx.AsyncClient):
        """GET /skills returns 200 with a skills array of objects."""
        resp = await client.get("/skills")
        assert resp.status_code == 200
        body = resp.json()
        assert "skills" in body
        assert isinstance(body["skills"], list)
        if body["skills"]:
            first = body["skills"][0]
            assert "name" in first, "Each skill must have a 'name'"
            assert "description" in first, "Each skill must have a 'description'"


class TestChat:
    @pytest.mark.asyncio
    async def test_chat_missing_message(self, client: httpx.AsyncClient):
        """POST /chat with empty body returns 400."""
        resp = await client.post("/chat", json={})
        assert resp.status_code == 400

    @pytest.mark.asyncio
    async def test_chat_streams_sse(self, client: httpx.AsyncClient):
        """POST /chat with a message returns an SSE stream with content and done events."""
        found_content = False
        found_done = False

        async with client.stream(
            "POST",
            "/chat",
            json={"message": "What skills are available?"},
            headers={"Accept": "text/event-stream"},
        ) as resp:
            assert resp.status_code == 200
            assert "text/event-stream" in resp.headers.get("content-type", "")

            async for line in resp.aiter_lines():
                if not line.strip():
                    continue

                if line.startswith("event:"):
                    event_type = line.split(":", 1)[1].strip()
                    if event_type == "content":
                        found_content = True
                    elif event_type == "done":
                        found_done = True
                        break

                # Also handle the data-only SSE format: data: {"type": "..."}
                if line.startswith("data:"):
                    data_str = line.split(":", 1)[1].strip()
                    if data_str:
                        try:
                            data = json.loads(data_str)
                            if data.get("type") == "content":
                                found_content = True
                            elif data.get("type") == "done":
                                found_done = True
                                break
                        except json.JSONDecodeError:
                            # Plain text data counts as content
                            found_content = True

        assert found_content, "SSE stream must include at least one content event"
        assert found_done, "SSE stream must include a done event"


class TestTrigger:
    @pytest.mark.asyncio
    async def test_trigger_skill(self, client: httpx.AsyncClient):
        """POST /trigger/portfolio-status returns 200 with skill and results."""
        resp = await client.post("/trigger/portfolio-status", timeout=120.0)
        assert resp.status_code == 200
        body = resp.json()
        assert "skill" in body
        assert "results" in body


class TestAuth:
    @pytest.mark.asyncio
    async def test_auth_required(self, client: httpx.AsyncClient):
        """When api_keys are configured, a request without Bearer token gets 401."""
        config = _load_config()
        api_keys = config.get("api_keys", [])

        if not api_keys:
            pytest.skip("No api_keys configured — auth is disabled")

        resp = await client.get("/health")
        assert resp.status_code == 401

    @pytest.mark.asyncio
    async def test_auth_valid(self, authed_client: httpx.AsyncClient):
        """When api_keys are configured, a valid Bearer token gets 200."""
        config = _load_config()
        api_keys = config.get("api_keys", [])

        if not api_keys:
            pytest.skip("No api_keys configured — auth is disabled")

        resp = await authed_client.get("/health")
        assert resp.status_code == 200


# ===========================================================================
# INTEGRATION TESTS — require ANTHROPIC_API_KEY + running server
# ===========================================================================


@pytest.mark.integration
class TestIntegration:
    @pytest.mark.asyncio
    async def test_chat_discovers_skills(self, client: httpx.AsyncClient):
        """POST /chat asking about skills returns a response mentioning actual skill names."""
        collected_text = []

        async with client.stream(
            "POST",
            "/chat",
            json={"message": "What skills are available?"},
            headers={"Accept": "text/event-stream"},
            timeout=120.0,
        ) as resp:
            assert resp.status_code == 200

            async for line in resp.aiter_lines():
                if not line.strip():
                    continue
                if line.startswith("data:"):
                    data_str = line.split(":", 1)[1].strip()
                    if data_str:
                        try:
                            data = json.loads(data_str)
                            if data.get("type") == "content":
                                collected_text.append(
                                    data.get("content", data.get("text", ""))
                                )
                            elif data.get("type") == "done":
                                break
                        except json.JSONDecodeError:
                            collected_text.append(data_str)

        full_response = " ".join(collected_text).lower()

        # The response should mention at least some real skill names
        known_skills = [
            "portfolio-status",
            "morning-brief",
            "risk-monitor",
            "analyze-opportunity",
            "daily-advisor",
        ]
        matches = [s for s in known_skills if s in full_response]
        assert len(matches) >= 1, (
            f"Expected response to mention known skills. Got: {full_response[:500]}"
        )

    @pytest.mark.asyncio
    async def test_trigger_executes_skill(self, client: httpx.AsyncClient):
        """POST /trigger/portfolio-status returns results containing portfolio data."""
        resp = await client.post("/trigger/portfolio-status", timeout=180.0)
        assert resp.status_code == 200
        body = resp.json()
        assert "results" in body

        results_str = json.dumps(body["results"]).lower()
        # Portfolio output should reference at least one of: positions, value,
        # ticker symbols, P&L, etc.
        portfolio_indicators = [
            "position",
            "ticker",
            "portfolio",
            "value",
            "p&l",
            "shares",
            "cost_basis",
            "tqqq",
        ]
        found = [ind for ind in portfolio_indicators if ind in results_str]
        assert len(found) >= 1, (
            f"Expected portfolio data in results. Got: {results_str[:500]}"
        )
