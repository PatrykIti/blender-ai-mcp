# TASK-188: AGENTS.md Governance Rules Merge

**Status:** ✅ Done
**Priority:** 🟡 Medium
**Category:** Repo Governance / Process
**Created:** 2026-06-26
**Completed:** 2026-06-26

## Objective

Enrich the root `AGENTS.md` rule set with the generic, useful process rules from
the `_TMP_AGENTS.md` donor (carried over from the TakeHand project), adapted to
this repository's real conventions (poetry/pre-commit, unit + Blender e2e,
`server/` + `blender_addon/` layout), without importing donor-specific stack
rules (uv/retrieval/graph/Tree-sitter/embeddings) or any naming scheme that
contradicts the existing task-file corpus.

## Scope

- Add the `docs/` vs `_docs/` documentation split rule (public/user-facing vs
  internal/technical/agent-facing); rule only, no directory creation or file
  migration (tracked separately as TASK-189).
- Add pre-implementation task audits and post-implementation drift passes to the
  Task Workflow, written provider-agnostic.
- Add a `Runtime And Data Safety` approval / egress / redaction kernel.
- Add a `Commit Hygiene` section.
- Strengthen Coding Standards (work-from-checkout, avoid `Any`, explicit async
  boundaries, no weakening of validation/lint/security gates).
- Codify the repo's real task-file naming contract in Task Governance
  (underscore slugs, hyphenated numeric segments, zero-padded new children,
  legacy grandfathered) — explicitly rejecting the donor's hyphen-only / `-LNN` /
  `-SNN` / `# FileName:` / `Parent Task:` scheme.
- Codify the repo's real changelog format in Changelog Policy
  (`<N>-<date>-<slug>.md`, `# N. Title` / `Date:` / lede / `## Changed` /
  `## Validation`, plus the index-row format).
- Add a validation-honesty rule to Testing Expectations.
- Realign the donor example templates `_docs/_TASKS/_EXAMPLE_TASKS.md` and
  `_docs/_CHANGELOG/_EXAMPLE_CHANGELOG.md` to the repo's real conventions.
- Remove the fully-merged `_TMP_AGENTS.md` donor file.

## Non-Goals

- Creating the `docs/` directory or migrating any docs (see TASK-189).
- Renaming any existing task or changelog files.
- Porting donor stack/tooling rules that do not apply to this repo.

## Repository Touchpoints

| Path | Expected Ownership | Why In Scope |
|------|--------------------|--------------|
| `AGENTS.md` | Governance | Primary rule set being enriched |
| `_docs/_TASKS/_EXAMPLE_TASKS.md` | Docs | Example task template realigned to real conventions |
| `_docs/_CHANGELOG/_EXAMPLE_CHANGELOG.md` | Docs | Example changelog template realigned to real conventions |
| `_docs/_TASKS/README.md` | Docs | Board statistics + Done row |
| `_docs/_CHANGELOG/README.md` | Docs | Changelog index row |
| `_TMP_AGENTS.md` | (removed) | Donor file, fully merged |

## Acceptance Criteria

- `AGENTS.md` contains the docs split, the pre/post audit loop, Runtime And Data
  Safety, Commit Hygiene, strengthened Coding Standards, the real task-naming
  contract, and the real changelog format.
- No donor-specific scheme leaks in (`uv run` / `takehand` / `Parent Task` /
  `-LNN` / `-SNN` / mandatory `# FileName:`).
- The example templates match the codified conventions.
- `_TMP_AGENTS.md` is removed.

## Docs To Update

- `AGENTS.md`, the two example templates, this board, and the changelog.

## Changelog Impact

`_docs/_CHANGELOG/398-2026-06-26-task-188-agents-governance-merge.md` plus its
index row in `_docs/_CHANGELOG/README.md`.

## Validation

- `git diff --check`
- `grep` guard for donor-only patterns in `AGENTS.md`
- `poetry run pre-commit run --files <changed docs>` (docs/process-only change)

## Completion Summary

Implemented via a parallel read-only understanding pass that audited the repo's
real task-numbering, changelog format, and `_docs/` layout before editing, then a
single-author merge into `AGENTS.md`. The donor's strict hyphen-only / `-LNN` /
`-SNN` task scheme and its bold-metadata / `Type:` / `Follow-ups:` changelog
example were rejected as contradicting ~560 existing task files and the live
changelog practice; only the durable concepts were ported onto the existing
conventions. Follow-on public-docs migration is tracked as
[TASK-189](./TASK-189_Public_Docs_Directory_Split_And_Migration.md).
