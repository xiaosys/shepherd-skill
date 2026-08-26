# Routed／Parallel 合同与证据

只在已经选择 routed 或 parallel 时读取本文件。它定义 Planner 派发前的路由回执、Worker 合同、候选证据、Terra 升级门和最终报告；不要把这些模板复制进每个项目的长期真源。

## 1. 路由回执

Planner 在任何 Worker-owned path 被修改前记录：

~~~yaml
route_receipt:
  run_id: 派发前生成的唯一运行 ID
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
  review_policy: none | explicit | semantic_risk
  review_required: true | false
  review_triggers: [] | 触发 reviewer 的语义风险或用户要求
  handoff_mode: inline | local_files
  handoff_dir: local_files 使用的绝对目录 | not_applicable
  authorized_handoff_root: local_files 时父任务明确授权的绝对目录 | not_applicable
  handoff_reason: inline 或启用 local_files 的可核验理由
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
artifact_handoff:
  mode: inline | local_files
  condition: 仅当工件大到需截断、反复传递或明显挤占主上下文时才可 local_files；否则 inline
  run_id: 与 route_receipt 相同的唯一运行 ID
  paths: 预期的绝对路径列表；实际工件 manifest 在 candidate receipt 生成
  authorized_handoff_root: local_files 时父任务明确授权的绝对目录；inline 写 not_applicable
  path_validation: 生成前 realpath 必须位于 authorized_handoff_root 内；拒绝 ..、越界和 symlink 跳转
  contents: 不得含密钥或无关隐私
  cleanup: never_automatic
return:
  summary: 必须返回的短摘要，即使使用 local_files
  candidate_sha: 候选提交或 uncommitted
  changed_paths: 实际路径
  artifacts_manifest: 工件 path、sha256、bytes 与 run_id；无工件写 []
  checks: 实际检查
  unrun: 未运行要求及原因
  risks: 已知限制、残余风险和外部门
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
summary: 交付内容的短摘要
executor_model: 实际模型或 unknown
executor_reasoning_effort: 实际强度或 unknown
model_evidence: accepted_override | runtime_report | unknown
actual_root: git rev-parse --show-toplevel 的原始输出；非 Git 任务写 not_applicable
base_sha: 实际基线
run_id: 与 route_receipt 相同的唯一运行 ID
candidate_sha: 候选提交；无提交写 uncommitted
head_sha: 生成候选回执时的实际 HEAD
candidate_binding_mode: commit_sha | unstaged_tracked_diff
staged_state: clean | nonempty | unknown
untracked_state: none | present | unknown
dirty_state: clean | dirty | unknown
candidate_diff_sha256: 未提交时对实际候选内容执行 git diff --binary 的 SHA-256；已提交候选可写 not_applicable
diff_scope: exact changed_paths；hash 必须覆盖实际候选内容而非仅摘要
changed_paths: 实际路径
artifacts_manifest: [] | 每个工件的绝对 path、sha256、bytes 与 run_id；与 artifact_handoff 逐项绑定
checks: 命令、退出状态、关键产物和结果
unrun: 未运行要求及原因
risks: 已知限制、残余风险和外部门
~~~

Planner 对照实际 diff、Git 状态和产物，不把回执本身当成事实。完整测试套件默认由 Executor 在精确 candidate SHA 上运行一次；Planner 核对日志或产物并运行必要的聚焦检查或最小反例。只有 SHA、迁移头、依赖或环境改变时才重复完整门禁。

`candidate_binding_mode=commit_sha` 优先用于高风险 fresh review；Worker 未获提交授权时不得自行 commit。`unstaged_tracked_diff` 只有在 `git diff --cached --quiet` 成功且 `git ls-files --others --exclude-standard` 无候选 untracked 路径时有效；必须记录该命令得到的 `git diff --binary` SHA-256、`head_sha`、exact `diff_scope` 和 dirty state。任一条件不成立即 `UNVERIFIED`，不能 PASS／ACCEPTED，除非另有明确、确定性且覆盖 staged、worktree、untracked 全部内容的授权绑定方法。

## 4. 独立 reviewer 门

低风险默认不启用 reviewer；用户明确要求或 route_receipt 中的语义风险触发时，`review_required=true`。Reviewer 必须使用 fresh、独立上下文，只读检查候选，不修改实现，不替代主 Sol 最终验收，也不自动升级 Terra。它先回报真实 Git 根、reviewed SHA、dirty state、review_triggers 和实际内容 hash，再检查规范与质量；不能证明模型、根、SHA、dirty、diff hash 或检查结果时保持 `UNVERIFIED`。

