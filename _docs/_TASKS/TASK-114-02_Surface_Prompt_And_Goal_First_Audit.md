# TASK-114-02: Surface, Prompt, and Goal-First Audit

**Parent:** [TASK-114](./TASK-114_Existing_Tool_Surface_Audit_And_Alignment.md)  
**Status:** ⏳ To Do  
**Priority:** 🔴 High

---

## Objective

Audit whether surfaces, prompt assets, and examples consistently enforce the new goal-first and macro/workflow-first model.

---

## Repository Touchpoints

- `server/adapters/mcp/surfaces.py`
- `_docs/_PROMPTS/*.md`
- `_docs/_MCP_SERVER/README.md`
- `README.md`

---

## Planned Work

- find places where manual/no-router usage is still overrepresented
- find places where `router_set_goal(...)` should be stronger or clearer
- find examples/prompts that still bias the model toward low-level manual tool selection

---

## Acceptance Criteria

- the repo has an explicit list of prompt/surface mismatches against the goal-first model
