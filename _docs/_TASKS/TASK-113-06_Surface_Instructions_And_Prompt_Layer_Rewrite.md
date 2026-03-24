# TASK-113-06: Surface Instructions and Prompt Layer Rewrite

**Parent:** [TASK-113](./TASK-113_Tool_Layering_Goal_First_And_Vision_Assertion_Strategy.md)  
**Status:** ⏳ To Do  
**Priority:** 🔴 High  
**Depends On:** TASK-113-02, TASK-113-03, TASK-113-05

---

## Objective

Rewrite surface `instructions` and MCP prompt assets so they teach the new operating model instead of the old flat-catalog/tool-first one.

---

## Repository Touchpoints

- `_docs/_PROMPTS/README.md`
- `_docs/_PROMPTS/WORKFLOW_ROUTER_FIRST.md`
- `_docs/_PROMPTS/MANUAL_TOOLS_NO_ROUTER.md`
- `server/adapters/mcp/surfaces.py`

---

## Planned Work

- define the new instruction style for production surfaces
- rewrite prompt assets around:
  - goal-first
  - macro/workflow-first
  - verify-after-change
  - vision+assert guidance

---

## Acceptance Criteria

- prompt/instruction layer teaches the intended product model directly
- old “here is the whole flat catalog, choose anything” mentality no longer dominates prompts
