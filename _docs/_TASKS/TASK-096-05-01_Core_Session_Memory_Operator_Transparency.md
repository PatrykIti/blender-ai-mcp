# TASK-096-05-01: Core Session Memory and Operator Transparency

**Parent:** [TASK-096-05](./TASK-096-05_Session_Memory_and_Operator_Transparency.md)  
**Status:** ⬜ Planned  
**Priority:** 🟡 Medium  
**Depends On:** [TASK-085-01](./TASK-085-01_Session_State_Model_and_Capability_Phases.md), [TASK-096-03](./TASK-096-03_Auto_Fix_Ask_Block_Policy_Engine.md)

---

## Objective

Implement the core code changes for **Session Memory and Operator Transparency**.

---

## Repository Touchpoints

- `server/adapters/mcp/session_state.py`
- `server/adapters/mcp/execution_report.py`
- `server/adapters/mcp/areas/router.py`
- `server/application/tool_handlers/router_handler.py`
- `server/adapters/mcp/contracts/router.py`
---

## Planned Work

### Slice Outputs

- normalize confidence/policy context into deterministic decision inputs
- route medium-confidence and session-memory behavior through explicit policy semantics
- expose operator-visible policy context without ambiguity

### Implementation Checklist

- touch `server/adapters/mcp/session_state.py` with explicit change notes and boundary rationale
- touch `server/adapters/mcp/execution_report.py` with explicit change notes and boundary rationale
- touch `server/adapters/mcp/areas/router.py` with explicit change notes and boundary rationale
- touch `server/application/tool_handlers/router_handler.py` with explicit change notes and boundary rationale
- touch `server/adapters/mcp/contracts/router.py` with explicit change notes and boundary rationale
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

---

## Atomic Work Items

1. Implement confidence/session/policy behavior in listed touchpoints.
2. Add tests for deterministic decisions, escalation, and session persistence/reset.
3. Capture policy decision traces for representative risk classes.
4. Document operator-facing policy semantics and fields.
