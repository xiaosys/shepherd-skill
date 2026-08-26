# Shepherd Skill

一个证据驱动的 Planner–Executor Skill：Sol 负责真源、规划和最终验收，Luna 承担边界明确的实现与测试，Terra 只在证据表明 Luna 不足时介入。

它优化的是得到一个可验收结果的预期成本，不是 Agent 数量或原始 token。显式要求 Sol→Luna 时采用严格路由锁；无法证明 model override 已生效，就在实现写入前停止。隐式触发时则比较委派收益与交接成本，小任务仍可 direct。

默认低风险任务由主 Sol 验收，不收取固定 reviewer 税；只有用户明确要求，或涉及权限／安全／隐私、破坏性数据、生产／发布边界、共享 schema／API／迁移、并发／幂等或多个候选共享契约集成时，才启用 fresh、只读、独立 reviewer。大工件仅在需要截断、反复传递或明显挤占上下文时使用 `local_files`，且必须由父任务提供精确绝对 `authorized_handoff_root`；生成前校验 realpath，拒绝 `..`、越界或 symlink 跳转，不默认推导 `~/.codex`、`/tmp` 或任何 Git 根外目录，小工件 inline，实际回执再绑定 manifest 与候选／审查 diff hash。工件不得含密钥或无关隐私。Shepherd 没有 Superpowers 运行时依赖。

## 安装

Codex 的用户级 Skill 入口位于 ~/.agents/skills。推荐保留 Git checkout，并用软链加载，避免维护复制副本：

~~~bash
git clone https://github.com/xiaosys/shepherd-skill.git
mkdir -p "$HOME/.agents/skills"
ln -s "$(pwd)/shepherd-skill/shepherd" "$HOME/.agents/skills/shepherd"
~~~

如果目标已存在，先确认来源，不要直接覆盖。Codex 通常会自动发现变更；未出现时再重启或刷新。

## 使用

~~~text
$shepherd

请让 Sol 读取真源、定义合同并做最终验收，把边界明确的实现和测试交给 Luna。
~~~

主要模式：

- direct：任务很小，委派成本不划算；
- routed：Sol 规划 → 一个 Luna Worker → Sol 验收；
- parallel：仅对真正独立、路径不重叠且各有 oracle 的包并行。

没有可比 usage 基线时，本 Skill 只报告“路由已执行，节省量未测”，不会根据 API 单价或调用了 Luna 宣称节省比例。

## English summary

Shepherd is an evidence-driven Planner–Executor skill. Sol owns source-of-truth reading, planning, risk decisions, and final acceptance; Luna performs bounded implementation and tests; Terra is reserved for evidence-backed capability gaps.

Explicit Sol-to-Luna requests use a strict pre-write routing lock. Implicit activation remains adaptive so tiny tasks are not burdened with delegation overhead. Savings are reported only when comparable usage evidence exists.

Low-risk work is accepted by the main Sol without a fixed reviewer tax. A fresh, read-only, independent reviewer is required only when explicitly requested or when semantic risk involves permissions/security/privacy, destructive data, production or release boundaries, shared schemas/APIs/migrations, concurrency/idempotency, or integrating multiple candidates under a shared contract. Large artifacts use `local_files` only when inline transfer would require truncation, repeated handoff, or materially crowd the context; the parent must provide an exact absolute `authorized_handoff_root`, realpath validation rejects `..`, escapes, and symlink traversal, no `~/.codex`, `/tmp`, or Git-root-outside directory is inferred, and candidate/review diff hashes and manifests are bound only in actual receipts. Artifacts must contain no secrets or unrelated private data. Shepherd has no Superpowers runtime dependency.

Install the shepherd directory under ~/.agents/skills, preferably as a symlink to a Git checkout.

## License

MIT. See [LICENSE](LICENSE).
