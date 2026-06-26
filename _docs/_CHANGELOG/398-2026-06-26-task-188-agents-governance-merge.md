# 398. TASK-188 AGENTS governance rules merge

Date: 2026-06-26

Merged the generic, useful process rules from the `_TMP_AGENTS.md` donor (from
the TakeHand project) into the root `AGENTS.md`, adapted to this repository's real
conventions. Donor-specific stack rules (uv / retrieval / graph / Tree-sitter /
embeddings) and any naming scheme that would contradict the existing task corpus
were intentionally dropped. No runtime / server / addon / router behavior
changed; this is a docs/process-only change. The public `docs/` directory was
deliberately not created here and is tracked as TASK-189.

## Changed

- `AGENTS.md`: added a `docs/` vs `_docs/` documentation-split rule, a
  `Runtime And Data Safety` approval / egress / redaction kernel, a
  `Commit Hygiene` section, and pre-implementation task audits plus
  post-implementation drift passes in the Task Workflow (written
  provider-agnostic).
- `AGENTS.md`: strengthened Coding Standards (work-from-checkout, avoid `Any`,
  explicit async boundaries, no weakening of validation/lint/security gates) and
  added a validation-honesty rule to Testing Expectations.
- `AGENTS.md`: codified the repo's real task-file naming contract (underscore
  slugs, hyphenated numeric segments, zero-padded new children, legacy
  grandfathered) and the real changelog format, explicitly rejecting the donor's
  hyphen-only / `-LNN` / `-SNN` / `# FileName:` / `Parent Task:` scheme and its
  bold-metadata `Type:` / `Follow-ups:` changelog example.
- Realigned `_docs/_TASKS/_EXAMPLE_TASKS.md` and
  `_docs/_CHANGELOG/_EXAMPLE_CHANGELOG.md` from the donor (TakeHand) shape to the
  repo's real conventions.
- Added `TASK-188` (this change, done) and `TASK-189` (public `docs/` migration,
  to do); updated the task board statistics, Done, and To Do rows.
- Removed the fully-merged `_TMP_AGENTS.md` donor file.

## Validation

Docs/process-only change:

- `git diff --check`
- `grep` guard: no `uv run` / `takehand` / `Parent Task` / `-LNN` / `-SNN` /
  mandatory `# FileName:` mandates leaked into `AGENTS.md`
- `PRE_COMMIT_HOME=/tmp/pre-commit-cache poetry run pre-commit run --files _docs/_TASKS/README.md _docs/_CHANGELOG/README.md AGENTS.md _docs/_TASKS/_EXAMPLE_TASKS.md _docs/_CHANGELOG/_EXAMPLE_CHANGELOG.md _docs/_TASKS/TASK-188_AGENTS_Governance_Rules_Merge.md _docs/_TASKS/TASK-189_Public_Docs_Directory_Split_And_Migration.md _docs/_CHANGELOG/398-2026-06-26-task-188-agents-governance-merge.md --show-diff-on-failure`
