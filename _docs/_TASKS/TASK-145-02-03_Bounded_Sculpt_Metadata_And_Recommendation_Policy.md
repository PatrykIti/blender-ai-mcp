# TASK-145-02-03: Bounded Sculpt Metadata and Recommendation Policy

**Parent:** [TASK-145-02](./TASK-145-02_Sculpt_Handoff_Context_And_Precondition_Model.md)
**Status:** ✅ Done
**Priority:** 🔴 High
**Depends On:** [TASK-145-02-01](./TASK-145-02-01_Sculpt_Handoff_Contract_And_Local_Target_Semantics.md), [TASK-145-02-02](./TASK-145-02-02_View_Relation_And_Proportion_Preconditions_For_Sculpt.md)

## Objective

Align sculpt handoff with the real sculpt capability surface so the guided
runtime recommends only the intended deterministic subset and does not reopen
brush/setup or broad whole-mesh sculpt paths by accident.

## Implementation Notes

- Update the real recommendation owners, not only metadata:
  - `ReferenceRefinementHandoffContract`
  - `_SCULPT_RECOMMENDED_TOOLS`
  - `_build_refinement_handoff(...)`
- Metadata/search wording must describe the same bounded deterministic subset
  that the handoff can actually recommend.
- If a sculpt tool is visible in search but never recommended by the bounded
  handoff, document why it is excluded from planner-driven handoff.
- Resolve `sculpt_crease_region` explicitly. The public sculpt surface and
  router metadata include it, while today's `_SCULPT_RECOMMENDED_TOOLS` handoff
  subset does not. This task must either add it to the bounded recommended
  subset with matching policy/tests, or document why crease-region work remains
  searchable but outside planner-driven sculpt handoff.
- Progressive unlock, if implemented later, must be handoff-state driven and
  limited to the same deterministic subset.
- A sculpt visibility unlock must also update guided execution policy. Before
  any `sculpt_*` tool becomes guided-visible, either:
  - add an explicit guided family / mapping for the bounded sculpt subset in
    `GuidedFlowFamilyLiteral` and `GUIDED_TOOL_FAMILY_MAP`
  - or make unmapped `sculpt_*` mutators fail closed in `router_helper.py`
    until that mapping exists.
- When that execution policy changes, include
  `tests/unit/adapters/mcp/test_context_bridge.py`; it owns the existing
  role-group spoofing and unmapped mutator fail-closed coverage for
  `router_helper.py`.
- Visibility/search metadata is not enough for sculpt safety. The execution
  gate must block visible sculpt mutators whose family is not allowed by the
  current `guided_flow_state`.

## Runtime / Security Contract

- Visibility level: sculpt tools remain hidden by default on `llm-guided`.
  Handoff metadata may recommend a bounded deterministic subset, but visibility
  does not change unless the implementation explicitly normalizes that bounded
  fact into existing `guided_handoff` / `guided_flow_state`.
- Behavior: handoff metadata is read-only; every `sculpt_*` tool is mutating and
  must remain behind guided visibility and guided execution gates.
- Session/auth assumptions: stdio and Streamable HTTP must derive any sculpt
  visibility from the same session state. Local Blender RPC stays behind the
  existing server/addon connection and is not a new public client auth boundary.
- Parameter validation: reject or omit unsupported sculpt tools, unsupported
  families, unsupported argument hints, and caller-supplied role/family spoofing.
  Do not introduce hidden model-facing sculpt arguments.
- Side effects and recovery: do not change Blender mode, selection, geometry, or
  native MCP visibility from metadata alone. Any visibility change must refresh
  in the active MCP request path and remain recoverable through
  `router_get_status` / the existing visibility refresh path.
- Limits and redaction: keep handoff/search payloads compact and avoid provider
  secrets, local file contents beyond configured artifact references, or
  unbounded image/debug data in logs or responses.

## Pseudocode

