# TASK-089-04: Router, Workflow, and Execution Report Contracts

**Parent:** [TASK-089](./TASK-089_Typed_Contracts_and_Structured_Responses.md)  
**Status:** ⬜ Planned  
**Priority:** 🔴 High  
**Depends On:** [TASK-089-01](./TASK-089-01_Contract_Catalog_and_Response_Guidelines.md)

---

## Objective

Introduce typed contracts for `router_set_goal`, router status, workflow catalog responses, and execution reporting.

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

### Execution Awareness Rule

The execution report should let an LLM and an operator see:

- what the router decided
- which steps were injected or corrected
- what actually executed
- what failed, blocked, or needs input next

---

## Layered Subtasks

| ID | Title | Focus |
|----|-------|-------|
| [TASK-089-04-01](./TASK-089-04-01_Core_Router_Workflow_Execution_Report.md) | Core Router, Workflow, and Execution Report Contracts | Core implementation layer |
| [TASK-089-04-02](./TASK-089-04-02_Tests_Router_Workflow_Execution_Report.md) | Tests and Docs Router, Workflow, and Execution Report Contracts | Tests, docs, and QA |

---

## Acceptance Criteria

- router and workflow interactions are machine-readable, not only prose-readable

---

## Atomic Work Items

1. Define structured `router_set_goal` success, needs-input, no-match, and error contracts.
2. Define workflow catalog list/get/search/import contracts.
3. Define the execution report envelope used by router-aware adapter calls.
