# TASK-117-01-01: Shared Assertion Result Envelope

**Parent:** [TASK-117-01](./TASK-117-01_Assertion_Contracts_And_Shared_Semantics.md)  
**Status:** ✅ Done  
**Priority:** 🔴 High

**Completion Summary:** The repo now has one shared assertion payload envelope covering `assertion`, `passed`, `subject/target`, `expected`, `actual`, `delta`, `tolerance`, `units`, and `details`.

---

## Objective

Define one reusable structured payload shape for `scene_assert_*` tools.

---

## Required Contract Direction

Every assertion result should be able to carry:

- `passed`
- `assertion`
- `subject` / `target`
- `expected`
- `actual`
- `delta`
- `tolerance`
- `units`
- `details`

Keep it compact and machine-readable. Avoid prose-heavy verdicts.

---

## Repository Touchpoints

- `server/adapters/mcp/contracts/scene.py`
- `tests/unit/tools/scene/test_scene_contracts.py`
- `tests/unit/adapters/mcp/test_structured_contract_delivery.py`

---

## Acceptance Criteria

- one reusable envelope can support all first-wave assertion tools
- failure cases do not need custom ad hoc payload shapes
