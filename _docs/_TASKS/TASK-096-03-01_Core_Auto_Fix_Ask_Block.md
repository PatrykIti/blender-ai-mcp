# TASK-096-03-01: Core Auto-Fix, Ask, Block Policy Engine

**Parent:** [TASK-096-03](./TASK-096-03_Auto_Fix_Ask_Block_Policy_Engine.md)  
**Status:** ⬜ Planned  
**Priority:** 🔴 High  
**Depends On:** [TASK-096-02](./TASK-096-02_Confidence_Scoring_Normalization_Across_Engines.md)

---

## Objective

Implement the core code changes for **Auto-Fix, Ask, Block Policy Engine**.

---

## Repository Touchpoints

- `server/router/application/policy/correction_policy_engine.py`
- `server/router/application/router.py`
- `server/router/application/engines/tool_correction_engine.py`
- `tests/unit/router/application/test_correction_policy_engine.py`
---

## Planned Work

- create:
  - `server/router/application/policy/correction_policy_engine.py`
  - `tests/unit/router/application/test_correction_policy_engine.py`
---

## Acceptance Criteria

- the router has one explicit decision point for auto-fix, ask, or block behavior
---

## Atomic Work Items

1. Implement the leaf scope in the listed touchpoints.
2. Keep the implementation aligned with the parent task boundaries and the existing runtime call path.
