# TASK-084-04-01: Core Search Execution and Router-Aware Call Path

**Parent:** [TASK-084-04](./TASK-084-04_Search_Execution_and_Router_Aware_Call_Path.md)  
**Status:** ✅ Done  
**Priority:** 🔴 High  
**Depends On:** [TASK-084-02](./TASK-084-02_Search_Transform_and_Pinned_Entry_Surface.md)

---

## Objective

Implement the core code changes for **Search Execution and Router-Aware Call Path**.

## Completion Summary

This slice is now closed.

- `call_tool` is wired into the default search-first guided surface
- direct-vs-proxy public alias execution is parity-tested
- guided surfaces now use explicit fail-closed router behavior on router-processing failure

---

## Repository Touchpoints

- `server/adapters/mcp/router_helper.py`
- `server/adapters/mcp/dispatcher.py`
- `server/router/adapters/mcp_integration.py`
- `server/router/application/router.py`

---

## Planned Work

- define the canonical call path for:
  - direct public tool calls
  - search proxy execution
  - router-emitted internal tool calls
- use the built-in FastMCP `call_tool` proxy for discovered-tool execution
- define explicit router-failure policy per surface:
  - fail-closed on guided router-governed surfaces
  - explicit fail-open only on documented compatibility surfaces
- add parity tests for direct call vs discovered-call behavior
---

## Acceptance Criteria

- search discovery does not bypass router safety policy
- discovered-call execution remains behaviorally equivalent to direct calls
- direct calls and discovered calls expose the same router-failure disposition on a given surface
---

## Atomic Work Items

1. Document the canonical execution path for direct and discovered calls.
2. Prove that router interception still happens for discovered tools.
3. Prove that public alias resolution and hidden arguments still behave correctly when called through `call_tool`.
4. Implement and test one explicit router-failure policy per surface so discovered execution cannot silently diverge from direct execution.
