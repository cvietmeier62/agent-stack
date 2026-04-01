# =============================================================================
# Universal Agent Harness — Container Image
#
# BUILD (once):
#   cd ~/agent-harness && docker build -t agent-harness .
#
# RUN (mount any agent folder):
#   docker run -p 8000:8000 \
#     -e ANTHROPIC_API_KEY=sk-... \
#     -v ~/financial-engine:/app/agent \
#     agent-harness
#
# Different agent, same image:
#   docker run -p 8001:8001 \
#     -e ANTHROPIC_API_KEY=sk-... \
#     -v ~/isv-advisory:/app/agent \
#     agent-harness
# =============================================================================

FROM python:3.13-slim

# ---- System deps & Node.js 22 ----
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        curl ca-certificates gnupg \
    && mkdir -p /etc/apt/keyrings \
    && curl -fsSL https://deb.nodesource.com/gpgkey/nodesource-repo.gpg.key \
        | gpg --dearmor -o /etc/apt/keyrings/nodesource.gpg \
    && echo "deb [signed-by=/etc/apt/keyrings/nodesource.gpg] https://deb.nodesource.com/node_22.x nodistro main" \
        > /etc/apt/sources.list.d/nodesource.list \
    && apt-get update \
    && apt-get install -y --no-install-recommends nodejs \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# ---- Claude Code CLI ----
RUN npm install -g @anthropic-ai/claude-code

# ---- Harness Python deps ----
COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt && rm /tmp/requirements.txt

# ---- Common agent deps (most agents need these) ----
RUN pip install --no-cache-dir yfinance pandas numpy requests beautifulsoup4 supabase python-dateutil

# ---- Copy harness code ----
COPY server.py agentcore_app.py agent.config.json /app/harness/

WORKDIR /app

# ---- Agent directory is mounted at runtime via -v flag ----
# Create the mount point
RUN mkdir -p /app/agent

ENV AGENT_DIR=/app/agent
ENV ANTHROPIC_API_KEY=""
ENV PORT=8000

EXPOSE 8000

# ---- Entrypoint ----
CMD ["python", "-m", "uvicorn", "harness.server:app", "--host", "0.0.0.0", "--port", "8000"]
