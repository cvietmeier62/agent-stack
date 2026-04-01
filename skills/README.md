# Portable Skills

Portable skills that work in any agent. Copy any skill folder into your agent's `.claude/skills/` directory.

## Available Skills

| Skill | Description |
|-------|-------------|
| `panel-discussion/` | Assemble expert panels to stress-test decisions through structured debate. The universal thinking tool. |
| `agent-builder/` | Meta-skill that designs and scaffolds new AI agents from a natural language description. |

## Usage

```bash
# Copy a skill into your agent
cp -r skills/panel-discussion/ my-agent/.claude/skills/panel-discussion/
```

The skill will be automatically available as a slash command in Claude Code.
