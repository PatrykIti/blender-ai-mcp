# TASK-135-02: Curved Tail And Organic Appendage Build Path

**Status:** ✅ Done
**Priority:** 🔴 High
**Parent:** [TASK-135](./TASK-135_Anatomy_Aware_Reference_Guided_Low_Poly_Creature_Reconstruction.md)
**Category:** Reconstruction / Guided Creature Tooling
**Estimated Effort:** Medium
**Depends On:** [TASK-157](./TASK-157_Goal_Derived_Quality_Gates_And_Deterministic_Verification.md), [TASK-135-01](./TASK-135-01_Creature_Blockout_Completion_Contract_And_Required_Detail_Gates.md)

## Objective

Make reference-guided creature sessions able to build a recognizable curved or
arched tail instead of defaulting to one vertical oval primitive.

The repo already has `macro_adjust_segment_chain_arc(...)`, but that macro only
repositions an existing ordered segment chain. The guided creature flow still
needs a policy and build path that creates an appropriate tail chain in the
first place, seats the root into the body, and then arcs the ordered segments.

## Business Problem

For animals such as squirrels, a tail is one of the main silhouette anchors.
The latest blockout produced a tail that is recognizable as "large rear oval",
but not as a shaped bushy squirrel tail:

- the tail was one detached-looking primitive
- it did not bend or wrap along the reference silhouette
- it lacked a root/mid/tip structure that a low-poly model can still express
- the flow did not naturally choose the existing segment-chain arc macro

This keeps the result below the expected low-poly bar even when the broad
front/side reference proportions are partially followed.

## Repository Touchpoints

| Path / Module | Owner Seam / Current Lines | Expected Change |
|---------------|----------------------------|-----------------|
| `server/adapters/mcp/contracts/quality_gates.py` | `shape_profile`, `attachment_seam`, `recommended_bounded_tools`, creature templates around `quality_gates.py:409` | Keep curved-tail semantics on existing gate vocabulary; do not add tail-specific gate schema fields |
| `server/adapters/mcp/transforms/quality_gate_verifier.py` | `_verify_refinement_stage_gate(...)` at `quality_gate_verifier.py:495`, mesh-metric follow-up around `quality_gate_verifier.py:112` | Block curved-tail completion until shape/profile evidence exists; do not pass from prose or species names |
| `server/adapters/mcp/areas/reference.py` | staged checkpoint route projection around `reference.py:1490` | Surface curved-tail blockers through existing compare/iterate envelopes |
| `server/adapters/mcp/areas/reference_truth.py` | required creature seam and truth-follow-up assembly | Attach `TailRoot`/body seating truth to the same follow-up path as other creature seams |
| `server/adapters/mcp/areas/reference_planner.py` | `select_refinement_route(...)` at `reference_planner.py:542` | Route detached tail-root blockers to `macro`; route tail profile drift to `modeling_mesh` or existing arc macro recommendations |
| `server/adapters/mcp/areas/reference_feedback.py` | `reference_orchestrator_feedback` projection | Keep selected family, next action, and loop disposition aligned with curved-tail blockers |
| `server/adapters/mcp/areas/scene.py` | `macro_adjust_segment_chain_arc(...)` at `scene.py:881` | Reuse the shipped appendage-chain arc macro as the first repair primitive |
| `server/application/tool_handlers/macro_handler.py` | `adjust_segment_chain_arc(...)` handler around `macro_handler.py:1771` | Extend only if an explicit tail-builder macro is promoted after proof that current primitives are insufficient |
| `server/domain/tools/macro.py` | macro interface methods | Add new macro contract only for a promoted tail-builder follow-on |
| `server/adapters/mcp/dispatcher.py` | macro dispatcher mapping around `dispatcher.py:174` | Register a promoted tail-chain macro only if it becomes a real public macro |
| `server/adapters/mcp/transforms/visibility_policy.py` | `build_visibility_rules(...)` at `visibility_policy.py:591`, `visible_tools_for_gate_plan(...)` at `visibility_policy.py:702` | Expose arc/attachment tools only when gate blockers justify them |
| `server/adapters/mcp/router_helper.py` | guided execution-policy decision around `router_helper.py:757` | Map any promoted tail-chain mutator into guided enforcement before exposing it |
| `server/adapters/mcp/discovery/search_surface.py` and `search_documents.py` | `build_search_transform(...)` at `search_surface.py:435`, discovery entries | Add curved/bushy/arched appendage search cues to the live discovery surface |
| `server/router/infrastructure/tools_metadata/**` | scene/macro metadata JSON | Add metadata only for shipped visible tools or promoted macros |
| Prompt/docs surfaces | `_docs/_PROMPTS/REFERENCE_GUIDED_CREATURE_BUILD.md`, `_docs/_MCP_SERVER/README.md` | Document tail chain and arc gate flow after runtime behavior ships |
| Test lanes | `test_macro_adjust_segment_chain_arc.py`, `test_macro_adjust_segment_chain_arc_mcp.py`, guided visibility/search/context tests, E2E macro/vision tests | Add explicit chain, root seating, visibility, and Streamable parity assertions |

