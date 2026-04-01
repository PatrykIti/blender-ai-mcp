# TASK-117-01-02: Tolerance and Comparator Semantics

**Parent:** [TASK-117-01](./TASK-117-01_Assertion_Contracts_And_Shared_Semantics.md)  
**Status:** ✅ Done  
**Priority:** 🔴 High

**Completion Summary:** The first assertion family now uses explicit tolerance-aware comparator semantics with stable expected/actual/delta behavior across all implemented `scene_assert_*` tools.

---

## Objective

Define stable comparison semantics so assertion tools do not invent incompatible
pass/fail logic per endpoint.

---

## Exact Design Targets

- default tolerance rules per assertion family
- explicit comparator vocabulary such as:
  - `within_tolerance`
  - `max_gap`
  - `min_gap`
  - `ratio_range`
  - `axis_delta`
- consistent unit handling (`blender_units` unless clearly dimensionless)
- explicit handling of zero/near-zero comparisons

---

## Acceptance Criteria

- assertion pass/fail logic is deterministic and documented
- tolerances can be reused by router/workflows/tests without prose interpretation
