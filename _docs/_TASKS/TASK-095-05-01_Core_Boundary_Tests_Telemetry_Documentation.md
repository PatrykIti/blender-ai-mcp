# TASK-095-05-01: Core Boundary Tests, Telemetry, and Documentation

**Parent:** [TASK-095-05](./TASK-095-05_Boundary_Tests_Telemetry_and_Documentation.md)  
**Status:** ⬜ Planned  
**Priority:** 🟡 Medium  
**Depends On:** [TASK-095-02](./TASK-095-02_Discovery_Handoff_From_LaBSE_to_FastMCP_Search.md), [TASK-095-03](./TASK-095-03_Truth_and_Verification_Handoff_to_Inspection_Contracts.md), [TASK-095-04](./TASK-095-04_Parameter_Memory_and_Workflow_Matching_Hardening.md)

---

## Objective

Implement the core code changes for **Boundary Tests, Telemetry, and Documentation**.

---

## Repository Touchpoints

- `tests/unit/router/application/test_tool_correction_engine.py`
- `tests/unit/router/infrastructure/test_metadata_loader.py`
- `_docs/_ROUTER/semantic-boundary-audit.md`
- `_docs/_ROUTER/RESPONSIBILITY_BOUNDARIES.md`
---

## Planned Work

### Slice Outputs

- move target decisions from semantic inference to platform/inspection ownership
- harden allowed LaBSE roles for workflow/parameter semantics only
- surface boundary enforcement through tests and telemetry markers

### Implementation Checklist

- touch `tests/unit/router/application/test_tool_correction_engine.py` with explicit change notes and boundary rationale
- touch `tests/unit/router/infrastructure/test_metadata_loader.py` with explicit change notes and boundary rationale
- touch `_docs/_ROUTER/semantic-boundary-audit.md` with explicit change notes and boundary rationale
- touch `_docs/_ROUTER/RESPONSIBILITY_BOUNDARIES.md` with explicit change notes and boundary rationale
- add or update focused regression coverage for the slice behavior
- capture before/after evidence tied to the slice outputs

### Review Notes To Attach

- rationale per changed touchpoint and any explicit no-change decisions
- exact test commands and profile/config context used during validation
- deferred work list with safety rationale

---

## Acceptance Criteria

- semantic boundary rules are explicit and enforced in code paths
- discovery/truth responsibilities are not delegated to LaBSE
- boundary violations are detectable in regression tests and telemetry
- slice preserves multilingual semantic benefits in allowed scope

---

## Atomic Work Items

1. Implement boundary enforcement changes in listed touchpoints.
2. Add tests for allowed-role and forbidden-role behaviors.
3. Capture one before/after decision trace showing ownership handoff.
4. Document boundary rationale and operational implications.
