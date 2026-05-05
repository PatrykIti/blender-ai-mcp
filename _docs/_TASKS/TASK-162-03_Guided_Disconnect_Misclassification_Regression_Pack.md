# TASK-162-03: Guided Disconnect Misclassification Regression Pack

**Parent:** [TASK-162](./TASK-162_Guided_Hidden_Tool_Error_Semantics_And_Recovery_Clarity.md)
**Status:** ⏳ To Do
**Priority:** 🔴 High
**Objective:** Add regression coverage and closeout notes proving that guided hidden-tool and stale-argument failures remain healthy MCP tool errors rather than apparent disconnects across the repo-owned seams involved in the transcripted failure family:

- the discovery / `call_tool(...)` seam, where this family owns the hidden-tool
  error wording directly
- the direct guided path only insofar as the repo can prevent the bad retry by
  hiding invalid mutators earlier after visibility narrows

This child task must leave both seams with explicit proof lanes and explicit closeout
documentation, without claiming that this family rewrites the raw direct hidden
tool error surface itself.

## Repository Touchpoints

- `server/adapters/mcp/discovery/search_surface.py`
- `server/adapters/mcp/transforms/visibility_policy.py`
- `server/adapters/mcp/areas/router.py`
- `server/adapters/mcp/router_helper.py`
- `server/adapters/mcp/session_capabilities_state.py`
- `tests/e2e/integration/test_guided_search_first_call_tool_boundary.py`
- `tests/e2e/integration/test_guided_surface_contract_parity.py`
- `tests/e2e/integration/test_guided_inspect_validate_handoff.py`
  This file must carry the post-handoff `inspect_validate +
  spatial_refresh_required` case proving those macros are hidden under the
  refresh barrier, not only the current steady inspect visibility assertion.
- `tests/e2e/integration/test_guided_streamable_spatial_support.py`
  This file must carry the synthetic Streamable HTTP `call_tool(...)`
  hidden-tool lane and the post-failure continuity check for that path, not
  only the current direct hidden-tool regression.
- `_docs/_MCP_SERVER/README.md`
- `_docs/_TASKS/README.md`

## Implementation Notes

- add one regression where:
  - the session is healthy
  - a known guided tool becomes hidden after spatial rearm on the guided
    discovery / `call_tool(...)` path
  - the client receives a recovery-oriented `ToolError`
  - subsequent MCP calls still succeed on the same session
  - the named stdio proof lane is extended to perform that post-failure
    follow-up call explicitly instead of only matching the first error text
- add one regression where:
  - the session is healthy
  - a direct guided tool that was valid earlier in the run becomes hidden after
    spatial rearm
  - the bad retry is prevented earlier because the now-invalid mutator is no
    longer visible on the shaped surface
- add one regression for the transcript-backed creature path where attachment
  repair macros are not exposed during `inspect_validate` refresh barriers if
  `attachment_alignment` would be fail-closed anyway
  - this proof must live in an inspect/validate lane such as
    `test_guided_inspect_validate_handoff.py`, extended with a post-handoff
    refresh-barrier case, not only in the build refresh streamable lane
- add one regression where `router_get_status(...)` no longer looks like a live
  source of stale `guided_handoff.direct_tools` after the shaped surface has
  already narrowed; persisted handoff stays historical intent while live
  `visibility_rules` remain authoritative
  - the named owner lanes must extend beyond initial handoff persistence or a
    static status snapshot and cover one post-transition divergence case
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
# The first step depends on current scene state.
# Empty / bootstrap-noise scenes can already land on bootstrap_primary_workset,
# while scenes with meaningful guided objects can stay at establish_spatial_context.
assert result["guided_flow_state"]["current_step"] in {
    "establish_spatial_context",
    "bootstrap_primary_workset",
}

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
- `tests/e2e/router/test_guided_manual_handoff.py`
- `tests/unit/adapters/mcp/test_search_surface.py`
- `tests/unit/adapters/mcp/test_visibility_policy.py`
- `tests/unit/adapters/mcp/test_router_elicitation.py`
- `tests/unit/adapters/mcp/test_session_phase.py`
- `tests/unit/adapters/mcp/test_public_surface_docs.py`

## Docs To Update

- `_docs/_MCP_SERVER/README.md`
- `_docs/_MCP_SERVER/MCP_CLIENT_CONFIG_EXAMPLES.md`
- `_docs/AVAILABLE_TOOLS_SUMMARY.md`
- `_docs/_PROMPTS/README.md`
- `_docs/_PROMPTS/GUIDED_SESSION_START.md`
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
- `# _docs/_PROMPTS/GUIDED_SESSION_START.md is consistency-audited here because the current public docs parity suite does not load it directly.`
- `rg -n "search_tools\\(\\.\\.\\.\\)|call_tool\\(\\.\\.\\.\\)|Unknown tool|required_checks|guided_handoff|visibility_rules|macro_attach_part_to_surface|macro_align_part_with_contact|macro_cleanup_part_intersections" README.md _docs/_MCP_SERVER/README.md _docs/_MCP_SERVER/MCP_CLIENT_CONFIG_EXAMPLES.md _docs/AVAILABLE_TOOLS_SUMMARY.md _docs/_PROMPTS/README.md _docs/_PROMPTS/GUIDED_SESSION_START.md _docs/_PROMPTS/WORKFLOW_ROUTER_FIRST.md _docs/_PROMPTS/REFERENCE_GUIDED_CREATURE_BUILD.md _docs/_TASKS/README.md _docs/_TASKS/TASK-162*.md`
- `PYTHONPATH=. poetry run pytest tests/e2e/integration/test_guided_search_first_call_tool_boundary.py tests/e2e/integration/test_guided_surface_contract_parity.py tests/e2e/integration/test_guided_inspect_validate_handoff.py tests/e2e/integration/test_guided_streamable_spatial_support.py tests/e2e/router/test_guided_manual_handoff.py -q`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_search_surface.py tests/unit/adapters/mcp/test_visibility_policy.py tests/unit/adapters/mcp/test_router_elicitation.py tests/unit/adapters/mcp/test_session_phase.py tests/unit/adapters/mcp/test_public_surface_docs.py -q`
- `poetry run python scripts/run_e2e_tests.py`
- `poetry run pytest ./tests/unit`

## Acceptance Criteria

- a hidden-tool failure on the guided discovery / `call_tool(...)` path is
  provably a deterministic tool-contract error with healthy post-failure
  session/transport continuity in the named stdio and Streamable HTTP lanes
- on the direct guided path, the transcript-backed invalid mutator is no longer
  visible after visibility narrowing, so the model is not led into a
  visible-but-blocked retry
- on the transcript-backed creature path, the attachment-repair macros are not
  shown during `inspect_validate` refresh barriers when they would be blocked
  by `attachment_alignment` family gating
- after visibility narrows, `router_get_status(...)` no longer misleads the
  client by presenting persisted `guided_handoff` guidance as if it were the
  current live surface; the split between historical handoff intent and current
  `visibility_rules` is explicit in regression coverage
- a stale-argument failure on the same seam is provably distinguishable from a
  disconnect in integration coverage, and the proof is attached to an explicit
  `call_tool(...)` regression rather than only a direct tool call
- subsequent calls on the same guided session still work after the failure
  path, proving transport health on the named lanes that are expected to carry
  a post-failure follow-up call

## Status / Board Update

- active child under open parent `TASK-162`; no separate board row
