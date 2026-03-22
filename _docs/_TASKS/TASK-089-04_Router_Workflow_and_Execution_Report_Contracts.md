# TASK-089-04: Router, Workflow, and Execution Report Contracts

**Parent:** [TASK-089](./TASK-089_Typed_Contracts_and_Structured_Responses.md)  
**Status:** 🚧 In Progress  
**Priority:** 🔴 High  
**Depends On:** [TASK-089-01](./TASK-089-01_Contract_Catalog_and_Response_Guidelines.md), [TASK-087-01](./TASK-087-01_Elicitation_Domain_Model_and_Response_Contracts.md)

---

## Objective

Introduce typed contracts for `router_set_goal`, router status, workflow catalog responses, and the base execution-report envelope used by router-aware adapter calls.

---

## Repository Touchpoints

- `server/application/tool_handlers/router_handler.py`
- `server/application/tool_handlers/workflow_catalog_handler.py`
- `server/adapters/mcp/areas/router.py`
- `server/adapters/mcp/areas/workflow_catalog.py`
- `server/adapters/mcp/router_helper.py`

---

## Planned Work

- create:
  - `server/adapters/mcp/contracts/router.py`
  - `server/adapters/mcp/contracts/workflow_catalog.py`
  - `tests/unit/router/application/test_router_contracts.py`
- remove direct `json.dumps(...)` returns from `router.py` and `workflow_catalog.py` for contract-enabled paths

### Execution Awareness Rule

The execution report should let an LLM and an operator see:

- what the router decided
- which steps were injected or corrected
- what actually executed
- what failed, blocked, or needs input next

### Ownership Rule

This task owns the base execution-report contract and adapter-facing response envelope.
Later audit/postcondition work in TASK-097 must extend this contract rather than redefining it from scratch.

For `router_set_goal` specifically:

- TASK-087-01 owns the clarification-plan model and the typed `needs_input` question payload
- TASK-089-04 owns the surrounding public response envelope, output schema, and non-clarification success / no-match / error contracts

Reuse the TASK-087-01 clarification model instead of redefining it here.

---

## Layered Subtasks

| ID | Title | Focus |
|----|-------|-------|
| [TASK-089-04-01](./TASK-089-04-01_Core_Router_Workflow_Execution_Report.md) | Core Router, Workflow, and Execution Report Contracts | Core implementation layer |
| [TASK-089-04-02](./TASK-089-04-02_Tests_Router_Workflow_Execution_Report.md) | Tests and Docs Router, Workflow, and Execution Report Contracts | Tests, docs, and QA |

---

## Acceptance Criteria

- router and workflow interactions are machine-readable, not only prose-readable
- structured router/workflow responses use `structuredContent` with contract-aligned `outputSchema`
- `router_set_goal` clarification payloads reuse the TASK-087 clarification schema instead of introducing a competing one

---

## Atomic Work Items

1. Define structured `router_set_goal` success, no-match, and error contracts, and reuse the typed `needs_input` clarification shape from TASK-087-01 instead of redefining it.
2. Define workflow catalog list/get/search/import contracts.
3. Return native object/model payloads from router and workflow catalog adapters instead of JSON strings.
4. Define the base execution report envelope used by router-aware adapter calls.
5. Keep audit-trail and postcondition-verification fields out of the base contract until TASK-097 layers them on intentionally.
