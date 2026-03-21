# TASK-096-04-01: Core Medium-Confidence Elicitation and Escalation

**Parent:** [TASK-096-04](./TASK-096-04_Medium_Confidence_Elicitation_and_Escalation.md)  
**Status:** ⬜ Planned  
**Priority:** 🔴 High  
**Depends On:** [TASK-087-02](./TASK-087-02_Router_Parameter_Resolution_Integration.md), [TASK-096-03](./TASK-096-03_Auto_Fix_Ask_Block_Policy_Engine.md)

---

## Objective

Implement the core code changes for **Medium-Confidence Elicitation and Escalation**.

---

## Repository Touchpoints

- `server/adapters/mcp/areas/router.py`
- `server/application/tool_handlers/router_handler.py`
- `server/router/application/policy/correction_policy_engine.py`
- `server/adapters/mcp/elicitation_contracts.py`
- `server/infrastructure/di.py`
- `tests/unit/router/application/test_router_handler_parameters.py`
---

## Planned Work

### Slice Outputs

- normalize confidence/policy context into deterministic decision inputs
- route medium-confidence and session-memory behavior through explicit policy semantics
- expose operator-visible policy context without ambiguity

### Implementation Checklist

- touch `server/adapters/mcp/areas/router.py` with explicit change notes and boundary rationale
- touch `server/application/tool_handlers/router_handler.py` with explicit change notes and boundary rationale
- touch `server/router/application/policy/correction_policy_engine.py` with explicit change notes and boundary rationale
- touch `server/adapters/mcp/elicitation_contracts.py` with explicit change notes and boundary rationale
- touch `server/infrastructure/di.py` with explicit change notes and boundary rationale when adding or changing runtime collaborators
- touch `tests/unit/router/application/test_router_handler_parameters.py` with explicit change notes and boundary rationale
- add or update focused regression coverage for the slice behavior
- capture before/after evidence tied to the slice outputs

### Review Notes To Attach

- rationale per changed touchpoint and any explicit no-change decisions
- exact test commands and profile/config context used during validation
- deferred work list with safety rationale

---

## Acceptance Criteria

- policy decisions are deterministic for equivalent inputs
- session/operator context is consistent with executed decisions
- escalation behavior is test-covered and contract-driven
- slice integrates with audit/reporting layers without hidden heuristics
- runtime collaborator wiring stays explicit through DI

---

## Atomic Work Items

1. Implement confidence/session/policy behavior in listed touchpoints.
2. Add tests for deterministic decisions, escalation, and session persistence/reset.
3. Capture policy decision traces for representative risk classes.
4. Document operator-facing policy semantics and fields.
