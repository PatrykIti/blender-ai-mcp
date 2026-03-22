# TASK-097-05-02: Tests and Docs Audit Exposure in MCP Responses and Logs

**Parent:** [TASK-097-05](./TASK-097-05_Audit_Exposure_in_MCP_Responses_and_Logs.md)  
**Status:** ✅ Done  
**Priority:** 🟡 Medium  
**Depends On:** [TASK-097-05-01](./TASK-097-05-01_Core_Audit_Exposure_MCP_Responses.md)

---

## Objective

Add tests and documentation updates for **Audit Exposure in MCP Responses and Logs**.

---

## Repository Touchpoints

- `tests/unit/`
- `_docs/`

---

## Planned Work

### Regression Scenarios (Required)

1. response exposure path: MCP responses include structured correction audit fields required by the contract.
2. logging exposure path: logs include correlatable audit identifiers and execution context for corrected runs.
3. masking path: sensitive fields are redacted/masked according to audit exposure policy.
4. compatibility path: summary/legacy response variants preserve compatibility while still exposing required audit metadata.

### Metrics To Capture

- audit field completeness ratio in MCP responses
- response/log correlation coverage using shared audit identifiers
- masking/redaction violation count (target: 0)

### Documentation Deliverables

- update task-linked docs with a before/after summary tied to the captured metrics
- document exact test commands, fixtures, and profile/config used during validation
- record compatibility or migration notes when behavior differs between surfaces

---

## Acceptance Criteria

- all required regression scenarios are implemented and passing in CI/local test runs
- metrics are captured with baseline vs post-change values and attached to the task update
- docs include the regression matrix and explain expected behavior boundaries
- no untracked regressions are observed on related contract renderer and telemetry/logging paths

---

## Atomic Work Items

1. Implement the required regression scenarios in focused unit/integration tests.
2. Run the target suites, collect metric outputs, and compare to baseline values.
3. Update docs with regression matrix, metric table, and migration/compatibility notes.
4. Verify adjacent surfaces for spillover regressions and document the result.
