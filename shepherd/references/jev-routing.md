# Jev 预路由

Jev 是 TypeSafe 的 System One 模型：它对给定 state 回答有界的 Choice／Score／Noul 问题，返回结构化答案和概率，不生成代码、计划或解释。Shepherd 只在路由边界确实模糊时把它用作预路由建议器。

当前事实以 TypeSafe 在线文档为准：

- [System One](https://docs.typesafe.ai/concepts/system-one)
- [Confidence](https://docs.typesafe.ai/confidence)
- [Confidence-gated routing](https://docs.typesafe.ai/patterns/confidence-routing)
- [HTTP API](https://docs.typesafe.ai/api)

## 适合与不适合

适合：大量相似任务要稳定分流；自然语言目标同时出现多个工作包；人工启发式经常在 direct／routed 之间摇摆；希望收集概率分布用于后续校准。

不适合：一次明显的微小修改；可由确定性规则直接判断；需要理解完整代码或长日志后才能规划；权限、安全、隐私、生产发布等高风险裁决；选择具体模型和 reasoning effort；判断实现是否完成或审查是否通过。

Jev 不是 Agent，也不具备执行权。它的建议不能改变父任务授权、项目规则、strict pin、写入 owner、review trigger 或验收 oracle。

## 最小 state

只发送完成路由所需的脱敏元数据，推荐字段：

```json
{
  "goal": "短句描述目标，不含代码或个人数据",
  "authorization": "read_only | write_allowed | analysis_only",
  "scope_clarity": "clear | partial | unclear",
  "write_scope": ["逻辑模块名，不是敏感绝对路径"],
  "risk_signals": ["security", "privacy", "production", "shared_schema"],
  "acceptance_oracle": "可观察完成条件的摘要",
  "task_dependencies": "none | serial | independent",
  "runtime_constraints": ["strict_model_pin", "single_writer"]
}
```

禁止发送密钥、令牌、原始代码、完整日志、私人聊天、候选人资料、薪酬、面试评价或其他不需要离开本机的内容。需要这些内容才能判断时，跳过 Jev，由 Planner 在本地处理。

## 调用与解释

本仓库的适配命令默认 dry-run：

```bash
python3 shepherd/scripts/jev_route.py --input route-state.json
```

确认 state 已脱敏、外发已获授权，并在环境中设置 `TYPESAFE_API_KEY`，或将 Key 存为 macOS 钥匙串的 `service=typesafe-ai`、`account=api_key` 后才执行。环境变量优先，钥匙串作为本机回退；Key 不写入 Skill、state 或日志：

```bash
python3 shepherd/scripts/jev_route.py --input route-state.json --execute
```

也可从标准输入读取，避免把 state 放入命令历史：

```bash
python3 shepherd/scripts/jev_route.py --execute < route-state.json
```

命令发送一个 Choice 和一个 Score：

- `route`：`direct`、`routed`、`parallel`、`planner_review`。
- `complexity`：从确定性小任务到高耦合／未知根因的三级描述。

Choice 的 `confidence` 表示选项分布的集中程度，不等于路由正确率；Score 也只是任务描述下的语义判断。不要把某个固定阈值写成永久真理。先保守收集一组由 Planner 标注的真实任务，比较 Jev 建议、置信度与最终验收成本，再确定自动采用范围。

在完成本地校准前，建议采取下列行为而非固定数值：

1. `planner_review`、低置信度或分布接近时，由 Planner 按 `SKILL.md` 判断。
2. Jev 建议与权限、strict pin、review trigger 或确定性规则冲突时，确定性规则优先并记录拒绝原因。
3. 建议 `parallel` 时仍逐项证明至少两个独立包、互不冲突的写入范围和各自 oracle。
4. 建议 `routed` 时仍由 Planner 填写合同并选择实际可用模型／档位。
5. 无 key、网络关闭、超时、401、429、529、响应字段异常或模型变化时，回退到原有规则；失败不是升级模型或扩大权限的理由。

## 模式与回退

模式是 Planner 的工作流约定，现有 `jev_route.py` 只有默认 dry-run 和 `--execute`；不要虚构 `--routing`、自动旁观、日志或统计能力。

| 模式 | 何时使用 | 行为 |
| --- | --- | --- |
| `off` | 明确的小任务、已有合同、无需 Jev 或暂停评估 | 不执行脚本、不读 key、不发请求；按原 Skill 派单。需要对照时复用正常任务回执 |
| `shadow` | 已授权的脱敏调用，评估尚未校准的任务类型 | 先记录 Planner 的路由及理由，再调用 Jev；保留建议供事后比较，不改变本次派单 |
| `advisory` | 已有同类校准证据，且 Jev 有望解决当前分工歧义 | Planner 审阅结果，逐项核对边界后采用或拒绝；不自动派单、不选择具体模型 |

dry-run 只证明请求如何构造，不是 shadow、成功调用或已测基线；它会将输入 state 打印到标准输出，输入仍须脱敏。shadow 也会外发摘要并产生 Jev 开销，不能作为零成本对照。advisory 的校准证据随任务类型、schema、实际模型变化重新评估，不设通用置信度自动批准线。

无 key、超时、服务错误或无效响应时，记录 `fallback` 和简短原因，沿原规则继续；不得将这次调用记为成功建议。现有脚本只负责请求和 JSON 解析：进程成功不证明答案有效，Planner 仍需检查 route 选项、答案类型、概率字段和实际模型是否符合预期。脚本报错或字段异常都由 Planner 回退，并非脚本自动派单。一次失败不循环重试；相同问题连续出现时，对本轮后续任务设 off，等有配置修复或服务恢复证据再评估。

需要完整代码、聊天或业务数据才能判断时，直接 off。字段白名单和长度截断不等于脱敏；不得将代码或敏感内容塞进 `goal` 等允许字段绕过此边界。

## 观测与校准

复用项目已有任务回执或交接记录，无既有文件落点时直接在当前任务简记，不另建数据库、常驻服务或全量日志。仅在实际调用或获准比较时记录下列必要字段；未知值记 `unmeasured`，不要用 0 代替：

- **任务与基线**：run_id、脱敏任务类型、复杂度、验收条件、代码基线（适用时）、模式，以及 shadow 调用前的 Planner 判断。
- **路由观测**：请求 schema、请求模型与返回的实际模型、Choice／Score 原始答案、probabilities／confidence、状态（`skipped`／`suggested`／`fallback`）、简短原因、Jev 耗时及可得 usage。不保存原始 state 或整份响应。
- **实际执行**：Planner 最终路由、采用／拒绝理由、实际 Executor 模型与档位及其证据；建议本身不能证明分工或模型 override 已发生。
- **最终结果**：验收结论和证据、返修／升级次数、从开始到最终验收或停止的总耗时、Planner／Executor／Reviewer 与 Jev 的可得总用量；失败和中途停止也保留。

先看任务成功率和必要审查是否保持，再看返工、总耗时和用量。只统计成功任务、单次请求输出 token 或 Jev 延迟，都会漏掉总成本；缓存输入、输出和隐藏推理按提供方口径分开，避免把输出中已包含的推理 token 重复加总。没有完整计量时明确缺项，不能换算为订阅额度节省比例。

对照按任务类型与相近难度分组，如修 bug 与新增功能分开；尽量保持模型／档位、工具、验收条件和初始上下文一致。重跑同题时从同一干净基线开始，不读取另一组的解法；正常工作区已有修改不回滚，使用获准的隔离环境。记录样本数与不可比因素，样本少时只报告观察。shadow 衡量建议差异和额外开销，不能证明采用建议后的收益；收益比较用 off 与 advisory。

如出现错误分工导致验收下降、越界建议或同类任务总成本持续升高，退回 off 并检查具体失败，不靠降低置信度阈值提高路由率。修正后再做有限比较；没有有效基线时只报告“已使用建议，节省量未测”。不为凑样本自动重复昂贵任务。

## 蒸馏来源与适用边界

参考 [vinilana/jev-gateway](https://github.com/vinilana/jev-gateway/tree/6b1c204f8d86093a1bbc537ce6562e52225c4f25)（2026-09-19 检查的版本）的路由开关、失败回退、请求观测和按任务对照方法。这里采用的是这些设计原则，没有安装网关或复制其工具控制逻辑。

- 网关控制单次工具选择；Shepherd 控制任务分工。同名 `direct` 在这里仅表示主 Agent 直接处理。
- 不迁入全对话上下文转发、合成工具调用、强制工具、`ARGS_MODEL` 或默认置信度阈值；这些会改变当前数据边界或执行控制。
- 网关 README 的实验包含收益与质量下降案例，属于作者特定任务的小样本结果，不是本 Skill 或 Sean 订阅额度的节省证据。
