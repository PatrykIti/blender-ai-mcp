# TASK-162-02: Guided Handoff And Discovery Contract Clarification

**Parent:** [TASK-162](./TASK-162_Guided_Hidden_Tool_Error_Semantics_And_Recovery_Clarity.md)
**Status:** ⏳ To Do
**Priority:** 🔴 High
**Objective:** Align the `guided_manual_build` handoff, shaped visibility contract, and public docs so `direct_tools`, `supporting_tools`, and `search_tools(...)` form one coherent operator path. The remaining problem is not that the repo broadly teaches stale-name guessing today, but that stale persisted handoff/status guidance can drift away from the already-correct search-first live surface after visibility changes.

## Repository Touchpoints

- `server/adapters/mcp/transforms/visibility_policy.py`
- `server/adapters/mcp/areas/router.py`
- `server/adapters/mcp/session_capabilities_state.py`
- `server/adapters/mcp/session_capabilities_bootstrap.py`
- `server/adapters/mcp/surfaces.py`
- `server/application/tool_handlers/router_handler.py`
- `_docs/_MCP_SERVER/README.md`
- `_docs/_MCP_SERVER/MCP_CLIENT_CONFIG_EXAMPLES.md`
- `_docs/AVAILABLE_TOOLS_SUMMARY.md`
- `tests/unit/adapters/mcp/test_visibility_policy.py`
- `tests/unit/adapters/mcp/test_session_phase.py`
- `tests/unit/adapters/mcp/test_router_elicitation.py`
- `tests/e2e/integration/test_guided_surface_contract_parity.py`
- `tests/e2e/integration/test_guided_inspect_validate_handoff.py`

## Implementation Notes

- keep `guided_handoff.direct_tools` limited to tools intended for direct use on
  the current shaped surface
- update the adapter-owned handoff builder in `visibility_policy.py` and the
  MCP-facing router response assembly, not only the coarse no-match shell in
  `router_handler.py`
- keep `router_get_status(...)` semantics aligned with the live product
  contract: the persisted `guided_handoff` remains historical intent, while
  live `visibility_rules` stay the authoritative current surface after a
  refresh barrier narrows visibility
- call out the live split explicitly:
  - generic `guided_manual_build` always emits a handoff payload
  - the stronger coupling between `guided_handoff.direct_tools` and the shaped
    build surface currently exists only for the creature blockout recipe
  - the generic build visibility fallback still comes from
    `GUIDED_BUILD_ESCAPE_HATCH_TOOLS`
- implement the selected product strategy from `TASK-162`: if a refresh barrier
  would fail-close `attachment_alignment`, remove
  `macro_attach_part_to_surface`, `macro_align_part_with_contact`, and
  `macro_cleanup_part_intersections` from the directly visible shaped surface
  for that moment instead of leaving them visible as bait
  - this remaining visible-but-blocked drift is specifically on the
    `inspect_validate` surface; build-phase refresh already collapses to
    spatial-context tools
- ensure the handoff message explicitly says that `direct_tools` are only valid
  while visible, and stale names must not be guessed through `call_tool(...)`
- keep `discovery_tools=["search_tools","call_tool"]`, but update examples so
  they describe search-first recovery rather than speculative retries
- keep the live `surfaces.py` instructions aligned with the same discovery-first
  contract that `_docs/_MCP_SERVER/README.md` and `_docs/AVAILABLE_TOOLS_SUMMARY.md`
  describe
- review whether `supporting_tools` should include phase-pinned spatial refresh
  tools more explicitly when later build families are temporarily hidden
- preserve the FastMCP platform responsibility: this is client-surface shaping,
  not router policy duplication

## Pseudocode

