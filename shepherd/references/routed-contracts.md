# Routed／Parallel 合同与证据

仅写入候选、高风险独立审查或多候选集成需要完整读取本文件；普通只读辅助任务使用 SKILL.md 的 brief 合同，不加载本文件。这里定义路由、候选绑定、升级和最终证据，不复制进项目长期真源。当前模型与档位默认值只维护在 SKILL.md 第 3 节。

## 1. 路由回执

Planner 在任何 Worker-owned path 被修改前记录：

~~~yaml
route_receipt:
  run_id: 派发前生成的唯一运行 ID
  trigger: explicit | implicit
  policy: strict | adaptive
  mode: routed | parallel
  planner_model: 实际模型或 unknown
  planner_evidence: runtime_report | unknown
  planner_requirement: 精确锁定模型 | default_preference
  executor_requirement: 精确锁定模型与档位 | default_pool
  selection_reason: 任务类型、已证实复杂度或同类验收证据；无需虚构成本数值
  pre_router:
    kind: disabled | jev
    status: used | unavailable | error | invalid | not_applicable
    schema_version: shepherd-route-v1 | not_applicable
    actual_model: API 返回模型 | not_applicable
    suggestion: direct | routed | parallel | planner_review | none
    probabilities: 脱敏后的原始 Choice 分布 | not_applicable
    confidence: 0..1 | not_applicable
    complexity: 原始 Score／probabilities | not_applicable
    adopted: true | false | not_applicable
    decision_reason: 采用、拒绝或 fallback 的理由
  requested_executor: 精确模型
  requested_reasoning_effort: 按任务填写；Luna 只读默认 medium，实现默认 high
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

`pre_router` 是可选审计字段。Jev 结果只能辅助 `selection_reason`，不能覆盖 `policy`、strict pin、`fallback_authorized`、权限或 reviewer 门禁，也不能写进 `checks`、验收 oracle、`spec_verdict`、`quality_verdict`、发布或生产证据。未调用时使用 `disabled/not_applicable`；服务或 key 不可用、响应错误时记录实际状态并按 SKILL.md 的确定性规则回退，不伪造建议或 confidence。

strict 锁定的 Planner 必须有匹配的实际模型证据；锁定的 Executor 必须有匹配的 model/effort override 证据，model_evidence=unknown 不合格。默认模型偏好没有证据时如实记 unknown，不声称已核验；任何调用都不能仅靠 Agent 自述证明模型。失败时只停止依赖该路由的部分，不由 Planner 写 Worker-owned paths。工作区明确由主 Codex 独写的治理路径按 SKILL.md 的例外处理，并记录 owned_paths=read_only、主写入者和例外理由。

## 2. 最小任务合同

~~~yaml
goal: 这一个子任务必须交付的结果
target_kind: git | non_git
target_root: Git 任务为真实 Git 根；非 Git 任务为父任务授权的绝对根
base_sha: 共同基线；非 Git 任务写 not_applicable
baseline_content_manifest: 非 Git 任务的精确 path、存在状态、sha256；Git 任务写 not_applicable
mode: read_only | write
target_modules: 目标模块
owned_paths: 唯一写入边界；只读任务写 read_only
depends_on: 前置包或 none
allow_shared_contract_changes: false | 明确列出允许项
do_not_touch: 禁止路径、契约、数据和外部系统
acceptance: 可观察、可判定的完成条件
verification: 必须执行的命令或人工检查
stop_after: 完成本包后 Worker 停止；Planner 仅按既有阶段授权推进依赖包
attempt_budget: 一次初始执行 + 至多一次同目标定向返修；明确任务另设预算时遵守
progress_oracle: 新证据排除原因、原验收项通过或缺陷减少；不以改动量计进展
handoff_context: 新任务只传最小合同；follow-up 只传 run_id、变化和新证据
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
target_kind: git | non_git
actual_root: Git 为 git rev-parse --show-toplevel 原始输出；非 Git 为验证后的授权绝对根
base_sha: Git 的实际基线；非 Git 写 not_applicable
run_id: 与 route_receipt 相同的唯一运行 ID
candidate_sha: Git 的候选提交；未提交写 uncommitted；非 Git 写 not_applicable
head_sha: Git 生成候选回执时的实际 HEAD；非 Git 写 not_applicable
candidate_binding_mode: commit_sha | unstaged_tracked_diff | non_git_content_hash
staged_state: Git 候选为 clean | nonempty | unknown；非 Git 写 not_applicable
untracked_state: Git 候选为 none | present | unknown；非 Git 写 not_applicable
dirty_state: Git 候选为 clean | dirty | unknown；非 Git 写 not_applicable
candidate_diff_sha256: Git 未提交候选对实际内容执行 git diff --binary 的 SHA-256；Git 已提交或非 Git 写 not_applicable
candidate_content_manifest: 非 Git 候选的精确 path、存在状态、sha256；Git 候选写 not_applicable
diff_scope: Git 为 exact changed_paths 且 diff hash 覆盖实际候选内容；非 Git 为授权 roster 的 exact changed_paths，内容由 candidate_content_manifest/hash 覆盖
changed_paths: 实际路径
artifacts_manifest: [] | 每个工件的绝对 path、sha256、bytes 与 run_id；与 artifact_handoff 逐项绑定
checks: 命令、退出状态、关键产物和结果
unrun: 未运行要求及原因
risks: 已知限制、残余风险和外部门
~~~

