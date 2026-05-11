# TASK-135-03-02-02: Existing Profile Tool Proof And Geometry Cases

**Status:** ⏳ To Do
**Priority:** 🔴 High
**Parent:** [TASK-135-03-02](./TASK-135-03-02_Bounded_Profile_Tools_And_Optional_Macro_Wave.md)
**Depends On:** [TASK-135-03-02-01](./TASK-135-03-02-01_Refinement_Visibility_Search_And_Planner_Routing.md)
**Objective:** Prove that the shipped mesh, modeling, and existing macro tools can handle the first low-poly creature profile cases before any new profile macro is promoted.
**Acceptance Criteria:** representative body, ear, limb, snout, and tail profile corrections can be expressed with existing bounded tools or the task records a concrete repeated choreography gap for `TASK-135-03-02-03`.

## Repository Touchpoints

| Path / Module | Owner Seam / Current Lines | Change Contract |
|---------------|----------------------------|-----------------|
| `server/adapters/mcp/areas/mesh.py` | `mesh_select(...)` at `mesh.py:105`; `mesh_select_targeted(...)` at `mesh.py:167`; `mesh_extrude_region(...)` at `mesh.py:365`; `mesh_bevel(...)` at `mesh.py:399`; `mesh_loop_cut(...)` at `mesh.py:420`; `mesh_symmetrize(...)` at `mesh.py:2045` | Use existing mesh operations for profile cases; update wrappers only for real contract gaps |
| `server/adapters/mcp/areas/modeling.py` | `modeling_transform_object(...)` at `modeling.py:927` and bounded create/transform wrappers | Use object-level scale/transform operations only when the guided-family policy from `TASK-135-03-02-01` permits them; otherwise keep profile proof on mesh/macro tools before adding macros |
| `server/adapters/mcp/areas/scene.py` | `macro_adjust_segment_chain_arc(...)` at `scene.py:881`; attach/align macros | Reuse existing macros for tail arcs and seating proof |
| `server/application/tool_handlers/macro_handler.py` | `adjust_segment_chain_arc(...)` around `macro_handler.py:1771` | Add assertions or result metadata only if existing contract lacks proof evidence |
| `blender_addon/application/handlers/mesh.py` and `modeling.py` | addon-side mutators | Touch only if a profile proof needs new Blender-side behavior |
| `tests/unit/tools/macro/test_macro_adjust_segment_chain_arc.py` | macro unit proof | Add creature-tail-like chain cases and verification hints |
| `tests/unit/tools/scene/test_macro_adjust_segment_chain_arc_mcp.py` | MCP macro contract proof | Assert structured contract survives scene macro wrapper |
| `tests/unit/tools/mesh/**` and `tests/unit/tools/modeling/**` | targeted bounded operation tests | Add only for changed mesh/modeling behavior |
| `tests/e2e/tools/macro/test_macro_adjust_segment_chain_arc.py` | Blender-backed tail arc proof | Add TailRoot/TailMid/TailTip case with root still seated after arc |
| `tests/e2e/tools/mesh/**` | Blender-backed mesh proof | Add only when a concrete profile operation changes real geometry |
| `tests/e2e/vision/test_reference_stage_truth_handoff.py` | staged proof | Assert profiled parts clear the relevant refinement blocker after checkpoint refresh |

## Implementation Notes

- Start with existing operations and document the exact operation sequence for
  each proof case.
- Keep proof cases low-poly/faceted: no broad sculpt, no rigging, no curve
  system baseline.
- Do not add a macro just because a sequence is multi-step; add it only if the
  same unsafe selection/setup choreography repeats across more than one part
  class after bounded tools are tried.
- Record failed proof cases with the object class, required setup, failing
  operation, and why existing tools are too broad or unsafe.

## Pseudocode

```python
profile_cases = [
    "flatten_body_mass",
    "point_ear_pair",
    "seat_limb_contact_patch",
    "wedge_snout_profile",
    "arc_tail_chain",
]

for case in profile_cases:
    sequence = plan_existing_tool_sequence(case)
    result = run_sequence_on_fixture(sequence)
    checkpoint = reference_iterate_stage_checkpoint(...)
    if checkpoint.blocks_for_same_profile_reason:
        record_gap(case, sequence, checkpoint.completion_blockers)

if repeated_gap_across_multiple_part_classes:
    open_or_continue("TASK-135-03-02-03")
else:
    close_without_new_macro()
```

