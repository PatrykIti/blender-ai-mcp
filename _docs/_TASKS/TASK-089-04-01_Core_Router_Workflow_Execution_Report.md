# TASK-089-04-01: Core Router, Workflow, and Execution Report Contracts

**Parent:** [TASK-089-04](./TASK-089-04_Router_Workflow_and_Execution_Report_Contracts.md)  
**Status:** ⬜ Planned  
**Priority:** 🔴 High  
**Depends On:** [TASK-089-01](./TASK-089-01_Contract_Catalog_and_Response_Guidelines.md), [TASK-087-01](./TASK-087-01_Elicitation_Domain_Model_and_Response_Contracts.md)

---

## Objective

Implement the core code changes for **Router, Workflow, and Execution Report Contracts**.

---

## Repository Touchpoints

- `server/adapters/mcp/contracts/router.py`
- `server/adapters/mcp/contracts/workflow_catalog.py`
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

### Execution Awareness Rule

The execution report should let an LLM and an operator see:

- what the router decided
- which steps were injected or corrected
- what actually executed
- what failed, blocked, or needs input next

### Clarification Contract Rule

When `router_set_goal` needs clarification:

- reuse the typed clarification / `needs_input` model from TASK-087-01
- do not define a second question schema inside the router contract layer
---

## Layered Subtasks

| ID | Title | Focus |
|----|-------|-------|
| [TASK-089-04-01-01](./TASK-089-04-01-01_Router_Contracts_and_Execution_Report.md) | Router Contracts and Execution Report | Core slice |
| [TASK-089-04-01-02](./TASK-089-04-01-02_Workflow_Catalog_Contracts.md) | Workflow Catalog Contracts | Core slice |

---

## Acceptance Criteria

- router and workflow interactions are machine-readable, not only prose-readable
- `router_set_goal` clarification payloads reuse the TASK-087 model rather than diverging from it
---

## Atomic Work Items

1. Define structured `router_set_goal` success, no-match, and error contracts, and embed the typed `needs_input` clarification model from TASK-087-01.
2. Define workflow catalog list/get/search/import contracts.
3. Define the execution report envelope used by router-aware adapter calls.
