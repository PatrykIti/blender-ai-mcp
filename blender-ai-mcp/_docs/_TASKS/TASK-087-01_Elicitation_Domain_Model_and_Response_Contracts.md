# TASK-087-01: Clarification Requirements Model and MCP Elicitation Mapping

**Parent:** [TASK-087](./TASK-087_Structured_User_Elicitation.md)  
**Status:** ✅ Done  
**Priority:** 🔴 High  
**Depends On:** [TASK-083-05](./TASK-083-05_Context_Session_and_Execution_Bridge.md)

---

## Objective

Define a domain-neutral clarification-requirements model derived from `ParameterSchema`, then map it at the FastMCP adapter layer to native elicitation or compatibility fallback payloads.

---

## Repository Touchpoints

- `server/router/domain/entities/parameter.py`
- `server/application/tool_handlers/router_handler.py`
- `server/adapters/mcp/context_utils.py`

---

## Planned Work

- create:
  - `server/router/domain/entities/clarification.py`
  - `server/adapters/mcp/elicitation_contracts.py`
  - `tests/unit/router/domain/entities/test_clarification.py`

---

## Pseudocode

```python
@dataclass
class ClarificationRequirement:
    field_name: str
    prompt: str
    value_type: str
    required: bool
    choices: list[str] | None
    allows_multiple: bool = False


@dataclass
class ClarificationPlan:
    goal: str
    workflow_name: str
    requirements: list[ClarificationRequirement]
```

MCP-specific fields such as `request_id`, `question_set_id`, and protocol actions belong in the adapter mapping layer, not in router domain entities.

### Ownership Rule

This subtask owns the domain-neutral clarification plan and the typed missing-input payload for unresolved fields.

It does not own the broader success / no-match / error envelope for `router_set_goal`.
That adapter-facing wrapper belongs to TASK-089-04 and must reuse these clarification models rather than redefining them.

---

## Layered Subtasks

| ID | Title | Focus |
|----|-------|-------|
| [TASK-087-01-01](./TASK-087-01-01_Core_Elicitation_Domain_Response_Contracts.md) | Core Elicitation Domain Model and Response Contracts | Core implementation layer |
| [TASK-087-01-02](./TASK-087-01-02_Tests_Elicitation_Domain_Response_Contracts.md) | Tests and Docs Elicitation Domain Model and Response Contracts | Tests, docs, and QA |

---

## Acceptance Criteria

- unresolved parameters can be mapped into typed clarification requirements
- domain/application models stay free of MCP protocol identifiers and action enums
- the adapter layer can map the same clarification plan to native `ctx.elicit(...)` or to a typed `needs_input` fallback
- TASK-089-04 can embed or reference the same clarification model without introducing schema drift

---

## Atomic Work Items

1. Define domain-neutral clarification requirement and clarification plan models derived from `ParameterSchema`.
2. Keep MCP request IDs, question-set IDs, and protocol action handling in `server/adapters/mcp/elicitation_contracts.py`.
3. Define serializable persistence rules for partial answers and unresolved fields.
4. Add adapter tests proving the same clarification plan can drive native elicitation, compatibility fallback, and the adapter-facing wrapper used by TASK-089-04 without schema drift.
