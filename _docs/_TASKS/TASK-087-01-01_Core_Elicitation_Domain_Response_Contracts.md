# TASK-087-01-01: Core Elicitation Domain Model and Response Contracts

**Parent:** [TASK-087-01](./TASK-087-01_Elicitation_Domain_Model_and_Response_Contracts.md)  
**Status:** ✅ Done  
**Priority:** 🔴 High  
**Depends On:** [TASK-083-05](./TASK-083-05_Context_Session_and_Execution_Bridge.md)

---

## Objective

Implement the core code changes for **Elicitation Domain Model and Response Contracts**.

---

## Repository Touchpoints

- `server/router/domain/entities/parameter.py`
- `server/application/tool_handlers/router_handler.py`
- `server/adapters/mcp/context_utils.py`

---

## Planned Work

- create:
  - `server/router/domain/entities/elicitation.py`
  - `server/adapters/mcp/elicitation_contracts.py`
  - `tests/unit/router/domain/entities/test_elicitation.py`
---

## Acceptance Criteria

- unresolved parameters can be mapped into typed elicitation fields
- the contract explicitly supports `accept`, `decline`, and `cancel`
---

## Atomic Work Items

1. Define typed question and answer payloads derived from `ParameterSchema`.
2. Add stable IDs for request, question set, and individual fields.
3. Add serializable persistence rules for partial answers.
