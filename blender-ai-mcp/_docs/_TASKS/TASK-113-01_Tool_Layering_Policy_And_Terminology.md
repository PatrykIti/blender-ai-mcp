# TASK-113-01: Tool Layering Policy and Terminology

**Parent:** [TASK-113](./TASK-113_Tool_Layering_Goal_First_And_Vision_Assertion_Strategy.md)  
**Status:** ✅ Done  
**Priority:** 🔴 High  
**Depends On:** None

**Completion Summary:** The repo now has one canonical policy source for tool layering and one explicit historical-notation rule for superseded docs/tasks. Main docs now point back to that policy instead of redefining the architecture locally.

---

## Objective

Create one canonical written policy for the new tool model and make sure old terminology does not keep reintroducing the flat-catalog mindset.

---

## Repository Touchpoints

- `_docs/ARCHITECTURE.md` or a new dedicated policy doc location under `_docs/`
- `_docs/_MCP_SERVER/README.md`
- `_docs/AVAILABLE_TOOLS_SUMMARY.md`
- `_docs/_TASKS/README.md`
- `_docs/_DEV/README.md`

---

## Planned Work

- define canonical terms:
  - `atomic tool`
  - `macro tool`
  - `workflow tool`
  - `goal-first`
  - `public surface`
  - `hidden/internal layer`
  - `measure/assert layer`
  - `vision interpretation layer`
- define where the canonical policy lives and which docs must defer to it
- add historical supersession guidance so old docs are not silently treated as still-current policy

---

## Acceptance Criteria

- one canonical policy source is chosen and referenced by the rest of `_docs/`
- terminology is normalized across the active architecture docs
- the repo has an explicit historical/superseded notation rule
