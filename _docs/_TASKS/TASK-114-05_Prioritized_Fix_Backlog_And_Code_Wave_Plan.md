# TASK-114-05: Prioritized Fix Backlog and Code Wave Plan

**Parent:** [TASK-114](./TASK-114_Existing_Tool_Surface_Audit_And_Alignment.md)  
**Status:** ✅ Done  
**Priority:** 🔴 High

**Completion Summary:** The audit has now been turned into an execution-ready backlog. The repo has a prioritized register of existing-tool fixes plus a concrete first measure/assert implementation wave to execute next.

---

## Objective

Turn the audit output into a concrete execution backlog and the next implementation waves.

---

## Repository Touchpoints

- `_docs/_TASKS/README.md`
- `README.md`
- `_docs/_CHANGELOG/*.md`
- future implementation tasks created from the audit

---

## Planned Work

- prioritize which existing tools/descriptions get fixed first
- separate wording-only fixes from true behavior fixes
- define the first measure/assert code wave
- define the next macro/workflow tool wave after that

---

## Acceptance Criteria

- the audit ends with an execution-ready backlog, not just observations

## Backlog Shape

### Wave A: Existing Tool / Surface Wording Fixes

Do first:

- highest-signal user-facing wording drift
- MCP-facing docstring drift in high-impact areas
- metadata/example drift that still points toward old low-level/manual-first flows

### Wave B: First Measure/Assert Atomic Family

Do second:

- the first deterministic truth-layer atomics
- enough to cover proportion, gap/contact, alignment, and overlap checks

### Wave C: Later Macro / Workflow Additions

Do only after:

- wording drift is reduced
- first truth-layer atomics exist

This avoids building new higher-level tools on top of an ambiguous verification model.