~~~yaml
review_receipt:
  status: PASS | CHANGES_REQUIRED | UNVERIFIED
  reviewer_model: 实际模型或 unknown
  model_evidence: accepted_override | runtime_report | unknown
  run_id: 与 route_receipt 相同的唯一运行 ID
  review_triggers: [] | 实际触发 reviewer 的语义风险或用户要求
  actual_root: git rev-parse --show-toplevel 的原始输出
  reviewed_sha: 实际审查的候选 SHA；未提交写 uncommitted
  reviewed_head_sha: 被审查回执记录的实际 HEAD
  reviewed_binding_mode: commit_sha | unstaged_tracked_diff
  staged_state: clean | nonempty | unknown
  untracked_state: none | present | unknown
  dirty_state: clean | dirty | unknown
  reviewed_diff_sha256: 未提交时必须与被审查 candidate_diff_sha256 相同；已提交可写 not_applicable
  diff_scope: 与 candidate receipt 相同的 changed_paths
  artifacts_manifest: 与 candidate receipt 相同的 path、sha256、bytes、run_id
  spec_verdict: PASS | FAIL | UNVERIFIED
  quality_verdict: PASS | FAIL | UNVERIFIED
  checks: 命令、退出状态、关键证据
  findings: [] | 必须处理的问题
  unverified: [] | 未能证明的项目
  report_path: 绝对报告路径 | not_applicable
~~~

`PASS` 不能掩盖 `CHANGES_REQUIRED`、`UNVERIFIED`、错根、错 SHA、run_id／HEAD／binding mode／staged／untracked 不匹配、未知 dirty_state 或缺失／不匹配的 reviewed_diff_sha256。任何内容或 HEAD 改动后旧 PASS 失效；最终 integrated SHA 与 reviewed candidate 不一致时必须复审／重核。高风险 reviewer 不可用或证据不足不得 `ACCEPTED`；发现问题优先 follow-up 原 Luna，不按 finding 新开多个修复 Agent。

## 5. Terra 升级证据

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

## 6. 并行与集成

- parallel 的每个包必须有独立 owned_paths、独立 oracle 和明确 depends_on。
- 共享 schema、公共接口、迁移序列或同一文件不能并行写；把它们串行化或交给唯一 owner。
- 多写入候选使用隔离 worktree，唯一协调者按依赖顺序集成。
- Worker 不在协调 worktree 合并、变基或解决冲突。
- 集成冲突需要实现判断时，交回原 Worker；strict 模式下 Sol 不亲自修改实现。

## 7. 接受状态与证据等级

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

## 8. 最终报告

~~~text
Outcome: ACCEPTED | PARTIAL | BLOCKED
Mode / routing: direct | Sol → Luna → Sol | parallel
Route evidence: trigger、policy、requested executor／reasoning_effort、model evidence、fallback
Baseline / final SHA: 精确值或 not_applicable
Accepted work: 候选和范围
run_id: 与 route → candidate → review 相同的唯一运行 ID
review_required: true | false
review_triggers: [] | 实际触发 reviewer 的语义风险或用户要求
Independent review: not_required | PASS | CHANGES_REQUIRED | UNVERIFIED
Reviewed candidate: commit SHA | diff sha256
Artifact handoff: inline | manifest(paths + sha256)
Verification: 实际检查、关键产物和结果
Usage evidence: input、cached、uncached、cache-write、output、retries，或 unmeasured
Unverified: 未测项与外部门
Release boundary: local | staging | pilot | production
Next: 一个具体动作或 none
~~~

当 `review_required=true` 时，只有相同 `run_id` 且绑定同一候选内容的 fresh `PASS` receipt 才能使 Outcome=`ACCEPTED`；否则只能 `PARTIAL` 或 `BLOCKED`。此时不得出现 `ACCEPTED` 与 `UNVERIFIED`、`CHANGES_REQUIRED` 或 `not_required` 同时成立；`review_required=false` 时才可使用 `not_required`。route、candidate、review、final 的 run_id 错配也不得 `ACCEPTED`。

没有同类基线或运行时 usage 时，Usage evidence 写 unmeasured，并明确“路由已执行，节省量未测”。不得把 API 单价、调用了 Luna 或并行数量换算成 Codex 账户节省比例。
