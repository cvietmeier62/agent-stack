# Stack Decisions (locked)

## Runtime: Strands Agents SDK
- `pip install strands-agents strands-agents-tools`
- Agent = BedrockModel + system_prompt + tools + AgentSkills plugin
- Model: BedrockModel("us.anthropic.claude-sonnet-4-6-20260514") — swappable
- Tools: file_read, file_write, editor, shell, http_request from strands_tools
- Skills: AgentSkills(skills="./skills/") per agentskills.io spec
- Container: Python 3.13 only. NO Node.js. NO Claude CLI.

## Storage: Amazon S3 + S3 Files
- S3 Files is NEW (April 7, 2026). Mounts S3 buckets as native file systems.
- ALWAYS WebSearch "Amazon S3 Files" before writing S3 Files code
- Bucket: kiro-sales-{account-id}
- shared/ = skills, steering, scripts (read-only)
- users/{user_id}/ = accounts, outputs, data (read-write)
- Frontend: presigned URLs for upload/download
- Harness: S3 Files mount at /mnt/s3/ on AgentCore Runtime

## Frontend: Next.js 16
- App Router. Server Components default.
- proxy.ts for auth (NOT middleware.ts)
- AI SDK v6 + AI Elements for chat rendering
- shadcn/ui. Dark mode. JetBrains Mono.

## Auth: Amazon Cognito
- Hosted UI for sign-in/sign-up
- Or Clerk if faster to implement — research both, pick one
- userId maps to S3 prefix users/{userId}/

## Deploy: All AWS
- **Agent: AgentCore Runtime** (NOT raw ECS Fargate)
  - Managed agent hosting: built-in memory, identity, observability, policy
  - `pip install bedrock-agentcore-toolkit && agentcore configure && agentcore deploy`
  - Handles: ECR, IAM, container build, scaling automatically
- **Frontend: AWS Amplify** (fast) or ECS Fargate + CloudFront (control)
- **Storage: S3 + S3 Files mount** for AgentCore workspace
- Reference: https://github.com/aws-samples/sample-strands-agentcore-starter
- Optional CDK in infra/ for full IaC control