Planner 对照实际 diff、Git 状态和产物，不把回执本身当成事实。Executor 在被绑定的精确候选上运行合同与仓库要求的相关检查，不默认执行完整测试套件；全套若为既定门禁则必须执行。Planner 核对证据并做必要的聚焦检查或最小反例，不重复执行完整子任务。仅内容、迁移头、依赖、环境变化、失败或未解决风险才补验证；最终集成门禁按仓库要求执行。不能用摘要缺少原始证据为理由直接宣称 PASS，也不为获取证据重跑已经有有效记录的相同检查。

`candidate_binding_mode=commit_sha` 优先用于高风险 Git fresh review；Worker 未获提交授权时不得自行 commit。`unstaged_tracked_diff` 只有在 `git diff --cached --quiet` 成功且 `git ls-files --others --exclude-standard` 无候选 untracked 路径时有效。非 Git 任务使用 `non_git_content_hash`，逐项记录获准 roster 的存在状态与内容 hash，不运行 `git init`。任一模式缺少完整绑定即 `UNVERIFIED`。

## 4. 独立 reviewer 门

低风险默认不启用 reviewer；用户明确要求或 route_receipt 中的语义风险触发时，`review_required=true`。Reviewer 必须使用 fresh、独立上下文，只读检查候选，不修改实现，不替代主 Astra 最终验收，也不自动升级 Terra。它先按 `target_kind` 回报绑定证据再检查规范与质量：Git 候选回报真实 Git 根、SHA、dirty/staged/untracked state 与 diff hash；非 Git 候选回报授权绝对根、逐路径存在状态与内容 manifest/hash，所有 Git 专属字段明确写 `not_applicable`。不能证明模型、对应类型的根与完整绑定或检查结果时保持 `UNVERIFIED`。

~~~yaml
review_receipt:
  status: PASS | CHANGES_REQUIRED | UNVERIFIED
  reviewer_model: 实际模型或 unknown
  model_evidence: accepted_override | runtime_report | unknown
  run_id: 与 route_receipt 相同的唯一运行 ID
  review_triggers: [] | 实际触发 reviewer 的语义风险或用户要求
  target_kind: git | non_git
  actual_root: Git 的真实根或非 Git 的授权绝对根
  reviewed_sha: Git 候选的实际 SHA；未提交写 uncommitted；非 Git 写 not_applicable
  reviewed_head_sha: Git 候选回执记录的实际 HEAD；非 Git 写 not_applicable
  reviewed_binding_mode: commit_sha | unstaged_tracked_diff | non_git_content_hash
  staged_state: Git 候选为 clean | nonempty | unknown；非 Git写 not_applicable
  untracked_state: Git 候选为 none | present | unknown；非 Git 写 not_applicable
  dirty_state: Git 候选为 clean | dirty | unknown；非 Git 写 not_applicable
  reviewed_diff_sha256: Git 未提交候选必须与 candidate_diff_sha256 相同；Git 已提交或非 Git 写 not_applicable
  reviewed_content_manifest: 非 Git 时必须与 candidate_content_manifest 相同；Git 时写 not_applicable
  diff_scope: 与 candidate receipt 相同的 changed_paths
  artifacts_manifest: 与 candidate receipt 相同的 path、sha256、bytes、run_id
  spec_verdict: PASS | FAIL | UNVERIFIED
  quality_verdict: PASS | FAIL | UNVERIFIED
  checks: 命令、退出状态、关键证据
  findings: [] | 必须处理的问题
  unverified: [] | 未能证明的项目
  report_path: 绝对报告路径 | not_applicable
~~~

`PASS` 不能掩盖 `CHANGES_REQUIRED`、`UNVERIFIED` 或绑定不匹配。Git 候选的阻断项包括错根、错 SHA、run_id／HEAD／binding mode／staged／untracked 不匹配、未知 dirty_state 或缺失／不匹配的 reviewed_diff_sha256；非 Git 候选的阻断项包括错授权根、run_id／binding mode 不匹配，以及 roster 路径存在状态或 reviewed_content_manifest/hash 缺失／不匹配，Git 专属字段必须为 `not_applicable`。任何候选内容或其对应绑定改动后旧 PASS 失效；Git 的最终 integrated SHA、或非 Git 的最终 content manifest 与 reviewed candidate 不一致时必须复审／重核。高风险 reviewer 不可用或证据不足不得 `ACCEPTED`；发现问题优先 follow-up 原 Executor，只传变化与新证据，不按 finding 新开多个修复 Agent。

## 5. 执行模型选择与返修证据

