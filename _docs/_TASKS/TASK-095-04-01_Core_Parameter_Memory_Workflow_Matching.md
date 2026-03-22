# TASK-095-04-01: Core Parameter Memory and Workflow Matching Hardening

**Parent:** [TASK-095-04](./TASK-095-04_Parameter_Memory_and_Workflow_Matching_Hardening.md)  
**Status:** ✅ Done  
**Priority:** 🔴 High  
**Depends On:** [TASK-095-01](./TASK-095-01_Semantic_Responsibility_Policy_and_Code_Audit.md)

---

## Objective

Implement the core code changes for **Parameter Memory and Workflow Matching Hardening**.

---

## Repository Touchpoints

- `server/router/application/resolver/parameter_resolver.py`
- `server/router/application/resolver/parameter_store.py`
- `server/router/application/matcher/semantic_workflow_matcher.py`
- `server/router/application/matcher/ensemble_aggregator.py`

---

## Planned Work

### Slice Outputs

- move target decisions from semantic inference to platform/inspection ownership
- harden allowed LaBSE roles for workflow/parameter semantics only
- surface boundary enforcement through tests and telemetry markers

### Implementation Checklist

- touch `server/router/application/resolver/parameter_resolver.py` with explicit change notes and boundary rationale
- touch `server/router/application/resolver/parameter_store.py` with explicit change notes and boundary rationale
- touch `server/router/application/matcher/semantic_workflow_matcher.py` with explicit change notes and boundary rationale
- touch `server/router/application/matcher/ensemble_aggregator.py` with explicit change notes and boundary rationale
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
