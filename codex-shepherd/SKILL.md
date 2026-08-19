---
name: codex-shepherd
description: "Reduce expensive-model execution cost in Codex with Planner–Executor routing: Sol reads sources of truth, plans, arbitrates, and performs final acceptance; Luna executes bounded implementation and tests; Terra is used only after evidence confirms a capability gap. Also coordinates subagents, Git worktrees, independent review, and evidence-backed acceptance. Use for shepherd or dispatcher mode, Sol-plans/Luna-executes workflows, reducing Sol usage, parallel agents, worktrees, multi-package coordination, or independent review. Do not use for simple explanations or tiny edits closed by one deterministic check."
---

# Codex Shepherd

Use this Skill as a model router, delegation gatekeeper, and acceptance controller. Separate high-uncertainty reasoning from high-throughput execution: Sol is the Planner/Coordinator/Final Reviewer, Luna is the Executor, and Terra is an evidence-triggered capability escalation. Optimize cost-weighted use of expensive models and verifiable progress, not agent count. Raw token totals may increase even when cost falls.

## 1. Establish source of truth and authorization

Before planning or dispatching:

1. Read applicable system, user, and `AGENTS.md` instructions. Project rules and current user authority override this Skill.
2. Verify target directory, actual Git root, branch, HEAD, dirty state, target worktree, task source of truth, acceptance criteria, and existing candidates. External tools must report `git rev-parse --show-toplevel` and the actual target SHA.
3. Query the live runtime for supported agent types, models, reasoning levels, and concurrency slots. Do not infer them from old documentation.
4. Treat parent-task authority and data boundaries as absolute ceilings. A subagent, worktree, or external reviewer may not broaden read, write, network, commit, push, deploy, or real-data authority.
5. Reuse the project's existing `TASK.md`, workboard, or task system; do not create a parallel long-lived progress source.
6. For long work, record a minimal checkpoint after material state changes: current package, owner, base/candidate/integrated SHA, completed checks, untested items, and the next stop point. Recover from source-of-truth files, Git, and run evidence, not chat narration.

If the Git root, baseline, target, authority, dirty state, or acceptance definition is untrustworthy, restore context or return `BLOCKED` before dispatching. Never automatically include, overwrite, clean, or commit unknown dirty state, user changes, or untracked files.

## 2. Choose the minimum sufficient mode

| Mode | Use when | Default route |
| --- | --- | --- |
| `direct` | Explanation, small read-only check, or tiny edit closed by one deterministic verification | Main agent completes directly |
| `routed` | Medium/large package with a bounded contract and implementation or test work that would consume substantial context | Sol plans → one Luna worker executes → Sol accepts |
| `parallel` | At least two truly independent packages with non-overlapping paths and separate acceptance oracles | Sol coordinates → isolated workers → serial integration |

When the user explicitly asks for Sol to plan and Luna or another cheaper model to execute, `routed` is the default. Do not keep Sol in the execution loop merely because it could complete the work. Use `direct` only when writing and accepting a delegation contract would cost at least as much as the task itself, and state that reason.

If the main agent is not Sol, model override is unavailable, or the worker's actual model cannot be verified, report the limitation. Never execute with the parent model and claim successful routing.

### Delegation-benefit gate

Delegate only when the benefit clearly exceeds the costs of task specification, waiting, integration, and conflicts:

- Independent work shortens the critical path.
- Moving bounded execution from Sol to Luna reduces cost-weighted model usage.
- Large searches, logs, or test output benefit from isolated context.
- Subtasks have non-overlapping boundaries and independent acceptance methods.
- Fresh context or a different model could change the decision.

Use `direct` when one local change and deterministic verification close the task, subtasks share the same implementation boundary, no acceptance oracle can be defined, or coordination costs exceed execution costs.

In `routed` mode, default to one Luna worker. Enter `parallel` only when the dependency graph proves independence and never exceed live runtime capacity. Allow one active writer and one delegation layer; workers do not recursively delegate. Prefer a follow-up that corrects the existing worker's contract over creating new agents for ordinary rework.

If the user explicitly requests real subagents, dispatch at least one bounded subtask with an acceptance method. If the runtime cannot support it or no safe boundary/oracle exists, state the limitation; never present local simulation, ordinary tool calls, or role-play as delegation. Preserve capacity for implementation, review, or recovery.