默认 Astra 将常规开发拆为有界 Luna high 包。以下情形可选 Terra high：

1. 高耦合、未知根因或复杂约束使任务无法可靠拆小，Planner 记录具体证据；
2. 同类任务、环境和 oracle 的代表性结果表明 Luna 总完成成本更高；
3. 本次有证据的定向返修仍无实质进展，已区分合同、上下文、环境、权限和冲突原因，剩余问题确属能力不足。

第一次工具失败、文件数多或“不满意”本身不是升级证据；不要求为了升级先重复失败。记录与本次选择相关的简短依据即可：

~~~yaml
choice: Luna | Terra | Sol
task_evidence: 具体难点、同类验收结果或失败证据
attempts_used: 当前同目标已用初始执行/返修次数
last_change: 上轮改变的假设、输入或实现
progress: 新证据、通过的原验收项、减少的缺陷，或 none
excluded_causes: 已核对的上下文、合同、环境、权限、冲突及证据
remaining_gap: 需要更强执行模型解决的具体问题
next_action: 同目标定向返修 | 重拟有界合同 | 有证据升级 | 受阻交回
~~~

同一目标默认初始执行一次、定向返修至多一次。没有新假设或证据不做返修；同一问题无进展时停止原路径，重新分类，不通过换 Agent、改写错误名或拆成同义任务重置预算。真正改变范围或验收前核对是否越过阶段授权；模型升级仍服从 strict pin 和实际调用权限。Terra 仍不足时可按同一证据门选择 Sol high；接管执行或添加昂贵 Astra reviewer 需要说明原因并获对应授权。

## 6. 并行与集成

- parallel 的每个包必须有独立 owned_paths、独立 oracle 和明确 depends_on。
- 共享 schema、公共接口、迁移序列或同一文件不能并行写；把它们串行化或交给唯一 owner。
- 多写入候选使用隔离 worktree，唯一协调者按依赖顺序集成。
- Worker 不在协调 worktree 合并、变基或解决冲突。
- 集成冲突需要实现判断时，交回原 Worker；strict 模式下 Planner 不亲自修改实现。

## 7. 接受状态与证据等级

~~~text
PLANNED → RUNNING → CANDIDATE → INTEGRATED → ACCEPTED
                    ↘ BLOCKED | SUPERSEDED
~~~

测试、review、外部门和 release boundary 是证据字段，不扩展成状态。Git 目标只有精确 integrated SHA 通过要求的最终门禁才能 `ACCEPTED`；非 Git 目标只有授权 roster 的最终路径存在状态与 content manifest/hash 精确匹配被审候选并通过相同要求的最终门禁才能 `ACCEPTED`，Git 专属字段为 `not_applicable`。不得为满足此门禁运行 `git init`。

始终区分：

- 本地／合成验证；
- 开发候选；
- staging 或公司环境；
- 真实 pilot；
- production。

较低等级证据不授权更高等级结论。进度按通过的验收单位、证据包和外部门计算，不按 Agent 数量、代码量、聊天时长或未定义百分比计算。

## 8. 最终报告

下列字段是内部证据清单，不要求每次逐项向 Sean 展示。用户回执只说结果、关键证据、未验证项及下一步；完整绑定保留在获准工件或任务回执中，原始日志不反复回灌 Planner。

~~~text
Outcome: ACCEPTED | PARTIAL | BLOCKED
Mode / routing: direct | 实际 Planner → 实际 Executor → 实际 Planner | parallel
Route evidence: trigger、policy、requested executor／reasoning_effort、model evidence、fallback
Baseline / final binding: Git 的精确 SHA，或非 Git 的 baseline/final content manifest
Accepted work: 候选和范围
run_id: 与 route → candidate → review 相同的唯一运行 ID
review_required: true | false
review_triggers: [] | 实际触发 reviewer 的语义风险或用户要求
Independent review: not_required | PASS | CHANGES_REQUIRED | UNVERIFIED
Reviewed candidate: commit SHA | diff sha256 | non-Git content manifest hash
Artifact handoff: inline | manifest(paths + sha256)
Verification: 实际检查、关键产物和结果
Usage evidence: input、cached、uncached、cache-write、output、retries，或 unmeasured
Unverified: 未测项与外部门
Release boundary: local | staging | pilot | production
Next: 一个具体动作或 none
~~~

当 `review_required=true` 时，只有相同 `run_id` 且绑定同一候选内容的 fresh `PASS` receipt 才能使 Outcome=`ACCEPTED`；否则只能 `PARTIAL` 或 `BLOCKED`。此时不得出现 `ACCEPTED` 与 `UNVERIFIED`、`CHANGES_REQUIRED` 或 `not_required` 同时成立；`review_required=false` 时才可使用 `not_required`。route、candidate、review、final 的 run_id 错配也不得 `ACCEPTED`。

没有同类基线或运行时 usage 时，Usage evidence 写 unmeasured，并明确“路由已执行，节省量未测”。不得把 API 单价、调用了 Luna 或并行数量换算成 Codex 账户节省比例。