## Implementation Notes

- Keep `macro_adjust_segment_chain_arc(...)` as the first reusable primitive for
  ordered appendage arcs.
- Add a guided creature build policy that prefers a multi-segment tail for
  reference cues such as:
  - bushy tail
  - curved tail
  - arched tail
  - tail wrapping up behind the body
- Define the expected segment vocabulary, for example:
  - `TailRoot`
  - `TailMid`
  - `TailTip`
  - or `Tail_01`, `Tail_02`, `Tail_03`, `Tail_04`
- Seat the tail root to the body with a creature seam macro before or after the
  arc operation.
- Consider adding a new bounded macro only if prompt/search policy is not
  enough:
  - `macro_build_curved_tail_chain`
  - input: root object/body, segment count, arc plane, total angle, taper
  - output: created segment names, root seam verdict, arc verification hints
- If `macro_build_curved_tail_chain` is promoted, keep it on the existing
  public scene-macro surface and update the same-surface layers in one slice:
  `server/domain/tools/macro.py`,
  `server/application/tool_handlers/macro_handler.py`,
  `server/adapters/mcp/areas/scene.py`,
  `server/adapters/mcp/dispatcher.py`,
  `server/adapters/mcp/transforms/visibility_policy.py`, and guided execution
  enforcement in `server/adapters/mcp/router_helper.py`, plus router metadata,
  tests, and docs. Only extend DI or addon handlers if the macro cannot be
  composed from the current server-side modeling/scene RPC path.
- Keep the first version low-poly and object-based; do not require rigging,
  sculpt, or a heavy curve system for the baseline.
- Before `TASK-135-03-01` lands, keep this work on the current
  `place_secondary_parts` plus checkpoint cadence. Do not introduce a
  tail-specific guided step or a separate refinement-stage state model here.
- Model this as one generic `shape_profile` gate plus existing staged truth
  and planner surfaces:
  - keep the curved-tail requirement in the gate label/target semantics, not as
    ad hoc gate fields such as `profile_kind`, `required_segments`, or
    `root_attachment_gate`
  - keep `TailRoot` seated to `Body` through the existing attachment/truth path,
    while tail-chain segment count remains a creature-tail policy/verifier
    expectation rather than a new guided role-group or gate-schema field
  - keep that segment-count expectation owned by the current verifier/truth
    path, for example `reference_truth.py` plus
    `quality_gate_verifier.py`, rather than by guided role cardinality in
    `session_capabilities_flow.py`
  - if the creature domain template needs a correction-family hint, stay on the
    current gate vocabulary such as
    `allowed_correction_families=["attachment_alignment", "secondary_parts"]`
  - let `recommended_bounded_tools` remain a server-derived blocker output from
    gate status, truth follow-up, and search shaping instead of a declarative
    gate input field

## Pseudocode

```python
if creature_profile.tail_shape in {"curved", "bushy", "arched"}:
    if not tail_segments_exist:
        modeling_create_primitive(primitive_type="SPHERE", name="TailRoot", size=1.0)
        modeling_transform_object(name="TailRoot", scale=[0.9, 0.35, 0.35])
        modeling_create_primitive(primitive_type="SPHERE", name="TailMid", size=0.9)
        modeling_transform_object(name="TailMid", scale=[0.8, 0.3, 0.3])
        modeling_create_primitive(primitive_type="SPHERE", name="TailTip", size=0.8)
        modeling_transform_object(name="TailTip", scale=[0.7, 0.25, 0.25])
        guided_register_part(object_name="TailRoot", role="tail_mass")

    macro_attach_part_to_surface(
        part_object="TailRoot",
        surface_object="Body",
        surface_axis="X",
        surface_side="negative",
    )

    macro_adjust_segment_chain_arc(
        segment_objects=["TailRoot", "TailMid", "TailTip"],
        rotation_axis="Y",
        total_angle=80,
    )
```

