# Shepherd Skill

An evidence-driven Planner–Executor Skill that reduces expensive-model execution cost: Sol plans and accepts, Luna executes bounded work, and Terra is used only for a confirmed capability gap.

## Install

Copy or clone the `codex-shepherd` directory into your Codex skills directory:

```bash
git clone https://github.com/xiaosys/shepherd-skill.git
cp -R shepherd-skill/codex-shepherd ~/.codex/skills/
```

Restart or refresh Codex so it discovers the Skill.

## Scope

Use it when Sol should retain planning, risk decisions, and final acceptance while Luna performs bounded implementation and tests. It also supports multi-agent work, worktree coordination, and independent review. Tiny tasks remain direct when delegation would cost more than execution.

The optimization target is cost-weighted model usage, especially Sol uncached input and output—not raw token count alone. Without usage measurements and a baseline, the Skill reports routing as implemented but savings as unmeasured.

## License

MIT. See [LICENSE](LICENSE).
