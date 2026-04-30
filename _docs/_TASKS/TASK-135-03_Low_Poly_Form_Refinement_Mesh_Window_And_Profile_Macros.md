# TASK-135-03: Low-Poly Form Refinement Mesh Window And Profile Macros

**Status:** ⏳ To Do
**Priority:** 🔴 High
**Parent:** [TASK-135](./TASK-135_Anatomy_Aware_Reference_Guided_Low_Poly_Creature_Reconstruction.md)
**Category:** Reconstruction / Guided Mesh Refinement
**Estimated Effort:** Large
**Depends On:** [TASK-157](./TASK-157_Goal_Derived_Quality_Gates_And_Deterministic_Verification.md)

## Objective

Add a stage-gated low-poly form refinement path after primitive mass placement,
so guided creature sessions can move beyond "geometric blobs placed near each
other" while still staying bounded and LLM-safe.

The goal is not photoreal sculpting. The goal is a recognizable low-poly
creature profile:

- tapered or flattened body masses where the reference requires it
- seated limbs instead of separate balls
- pointed or wedge-like ears
- small eyes/nose/snout details
- shaped tail segments
- visibly attached parts

## Business Problem

The current creature recipe exposes modeling and mesh tools, but the flow can
still behave as though primitive placement is the whole product. That creates
results that technically contain the requested object names, but still look like
unrefined spheres/ellipsoids.

For low-poly reconstruction, the expected baseline should be:

- primary masses first
- attachment/seam repair
- then a bounded mesh/modeling refinement window
- then final checkpoint

Without an explicit refinement window, clients often stop too early or avoid
mesh tools entirely.

## Repository Touchpoints

| Path / Module | Expected Change |
|---------------|-----------------|
| `server/adapters/mcp/session_capabilities.py` | Add `refine_low_poly_forms` gate/step state and stale tracking |
| `server/adapters/mcp/transforms/visibility_policy.py` | Open bounded mesh/modeling tools only when refinement prerequisites pass |
| `server/adapters/mcp/discovery/search_documents.py` | Add low-poly profile/refinement search cues |
| `server/adapters/mcp/areas/mesh.py` | Ensure selected mesh tools work in the guided refinement window |
| `server/adapters/mcp/areas/modeling.py` | Keep bounded transforms available for part profiling |
| `server/adapters/mcp/areas/scene.py` | Add or expose profile macros if needed |
| `server/router/infrastructure/tools_metadata/` | Add gate metadata for refinement tools and macros |
| `server/application/tool_handlers/macro_handler.py` | Add optional profile macros only when existing mesh tools are insufficient |
| `blender_addon/application/handlers/mesh_handler.py` | Update if new mesh operations are required |
| `blender_addon/application/handlers/modeling_handler.py` | Update if profile macros need addon support |
| `tests/unit/adapters/mcp/` | Visibility, checkpoint, gate prerequisite tests |
| `tests/unit/tools/macro/` | Profile macro tests if macros are introduced |
| `tests/e2e/tools/mesh/` | Blender-backed mesh refinement tests |
| `tests/e2e/vision/` | Primitive-only creature cannot complete before refinement gate |
| `_docs/_PROMPTS/REFERENCE_GUIDED_CREATURE_BUILD.md` | Document refinement window and completion blockers |
| `_docs/_MCP_SERVER/README.md` | Document gated mesh visibility and profile gate semantics |

## Implementation Notes

- Add an explicit guided creature step such as `refine_low_poly_forms` after
  required masses and seams are stable enough.
- Keep the visible tool window narrow and role-aware:
  - `mesh_select`
  - `mesh_select_targeted`
  - `mesh_extrude_region`
  - `mesh_loop_cut`
  - `mesh_bevel`
  - `mesh_symmetrize`
  - bounded modeling transforms
  - selected creature macros
- Do not unlock broad sculpt by default for this stage.
- Prefer reusable bounded macros where repeated primitive-to-form refinement is
  common, for example:
  - `macro_refine_creature_part_profile`
  - `macro_point_creature_ears`
  - `macro_flatten_limb_contact_patch`
  - `macro_add_creature_eye_pair`
- Keep macros optional if existing mesh/modeling tools can safely express the
  first slice.
- Add relation-aware preconditions:
  - do not refine final form while required seams still float
  - do not use mesh edits to hide unresolved attachment failures
  - do not call the model complete immediately after primitive creation
- Model refinement as a generic `refinement_stage` gate with creature-specific
  `shape_profile` child gates for body, ears, limbs, snout, and tail where
  reference evidence requires them.
- Consume `TASK-157` evidence refs rather than calling perception directly:
  `reference_understanding` may explain that the target is a faceted
  squirrel-like creature with wedge ears and a curled tail, while
  `silhouette_analysis` or future segmentation masks may support active
  `shape_profile` gates. The refinement stage still opens bounded mesh/modeling
  tools only after gate prerequisites pass.
- Keep broad sculpt out of the default low-poly refinement path. Sculpt remains
  a planner-driven, preconditioned handoff from `TASK-145`, not the baseline
  answer for faceted low-poly profile work.

## Pseudocode

```python
if current_step == "place_secondary_parts" and required_roles_complete:
    if required_seams_stable:
        advance_to("refine_low_poly_forms")

if current_step == "refine_low_poly_forms":
    allowed_families = ["modeling_mesh", "macro", "reference_context"]
    allowed_tools = [
        "mesh_select",
        "mesh_select_targeted",
        "mesh_extrude_region",
        "mesh_loop_cut",
        "mesh_bevel",
        "mesh_symmetrize",
        "macro_refine_creature_part_profile",
    ]
```

## Tests To Add/Update

| Layer | Tests |
|-------|-------|
| Unit guided state | `refine_low_poly_forms` appears only after required roles/seams are stable |
| Unit visibility | Mesh tools open for refinement gate and remain hidden before prerequisites |
| Unit search | "profile low-poly body/ears/limbs" returns bounded mesh/profile tools |
| Unit safety | Sculpt remains hidden unless planner emits explicit sculpt handoff |
| Unit checkpoint | Primitive-only creature reports refinement blockers |
| Unit evidence refs | Perception/reference-derived shape-profile evidence opens only bounded profile tools after prerequisites |
| E2E mesh | A selected part can be profiled through guided mesh tools without losing state |
| E2E vision | Primitive-only squirrel cannot pass final completion before refinement gate |
| E2E macro | Any new profile macro has Blender-backed geometry assertions |

## Docs To Update

- `_docs/_PROMPTS/REFERENCE_GUIDED_CREATURE_BUILD.md`
- `_docs/_MCP_SERVER/README.md`
- `_docs/AVAILABLE_TOOLS_SUMMARY.md`
- `_docs/_TESTS/README.md`

## Changelog Impact

- Add a `_docs/_CHANGELOG/*` entry when the refinement stage or first profile
  macro ships.

## Acceptance Criteria

- The guided creature recipe has a clear refinement stage after primitive
  placement and seam stabilization.
- Mesh tools are available when they are actually needed for low-poly form
  refinement, not only hidden behind generic discovery.
- Primitive-only blobs are no longer considered the final expected output for
  a reference-guided creature session.
- The first implementation keeps the surface bounded, role-aware, and
  compatible with existing guided state and visibility policy.
