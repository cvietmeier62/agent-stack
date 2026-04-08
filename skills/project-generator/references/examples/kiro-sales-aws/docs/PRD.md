# Kiro Sales — Agent Mission Brief (PRD v3)

> This document is designed to be read by an AI coding agent as the primary context for building the Kiro Sales web application. It contains verified technical context, research instructions, and chains of thought.
>
> **v3 changes:** Harness rebuilt on Strands Agents SDK (AWS open source) instead of Claude Agent SDK. Skills are portable — same SKILL.md files, same Agent Skills spec (agentskills.io). Strands provides model flexibility, AWS-native deployment, and simpler containers (Python only, no Node.js).

---

## Mission

Build a web application that gives sales reps a personal AI sales advisor. The builder (Christian) provides the intelligence (skills, steering, tools). Users provide their data (accounts, notes, transcripts). The app connects them through a chat interface with a file browser.

**Existing system:** 30 users on Kiro/Claude Code with manual onboarding (30 min per person).
**Target:** Self-service web app where onboarding takes < 5 minutes.

---

## Pre-Build Research Instructions

Before writing ANY code, the building agent MUST:

1. **Read the Strands Agents SDK docs** — WebSearch: "Strands Agents SDK quickstart" and go to https://strandsagents.com/ — understand how Agent() works, how tools are provided, how AgentSkills plugin loads SKILL.md files, and how streaming works.

2. **Read the Agent Skills specification** — Go to https://agentskills.io/specification — understand the SKILL.md format (frontmatter: name, description, allowed-tools; body: markdown instructions; progressive disclosure: metadata at startup, full content on activation).

3. **Read the Strands + AgentCore starter kit** — WebSearch: "sample-strands-agentcore-starter" and go to https://github.com/aws-samples/sample-strands-agentcore-starter — understand the FastAPI + Strands + SSE streaming pattern, the project structure, and the deployment pattern.

4. **Read the Strands + AgentCore reference architecture** — Go to https://github.com/aws-samples/sample-strands-agent-with-agentcore — understand the skill-based progressive disclosure pattern (L1: catalog, L2: full SKILL.md, L3: execution), the tool architecture, and multi-agent coordination.

5. **Read S3 Files documentation** — WebSearch: "Amazon S3 Files mount setup" and go to https://aws.amazon.com/s3/features/files/ — understand how S3 buckets mount as native file systems, mount targets in VPCs, and 25,000 concurrent connection support.

6. **Read AI SDK v6 useChat docs** — Go to https://sdk.vercel.ai/docs — understand useChat with DefaultChatTransport for SSE streaming, and how AI Elements render chat messages.

7. **Read the existing harness** at `~/agent-stack/harness/server.py` — understand the current Claude Agent SDK implementation so you can translate the same patterns to Strands.

---

## Verified Technical Context

> These facts were verified during development and research. Do NOT hallucinate alternatives.

### Strands Agents SDK (VERIFIED — researched from official docs + GitHub)

Strands is AWS's open-source agent framework. Apache 2.0. Powers Amazon Q Developer, AWS Glue, Kiro.

**Creating an agent:**
```python
from strands import Agent
from strands.models import BedrockModel

model = BedrockModel(
    model_id="us.anthropic.claude-sonnet-4-6-20260514",
    region_name="us-west-2"
)

agent = Agent(
    model=model,
    system_prompt="You are a sales advisor...",
    tools=[file_read, shell, http_request],  # Explicit tool list
)

# Synchronous
result = agent("Prep me for my call with Acme Corp")
print(result)

# Streaming (async iterator)
async for event in agent.stream_async("Prep me for my call"):
    if hasattr(event, 'data'):
        print(event.data, end='', flush=True)
```

**Loading skills (AgentSkills plugin):**
```python
from strands import Agent, AgentSkills
from strands_tools import file_read, shell, http_request

# Load skills from a directory
skills_plugin = AgentSkills(skills="./skills/")

agent = Agent(
    model=model,
    plugins=[skills_plugin],
    tools=[file_read, shell, http_request],  # Agent needs these to execute skill instructions
)
```

The AgentSkills plugin:
1. **Discovery:** Reads SKILL.md frontmatter (name, description) → injects into system prompt as XML
2. **Activation:** When agent calls the `skills` tool with a skill name → receives full instructions + resource file listings
3. **Execution:** Agent follows loaded instructions, uses provided tools (file_read, shell, etc.)

