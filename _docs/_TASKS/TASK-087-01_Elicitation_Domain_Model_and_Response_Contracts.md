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

## Layered Subtasks

| ID | Title | Focus |
|----|-------|-------|
| [TASK-087-01-01](./TASK-087-01-01_Core_Elicitation_Domain_Response_Contracts.md) | Core Elicitation Domain Model and Response Contracts | Core implementation layer |
| [TASK-087-01-02](./TASK-087-01-02_Tests_Elicitation_Domain_Response_Contracts.md) | Tests and Docs Elicitation Domain Model and Response Contracts | Tests, docs, and QA |

---

## Acceptance Criteria

- unresolved parameters can be mapped into typed elicitation fields
- the contract explicitly supports `accept`, `decline`, and `cancel`

---

## Atomic Work Items

1. Define typed question and answer payloads derived from `ParameterSchema`.
2. Add stable IDs for request, question set, and individual fields.
3. Add serializable persistence rules for partial answers.
