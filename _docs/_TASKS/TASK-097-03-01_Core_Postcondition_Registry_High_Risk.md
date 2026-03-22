# TASK-097-03-01: Core Postcondition Registry for High-Risk Fixes

**Parent:** [TASK-097-03](./TASK-097-03_Postcondition_Registry_for_High_Risk_Fixes.md)  
**Status:** ✅ Done  
**Priority:** 🔴 High  
**Depends On:** [TASK-097-01](./TASK-097-01_Correction_Event_Model_and_Audit_Schema.md)

---

## Objective

Implement the core code changes for **Postcondition Registry for High-Risk Fixes**.

---

## Repository Touchpoints

- `server/router/domain/entities/postcondition.py`
- `server/router/application/policy/postcondition_registry.py`
- `server/router/application/engines/tool_correction_engine.py`
- `server/infrastructure/di.py`
- `tests/unit/router/application/test_correction_policy_engine.py`
---

## Planned Work

- create:
  - `server/router/domain/entities/postcondition.py`
  - `server/router/application/policy/postcondition_registry.py`
- wire postcondition registry runtime access through `server/infrastructure/di.py`

### High-Risk Baseline

Start with fixes that most affect LLM spatial awareness and execution correctness:

- mode corrections
- active-object corrections
- selection injection
- parameter clamps with visible geometric impact
---

## Acceptance Criteria

- the repo knows which fixes require post-execution verification
- postcondition registry runtime wiring is explicit through DI
---

## Atomic Work Items

1. Classify the initial high-risk correction set.
2. Define one postcondition entry per correction family.
3. Add tests for registry lookup and verification trigger conditions.
