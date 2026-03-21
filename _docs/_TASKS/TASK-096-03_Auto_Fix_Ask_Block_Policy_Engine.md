# TASK-096-03: Auto-Fix, Ask, Block Policy Engine

**Parent:** [TASK-096](./TASK-096_Confidence_Policy_for_Auto_Correction.md)  
**Status:** ⬜ Planned  
**Priority:** 🔴 High  
**Depends On:** [TASK-096-02](./TASK-096-02_Confidence_Scoring_Normalization_Across_Engines.md)

---

## Objective

Implement a single policy engine that maps `confidence + risk + correction_type` into `auto-fix`, `ask`, or `block`.

---

## Planned Work

- create:
  - `server/router/application/policy/correction_policy_engine.py`
  - `tests/unit/router/application/test_correction_policy_engine.py`

---

## Pseudocode

```python
if correction_type == SAFE_PRECONDITION_FIX and risk == "low":
    return AUTO_FIX
if confidence == "MEDIUM":
    return ASK
if confidence in {"LOW", "NONE"}:
    return BLOCK
```

---

## Acceptance Criteria

- the router has one explicit decision point for auto-fix, ask, or block behavior