**Model flexibility (swap in one line):**
```python
# Claude via Bedrock
model = BedrockModel("us.anthropic.claude-sonnet-4-6-20260514")

# Amazon Nova
model = BedrockModel("amazon.nova-premier-v1:0")

# OpenAI
from strands.models import OpenAIModel
model = OpenAIModel("gpt-5.4")

# Ollama (local)
from strands.models import OllamaModel
model = OllamaModel("llama3")
```

**Tools available from strands-agents-tools:**
- `file_read` — read files (equivalent to Claude SDK's Read)
- `file_write` — write files (equivalent to Claude SDK's Write)
- `editor` — edit files (equivalent to Claude SDK's Edit)
- `shell` — execute shell commands (equivalent to Claude SDK's Bash)
- `http_request` — HTTP requests (equivalent to Claude SDK's WebFetch)
- `python_repl` — execute Python code
- `retrieve` — RAG retrieval

**Multi-agent patterns:**
```python
from strands import Agent, Graph, Swarm

# Graph: explicit orchestration (like daily-advisor dispatching sub-agents)
graph = Graph(agents=[macro_agent, portfolio_agent, risk_agent], flow="parallel")

# Swarm: dynamic handoffs between agents
swarm = Swarm(agents=[classifier, specialist_a, specialist_b])
```

**Container dependencies:** Python 3.13 only. No Node.js. No Claude CLI. ~150MB image vs ~400MB for Claude Agent SDK.

### Agent Skills Spec (VERIFIED — agentskills.io)

The SKILL.md format is a SHARED OPEN STANDARD used by both Strands and Claude Agent SDK.

**Required frontmatter:**
```yaml
---
name: call-prep
description: Prepare talking points and a slide deck for an upcoming customer call. Use when the user asks to prep for a call or meeting.
---
```

**Optional frontmatter:** `allowed-tools`, `metadata`, `license`, `compatibility`

**Body:** Markdown instructions. Steps, examples, edge cases. Agent loads full body on activation (progressive disclosure).

**Directory structure:**
```
call-prep/
├── SKILL.md          # Required: metadata + instructions
├── scripts/          # Optional: executable code
├── references/       # Optional: documentation
└── assets/           # Optional: templates, resources
```

**CRITICAL:** Skills reference tools by behavior ("read the file", "run the script"), not by tool name. The skill says "Read `accounts/{name}/notes.md`" — in Claude SDK that's the `Read` tool, in Strands that's `file_read`. The skill INSTRUCTIONS are portable. The agent interprets them using whatever tools are available.

### S3 Files (VERIFIED — launched April 2026)

Amazon S3 Files mounts S3 buckets as native file systems using EFS.

**Key facts:**
- Mount via "mount target" in VPC → network endpoint
- Up to 25,000 concurrent connections
- Supported on: EC2, ECS, EKS, Fargate, Lambda
- Both file system AND S3 object APIs work on same data
- Setup: S3 console → File systems → Create → select bucket → create mount target

**For this project:** Create S3 bucket `kiro-sales`. Mount at `/mnt/s3/kiro-sales/` in the ECS container. Agent reads/writes via standard file operations.

### Workspace Merging (Symlinks — V1)

Each user request creates a merged workspace:
```
/tmp/workspace-{user_id}/
├── CLAUDE.md           → symlink to /mnt/s3/kiro-sales/shared/CLAUDE.md
├── skills/             → symlink to /mnt/s3/kiro-sales/shared/skills/
├── scripts/            → symlink to /mnt/s3/kiro-sales/shared/scripts/
├── accounts/           → symlink to /mnt/s3/kiro-sales/users/{user_id}/accounts/
├── outputs/            → symlink to /mnt/s3/kiro-sales/users/{user_id}/outputs/
└── data/               → symlink to /mnt/s3/kiro-sales/users/{user_id}/data/
```

Skills are shared (read-only). Data is personal (read-write). Agent sees one flat workspace.

---

## Product Architecture

```
┌──────────────────────────────────────────────────────────┐
│                     WEB APP (Next.js on Vercel)          │
│                                                          │
│  ┌─────────────┐  ┌──────────────────────────────────┐   │
│  │ FILE PANEL  │  │  CHAT INTERFACE                  │   │
│  │             │  │                                  │   │
│  │ ▾ System    │  │  AI Elements message rendering   │   │
│  │   skills/   │  │  SSE streaming from harness      │   │
│  │   CLAUDE.md │  │  File artifact download cards    │   │
│  │             │  │                                  │   │
│  │ ▾ Personal  │  │                                  │   │
│  │   accounts/ │  │  ─────────────────────────────── │   │
│  │   outputs/  │  │  [Type a message...]      [Send] │   │
│  │ [Upload]    │  │                                  │   │
│  └─────────────┘  └──────────────────────────────────┘   │
└───────────┬──────────────────────┬───────────────────────┘
            │                      │
    ┌───────▼───────┐      ┌──────▼──────────────────┐
    │  S3 BUCKET    │      │  HARNESS (ECS + S3      │
    │  (kiro-sales) │      │  Files mount)           │
    │               │      │                          │
    │  /shared/     │      │  FastAPI + Strands SDK   │
    │    CLAUDE.md  │      │  AgentSkills plugin      │
    │    skills/    │◄─────│  file_read, shell tools  │
    │    scripts/   │      │  BedrockModel (Claude)   │
    │               │      │                          │
    │  /users/      │      │  Per-user workspace      │
    │    {id}/      │◄─────│  via symlinks            │
    │      accounts/│      │                          │
    │      outputs/ │      │  SSE streaming to        │
    │               │      │  frontend                │
    └───────────────┘      └──────────────────────────┘
```

---

## The Harness (Strands Version)

Replace the current Claude Agent SDK harness with Strands. Same endpoints, same SSE streaming, different runtime.

```python
# harness/server.py — Strands Agents version
import os, json, asyncio, time, tempfile, logging
from pathlib import Path
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from strands import Agent, AgentSkills
from strands.models import BedrockModel
from strands_tools import file_read, file_write, editor, shell, http_request

# Config
HARNESS_DIR = Path(__file__).parent
with open(HARNESS_DIR / "agent.config.json") as f:
    CONFIG = json.load(f)

SHARED_DIR = os.environ.get("SHARED_DIR", "/mnt/s3/kiro-sales/shared")
USERS_DIR = os.environ.get("USERS_DIR", "/mnt/s3/kiro-sales/users")
MODEL_ID = os.environ.get("MODEL_ID", "us.anthropic.claude-sonnet-4-6-20260514")

app = FastAPI(title="Kiro Sales Harness")
app.add_middleware(CORSMiddleware, allow_origins=CONFIG.get("cors_origins", ["*"]),
                   allow_methods=["*"], allow_headers=["*"])

logger = logging.getLogger("harness")
START_TIME = time.time()

def create_workspace(user_id: str) -> str:
    """Create a merged workspace with symlinks: shared/ + users/{id}/."""
    workspace = Path(tempfile.mkdtemp(prefix=f"workspace-{user_id}-"))
    shared = Path(SHARED_DIR)
    user = Path(USERS_DIR) / user_id

    # Symlink shared files (read-only)
    for item in ["CLAUDE.md", "skills", "scripts"]:
        src = shared / item
        if src.exists():
            os.symlink(src, workspace / item)

    # Symlink user files (read-write)
    user.mkdir(parents=True, exist_ok=True)
    for item in ["accounts", "outputs", "data"]:
        src = user / item
        src.mkdir(parents=True, exist_ok=True)
        os.symlink(src, workspace / item)

    return str(workspace)

def create_agent(workspace_dir: str) -> Agent:
    """Create a Strands Agent with skills loaded from the workspace."""
    model = BedrockModel(model_id=MODEL_ID, region_name="us-west-2")

    # Load skills from the workspace
    skills_dir = os.path.join(workspace_dir, "skills")
    plugins = []
    if os.path.isdir(skills_dir):
        plugins.append(AgentSkills(skills=skills_dir))

    # Read steering file as system prompt
    steering_path = os.path.join(workspace_dir, "CLAUDE.md")
    system_prompt = ""
    if os.path.isfile(steering_path):
        with open(steering_path) as f:
            system_prompt = f.read()

    return Agent(
        model=model,
        system_prompt=system_prompt,
        tools=[file_read, file_write, editor, shell, http_request],
        plugins=plugins,
    )

class ChatRequest(BaseModel):
    message: str
    user_id: str

@app.post("/chat")
async def chat(req: ChatRequest):
    workspace = create_workspace(req.user_id)
    agent = create_agent(workspace)

    async def stream():
        try:
            # Use Strands streaming
            async for event in agent.stream_async(req.message):
                if hasattr(event, 'data') and event.data:
                    yield f"data: {json.dumps({'type': 'content', 'content': event.data})}\n\n"
            yield f"data: {json.dumps({'type': 'done'})}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'content': str(e)})}\n\n"
        finally:
            # Cleanup workspace symlinks
            import shutil
            shutil.rmtree(workspace, ignore_errors=True)

    return StreamingResponse(stream(), media_type="text/event-stream")

@app.get("/skills")
async def list_skills():
    skills = []
    skills_dir = Path(SHARED_DIR) / "skills"
    if skills_dir.is_dir():
        for skill_md in sorted(skills_dir.glob("*/SKILL.md")):
            try:
                text = skill_md.read_text()
                if text.startswith("---"):
                    import yaml
                    parts = text.split("---", 2)
                    fm = yaml.safe_load(parts[1]) if len(parts) >= 3 else {}
                    skills.append({
                        "name": fm.get("name", skill_md.parent.name),
                        "description": fm.get("description", ""),
                    })
            except Exception:
                pass
    return {"skills": skills}

@app.get("/health")
async def health():
    return {"status": "ok", "shared_dir": SHARED_DIR, "uptime_seconds": round(time.time() - START_TIME, 2)}
```

**Container requirements:** Python 3.13 only. ~150MB image.

```dockerfile
FROM python:3.13-slim
RUN pip install --no-cache-dir strands-agents strands-agents-tools fastapi uvicorn[standard] pyyaml boto3
COPY server.py agent.config.json /app/harness/
WORKDIR /app
ENV SHARED_DIR=/mnt/s3/kiro-sales/shared
ENV USERS_DIR=/mnt/s3/kiro-sales/users
ENV MODEL_ID=us.anthropic.claude-sonnet-4-6-20260514
EXPOSE 8000
CMD ["uvicorn", "harness.server:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## User Experience

### Onboarding (< 5 minutes)
1. Open URL → sign in with SSO
2. See empty "Personal Files" panel + chat input
3. Upload accounts folder (drag-and-drop or zip)
4. Chat says: "I found 12 accounts. Try 'Prep me for my Acme Corp call'"

### Daily Use
1. Open app → left panel shows files, right panel is chat
2. Type: "Prep me for my call with Contoso tomorrow"
3. Agent reads account data → runs call-prep skill → generates talking points + deck
4. Output in chat. Files appear in "Personal > outputs/"
5. Download deck, join call

### After a Call
1. Drop meeting notes in chat or upload transcript
2. Agent updates account record, identifies next steps, drafts follow-up
3. Updated files in personal folder

---

## Components to Build

### Frontend (Next.js on Vercel)

| Component | File | Purpose | Research |
|-----------|------|---------|----------|
| Layout | `src/app/layout.tsx` | Two-panel: file browser (280px) + chat | Next.js 16 layout |
| Chat Page | `src/app/page.tsx` | useChat with SSE to harness | AI SDK v6 useChat |
| Chat Proxy | `src/app/api/chat/route.ts` | Proxies to harness with userId from Clerk | Pass userId from auth session |
| File List API | `src/app/api/files/route.ts` | S3 ListObjectsV2 for shared/ and users/{id}/ | AWS SDK v3 pattern |
| Upload API | `src/app/api/files/upload/route.ts` | Presigned URL for browser→S3 upload | PutObjectCommand + getSignedUrl |
| Download API | `src/app/api/files/[...path]/route.ts` | Presigned URL for download | GetObjectCommand + getSignedUrl |
| File Browser | `src/components/file-browser.tsx` | Two sections (System/Personal), tree view, upload/download | Client component |
| File Upload | `src/components/file-upload.tsx` | Drag-and-drop zone | react-dropzone or native |
| Artifact Card | `src/components/artifact-card.tsx` | Download card in chat for generated files | Custom message renderer |
| Auth | `src/proxy.ts` | Clerk middleware | clerkMiddleware() |

### Backend (Strands Harness on ECS)

| Component | File | Purpose |
|-----------|------|---------|
| Server | `harness/server.py` | FastAPI + Strands Agent + SSE streaming + workspace merger |
| Config | `harness/agent.config.json` | Model, cors, timeout settings |
| Dockerfile | `harness/Dockerfile` | Python 3.13 + Strands deps |
| Skills | `shared/skills/*/SKILL.md` | Kiro Sales skill files |
| Steering | `shared/CLAUDE.md` | Sales advisor persona + conventions |
| Tools | `shared/scripts/` | PowerPoint builder, CRM fetcher, etc. |

### Environment Variables

```
# Frontend (Vercel)
CLERK_SECRET_KEY=sk_...
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_...
NEXT_PUBLIC_CLERK_SIGN_IN_URL=/sign-in
NEXT_PUBLIC_CLERK_SIGN_UP_URL=/sign-up
AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...
AWS_REGION=us-east-1
S3_BUCKET=kiro-sales
HARNESS_URL=https://harness.internal.example.com

# Backend (ECS)
SHARED_DIR=/mnt/s3/kiro-sales/shared
USERS_DIR=/mnt/s3/kiro-sales/users
MODEL_ID=us.anthropic.claude-sonnet-4-6-20260514
AWS_REGION=us-west-2
```

---

## What We're NOT Building

- General-purpose agent platform
- Skills marketplace or skill authoring UI
- Claude Code / Cowork clone
- Real-time collaboration between users
- Mobile native app
- Salesforce integration (V2)

---

## Build Sequence

| Phase | What | Days | Chain of Thought |
|-------|------|------|-----------------|
| 1 | **Scaffold** — create-next-app, shadcn, Clerk, AWS SDK. Two-panel layout. | 1 | `npx create-next-app`. `npx shadcn@latest init`. Install Clerk, @aws-sdk/client-s3, @aws-sdk/s3-request-presigner. Create proxy.ts with clerkMiddleware(). |
| 2 | **Harness** — Rewrite server.py with Strands. Test locally. | 1 | `pip install strands-agents strands-agents-tools`. Write server.py per the code above. Test: `SHARED_DIR=./shared USERS_DIR=./users uvicorn harness.server:app`. |
| 3 | **Chat** — AI SDK useChat connected to harness via proxy route. SSE streaming. AI Elements. | 1 | WebSearch "AI SDK v6 useChat DefaultChatTransport". Install ai, @ai-sdk/react. Run npx ai-elements@latest. |
| 4 | **File browser** — Left panel. S3 list/upload/download. System + Personal sections. | 1 | Build file-browser.tsx. Use S3 ListObjectsV2 + presigned URLs. |
| 5 | **Workspace merger** — Symlink shared/ + users/{id}/ per request in harness. | 0.5 | Already in server.py code above. Test with real S3 data. |
| 6 | **Deploy** — Vercel for frontend, ECS for harness with S3 Files mount. | 1 | vercel deploy. Docker build + ECS task def with S3 Files volume. |
| 7 | **Test with 5 colleagues** | ongoing | Create accounts, upload data, gather feedback. |

---

## Success Metrics

- **Onboarding:** Signup to first useful output < 5 minutes
- **Daily use:** 10+ users, 3+ questions/day within 30 days
- **Value:** Call prep time 45 min → 5 min
- **The moment:** VP asks "How did you know all that?"

---

## Reference Links

- Strands Agents SDK: https://strandsagents.com/
- Strands GitHub: https://github.com/strands-agents/sdk-python
- Strands Tools: https://github.com/strands-agents/tools
- Strands Skills: https://strandsagents.com/docs/user-guide/concepts/plugins/skills/
- Agent Skills Spec: https://agentskills.io/specification
- Strands + AgentCore Starter: https://github.com/aws-samples/sample-strands-agentcore-starter
- Strands + AgentCore Reference: https://github.com/aws-samples/sample-strands-agent-with-agentcore
- Amazon S3 Files: https://aws.amazon.com/s3/features/files/
- AI SDK v6: https://sdk.vercel.ai/docs
- AI Elements: https://sdk.vercel.ai/docs/ai-sdk-ui/chatbot
- Clerk + Next.js: https://clerk.com/docs/quickstarts/nextjs
- Existing Claude Agent SDK harness (for reference): ~/agent-stack/harness/server.py
- Financial Engine (reference implementation): ~/financial-engine/