## Runtime / Security Contract Notes

- Visibility level: keep `macro_adjust_segment_chain_arc(...)` and any follow-on
  tail builder on the existing public scene-macro surface. Do not create a
  creature-only appendage runtime or a second discovery path outside current
  MCP seams.
- Read-only vs mutating behavior: tail profile gates, blockers, and search
  hints are server/session-state outputs. Tail creation, seating, and arc
  adjustment stay mutating macro/modeling work and must mark affected
  shape-profile and attachment evidence stale after execution.
- Mode and selection impact: the default path stays object-based. If a follow-on
  needs temporary mesh preparation, it must restore the caller's expected mode
  and selection through the existing guided runtime patterns before returning.
- Session and auth assumptions: tail-chain/profile state stays scoped to the
  active stdio or Streamable HTTP session, with local Blender RPC as the only
  trusted mutating backend.
- Parameter validation and compatibility: `shape_profile` payloads, recommended
  tool ids, segment lists, and any new macro arguments use strict typed
  contracts with reject-unknown behavior. Compatibility shims stay explicit in
  the owning contract layer.
- Side effects, recovery, and logging: tail-chain/profile cues may consume
  shipped `reference_understanding_summary` or silhouette support evidence from
  the closed `TASK-163` seams, but those signals stay advisory-only and cannot
  bypass current gate or visibility policy. Any new tail builder must stay
  deterministic, object-based, bounded in segment count/transform range, fail
  closed to blockers when attachment proof is stale, and keep provider keys or
  local paths out of logs.
- Resource and timeout limits: keep the first slice bounded to one ordered tail
  chain on the current target scope, cap the default chain to 3-4 segments, and
  reuse one attach plus one arc pass per checkpoint iteration instead of
  unbounded per-segment repair loops or curve-system generation.

## Tests To Add/Update

| Layer | Tests |
|-------|-------|
| Unit gate template | Curved squirrel tail emits one normal `shape_profile` gate whose label/target semantics describe the curved-tail expectation without new schema fields |
| Unit search | Curved/bushy/arched tail queries rank `macro_adjust_segment_chain_arc` |
| Unit checkpoint semantics | Curved-tail blockers reuse the existing compare/iterate checkpoint summaries and recommended-tool surfaces |
| Unit guided public surface | Guided visibility/search exposure, contract parity, and public docs stay aligned if curved-tail blockers or macro wording become client-visible |
| Unit macro | Existing arc macro handles three or more tail-like segments |
| Unit MCP contract | Arc macro returns structured verification recommendations |
| E2E macro | TailRoot/TailMid/TailTip arc while TailRoot remains attached to Body |
| E2E checkpoint route | Curved-tail blockers stay aligned with the staged truth/planner handoff surfaces |
| E2E vision | One detached vertical oval tail fails the curved-tail profile gate |

## Docs To Update

- `README.md`
- `_docs/_MCP_SERVER/MCP_CLIENT_CONFIG_EXAMPLES.md`
- `_docs/_PROMPTS/REFERENCE_GUIDED_CREATURE_BUILD.md`
- `_docs/_PROMPTS/README.md`
- `_docs/_PROMPTS/GUIDED_SESSION_START.md`
- `_docs/_PROMPTS/WORKFLOW_ROUTER_FIRST.md`
- `_docs/_PROMPTS/MANUAL_TOOLS_NO_ROUTER.md`
- `_docs/_MCP_SERVER/README.md`
- `_docs/AVAILABLE_TOOLS_SUMMARY.md`
- `_docs/_VISION/README.md`
- relevant `_docs/_VISION/*` creature and refinement docs enforced by
  `test_public_surface_docs.py` when public guided-surface wording changes
- `_docs/_CHANGELOG/README.md`
- `_docs/_TESTS/README.md`

## Changelog Impact

- Add a `_docs/_CHANGELOG/*` entry when the tail-chain path ships.

## Validation Commands

