# Step 9: Finalize

Create remaining files, copy skills, init git, push to GitHub.

## Actions

1. Create `.gitignore`:
```
node_modules/
.next/
.env*.local
*.tsbuildinfo
__pycache__/
*.pyc
.venv/
cdk.out/
```

2. Copy portable skills:
```bash
cp -r ~/agent-stack/skills/panel-discussion {project}/.claude/skills/
```

3. Create any empty directories needed:
```bash
mkdir -p {project}/src
mkdir -p {project}/docs
```

4. Git init and push:
```bash
cd {project}
git init && git branch -m main
git add -A
git commit -m "Initial project spec: {one-line description}

{N} files, {M} tasks across {P} phases.
Agent-executable spec for multi-session Claude Code.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>"

gh repo create {project-name} --private --source . --push
```

5. Present to Christian:
```
Project: {name}
GitHub: {url}
Files: {count}
Tasks: {count} across {phases} phases
Estimated sessions: {count}

Clone anywhere, open in Claude Code, it starts building Task 0.1.
```
