# TASK-084-04: Search Execution and Router-Aware Call Path

**Parent:** [TASK-084](./TASK-084_Dynamic_Tool_Discovery.md)  
**Status:** 🚧 In Progress  
**Priority:** 🔴 High  
**Depends On:** [TASK-084-02](./TASK-084-02_Search_Transform_and_Pinned_Entry_Surface.md)

---

## Objective

Ensure that tools discovered through search execute through the same router and dispatcher policy path as directly listed tools.

## Current State

The preview search surface now proves the basic execution path:

- discovered-tool execution goes through the built-in `call_tool` proxy
- public alias resolution works through the same canonical-name path as direct calls
- direct public alias calls and proxied calls are parity-tested on the preview surface

This slice remains open because one explicit per-surface router-failure disposition and full auth/visibility parity belong to the later product rollout phase.

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
- add parity tests for direct call vs discovered-call behavior

---

## Pseudocode

```python
def execute_discovered_tool(name, params, ctx):
    return call_tool(name=name, arguments=params)
```

### Design Rule

Do not add a custom discovery execution proxy unless a concrete FastMCP limitation appears in testing.
The default assumption should be that discovered-tool execution goes through the standard transform and middleware chain.

### Failure Policy Rule

This task must define one explicit router-failure disposition per public surface.

Recommended baseline for this repo:

- `llm-guided` and other guided router-governed surfaces are **fail-closed** on router-processing failure
- those guided surfaces return a typed router / execution-report error instead of silently bypassing to direct execution
- `legacy-flat` or other explicit compatibility surfaces may allow **fail-open** behavior only as a documented compatibility mode, and only if direct calls and discovered `call_tool` calls use the same disposition

Do not let `route_tool_call(...)` and middleware-style integration keep different implicit failure behavior once discovered execution is part of the product surface.

---

## Layered Subtasks

| ID | Title | Focus |
|----|-------|-------|
| [TASK-084-04-01](./TASK-084-04-01_Core_Search_Execution_Router_Aware.md) | Core Search Execution and Router-Aware Call Path | Core implementation layer |
| [TASK-084-04-02](./TASK-084-04-02_Tests_Search_Execution_Router_Aware.md) | Tests and Docs Search Execution and Router-Aware Call Path | Tests, docs, and QA |

---

## Acceptance Criteria

- search discovery does not bypass router safety policy
- discovered-call execution remains behaviorally equivalent to direct calls
- direct calls and discovered calls share the same router-failure policy on a given surface

---

## Atomic Work Items

1. Document the canonical execution path for direct and discovered calls.
2. Prove that router interception still happens for discovered tools.
3. Prove that public alias resolution and hidden arguments still behave correctly when called through `call_tool`.
4. Define and test the router-failure disposition for guided and compatibility surfaces so direct and discovered calls stay aligned.
