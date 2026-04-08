# TASK-150-03-03-06-02: Operator Docs And Troubleshooting For Execution Enforcement

**Parent:** [TASK-150-03-03-06](./TASK-150-03-03-06_Regression_And_Docs_For_Execution_Enforcement.md)
**Depends On:** [TASK-150-03-03-06-01](./TASK-150-03-03-06-01_Unit_And_Transport_Regression_Matrix_For_Family_Role_Enforcement.md)
**Status:** ⏳ To Do
**Priority:** 🔴 High

## Objective

Explain the new execution-enforcement semantics to operators and maintainers.

## Repository Touchpoints

- `README.md`
- `_docs/_MCP_SERVER/README.md`
- `_docs/_PROMPTS/README.md`

## Planned Doc Topics

- what shared tool families are
- what part roles are
- why this is more scalable than one macro/mega tool per domain part
- how to diagnose a blocked family/role response
- how to read:
  - `allowed_families`
  - `allowed_roles`
  - `missing_roles`
  - `required_role_groups`

## Acceptance Criteria

- docs make it clear that prompt bundles support the flow, but runtime policy
  remains authoritative
- troubleshooting guidance explains why “build unlocked” does not mean “every
  part can be created in any order”

## Planned Unit Test Scenarios

- docs parity tests assert:
  - `allowed_families`
  - `allowed_roles`
  - `missing_roles`
  - family/role troubleshooting wording

## Planned E2E / Transport Scenarios

- not required at this micro-leaf; behavior is covered by the regression
  matrix, while this leaf focuses on docs parity and troubleshooting wording