## 3. Fix Planner–Executor responsibilities

### Sol: Planner / Coordinator / Final Reviewer

Sol reads source-of-truth requirements, resolves direction-changing ambiguity, defines modules and safety boundaries, selects the base SHA/worktree/acceptance oracle, writes bounded contracts, reviews the actual diff and evidence, tests a minimal counterexample, and decides acceptance, rework, escalation, integration, or stop.

In `routed` mode, Sol does not perform large bounded implementation, mechanical searches, full-suite log processing, or repeated fixes. When the contract is wrong, Sol rewrites it and reuses the existing worker rather than taking execution back.

### Luna: default Executor

Luna implements code, tests, migrations, or documentation inside exact owned paths; performs mechanical search, focused tests, related regressions, and contract-required full gates; and returns actual SHAs, paths, command results, untested items, and risks.

When available, default to `gpt-5.6-luna`; a long but well-specified execution chain may use `reasoning_effort=high`. When overriding the model, use `fork_turns=none` and pass only the bounded contract and necessary source paths—not the full conversation or Sol's reasoning.

### Terra: escalation Executor

Escalate to `gpt-5.6-terra` only after a reproducible capability gap remains after ruling out missing context, an ambiguous contract, environment failures, permissions, and write conflicts. A first failure or a large file count is not escalation evidence.

### Capability-tier reference

Assess uncertainty, failure blast radius, acceptance-oracle strength, and parallel independence. Do not mechanically escalate models based only on file count or a first failure.

| Task properties | Preferred route in the current GPT-5.6 family |
| --- | --- |
| Clear, repeatable, high-throughput work with a strong oracle | Luna |
| Normal multi-file implementation, cross-file understanding, or unexplained debugging | Sol tightens the contract, then Luna; Terra only for a confirmed capability gap |
| High uncertainty, architecture, security, permissions, migrations, shared contracts, or final arbitration | Sol |
| Scope checking or an adversarial complementary view | Optional fresh external reviewer |

Use the lowest sufficient reasoning level: Low or Medium for simple tasks; High for a long Luna execution chain, complex logic, or review; XHigh or Max only for the hardest problems. Prefer native Codex `explorer`, `worker`, and `default` roles. Do not require a global default subagent model or create a custom agent before repeated drift demonstrates the need.

Model names and override capabilities are runtime facts. If the user specifies an unavailable exact model, report the supported options and request a substitute; never silently replace it. When the model catalog changes, route by capability tier rather than copying obsolete names.

## 4. Define a task contract and acceptance oracle

Before implementation delegation, answer: "What evidence proves this completed?" If you cannot, delegate exploration only or reduce uncertainty yourself.

Use this minimum contract:

```yaml
goal: result this subtask must deliver
target_root: absolute target directory, equal to the real Git root
base_sha: shared verifiable baseline; use not_applicable outside Git
mode: read_only | write
target_modules: target modules
owned_paths: exclusive write boundary; use read_only for read-only work
depends_on: preceding package or none
allow_shared_contract_changes: false or an explicit list
do_not_touch: forbidden paths, contracts, data, and external systems
acceptance: observable, decidable completion criteria
verification: required commands or manual checks
stop_after: stop after this package; do not begin the next item automatically
return: candidate_sha, changed_paths, checks, unrun, risks
```

Give workers purpose, constraints, and acceptance—not a full chat transcript, your reasoning, or the expected answer. Tell every worker it is not alone in the codebase and must not revert or tidy others' work.

## 5. Control parallel writes and worktrees

- Parallelize read-heavy exploration, test analysis, and source checks freely.
- Parallel writes require precise, non-overlapping path ownership. Only one writer at a time owns a file, migration sequence, schema, public interface, or shared contract.
- Before creating a worktree, check for an existing worktree by task ID, branch, and baseline; reuse it when safe.
- Multiple write candidates use separate worktrees and one coordinator serially integrates them. Workers do not merge, rebase, or resolve shared conflicts in the coordinator worktree.
- For multiple candidate releases or integrations, use the dedicated worktree-release-coordination workflow instead of duplicating its process here.
- The Executor runs the full suite once on the exact candidate SHA. Sol verifies logs and artifacts and runs only necessary focused checks or a minimal counterexample. Repeat full gates only when the SHA, migration head, dependency set, or environment changes.
- Do not automatically delete worktrees, branches, backups, or user files. Report cleanup recommendations unless separately authorized.

