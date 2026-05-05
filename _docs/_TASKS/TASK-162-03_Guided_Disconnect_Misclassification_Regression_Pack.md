# TASK-162-03: Guided Disconnect Misclassification Regression Pack

**Parent:** [TASK-162](./TASK-162_Guided_Hidden_Tool_Error_Semantics_And_Recovery_Clarity.md)
**Status:** ⏳ To Do
**Priority:** 🔴 High
**Objective:** Add regression coverage and closeout notes proving that guided hidden-tool and stale-argument failures on the discovery / `call_tool(...)` seam remain healthy MCP tool errors rather than apparent disconnects, with one explicit stdio lane and one explicit Streamable HTTP lane.

## Repository Touchpoints

- `tests/e2e/integration/test_guided_search_first_call_tool_boundary.py`
- `tests/e2e/integration/test_guided_surface_contract_parity.py`
- `tests/e2e/integration/test_guided_streamable_spatial_support.py`
- `_docs/_MCP_SERVER/README.md`
- `_docs/_TASKS/README.md`

## Implementation Notes

- add one regression where:
  - the session is healthy
  - a known guided tool becomes hidden after spatial rearm on the guided
    discovery / `call_tool(...)` path
  - the client receives a recovery-oriented `ToolError`
  - subsequent MCP calls still succeed on the same session
- add one regression for stale/legacy argument shapes on a visible macro so the
  failure is clearly a contract error rather than a transport symptom
- keep at least one stdio lane and one Streamable HTTP lane in scope
- the named files must be extended so they really cover this seam:
  - `test_guided_search_first_call_tool_boundary.py` or
    `test_guided_surface_contract_parity.py` must include the stale-argument
    failure through `call_tool(...)`, not only a direct visible-tool failure
  - `test_guided_streamable_spatial_support.py` must include the hidden-tool
    failure through `call_tool(...)` on Streamable HTTP, not only the direct
    hidden-tool lane
- close out the task with validation evidence that names the exact files and
  the final expected error wording

## Pseudocode

```python
result = await client.call_tool("router_set_goal", {...})
assert result["guided_flow_state"]["current_step"] == "bootstrap_primary_workset"

... create primary masses ...
... trigger spatial rearm ...

with pytest.raises(ToolError, match="scene_scope_graph"):
    await client.call_tool("call_tool", {"name": "macro_cleanup_part_intersections", ...})

status = await client.call_tool("router_get_status", {})
assert status["session_id"] == original_session_id
assert status["guided_flow_state"]["spatial_refresh_required"] is True
```

## Runtime / Security Contract Notes

- regression assertions should verify deterministic contract wording, not private
  exception internals
- do not rely on brittle stack-trace matching
- keep transport-health assertions bounded to supported MCP behavior such as
  successful subsequent calls on the same session

## Tests To Add/Update

- `tests/e2e/integration/test_guided_search_first_call_tool_boundary.py`
- `tests/e2e/integration/test_guided_surface_contract_parity.py`
- `tests/e2e/integration/test_guided_streamable_spatial_support.py`

## Docs To Update

- inherit umbrella docs and task closeout notes

## Changelog Impact

- include in the parent `TASK-162` changelog entry when shipped

## Validation Commands

- `PYTHONPATH=. poetry run pytest tests/e2e/integration/test_guided_search_first_call_tool_boundary.py tests/e2e/integration/test_guided_surface_contract_parity.py tests/e2e/integration/test_guided_streamable_spatial_support.py -q`
- `poetry run python scripts/run_e2e_tests.py`

## Acceptance Criteria

- a hidden-tool failure on the guided discovery / `call_tool(...)` path is
  provably distinguishable from a disconnect in both a stdio lane and a
  Streamable HTTP lane
- a stale-argument failure on the same seam is provably distinguishable from a
  disconnect in integration coverage, and the proof is attached to an explicit
  `call_tool(...)` regression rather than only a direct tool call
- subsequent calls on the same guided session still work after the failure
  path, proving transport health

## Status / Board Update

- active child under open parent `TASK-162`; no separate board row
