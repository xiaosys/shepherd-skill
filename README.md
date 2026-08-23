# Shepherd Skill

一个证据驱动的 Planner–Executor Skill：Sol 负责真源、规划和最终验收，Luna 承担边界明确的实现与测试，Terra 只在证据表明 Luna 不足时介入。

它优化的是得到一个可验收结果的预期成本，不是 Agent 数量或原始 token。显式要求 Sol→Luna 时采用严格路由锁；无法证明 model override 已生效，就在实现写入前停止。隐式触发时则比较委派收益与交接成本，小任务仍可 direct。

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

Install the shepherd directory under ~/.agents/skills, preferably as a symlink to a Git checkout.

## License

MIT. See [LICENSE](LICENSE).
