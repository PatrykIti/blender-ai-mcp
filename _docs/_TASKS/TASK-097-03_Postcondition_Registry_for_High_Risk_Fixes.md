# TASK-097-03: Postcondition Registry for High-Risk Fixes

**Parent:** [TASK-097](./TASK-097_Transparent_Correction_Audit_and_Postconditions.md)  
**Status:** 🚧 In Progress  
**Priority:** 🔴 High  
**Depends On:** [TASK-097-01](./TASK-097-01_Correction_Event_Model_and_Audit_Schema.md)

---

## Objective

Register which correction classes require postcondition verification after execution.

---

## Planned Work

- create:
  - `server/router/domain/entities/postcondition.py`
  - `server/router/application/policy/postcondition_registry.py`

### High-Risk Baseline

Start with fixes that most affect LLM spatial awareness and execution correctness:

- mode corrections
- active-object corrections
- selection injection
- parameter clamps with visible geometric impact

---

## Layered Subtasks

| ID | Title | Focus |
|----|-------|-------|
| [TASK-097-03-01](./TASK-097-03-01_Core_Postcondition_Registry_High_Risk.md) | Core Postcondition Registry for High-Risk Fixes | Core implementation layer |
| [TASK-097-03-02](./TASK-097-03-02_Tests_Postcondition_Registry_High_Risk.md) | Tests and Docs Postcondition Registry for High-Risk Fixes | Tests, docs, and QA |

---

## Acceptance Criteria

- the repo knows which fixes require post-execution verification

---

## Atomic Work Items

1. Classify the initial high-risk correction set.
2. Define one postcondition entry per correction family.
3. Add tests for registry lookup and verification trigger conditions.
