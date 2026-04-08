# Architecture (locked)

## All AWS — No External Dependencies

```
                    ┌─────────────────┐
                    │   CloudFront    │
                    │   (CDN + SSL)   │
                    └────────┬────────┘
                             │
              ┌──────────────┼──────────────┐
              │              │              │
     ┌────────▼───────┐   ┌─▼──────────────────┐
     │  Frontend      │   │  AgentCore Runtime  │
     │  (ECS Fargate  │   │  (managed agent     │
     │   or Amplify)  │   │   hosting)          │
     │               │   │                     │
     │  Next.js SSR  │   │  Strands SDK        │
     └────────────────┘   │  AgentSkills        │
                          │  Memory (STM+LTM)   │
                          │  Identity            │
                          │  Observability       │
                          └──────┬───────────────┘
                                 │
                          ┌──────▼───────┐
                          │  S3 + S3     │
                          │  Files mount │
                          │              │
                          │  /shared/    │
                          │  /users/     │
                          └──────────────┘
```

## Why AgentCore Runtime (not ECS Fargate directly)

AgentCore Runtime is PURPOSE-BUILT for hosting AI agents on AWS. It provides:
- **Managed containerized execution** — no ECS cluster management
- **Built-in Memory** — short-term (session) + long-term (cross-session) memory, managed
- **Built-in Identity** — auth for agents accessing AWS services + third-party APIs
- **Built-in Observability** — traces, metrics, logging without custom instrumentation
- **Built-in Policy** — fine-grained control over what actions agents can take
- **S3 Files support** — native volume mounting for agent workspaces
- **Strands-native** — designed to run Strands agents (same SDK that powers Kiro, Amazon Q)
- **Deploy with CLI:** `agentcore configure && agentcore deploy` — handles ECR, IAM, scaling

Using raw ECS Fargate means building all of the above yourself. AgentCore gives it for free.

## Two Services
- **Frontend:** Next.js SSR on ECS Fargate (or AWS Amplify for simpler deploy)
- **Agent:** Strands agent on AgentCore Runtime with S3 Files workspace

## Agent Entry Point (AgentCore pattern)

```python
# harness/main.py — AgentCore entry point
from bedrock_agentcore.runtime import BedrockAgentCoreApp
from strands import Agent, AgentSkills
from strands.models import BedrockModel
from strands_tools import file_read, file_write, editor, shell

app = BedrockAgentCoreApp()

@app.entrypoint
def invoke(payload):
    user_id = payload.get("user_id", "default")
    workspace = create_workspace(user_id)  # symlinks shared/ + users/{id}/

    model = BedrockModel("us.anthropic.claude-sonnet-4-6-20260514")
    skills = AgentSkills(skills=f"{workspace}/skills/")

    agent = Agent(
        model=model,
        system_prompt=open(f"{workspace}/CLAUDE.md").read(),
        tools=[file_read, file_write, editor, shell],
        plugins=[skills],
    )

    result = agent(payload.get("prompt", "Hello"))
    return {"result": str(result)}

if __name__ == "__main__":
    app.run()
```

Deploy: `agentcore configure -e harness/main.py && agentcore deploy`

## S3 Bucket Structure
```
s3://kiro-sales-{account-id}/
├── shared/                    # Maintained by Christian
│   ├── CLAUDE.md              # Agent steering
│   ├── skills/                # SKILL.md files
│   └── scripts/               # Tools
└── users/                     # Per-user data
    ├── user_abc123/
    │   ├── accounts/
    │   ├── outputs/
    │   └── data/
    └── ...
```

## Per-User Workspace Merging
Agent creates symlinks per request:
```
/tmp/workspace-{user_id}/
├── CLAUDE.md       → /mnt/s3/shared/CLAUDE.md
├── skills/         → /mnt/s3/shared/skills/
├── scripts/        → /mnt/s3/shared/scripts/
├── accounts/       → /mnt/s3/users/{user_id}/accounts/
├── outputs/        → /mnt/s3/users/{user_id}/outputs/
└── data/           → /mnt/s3/users/{user_id}/data/
```

## Infrastructure (in infra/)

### Option A: AgentCore CLI (recommended for speed)
```bash
pip install bedrock-agentcore-toolkit
agentcore configure -e harness/main.py
agentcore deploy
```
AgentCore handles: ECR, IAM, container build, scaling, memory, observability.

### Option B: CDK (for full control)
1. **StorageStack** — S3 bucket + S3 Files filesystem + VPC + mount targets
2. **AgentStack** — AgentCore Runtime deployment (uses @aws-cdk/aws-bedrock-agentcore-alpha)
3. **FrontendStack** — ECS Fargate or Amplify for Next.js SSR + CloudFront
4. **AuthStack** — Cognito user pool (or Clerk)

Deploy: `cd infra && cdk deploy --all`

**Start with Option A** (agentcore CLI). Switch to CDK when you need custom infrastructure.

## Data Flow
1. User → CloudFront → Next.js frontend
2. Frontend POST /api/chat → AgentCore Runtime endpoint
3. AgentCore creates agent instance, mounts S3 Files workspace
4. Strands Agent loads skills via AgentSkills, reads user data
5. Agent streams response back
6. AgentCore Memory persists conversation context automatically
