# TASK-113-03: Goal-First Orchestration and Session Contract

**Parent:** [TASK-113](./TASK-113_Tool_Layering_Goal_First_And_Vision_Assertion_Strategy.md)  
**Status:** ⏳ To Do  
**Priority:** 🔴 High  
**Depends On:** TASK-113-01, TASK-113-02

---

## Objective

Make `set_goal`-first behavior a product rule for normal LLM surfaces, not just a prompt convention.

---

## Repository Touchpoints

- `_docs/_MCP_SERVER/README.md`
- `_docs/_PROMPTS/README.md`
- `_docs/_ROUTER/README.md`
- `_docs/_ROUTER/RESPONSIBILITY_BOUNDARIES.md`
- `README.md`

---

## Planned Work

- define which surfaces require `router_set_goal(...)` before normal work
- define what session context the MCP server should persist from that goal
- define how later tools, vision, prompts, and verification should consume that context

---

## Acceptance Criteria

- the repo has an explicit product policy for `set_goal`-first orchestration
- surface docs and prompt docs agree on when it is mandatory vs optional
