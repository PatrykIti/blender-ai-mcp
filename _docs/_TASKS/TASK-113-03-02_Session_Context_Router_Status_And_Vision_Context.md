# TASK-113-03-02: Session Context, Router Status, and Vision Context

**Parent:** [TASK-113-03](./TASK-113-03_Goal_First_Orchestration_And_Session_Contract.md)  
**Status:** ✅ Done  
**Priority:** 🟡 Medium

**Completion Summary:** The docs now define the expected session-context contract after a goal is set: active goal, phase, current target when known, verification criteria, and the interpretation frame for before/after vision.

---

## Objective

Define what context should exist once a goal is set, and how downstream analysis/vision should use it.

---

## Exact Documentation Targets

- `_docs/_ROUTER/README.md`
- `_docs/_MCP_SERVER/README.md`
- future vision/assertion docs under TASK-113-05

---

## Required Context Model

- active goal / user intent
- current modeling phase
- current target object/component if known
- expected verification criteria
- what before/after analysis should be interpreted against

---

## Acceptance Criteria

- the repo has a documented session-context contract, not just a vague “router knows the goal”
- vision/context handoff is described explicitly
