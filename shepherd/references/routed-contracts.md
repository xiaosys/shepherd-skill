# Routed／Parallel 合同与证据

只在已经选择 routed 或 parallel 时读取本文件。它定义 Planner 派发前的路由回执、Worker 合同、候选证据、Terra 升级门和最终报告；不要把这些模板复制进每个项目的长期真源。

## 1. 路由回执

Planner 在任何 Worker-owned path 被修改前记录：

~~~yaml
route_receipt:
  trigger: explicit | implicit
  policy: strict | adaptive
  mode: routed | parallel
  planner_model: 实际模型或 unknown
  requested_executor: 精确模型
  requested_reasoning_effort: Luna 默认 high；其他模型写精确请求值
  agent_role: explorer | worker | default
  model_evidence: accepted_override | runtime_report | unknown
  dispatch_id: 运行时返回的 Agent／任务 ID
  fallback_authorized: false | 用户明确授权的范围
~~~

证据解释：

- accepted_override：运行时工具契约保证 model 与 reasoning_effort override，并且本次带精确请求值的调用已被接受；
- runtime_report：运行时提供了可核对的实际模型与 reasoning_effort 字段；
- unknown：模型或 reasoning_effort 任一项只有自述、猜测、旧文档，或工具可能静默降级。

显式 strict 路由不接受 model_evidence=unknown。调用失败或无法证明覆盖时返回 ROUTING_BLOCKED，不由 Planner 写 owned paths。

## 2. 最小任务合同

~~~yaml
goal: 这一个子任务必须交付的结果
target_root: 绝对目标目录；与真实 Git 根一致
base_sha: 共同基线；非 Git 任务写 not_applicable
mode: read_only | write
target_modules: 目标模块
owned_paths: 唯一写入边界；只读任务写 read_only
depends_on: 前置包或 none
allow_shared_contract_changes: false | 明确列出允许项
do_not_touch: 禁止路径、契约、数据和外部系统
acceptance: 可观察、可判定的完成条件
verification: 必须执行的命令或人工检查
stop_after: 完成本包后停止
return: candidate_sha、changed_paths、checks、unrun、risks
~~~

合同只携带目标、约束、必要真源路径、验收 oracle 和输出格式。不要传完整聊天、Planner 的隐藏推理、实现者辩护或预期答案。

Worker 必须知道：

- 它不是代码库中的唯一执行者，不得回退或整理他人的改动；
- 不得越过 owned_paths 或扩大父任务权限；
- 发现共享契约修改需求时停止并报告，不自行扩范围；
- 完成 stop_after 后停止，不启动下一包；
- 无法完成全部验收时返回 PARTIAL 或 BLOCKED，不伪装 CANDIDATE。

## 3. 候选回执

~~~yaml
status: CANDIDATE | PARTIAL | BLOCKED
executor_model: 实际模型或 unknown
executor_reasoning_effort: 实际强度或 unknown
model_evidence: accepted_override | runtime_report | unknown
actual_root: git rev-parse --show-toplevel 的原始输出；非 Git 任务写 not_applicable
base_sha: 实际基线
candidate_sha: 候选提交；无提交写 uncommitted
changed_paths: 实际路径
checks: 命令、退出状态、关键产物和结果
unrun: 未运行要求及原因
risks: 已知限制、残余风险和外部门
~~~

Planner 对照实际 diff、Git 状态和产物，不把回执本身当成事实。完整测试套件默认由 Executor 在精确 candidate SHA 上运行一次；Planner 核对日志或产物并运行必要的聚焦检查或最小反例。只有 SHA、迁移头、依赖或环境改变时才重复完整门禁。

## 4. Terra 升级证据

默认先由 Sol 收紧合同并交给 Luna。以下两种情况才可选 Terra：

1. 已有同类任务、同类环境和相同 oracle 的代表性证据，足以证明 Luna 的预期重试成本高于直接使用 Terra；
2. 本次 Luna 失败后，以下字段全部成立。

~~~yaml
failed_contract: 失败的精确合同
reproduction_command: 同合同、同环境下的复现命令；非命令任务写可复现步骤
failure_signature: 稳定错误或缺失行为
excluded_causes:
  context: 已排除的证据
  contract: 已排除的证据
  environment: 已排除的证据
  permission: 已排除的证据
  conflict: 已排除的证据
why_luna_is_insufficient: 能力不足而非偶发失败的依据
~~~

缺任一字段、第一次失败、文件较多或 Planner 不满意都不足以升级。相同失败原因连续出现两次时，停止重复路线，回到真源、合同和假设重新分类。

## 5. 并行与集成

- parallel 的每个包必须有独立 owned_paths、独立 oracle 和明确 depends_on。
- 共享 schema、公共接口、迁移序列或同一文件不能并行写；把它们串行化或交给唯一 owner。
- 多写入候选使用隔离 worktree，唯一协调者按依赖顺序集成。
- Worker 不在协调 worktree 合并、变基或解决冲突。
- 集成冲突需要实现判断时，交回原 Worker；strict 模式下 Sol 不亲自修改实现。

## 6. 接受状态与证据等级

~~~text
PLANNED → RUNNING → CANDIDATE → INTEGRATED → ACCEPTED
                    ↘ BLOCKED | SUPERSEDED
~~~

测试、review、外部门和 release boundary 是证据字段，不扩展成状态。只有精确 integrated SHA 通过要求的最终门禁才能 ACCEPTED。

始终区分：

- 本地／合成验证；
- 开发候选；
- staging 或公司环境；
- 真实 pilot；
- production。

较低等级证据不授权更高等级结论。进度按通过的验收单位、证据包和外部门计算，不按 Agent 数量、代码量、聊天时长或未定义百分比计算。

## 7. 最终报告

~~~text
Outcome: ACCEPTED | PARTIAL | BLOCKED
Mode / routing: direct | Sol → Luna → Sol | parallel
Route evidence: trigger、policy、requested executor／reasoning_effort、model evidence、fallback
Baseline / final SHA: 精确值或 not_applicable
Accepted work: 候选和范围
Verification: 实际检查、关键产物和结果
Usage evidence: input、cached、uncached、cache-write、output、retries，或 unmeasured
Unverified: 未测项与外部门
Release boundary: local | staging | pilot | production
Next: 一个具体动作或 none
~~~

没有同类基线或运行时 usage 时，Usage evidence 写 unmeasured，并明确“路由已执行，节省量未测”。不得把 API 单价、调用了 Luna 或并行数量换算成 Codex 账户节省比例。
