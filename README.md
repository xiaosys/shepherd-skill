# Shepherd Skill

> Plan clearly. Delegate economically. Verify with evidence.

Astra 规划与最终验收，低成本子 Agent 执行有界工作。目标是降低完成并验收的总成本，而不是增加 Agent 数量。

## 快速使用

~~~text
使用 $shepherd：Astra 做计划和验收，主动把有界实现、检索和测试交给便宜模型。
保留本项目审批、写入边界及验收门；没有新变化或失败，不重复已经有效的检查。
~~~

- 明确的只读提取、定位、摘要：Luna medium；简单低风险时可 low。
- 有界实现、修复和测试：Luna high。
- 高耦合、未知根因或有证据的能力缺口：Terra high。
- 高风险独立只读审查与更困难的执行：Sol high。
- Astra 保留当前主模型档位，负责规划、关键判断与最终验收。

以上是默认起点，精确路由及调整规则以 [SKILL.md](shepherd/SKILL.md) 为准。用户或项目指定模型时遵守指定；只有实际运行时支持的 model/effort 才能调用，不自动更改应用模型设置。

## 节省来自哪里

- 非平凡且可验收的执行优先委派；微小任务直接完成，不逐文件拆 Agent。
- 新 Worker 接收最小合同，不默认继承完整聊天；follow-up 只传变化和新证据。
- 执行者只回传摘要和必要证据，主 Agent 不重复扫描或执行整个子任务。
- 检查范围由合同和仓库决定，不默认跑全套；已有效的检查不重复。
- 同一目标默认一次初始执行、至多一次定向返修，无进展则重新判断，不靠换 Agent 重置次数。

子 Agent 仍消耗账户额度。没有同类可比基线和实际 usage 时，只报告“路由已执行，节省量未测”。

## 可选 Jev 预路由

Shepherd 可以在边界模糊、批量重复或路由经常摇摆的任务上调用 TypeSafe Jev，先把任务判为 `direct`、`routed`、`parallel` 或 `planner_review`，并返回概率和置信度。它是可选建议器，不是新的 Planner 或 Executor：权限、严格模型锁、review 门和最终验收仍由 Shepherd 的确定性规则控制。

官方没有单独发布 Jev CLI。本仓库提供一个零依赖适配命令 [jev_route.py](shepherd/scripts/jev_route.py)：默认只生成请求并输出到本地；只有显式加 `--execute`，且环境中已有 `TYPESAFE_API_KEY` 或 macOS 钥匙串存在 `typesafe-ai/api_key` 时才调用 `jev-latest`。完整输入边界、失败回退和校准方法见 [Jev 路由说明](shepherd/references/jev-routing.md)。

## 协作边界

Sage/Hermes 已是项目调度者时，Codex 只组织当前合同内的实现与检查，不另起项目计划或重复派单。默认一个活跃写入 Worker，可以与独立只读任务并行；多写入需要获准的隔离工作区和互不冲突的契约。Worker 不递归委派。

低风险由主 Planner 验收；权限、安全、隐私、破坏性数据、生产/发布、共享 schema/API/迁移、并发/幂等及共享契约集成，保留 fresh、独立、只读 reviewer 和真实候选绑定。审查不能替代 Sean 的审批。

[完整合同与证据](shepherd/references/routed-contracts.md) 仅供写入候选、高风险审查和集成使用；普通只读辅助使用 Skill 中的 brief 合同。

## 安装与维护

保留单一 Git 真源，通过当前运行时支持的符号链接入口加载 shepherd 目录。已有目标先核对来源；遵守用户的安装路径、审批、备份及提供方管理规则，不覆盖已有副本或全库清理。Skill 文本不能强制切换主模型，也不是文件系统权限隔离。

## English summary

Shepherd defaults to an Astra planner and low-cost, explicitly selected executors. Delegate useful bounded work proactively, keep tiny work direct, return concise evidence, and avoid repeating valid tests. Preserve project approvals, exact candidate provenance, independent high-risk review, and a single owner per write scope. Model/effort defaults are workload-based starting points, not a savings guarantee.

## License

MIT. See [LICENSE](LICENSE).
