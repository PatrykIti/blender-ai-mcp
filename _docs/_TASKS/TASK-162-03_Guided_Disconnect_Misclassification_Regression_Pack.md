# TASK-162-03: Guided Disconnect Misclassification Regression Pack

**Parent:** [TASK-162](./TASK-162_Guided_Hidden_Tool_Error_Semantics_And_Recovery_Clarity.md)
**Status:** ⏳ To Do
**Priority:** 🔴 High
**Objective:** Add regression coverage and closeout notes proving that guided hidden-tool and stale-argument failures remain healthy MCP tool errors rather than apparent disconnects across both repo-owned seams involved in the transcripted failure family:

- the discovery / `call_tool(...)` seam
- the direct guided hidden-tool seam after visibility narrows

The leaf must leave both seams with explicit proof lanes and explicit closeout
documentation.

## Repository Touchpoints

- `server/adapters/mcp/discovery/search_surface.py`
- `server/adapters/mcp/transforms/visibility_policy.py`
- `server/adapters/mcp/session_capabilities_state.py`
- `tests/e2e/integration/test_guided_search_first_call_tool_boundary.py`
- `tests/e2e/integration/test_guided_surface_contract_parity.py`
- `tests/e2e/integration/test_guided_inspect_validate_handoff.py`
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
- add one regression where:
  - the session is healthy
  - a direct guided tool that was valid earlier in the run becomes hidden after
    spatial rearm
  - the resulting failure is still clearly a guided-surface/tool-contract error
    rather than an apparent disconnect
- add one regression for the transcript-backed creature path where attachment
  repair macros are not exposed during `inspect_validate` refresh barriers if
  `attachment_alignment` would be fail-closed anyway
- add one regression where `router_get_status(...)` no longer looks like a live
  source of stale `guided_handoff.direct_tools` after the shaped surface has
  already narrowed
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
- `tests/e2e/integration/test_guided_inspect_validate_handoff.py`
- `tests/e2e/integration/test_guided_streamable_spatial_support.py`

## Docs To Update

- `_docs/_MCP_SERVER/README.md`
- `_docs/AVAILABLE_TOOLS_SUMMARY.md`
- `_docs/_PROMPTS/README.md`
- `_docs/_PROMPTS/WORKFLOW_ROUTER_FIRST.md`
- `_docs/_PROMPTS/REFERENCE_GUIDED_CREATURE_BUILD.md`
- `README.md`
- `_docs/_TASKS/README.md`
- inherit any additional umbrella closeout docs if the final implementation
  changes wider guided examples

## Changelog Impact

- include in the parent `TASK-162` changelog entry when shipped

## Validation Commands

- `git diff --check`
- `rg -n "search_tools\\(\\.\\.\\.\\)|call_tool\\(\\.\\.\\.\\)|Unknown tool|required_checks|guided_handoff" README.md _docs/_MCP_SERVER/README.md _docs/AVAILABLE_TOOLS_SUMMARY.md _docs/_PROMPTS/README.md _docs/_PROMPTS/WORKFLOW_ROUTER_FIRST.md _docs/_PROMPTS/REFERENCE_GUIDED_CREATURE_BUILD.md _docs/_TASKS/README.md _docs/_TASKS/TASK-162*.md`
- `PYTHONPATH=. poetry run pytest tests/e2e/integration/test_guided_search_first_call_tool_boundary.py tests/e2e/integration/test_guided_surface_contract_parity.py tests/e2e/integration/test_guided_inspect_validate_handoff.py tests/e2e/integration/test_guided_streamable_spatial_support.py -q`
- `poetry run python scripts/run_e2e_tests.py`

## Acceptance Criteria

- a hidden-tool failure on the guided discovery / `call_tool(...)` path is
  provably distinguishable from a disconnect in both a stdio lane and a
  Streamable HTTP lane
- a direct guided hidden-tool failure after visibility narrowing is also
  provably distinguishable from a disconnect in integration coverage
- on the transcript-backed creature path, the attachment-repair macros are not
  shown during `inspect_validate` refresh barriers when they would be blocked
  by `attachment_alignment` family gating
- after visibility narrows, `router_get_status(...)` no longer misleads the
  client with stale `guided_handoff` tool guidance that contradicts the current
  shaped surface
- a stale-argument failure on the same seam is provably distinguishable from a
  disconnect in integration coverage, and the proof is attached to an explicit
  `call_tool(...)` regression rather than only a direct tool call
- subsequent calls on the same guided session still work after the failure
  path, proving transport health

## Status / Board Update

- active child under open parent `TASK-162`; no separate board row
