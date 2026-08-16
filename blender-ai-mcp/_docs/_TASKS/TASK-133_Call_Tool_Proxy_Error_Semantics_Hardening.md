# TASK-133: call_tool Proxy Error Semantics Hardening

**Status:** ✅ Done
**Priority:** 🟠 High
**Category:** FastMCP Platform / Discovery Reliability
**Estimated Effort:** Small
**Dependencies:** TASK-084
**Follow-on After:** [TASK-084](./TASK-084_Dynamic_Tool_Discovery.md)

**Completion Summary:** The guided discovery `call_tool(...)` proxy now keeps
the same failure semantics as direct tool execution. Proxied `ValueError`-based
validation/runtime failures are no longer flattened into normal text
`ToolResult` payloads, and focused regression coverage proves the proxy now
fails loud instead of reporting apparent success.

## Objective

Close the review regression where the discovery `call_tool(...)` proxy masked
proxied tool failures by converting `ValueError` into a normal text result.

## Business Problem

The shaped guided surface relies on discovery plus proxy execution:

- `search_tools(...)`
- `call_tool(name=..., arguments=...)`

That only works safely if the proxy preserves direct-tool behavior.

When the proxy catches `ValueError` and returns normal text content:

- clients see an apparent success payload instead of a tool failure
- validation errors can be mistaken for successful execution with a warning
- downstream workflow steps can continue under false assumptions

## Business Outcome

If this follow-on is closed correctly, the repo regains:

- consistent failure handling between direct tool calls and discovery proxy
  execution
- more reliable client/workflow behavior on the shaped public surface
- regression coverage for proxied validation/runtime failures

## Scope

This follow-on covers:

- discovery `call_tool(...)` proxy error semantics
- focused regression coverage for proxied `ValueError` propagation
- concise MCP surface/changelog updates documenting the hardened contract

This follow-on does **not** cover:

- redesigning discovery ranking or visibility
- changing prompt-layer guidance
- broader FastMCP error taxonomy changes outside the discovery proxy path

## Repository Touchpoints

- `server/adapters/mcp/discovery/search_surface.py`
- `tests/unit/adapters/mcp/test_search_surface.py`
- `_docs/_MCP_SERVER/README.md`
- `_docs/_CHANGELOG/README.md`
- `_docs/_TASKS/README.md`

## Acceptance Criteria

- proxied `ValueError`-based tool failures do not get converted into normal
  success text results
- guided discovery proxy calls preserve the same failure semantics as direct
  tool execution
- focused regression coverage proves the failure path directly

## Docs To Update

- `_docs/_MCP_SERVER/README.md`
- `_docs/_CHANGELOG/README.md`
- `_docs/_TASKS/README.md`

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_search_surface.py`

## Changelog Impact

- add one `_docs/_CHANGELOG/*` entry for the discovery-proxy hardening

## Status / Board Update

- track this as a standalone completed follow-on on `_docs/_TASKS/README.md`

## Validation

- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_search_surface.py -q`
