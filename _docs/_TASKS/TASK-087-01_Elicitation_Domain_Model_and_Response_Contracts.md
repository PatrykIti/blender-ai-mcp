# TASK-087-01: Elicitation Domain Model and Response Contracts

**Parent:** [TASK-087](./TASK-087_Structured_User_Elicitation.md)  
**Status:** ⬜ Planned  
**Priority:** 🔴 High  
**Depends On:** [TASK-083-05](./TASK-083-05_Context_Session_and_Execution_Bridge.md)

---

## Objective

Define typed elicitation request and response models that can be derived from `ParameterSchema` and persisted safely across a session.

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

## Pseudocode

```python
@dataclass
class ElicitationRequest:
    request_id: str
    question_set_id: str
    goal: str
    workflow_name: str
    fields: list[ElicitationField]
```

---

## Acceptance Criteria

- unresolved parameters can be mapped into typed elicitation fields
- the contract explicitly supports `accept`, `decline`, and `cancel`

---

## Atomic Work Items

1. Define typed question and answer payloads derived from `ParameterSchema`.
2. Add stable IDs for request, question set, and individual fields.
3. Add serializable persistence rules for partial answers.
