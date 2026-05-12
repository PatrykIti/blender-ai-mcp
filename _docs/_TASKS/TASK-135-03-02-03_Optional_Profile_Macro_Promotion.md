# TASK-135-03-02-03: Optional Profile Macro Promotion

**Status:** ⏭️ Superseded
**Priority:** 🔴 High
**Parent:** [TASK-135-03-02](./TASK-135-03-02_Bounded_Profile_Tools_And_Optional_Macro_Wave.md)
**Depends On:** [TASK-135-03-02-02](./TASK-135-03-02-02_Existing_Profile_Tool_Proof_And_Geometry_Cases.md)
**Objective:** Promote the smallest deterministic profile macro only if existing mesh/modeling/macro proof shows a repeated unsafe or unbounded choreography gap.
**Acceptance Criteria:** no new macro is added without proof evidence from `TASK-135-03-02-02`; if promoted, the macro has domain, application, MCP, metadata, guided enforcement, unit, Streamable, Blender E2E, docs, and changelog coverage in the same slice.

## Repository Touchpoints

| Path / Module | Owner Seam / Current Lines | Change Contract |
|---------------|----------------------------|-----------------|
| `server/domain/tools/macro.py` | `IMacroTool` at `macro.py:5`; existing method pattern such as `adjust_segment_chain_arc(...)` at `macro.py:139` | Add one explicit interface method only for the promoted macro |
| `server/application/tool_handlers/macro_handler.py` | `MacroToolHandler` at `macro_handler.py:27`; existing `adjust_segment_chain_arc(...)` pattern at `macro_handler.py:1751`; `_make_capture_bundle_id(...)` at `macro_handler.py:2309` | Implement bounded deterministic orchestration over existing scene/modeling/mesh operations where possible |
| `server/adapters/mcp/areas/scene.py` | public macro wrapper near existing macro tools such as `scene.py:881` | Expose the macro on the current scene/macro surface, not a creature-only parallel tool |
| `server/adapters/mcp/dispatcher.py` | macro dispatcher mapping around `dispatcher.py:174` | Register the macro for routed/internal execution if needed |
| `server/adapters/mcp/router_helper.py` | guided execution-policy decision around `router_helper.py:667` | Map the macro to an allowed guided family before visibility exposes it |
| `server/adapters/mcp/transforms/visibility_policy.py` | `build_visibility_rules(...)` and `visible_tools_for_gate_plan(...)` | Expose the macro only for active refinement/profile blockers |
| `server/router/infrastructure/tools_metadata/scene/` | metadata JSON and schema checks for current scene/macro-surface tools | Add search/gate metadata for the promoted macro on the existing scene metadata surface; do not invent a separate macro metadata area unless the runtime tool area is split in the same task |
| `blender_addon/application/handlers/mesh.py` or `modeling.py` | addon-side operation only if server composition is insufficient | Touch addon only for unavoidable new Blender behavior |
| `tests/unit/tools/macro/**` and `tests/unit/tools/scene/**` | macro handler/MCP wrapper tests | Assert strict argument validation, bounded ranges, result contract, and error cases |
| `tests/unit/adapters/mcp/test_visibility_policy.py`, `test_search_surface.py`, `test_context_bridge.py` | visibility/search/enforcement tests | Assert the new macro appears only when active blockers justify it and guided enforcement allows it |
| `tests/e2e/integration/test_guided_streamable_spatial_support.py` | Streamable proof | Assert Streamable can discover/execute the macro only on the guided refinement surface |
| `tests/e2e/tools/macro/**` | Blender-backed macro proof | Assert real geometry outcome, mode/selection restoration, and gate-refresh handoff |

## Implementation Notes

- This leaf is conditional. Supersede it if `TASK-135-03-02-02` proves existing
  tools are sufficient.
- Candidate macro names remain examples until proof selects one:
  - `macro_refine_creature_part_profile`
  - `macro_point_creature_ears`
  - `macro_flatten_limb_contact_patch`
  - `macro_add_creature_eye_pair`
- The macro must be bounded by target objects, max transform/selection scope,
  and deterministic operation count.
- Do not add generic "profile anything" behavior. The macro must have a clear
  role/profile target and typed validation.