## 6. Review candidates with evidence

Require each candidate to return:

```yaml
status: CANDIDATE | PARTIAL | BLOCKED
executor_model: actual model or unknown
base_sha: actual baseline
candidate_sha: candidate commit; use uncommitted when absent
changed_paths: actual paths
checks: commands and results
unrun: required checks not run and why
risks: known limitations, residual risk, and external gates
```

Agent confidence is not evidence. Reviewers are sensors, not final arbiters:

- Low risk: deterministic checks plus coordinator diff review.
- Medium risk: add a fresh read-only reviewer.
- High risk: separately audit scope/acceptance and security/correctness, and verify one minimal counterexample capable of changing the decision.

Give reviewers the original request, acceptance criteria, relevant diff, test results, absolute root, and target SHA—not the implementer's defense. They must first report actual Git root, HEAD, dirty state, and checks run. A mismatched root/SHA, empty container, tool error, empty output, stale-worktree check, or implementation summary alone is not PASS. Exit code zero does not prove downstream artifacts or behavior; inspect the required result.

## 7. Accept serially and preserve evidence levels

Use this minimal state model:

```text
PLANNED → RUNNING → CANDIDATE → INTEGRATED → ACCEPTED
                    ↘ BLOCKED | SUPERSEDED
```

Record tests, reviews, and external gates as evidence fields rather than expanding the state machine. Only move from `INTEGRATED` to `ACCEPTED` after focused validation, regression checks, and final gates run on the exact integrated SHA. A worker branch passing does not prove the integrated tree passes.

Always distinguish local or synthetic proof, development candidate, company environment, real pilot, and production. Lower-grade evidence never authorizes a higher-grade conclusion or GO decision.

Measure progress in accepted units, evidence packages, and external gates—not agent count, code volume, chat duration, or undefined percentages. If an external gate remains closed, report the corresponding evidence level even when local code passes.

## 8. Repair by failure cause

Classify failure before retrying:

- Missing context: pause the writing worker and let Sol reread source of truth. Dispatch an Explorer only when independent read-only search has clear value; then update the contract and reuse the original worker by follow-up rather than adding another writer.
- Ambiguous request: rewrite the contract yourself.
- Environment or dependency error: diagnose the environment; do not hide it by switching models.
- Reproducible capability gap: Luna → Terra; if that still fails, Sol arbitrates.
- Write conflict: stop parallel work and reorder ownership and integration.
- Reviewer or tool failure: retain untested status; repair the call or choose an independent review path.

Before escalating to Terra, record minimum capability evidence: `failed_contract`, a `reproduction_command` under the same contract and environment, a stable `failure_signature`, `excluded_causes` (context, contract, environment, permission, conflict), and `why_luna_is_insufficient`. A missing field means the capability gap is unproven.

If the same failure cause occurs twice, do not repeat the route. Return to source of truth, contract, and assumptions. Stop accepting new candidates if target SHA changes, unexplained dirty state appears, acceptance definitions conflict, or a test failure cannot be explained.

## 9. Control communication and stop boundaries

Update the user only after the truth snapshot is established, work is dispatched, a candidate exists, review changes direction, integration validation completes, or a real blocker occurs. Do not stream every log line. On recovery, state the source of truth and SHA used to recover.

Maintain a compact package table: `package | owner | base | state | evidence | blocker`. Stop at `stop_after`; do not begin the next package unless the user's termination condition explicitly requires it.

## 10. Measure whether cost actually fell

Do not infer savings merely because Luna was called, and do not promise that raw token totals will fall. When usage is available, record `input`, `cached_input`, `uncached_input`, and `output` by model. Compare Sol uncached input/output and cost-weighted usage, while also reporting total tokens so many cheap agents cannot hide context inflation. Without a baseline or usage data, say "model routing implemented; savings unmeasured" and never claim a savings percentage.

Final delivery must state:

```text
Outcome: ACCEPTED | PARTIAL | BLOCKED
Mode / routing: direct | Sol → Luna → Sol | parallel
Baseline / final SHA: exact value or not_applicable
Accepted work: candidate and scope
Verification: actual checks and results
Usage evidence: measured metrics or unmeasured
Unverified: untested items and external gates
Release boundary: local | staging | pilot | production
Next: one specific action or none
```
