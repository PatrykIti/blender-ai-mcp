# TASK-121-05-06-03: Prompts and Tests for Guided Manual No-Match Flow

**Parent:** [TASK-121-05-06](./TASK-121-05-06_Guided_Manual_Build_Handoff_After_Weak_Or_Irrelevant_Workflow_Match.md)  
**Status:** ⏳ To Do  
**Priority:** 🟡 Medium

---

## Objective

Make the `no_match` -> guided manual-build continuation path explicit in
prompts, docs, and regression coverage.

---

## Implementation Direction

- prompt/docs should say that `no_match` is not a failure if the task is still
  buildable manually on the guided surface
- remove any residual wording that nudges the model to invent or import
  workflows as the default response to `no_match`
- add tests covering:
  - `no_match` guided continuation
  - avoidance of irrelevant workflow import suggestions

---

## Repository Touchpoints

- `_docs/_PROMPTS/`
- `README.md`
- `_docs/_MCP_SERVER/README.md`
- `tests/unit/adapters/mcp/`
- `tests/e2e/router/`

---

## Acceptance Criteria

- prompt/docs explain guided manual continuation after `no_match`
- tests protect against regression back into workflow-forcing behavior