- `git diff --check`
- `PRE_COMMIT_HOME=/tmp/pre-commit-cache poetry run pre-commit run --all-files --show-diff-on-failure`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_quality_gate_intake.py tests/unit/adapters/mcp/test_visibility_policy.py tests/unit/adapters/mcp/test_search_surface.py tests/unit/adapters/mcp/test_reference_images.py tests/unit/adapters/mcp/test_contract_payload_parity.py tests/unit/adapters/mcp/test_guided_mode.py tests/unit/adapters/mcp/test_guided_surface_benchmarks.py tests/unit/adapters/mcp/test_public_surface_docs.py tests/unit/tools/macro/test_macro_adjust_segment_chain_arc.py tests/unit/tools/scene/test_macro_adjust_segment_chain_arc_mcp.py -q`
- `poetry run pytest tests/e2e/integration/test_guided_gate_state_transport.py -q`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_context_bridge.py tests/unit/adapters/mcp/test_prompt_catalog.py tests/unit/adapters/mcp/test_prompt_provider.py -q`
- `PYTHONPATH=. poetry run pytest tests/e2e/integration/test_guided_surface_contract_parity.py tests/e2e/integration/test_guided_streamable_spatial_support.py tests/e2e/tools/macro/test_macro_adjust_segment_chain_arc.py tests/e2e/vision/test_goal_derived_gate_creature_completion.py tests/e2e/vision/test_reference_stage_truth_handoff.py -q`
- `Outside sandbox before closeout: PYTHONPATH=. poetry run pytest ./tests/unit`
- `Outside sandbox for Blender-backed runtime proof: poetry run python scripts/run_e2e_tests.py`

## Status / Board Update

- `TASK-135-02` is closed as the curved-tail / organic appendage gate slice.
- Parent `TASK-135` remains open for the `TASK-135-03*` low-poly refinement
  stage family.
- `_docs/_TASKS/README.md` board wording did not change because the promoted
  umbrella row remains open.
- No new `macro_build_curved_tail_chain` follow-on is opened from this slice:
  the shipped path deliberately uses generic `shape_profile` blockers plus the
  existing `macro_adjust_segment_chain_arc(...)` macro after an ordered
  root/mid/tip chain exists.

## Completion Summary

- 2026-05-11: Reference-understanding can derive a normal
  `shape_profile` quality gate for curved, arched, curled, or bushy tail cues
  without adding tail-specific schema fields.
- `shape_profile` blockers now recommend bounded profile/arc tooling,
  including `macro_adjust_segment_chain_arc(...)`, while visibility still waits
  behind unresolved required seam/support blockers.
- Guided search recovery recognizes profile/arc/curve blockers and can surface
  the existing arc macro instead of pushing the model toward goal reset or
  broad discovery.
- Blender-backed macro proof now covers the real creature-tail sequence:
  `TailRoot` is seated to `Body`, then `TailMid` / `TailTip` are arced while
  `TailRoot` remains in contact.
- Prompt, MCP, tool-summary, vision, test, changelog, and task docs now describe
  the shipped generic-gate tail-profile path.

## Validation Results

- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_quality_gate_intake.py::test_shape_profile_gate_recommends_bounded_profile_and_arc_tools tests/unit/adapters/mcp/test_search_surface.py::test_failed_tail_profile_gate_search_surfaces_arc_repair_tool tests/unit/adapters/mcp/test_reference_images.py::test_refresh_reference_understanding_summary_derives_curved_tail_shape_profile_gate -q`
  - passed outside sandbox, `3 passed`
- `PYTEST_ADDOPTS='-k macro_adjust_segment_chain_arc' poetry run python scripts/run_e2e_tests.py --skip-build`
  - passed outside sandbox, `2 passed, 472 deselected`
- `poetry run ruff check server/adapters/mcp/contracts/quality_gates.py server/adapters/mcp/discovery/search_surface.py server/adapters/mcp/vision/parsing.py server/adapters/mcp/vision/reference_gates.py server/adapters/mcp/areas/reference_understanding.py tests/unit/adapters/mcp/test_quality_gate_intake.py tests/unit/adapters/mcp/test_search_surface.py tests/unit/adapters/mcp/test_reference_images.py tests/e2e/tools/macro/test_macro_adjust_segment_chain_arc.py`
  - passed
- `PRE_COMMIT_HOME=/tmp/pre-commit-cache poetry run pre-commit run --all-files --show-diff-on-failure`
  - passed after rerun; first run reformatted one file through `ruff format`
- `git diff --check`
  - passed

## Acceptance Criteria

- The guided creature flow can represent a curved tail as an ordered chain of
  low-poly parts.
- `macro_adjust_segment_chain_arc(...)` is discoverable and recommended for
  ordered appendage arc repair.
- A squirrel-like tail can be seated to the body and arced without broad
  free-form transform guessing.
- The result keeps separate low-poly parts while still visually reading as one
  attached organic appendage.