## Pseudocode

```python
gap = load_gap_from("TASK-135-03-02-02")
if not gap.repeated_across_multiple_part_classes:
    mark_superseded("existing tools are sufficient")

contract = define_macro_contract(
    target_object=required_name,
    profile_operation=enum_values,
    max_extent_delta=bounded_float,
)
result = run_bounded_profile_operation(contract)
mark_gate_evidence_stale(target_object)
return MacroExecutionReportContract(
    macro_name=contract.name,
    affected_objects=[target_object],
    verification_recommendations=["scene_relation_graph", "mesh_inspect"],
)
```

## Runtime / Security Contract Notes

- Visibility level: public scene/macro surface, but guided-phase-only visibility
  when blocker state requires it.
- Read-only vs mutating behavior: mutating Blender operation through existing
  local RPC/addon path; must mark scene/gate evidence stale.
- Mode and selection impact: macro must restore expected mode/selection or
  report explicit restoration failure.
- Session/auth assumptions: local Blender RPC only; no external provider or
  file access.
- Parameter validation: reject unknown fields, invalid object names, unbounded
  deltas, and unsupported profile operations.
- Recovery: failures return structured macro report/error and bounded follow-up
  tools, not uncaught exceptions or final completion.

## Tests To Add/Update

| Test File | Cases / Assertions |
|-----------|--------------------|
| `tests/unit/tools/macro/**` | macro validates required target object, rejects unknown profile operations, clamps/blocks unbounded deltas, and returns structured report |
| `tests/unit/tools/scene/**` | MCP wrapper preserves structured macro response and routed partial-report errors |
| `tests/unit/adapters/mcp/test_visibility_policy.py` | macro visible only for matching refinement/profile blockers |
| `tests/unit/adapters/mcp/test_search_surface.py` | search returns macro only on guided surface when visible |
| `tests/unit/adapters/mcp/test_context_bridge.py` | guided execution enforcement maps macro to allowed family |
| `tests/e2e/integration/test_guided_streamable_spatial_support.py` | Streamable discovery/execution parity for the promoted macro |
| `tests/e2e/tools/macro/**` | Blender geometry changed as expected, mode/selection restored, and follow-up gate evidence is stale until refreshed |

## Docs To Update

- `_docs/_MCP_SERVER/README.md`
- `_docs/AVAILABLE_TOOLS_SUMMARY.md`
- `_docs/_PROMPTS/REFERENCE_GUIDED_CREATURE_BUILD.md`
- `_docs/_TESTS/README.md`
- `_docs/_CHANGELOG/README.md`

## Changelog Impact

- Add a `_docs/_CHANGELOG/*` entry when a new macro is promoted. Mark this leaf
  `⏭️ Superseded` if no macro is needed after `TASK-135-03-02-02`.

## Validation Commands

- `git diff --check`
- `PRE_COMMIT_HOME=/tmp/pre-commit-cache poetry run pre-commit run --all-files --show-diff-on-failure`
- `PYTHONPATH=. poetry run pytest tests/unit/tools/macro tests/unit/tools/scene tests/unit/adapters/mcp/test_visibility_policy.py tests/unit/adapters/mcp/test_search_surface.py tests/unit/adapters/mcp/test_context_bridge.py -q`
- `PYTHONPATH=. poetry run pytest tests/e2e/integration/test_guided_streamable_spatial_support.py tests/e2e/tools/macro -q`
- `Outside sandbox before closeout: PYTHONPATH=. poetry run pytest ./tests/unit`
- `Outside sandbox for Blender-backed runtime proof: poetry run python scripts/run_e2e_tests.py`

## Status / Board Update

- `TASK-135-03-02-03` is superseded by the existing-tool proof from
  `TASK-135-03-02-02`.
- `TASK-135-03-02`, `TASK-135-03`, and the umbrella `TASK-135` now close on
  the shipped bounded mesh/macro surface instead of promoting a new macro.

## Completion Summary

- 2026-05-11: The bounded proof wave did not expose any repeated unsafe
  selection/setup choreography across more than one creature part class.
- Because body, ear, snout, limb, and tail cases are already expressible on the
  shipped surface, no new profile macro was added under this task family.
