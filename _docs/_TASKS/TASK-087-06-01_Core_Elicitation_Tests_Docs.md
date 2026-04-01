# TASK-087-06-01: Core Elicitation Tests and Docs

**Parent:** [TASK-087-06](./TASK-087-06_Elicitation_Tests_and_Docs.md)  
**Status:** ✅ Done  
**Priority:** 🟡 Medium  
**Depends On:** [TASK-087-03](./TASK-087-03_Constrained_Choice_and_Multi_Select_Flows.md), [TASK-087-04](./TASK-087-04_Session_Persistence_Retry_and_Cancel_Semantics.md), [TASK-087-05](./TASK-087-05_Tool_Only_Fallback_and_Compatibility_Mode.md)

---

## Objective

Implement the core code changes for **Elicitation Tests and Docs**.

---

## Repository Touchpoints

- `tests/unit/router/domain/entities/test_elicitation.py`
- `tests/unit/router/application/test_router_handler_parameters.py`
- `_docs/_MCP_SERVER/README.md`
- `_docs/_PROMPTS/README.md`
- `README.md`
---

## Planned Work

### Regression Scenarios (Required)

1. accept/decline/cancel elicitation paths return deterministic contracts and session state updates.
2. router parameter resolution integrates correctly with native elicitation in async-capable surfaces.
3. tool-only fallback returns typed `needs_input` payloads equivalent to native elicitation semantics.
4. retry/cancel flows preserve or clear partial answers exactly as documented.

### Metrics To Capture

- contract schema validation pass rate for elicitation payloads
- native-vs-fallback parity mismatches (target: 0)
- mean interaction rounds to resolve required parameters

### Documentation Deliverables

- update `_docs/_MCP_SERVER/README.md` with native vs fallback behavior matrix
- update `_docs/_PROMPTS/README.md` with elicitation-aware prompting guidance
- update `README.md` with user-facing clarification flow summary
---

## Acceptance Criteria

- all required elicitation regression scenarios are implemented and passing
- captured metrics are attached with baseline vs post-change values
- docs explicitly describe both native elicitation and tool-only fallback behavior
- no behavioral drift between documented and tested interaction modes
---

## Atomic Work Items

1. Add/expand unit tests for elicitation contracts and router integration paths.
2. Add explicit parity tests for native elicitation vs tool-only fallback payloads.
3. Collect scenario metrics and attach them to the task progress notes.
4. Update docs with regression matrix, examples, and compatibility guidance.