```python
handoff = build_guided_handoff_payload(...)
handoff["message"] = (
    "Use directly visible tools first. "
    "If a needed tool is no longer visible, do not guess it into call_tool(...); "
    "refresh with search_tools(...) or the current guided_flow_state.required_checks first."
)

docs.example = [
    "... read guided_flow_state.required_checks ...",
    "... run the currently pending spatial checks ...",
    "... only after the barrier clears, search for attachment repair tools if still needed ...",
]
```

## Runtime / Security Contract Notes

- do not expose hidden tool names in bootstrap/planning examples beyond the
  tools already disclosed by the shaped surface
- keep direct-vs-discovery semantics stable across stdio and Streamable HTTP
- preserve reject-unknown and compatibility-shim wording for `call_tool(...)`

## Tests To Add/Update

- `tests/e2e/integration/test_guided_surface_contract_parity.py`
- `tests/e2e/integration/test_guided_inspect_validate_handoff.py`
- `tests/e2e/router/test_guided_manual_handoff.py`
- `tests/e2e/integration/test_guided_streamable_spatial_support.py`
- `tests/unit/adapters/mcp/test_visibility_policy.py`
- `tests/unit/adapters/mcp/test_session_phase.py`
- `tests/unit/adapters/mcp/test_router_elicitation.py`
- `tests/unit/adapters/mcp/test_public_surface_docs.py`

## Docs To Update

- `_docs/_MCP_SERVER/README.md`
- `_docs/AVAILABLE_TOOLS_SUMMARY.md`
- `_docs/_PROMPTS/README.md`
- `_docs/_PROMPTS/GUIDED_SESSION_START.md`
- `_docs/_PROMPTS/WORKFLOW_ROUTER_FIRST.md`
- `_docs/_PROMPTS/REFERENCE_GUIDED_CREATURE_BUILD.md`
- `README.md`

## Changelog Impact

- include in the parent `TASK-162` changelog entry when shipped

## Validation Commands

- `git diff --check`
- `rg -n "search_tools\\(\\.\\.\\.\\)|call_tool\\(\\.\\.\\.\\)|Unknown tool|required_checks|guided_handoff" README.md _docs/_MCP_SERVER/README.md _docs/_MCP_SERVER/MCP_CLIENT_CONFIG_EXAMPLES.md _docs/AVAILABLE_TOOLS_SUMMARY.md _docs/_PROMPTS/README.md _docs/_PROMPTS/GUIDED_SESSION_START.md _docs/_PROMPTS/WORKFLOW_ROUTER_FIRST.md _docs/_PROMPTS/REFERENCE_GUIDED_CREATURE_BUILD.md`
- `PYTHONPATH=. poetry run pytest tests/e2e/integration/test_guided_surface_contract_parity.py tests/e2e/integration/test_guided_inspect_validate_handoff.py -q`
- `PYTHONPATH=. poetry run pytest tests/e2e/router/test_guided_manual_handoff.py tests/e2e/integration/test_guided_streamable_spatial_support.py -q`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_visibility_policy.py -q`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_session_phase.py tests/unit/adapters/mcp/test_router_elicitation.py -q`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_public_surface_docs.py -q`
- `poetry run python scripts/run_e2e_tests.py`
- `poetry run pytest ./tests/unit`

## Acceptance Criteria

- the guided handoff no longer implies that stale direct-tool names may be
  retried blindly through `call_tool(...)`
- docs and shaped visibility semantics say the same thing about discovery-first
  recovery
- the task docs explicitly distinguish the generic `guided_manual_build`
  handoff payload from the recipe-specific creature blockout visibility coupling
- `router_get_status(...)` semantics clearly distinguish persisted
  `guided_handoff` intent from the currently authoritative live `visibility_rules`
- the inspect/build surfaces keep bounded repair tools visible only when the
  guided family policy actually allows them; during refresh barriers they are
  hidden instead of remaining visible-but-blocked, with the remaining fix scoped
  to the `inspect_validate` surface rather than the already-collapsed build
  refresh surface

## Status / Board Update

- active child under open parent `TASK-162`; no separate board row
