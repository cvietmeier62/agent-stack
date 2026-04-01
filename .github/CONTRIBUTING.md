# Contributing to Agent Stack

Thanks for your interest in contributing! Here's how to help.

## Ways to Contribute

### Add Example Agents
The best contribution is a new example agent in `examples/`. Follow the pattern:
- `CLAUDE.md` steering file
- `.claude/skills/` with 3-5 skills
- `data/strategy.json` with user preferences
- `README.md` explaining the agent

### Improve Documentation
Found something unclear? Fix it. The docs are in `docs/`.

### Add Portable Skills
Skills in `skills/` work with ANY agent. If you've built a skill that's domain-agnostic (like panel-discussion or agent-builder), contribute it.

### Report Issues
If the harness doesn't work as documented, open an issue with:
- What you expected
- What happened
- Your OS + Python version + Node.js version

## Guidelines

- Keep it simple. The whole point is markdown over code.
- Test your skills in Claude Code before contributing.
- Document everything. If someone can't understand your skill from the SKILL.md alone, it needs work.
- Follow the existing patterns. Look at the financial advisor architecture in THESIS.md for the reference.

## License

MIT. Your contributions are too.