```python
eligible_tools = tuple(_SCULPT_RECOMMENDED_TOOLS)
handoff = _build_refinement_handoff(compare_result, refinement_route)

if handoff.selected_family == "sculpt_region" and not sculpt_preconditions.blockers:
    handoff.recommended_tools = [
        tool for tool in handoff.recommended_tools
        if tool.tool_name in eligible_tools
    ]
else:
    handoff.recommended_tools = []

# If recommended tools should become visible, normalize that bounded fact into
# existing guided_handoff / guided_flow_state and let build_visibility_rules(...)
# materialize the native MCP surface.
# Do not expose sculpt tools until GUIDED_TOOL_FAMILY_MAP / guided execution
# policy can resolve and enforce the same bounded sculpt family.
```

## Repository Touchpoints

- `server/adapters/mcp/contracts/reference.py`
- `server/adapters/mcp/areas/reference.py`
- `server/adapters/mcp/areas/sculpt.py`
- `server/adapters/mcp/contracts/guided_flow.py`
- `server/adapters/mcp/transforms/visibility_policy.py`
- `server/adapters/mcp/router_helper.py`
- `server/router/infrastructure/tools_metadata/sculpt/`
- `_docs/_ROUTER/README.md` or the focused guided execution policy docs when
  guided sculpt execution mapping / fail-closed behavior changes
- `tests/unit/adapters/mcp/test_visibility_policy.py`
- `tests/unit/adapters/mcp/test_guided_mode.py`
- `tests/unit/adapters/mcp/test_guided_flow_state_contract.py`
- `tests/unit/adapters/mcp/test_context_bridge.py`
- `tests/unit/adapters/mcp/test_search_surface.py`
- `tests/unit/adapters/mcp/test_reference_images.py`

## Acceptance Criteria

- sculpt recommendation policy is explicit about which sculpt tools are
  eligible for planner-driven handoff
- `sculpt_crease_region` is consciously included in or excluded from the bounded
  planner-driven sculpt subset, with docs/tests matching that decision
- metadata/search wording reflects local deterministic region work, not broad
  "just sculpt it" behavior
- `llm-guided` does not auto-expose the whole sculpt capability by default
- if progressive unlock is later allowed, it is limited to the same bounded
  deterministic subset
- any guided-visible sculpt tool is governed by guided execution policy; no
  `sculpt_*` mutator can become visible while resolving to `family=None`
- metadata/search changes pass router metadata schema validation

## Docs To Update

- `_docs/_MCP_SERVER/README.md`
- `_docs/AVAILABLE_TOOLS_SUMMARY.md`
- `_docs/_PROMPTS/README.md`
- `_docs/_ROUTER/README.md` or focused guided execution policy docs when guided
  sculpt execution mapping / fail-closed behavior changes

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_visibility_policy.py`
- `tests/unit/adapters/mcp/test_guided_mode.py`
- `tests/unit/adapters/mcp/test_guided_flow_state_contract.py`
- `tests/unit/adapters/mcp/test_context_bridge.py`
- `tests/unit/adapters/mcp/test_search_surface.py`
- `tests/unit/adapters/mcp/test_reference_images.py`

## Validation Category

- Targeted unit lane:
  `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_reference_images.py tests/unit/adapters/mcp/test_visibility_policy.py tests/unit/adapters/mcp/test_guided_mode.py tests/unit/adapters/mcp/test_guided_flow_state_contract.py tests/unit/adapters/mcp/test_context_bridge.py tests/unit/adapters/mcp/test_search_surface.py -q`
- Router metadata schema lane when `server/router/infrastructure/tools_metadata/sculpt/*.json` changes:
  `PRE_COMMIT_HOME=/tmp/pre-commit-cache poetry run pre-commit run check-router-tool-metadata --all-files`
- Docs/preflight:
  `git diff --check`

## Changelog Impact

- covered by the parent TASK-145 changelog entry:
  [_docs/_CHANGELOG/276-2026-04-30-task-145-repair-planner-handoff.md](../_CHANGELOG/276-2026-04-30-task-145-repair-planner-handoff.md)

## Completion Summary

Closed by making the planner-driven sculpt subset explicit:
`sculpt_deform_region`, `sculpt_smooth_region`, `sculpt_inflate_region`,
`sculpt_pinch_region`, and `sculpt_crease_region`. The handoff stays
recommendation-only on `llm-guided`, and unmapped `sculpt_*` mutators now fail
closed under active guided execution policy unless a future family mapping
explicitly governs them.

## Status / Board Update

- closed under TASK-145-02
