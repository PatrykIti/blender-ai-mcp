# TASK-113-03-01: Set Goal First Requirement

**Parent:** [TASK-113-03](./TASK-113-03_Goal_First_Orchestration_And_Session_Contract.md)  
**Status:** ✅ Done  
**Priority:** 🔴 High

**Completion Summary:** The requirement is now stated at product-doc level: `router_set_goal(...)` is the default production entrypoint, while manual/debug/experimental surfaces are the explicit exceptions.

---

## Objective

State clearly where `router_set_goal(...)` is required and why.

---

## Exact Documentation Targets

- `_docs/_MCP_SERVER/README.md`
- `_docs/_PROMPTS/README.md`
- `_docs/_PROMPTS/WORKFLOW_ROUTER_FIRST.md`
- `README.md`

---

## Required Rule

- production-oriented LLM surfaces should start from `router_set_goal(...)`
- exceptions should be explicit:
  - maintainer/debug surfaces
  - narrow manual/test surfaces

---

## Why

- gives the platform session awareness
- improves tool guidance and verification context
- gives vision/macro/workflow layers the active goal context
- reduces “tool thrashing” without a clear session objective

---

## Acceptance Criteria

- the rule is product-level, not hidden in one prompt file
- exceptions are documented rather than implicit
