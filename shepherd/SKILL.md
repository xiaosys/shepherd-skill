---
name: shepherd
description: "用 Planner–Executor 路由让 Sol 负责规划与最终验收、Luna 执行边界明确的实现和测试，并以证据控制 Terra 升级。当用户明确调用 $shepherd 或要求牧羊人／包工头／Shepherd／dispatcher、Sol→Luna、降低 Sol 执行成本，或需要带任务合同与验收 oracle 的子 Agent／multi-agent 协同时使用；普通解释、单点微改和一般 worktree 操作不使用。"
---

# Shepherd

本 Skill 是模型路由器、委派准入器和验收控制器。目标是在权限与质量门槛不降低的前提下，最小化得到一个 ACCEPTED 结果的预期成本；不要把 Agent 数量、并行度、原始 token 或代码量当作成果。

Skill 是提示级策略，不是硬隔离。真正的路由证据来自当前运行时能力、带 model override 的派发调用、Worker 回执和最终验收。

## 1. 先锁定真源、授权与运行时

规划或派发前：

1. 读取适用的系统、用户和 AGENTS.md；它们高于本 Skill。
2. 核对目标目录、真实 Git 根、分支、HEAD、dirty state、任务真源、验收标准和已有候选。外部 Agent／reviewer 必须先运行并回传 git rev-parse --show-toplevel，不得把输入的目标子目录当作 Git 根；未知改动不得被纳入、覆盖、清理或提交。
3. 查询当前运行时支持的 Agent 角色、模型覆盖、推理强度、上下文继承方式和并发槽，不从旧文档猜测。
4. 父任务的读写、联网、提交、推送、部署、真实数据和外部操作授权是所有子 Agent 的绝对上限。
5. 当前处于计划、审查或诊断模式时，只允许相应的只读委派；路由不会扩大执行权限。

Git 根、基线、授权、验收口径或 runtime capability 不可信时，先修复上下文或返回 BLOCKED，不派发实现。

## 2. 选择最小充分路由

优先判断任务能否由确定性工具、脚本或一次直接检查完成；“Luna 更便宜”本身不是启动 Agent 的理由。

| 模式 | 适用条件 | 路由 |
| --- | --- | --- |
| direct | 解释、只读小检查、单点微改，或委派成本不低于执行成本 | 主 Agent 直接完成 |
| routed | 有界实现或测试会占用较多上下文，且可定义独立合同与 oracle | Sol 规划 → 一个 Luna → Sol 验收 |
| parallel | 至少两个独立包，路径不重叠，各有 oracle，且并行能缩短关键路径 | Sol 协调 → 隔离 Workers → 串行集成 |

### 显式请求：严格路由锁

当用户明确要求“Sol 规划、Luna 执行”、牧羊人或等价分层模式时：

- 默认 policy=strict。Sol 在派发被运行时接受并形成 route_receipt 前，不得修改 Worker-owned paths。
- 必须使用运行时真实支持的 model 与 reasoning_effort override；需要隔离父上下文时使用 fork_turns=none，只传合同和必要真源路径。
- 如果主 Agent 不是用户要求的 Planner、模型或 reasoning_effort 覆盖不可用、调用被降级，或 model_evidence 只能写 unknown，返回 ROUTING_BLOCKED。
- 只有用户另行授权 fallback，Sol 才能接管实现；不得静默用 Sol 完成后声称已分流。
- Sol 可以继续做只读规划、diff 审查、最终裁决及纯协调性的 Git 操作；需要修改实现或解决代码冲突时交回 Worker。

### 隐式触发：自适应收益门

隐式命中本 Skill 时，仅在下列收益明显覆盖任务说明、等待、重试和集成成本后选择 routed：

- 有界执行可从 Sol 上下文中隔离；
- 搜索、日志或测试输出较大；
- owned paths 和验收 oracle 清楚；
- 不同上下文或模型可能改变结果。

否则选择 direct，并用一句话说明委派为何不划算。并行只优化关键路径，不自动代表更省钱。

## 3. 分开 Agent 角色与模型

| 工作 | Agent 角色 | 默认模型 |
| --- | --- | --- |
| 有界只读搜索、范围核对、大输出归纳 | explorer | gpt-5.6-luna |
| 有界实现、测试、迁移或文档 | worker | gpt-5.6-luna |
| 已证实超出 Luna 的复杂执行 | worker | gpt-5.6-terra |
| 架构、权限、高风险决策和最终验收 | 主 Agent／fresh reviewer | Sol |

- 模型名以当前运行时为准；用户指定不可用模型时报告限制，不静默替换。
- Luna Agent（explorer 与 worker）默认使用 reasoning_effort=high，写入 Worker 不得低于 high；用户明确指定其他强度或运行时不支持时除外。xhigh／max 只在代表性任务证明有质量收益时使用；非 Luna 执行者仍使用最低充分强度。
- Terra 可在已有同类、同环境的代表性失败证据成立时直接选择；否则必须先排除合同、上下文、环境、权限和写入冲突。第一次失败或文件较多不是升级证据。

## 4. 派发前读取有界合同

选择 routed 或 parallel 后，必须先读取 [references/routed-contracts.md](references/routed-contracts.md)，填写 route_receipt 与任务合同，再派发。

共同边界：

- 默认一个活跃写入 Worker、只允许一层委派；Worker 不再递归派 Agent。
- 每个写入者拥有互不重叠的精确路径；同一文件、迁移序列、schema 或共享契约同时只有一个 owner。
- 告知 Worker 它不是代码库中的唯一执行者，不得回退、整理或覆盖他人的改动。
- 普通返工优先 follow-up 原 Worker；不要并行增加第二个写入者。
- 不占满所有槽位，为验收、恢复或用户新任务保留容量。
- 多候选集成时，若可用则使用 worktree-release-coordination；否则仍由唯一协调者串行集成。Worker 不合并、变基或解决共享冲突。
- 不自动删除 worktree、分支、备份或用户文件。

## 5. 用证据验收，不用 Agent 信心

- 候选必须绑定 git rev-parse --show-toplevel 的真实输出、base SHA、candidate SHA、changed paths、实际检查、未测项和风险。
- reviewer 必须先回报实际 Git root、HEAD、dirty state 和检查；错根、错 SHA、空输出、工具错误、旧工作树或只复述实现说明均不是 PASS。
- 命令退出 0 只证明该命令成功；验收要求产物或下游行为时必须检查对应结果。
- Worker 分支通过不代表集成树通过。只有精确 integrated SHA 完成所需聚焦验证、回归和最终门禁后，才可 ACCEPTED。
- 低等级证据不得升级为 staging、pilot、production 或其他更高等级 GO。
- 验证一个足以改变结论的最小反例；若出现未知 dirty state、目标 SHA 改变、验收冲突或无法解释的失败，停止接受新候选。

## 6. 失败、沟通与成本

按原因处理失败：缺上下文由 Sol 补真源并 follow-up；合同模糊由 Sol 重写；环境错误先修环境；写入冲突先停止并发；工具或 reviewer 故障保持 unverified；能力不足按 reference 的证据门升级 Terra。

只在真源确定、派发成功、候选形成、审查改变方向、集成验证结束或真正阻塞时更新用户。完成 stop_after 后停止，不自动启动下一包。

若运行时提供 usage，按模型记录 input、cached input、uncached input、cache-write input、output、重试和验收结果。没有可比基线时固定报告“路由已执行，节省量未测”，不得用调用了 Luna、并行数或 API 标价推断 Codex 账户节省。
