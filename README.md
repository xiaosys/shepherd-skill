# Shepherd Skill

An evidence-driven Skill for deciding whether a task merits delegation, coordinating subagents and Git worktrees, and accepting only verifiable results.

## Install

Copy or clone the `codex-shepherd` directory into your Codex skills directory:

```bash
git clone https://github.com/xiaosys/codex-shepherd-skill.git
cp -R codex-shepherd-skill/codex-shepherd ~/.codex/skills/
```

Restart or refresh Codex so it discovers the Skill.

## Scope

Use it for bounded multi-agent work, worktree coordination, or independent review. It deliberately recommends staying single-agent when delegation would add more coordination cost than value.

## License

MIT. See [LICENSE](LICENSE).
