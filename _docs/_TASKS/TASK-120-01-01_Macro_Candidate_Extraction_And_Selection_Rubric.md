# TASK-120-01-01: Macro Candidate Extraction and Selection Rubric

**Parent:** [TASK-120-01](./TASK-120-01_Macro_Candidate_Matrix_And_Shared_Contract.md)  
**Status:** ⏳ To Do  
**Priority:** 🔴 High

---

## Objective

Select the first macro families using a repeatable rubric based on real workflow
usage and public-surface pain points.

---

## Implementation Direction

- analyze existing custom workflows and grouped-tool usage patterns
- rank candidates by:
  - frequency
  - boundedness
  - value on `llm-guided`
  - compatibility with deterministic verification
  - ability to replace multiple low-level decisions
- explicitly separate:
  - good macro candidates
  - still-atomic actions
  - still-workflow-only flows

---

## Repository Touchpoints

- `server/router/application/workflows/custom/*.yaml`
- `_docs/_PROMPTS/*.md`
- `tests/e2e/router/`
- `_docs/_TASKS/TASK-113-04_Macro_And_Workflow_Tool_Design_Rules.md`

---

## Acceptance Criteria

- the first macro wave has an explicit candidate matrix and rejection rationale
- candidate selection is reproducible later for the second macro wave