## Runtime / Security Contract Notes

- Visibility level: this proof consumes tools exposed by `TASK-135-03-02-01`;
  it does not widen public discovery by itself.
- Read-only vs mutating behavior: proof sequences mutate Blender scene state and
  must mark relevant gate/shape-profile evidence stale before checkpoint refresh.
- Mode and selection impact: mesh operations may enter edit mode, but each proof
  must verify expected mode/selection restoration.
- Session/auth assumptions: local Blender RPC is the trusted mutating backend;
  no external provider loop is required for geometry proof.
- Resource limits: keep proof fixtures small and bounded to a selected object or
  ordered chain; no unbounded scene-wide profile pass.

## Tests To Add/Update

| Test File | Cases / Assertions |
|-----------|--------------------|
| `tests/e2e/tools/mesh/test_creature_profile_cases.py` or the nearest existing mesh E2E owner | `flatten_body_mass`: body bounding box/profile ratio changes toward the requested low-poly silhouette, face count stays bounded, and object remains selectable/inspectable |
| `tests/e2e/tools/mesh/test_creature_profile_cases.py` or the nearest existing mesh E2E owner | `point_ear_pair`: ear pair becomes wedge/point-like, remains symmetric within tolerance, and each ear still contacts or seats on the head |
| `tests/e2e/tools/mesh/test_creature_profile_cases.py` or the nearest existing mesh E2E owner | `seat_limb_contact_patch`: fore/rear limb contact patch clears `floating_gap` / support-contact blockers without hiding unresolved body seams |
| `tests/e2e/tools/mesh/test_creature_profile_cases.py` or the nearest existing mesh E2E owner | `wedge_snout_profile`: snout taper is visible in mesh/scene diagnostics and the snout remains attached to the head |
| `tests/unit/tools/macro/test_macro_adjust_segment_chain_arc.py` | three or four tail-like segments arc deterministically and return verification hints |
| `tests/unit/tools/scene/test_macro_adjust_segment_chain_arc_mcp.py` | MCP wrapper returns the same structured macro contract |
| `tests/unit/tools/mesh/**` | only for changed mesh wrappers; assert selection/mode behavior and typed errors |
| `tests/e2e/tools/macro/test_macro_adjust_segment_chain_arc.py` | `arc_tail_chain`: Blender TailRoot/TailMid/TailTip arc remains ordered, visibly curved, and root is still attachable/seated to Body |
| `tests/e2e/tools/mesh/**` | if mesh wrappers change, real geometry assertions prove profile operation outcome |
| `tests/e2e/vision/test_reference_stage_truth_handoff.py` | checkpoint after each proof sequence clears or narrows the corresponding body, ear, limb, snout, or tail refinement blocker |

## Docs To Update

- `_docs/_PROMPTS/REFERENCE_GUIDED_CREATURE_BUILD.md`
- `_docs/_MCP_SERVER/README.md`
- `_docs/_TESTS/README.md`
- `_docs/_CHANGELOG/README.md`

## Changelog Impact

- Add a `_docs/_CHANGELOG/*` entry if the proof changes runtime behavior or
  closes the bounded profile-tool wave without a new macro.

## Validation Commands

- `git diff --check`
- `PYTHONPATH=. poetry run pytest tests/unit/tools/macro/test_macro_adjust_segment_chain_arc.py tests/unit/tools/scene/test_macro_adjust_segment_chain_arc_mcp.py -q`
- `PYTHONPATH=. poetry run pytest tests/e2e/tools/macro/test_macro_adjust_segment_chain_arc.py tests/e2e/vision/test_reference_stage_truth_handoff.py -q`
- `Outside sandbox before closeout: PYTHONPATH=. poetry run pytest ./tests/unit`
- `Outside sandbox for Blender-backed runtime proof: poetry run python scripts/run_e2e_tests.py`

## Status / Board Update

- When this leaf ships, update its status and record whether `TASK-135-03-02-03`
  remains necessary or is superseded by existing-tool proof.
