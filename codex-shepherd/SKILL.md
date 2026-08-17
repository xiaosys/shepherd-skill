---
name: codex-shepherd
description: "Coordinate Codex subagents, Git worktrees, and independent reviews with the lowest practical coordination cost and evidence-backed acceptance. Use when the user or applicable AGENTS.md explicitly requests a shepherd or dispatcher mode, subagents, parallel work, worktrees, multi-package coordination, or independent review. Decide first whether delegation is beneficial; choose the currently available model by uncertainty, risk, verifiability, and independence. Do not use for ordinary single-agent edits, simple explanations, or tasks without independently verifiable subproblems."
---

# Codex Shepherd

Use this Skill as a delegation gatekeeper and acceptance controller. Optimize for verifiable progress, not agent count. Direct work, serial work, and declining delegation are all valid outcomes.

## 1. Establish source of truth and authorization

Before planning or dispatching:

1. Read applicable system, user, and `AGENTS.md` instructions. Project rules and current user authority override this Skill.
2. Verify target directory, actual Git root, branch, HEAD, dirty state, target worktree, task source of truth, acceptance criteria, and existing candidates. External tools must report `git rev-parse --show-toplevel` and the actual target SHA.
3. Query the live runtime for supported agent types, models, reasoning levels, and concurrency slots. Do not infer them from old documentation.
4. Treat parent-task authority and data boundaries as absolute ceilings. A subagent, worktree, or external reviewer may not broaden read, write, network, commit, push, deploy, or real-data authority.
5. Reuse the project's existing `TASK.md`, workboard, or task system; do not create a parallel long-lived progress source.
6. For long work, record a minimal checkpoint after material state changes: current package, owner, base/candidate/integrated SHA, completed checks, untested items, and the next stop point. Recover from source-of-truth files, Git, and run evidence, not chat narration.

If the Git root, baseline, target, authority, dirty state, or acceptance definition is untrustworthy, restore context or return `BLOCKED` before dispatching. Never automatically include, overwrite, clean, or commit unknown dirty state, user changes, or untracked files.

## 2. Pass the delegation-benefit gate

Delegate only when the benefit clearly exceeds the costs of task specification, waiting, integration, and conflicts:

- Independent work shortens the critical path.
- Large searches, logs, or test output benefit from isolated context.
- Subtasks have non-overlapping boundaries and independent acceptance methods.
- Fresh context or a different model could change the decision.

Work directly when one local change and deterministic verification close the task, subtasks share the same implementation boundary, no acceptance oracle can be defined, or coordination costs exceed execution costs.

Default to one subagent. Add concurrency only when the dependency graph proves independence and never exceed live runtime capacity. Default to one delegation layer; workers do not recursively delegate unless the task contract and applicable rules explicitly allow it.

If the user explicitly requests real subagents, dispatch at least one bounded subtask with an acceptance method. If the runtime cannot support it or no safe boundary/oracle exists, state the limitation; never present local simulation, ordinary tool calls, or role-play as delegation. Preserve capacity for implementation, review, or recovery.

## 3. Route by task properties

Assess uncertainty, failure blast radius, acceptance-oracle strength, and parallel independence. Do not mechanically escalate models based only on file count or a first failure.

| Task properties | Preferred route in the current GPT-5.6 family |
| --- | --- |
| Clear, repeatable, high-throughput work with a strong oracle | Luna |
| Normal multi-file implementation, cross-file understanding, or unexplained debugging | Terra |
| High uncertainty, architecture, security, permissions, migrations, shared contracts, or final arbitration | Sol |
| Scope checking or an adversarial complementary view | Optional fresh external reviewer |

Use the lowest sufficient reasoning level: Low or Medium for simple tasks; High for complex logic or review; XHigh or Max only for the hardest problems. Prefer native Codex `explorer`, `worker`, and `default` roles. Do not require a global default subagent model or create a custom agent before repeated drift demonstrates the need.

Model names and override capabilities are runtime facts. If the user specifies an unavailable exact model, report the supported options and request a substitute; never silently replace it. When the model catalog changes, route by capability tier rather than copying obsolete names.

## 4. Define a task contract and acceptance oracle

Before implementation delegation, answer: "What evidence proves this completed?" If you cannot, delegate exploration only or reduce uncertainty yourself.

Use this minimum contract:

```yaml
goal: result this subtask must deliver
target_root: absolute target directory, equal to the real Git root
base_sha: shared verifiable baseline; use not_applicable outside Git
mode: read_only | write
owned_paths: exclusive write boundary; use read_only for read-only work
depends_on: preceding package or none
shared_contracts: shared contracts owned or prohibited by this package; none if absent
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
- Do not automatically delete worktrees, branches, backups, or user files. Report cleanup recommendations unless separately authorized.

## 6. Review candidates with evidence

Require each candidate to return:

```yaml
status: CANDIDATE | PARTIAL | BLOCKED
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

- Missing context: dispatch an explorer or reread source of truth.
- Ambiguous request: rewrite the contract yourself.
- Environment or dependency error: diagnose the environment; do not hide it by switching models.
- Capability gap: then increase model capability or reasoning level.
- Write conflict: stop parallel work and reorder ownership and integration.
- Reviewer or tool failure: retain untested status; repair the call or choose an independent review path.

If the same failure cause occurs twice, do not repeat the route. Return to source of truth, contract, and assumptions. Stop accepting new candidates if target SHA changes, unexplained dirty state appears, acceptance definitions conflict, or a test failure cannot be explained.

## 9. Control communication and stop boundaries

Update the user only after the truth snapshot is established, work is dispatched, a candidate exists, review changes direction, integration validation completes, or a real blocker occurs. Do not stream every log line. On recovery, state the source of truth and SHA used to recover.

Maintain a compact package table: `package | owner | base | state | evidence | blocker`. Stop at `stop_after`; do not begin the next package unless the user's termination condition explicitly requires it.

Final delivery must state:

```text
Outcome: ACCEPTED | PARTIAL | BLOCKED
Direct or delegated: choice and reason
Baseline / final SHA: exact value or not_applicable
Accepted work: candidate and scope
Verification: actual checks and results
Unverified: untested items and external gates
Release boundary: local | staging | pilot | production
Next: one specific action or none
```
