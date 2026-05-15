# Reference-Guided Architecture Build

Stable MCP prompt asset name: `reference_guided_architecture_build`

Use this on the `llm-guided` surface when the active goal is to reconstruct a
small building, facade module, tower, gate, hut, well, or reusable architectural
asset from plan, elevation, section, or facade/photo references.

When the client tends to drift, prepend
[`GUIDED_SESSION_START.md`](./GUIDED_SESSION_START.md) first and treat that
asset as the generic search-first operating baseline.

## Best Fit

- facade-only reconstruction from front or side elevations
- small standalone building shells with roof and openings
- modular architectural assets with repeated bays, posts, columns, beams, or
  opening rhythm
- bounded hard-surface reconstruction where dimensions, contact, and relation
  semantics matter more than materials or photoreal rendering

## Recommended Flow

1. `router_get_status()`
2. `scene_clean_scene(...)` if stale geometry would confuse the target scope
3. `reference_images(action="attach", ...)` for available plan/elevation/photo
   references, one reference per attach call
4. `router_set_goal("rebuild the facade/building from the references", gate_proposal={...})`
5. if the router returns `continuation_mode="guided_manual_build"` and
   `guided_handoff.recipe_id == "reference_guided_architecture_build"`, stay on
   that bounded architecture surface instead of importing `simple_house_workflow`
6. inspect `guided_flow_state` before broad edits:
   - `domain_profile` should be `building`
   - `required_prompts` should include `reference_guided_architecture_build`
   - `current_step` and `required_checks` decide which tools are currently safe
7. build in short stages:
   - footprint and base massing
   - main volume and wall shell
   - facade openings, opening grid, and support/post rhythm
   - roof mass, roofline, and roof-wall seating
   - trim/detail only after structural checks are stable
8. after each stage run:
   - `scene_scope_graph(...)`
   - `scene_relation_graph(...)`
   - `scene_view_diagnostics(...)`
   - `reference_iterate_stage_checkpoint(..., preset_profile="compact")`
9. use the response in this order:
   - `loop_disposition`
   - `guided_reference_readiness`
   - `active_gate_plan`
   - `completion_blockers`
   - `recommended_bounded_tools`
   - `compare_diagnostics`
   - `truth_followup`
   - `correction_candidates`
   - `action_hints`
   - `silhouette_analysis`

## Gate Proposal Shape

Use the generic quality-gate contract. Do not invent architecture-only gate
types. Prefer:

- `required_part` for `footprint_mass`, `main_volume`, `wall_shell`,
  `roof_mass`, `facade_opening`, `opening_grid`, and `support_element`
- `attachment_seam` for `roof_wall` and `opening_wall`
- `opening_or_cut` for window/door cuts into the wall shell
- `support_contact` for posts, columns, beams, or buttresses that carry mass
- `shape_profile` or `proportion_ratio` for roofline, floor bands, bay rhythm,
  footprint ratio, and elevation/section profile checks
- `final_completion` only as the aggregate completion gate

Reference understanding, segmentation, silhouette, and classification outputs
are supporting evidence only. Gate pass/fail authority remains deterministic
scene truth, spatial relation, mesh metric, or assertion evidence.

## Interface Semantics

Treat architectural contacts by intent:

- an opening is cut into a wall shell
- a roof is seated on a wall/main volume
- a beam or supported mass is carried by posts, columns, or supports
- repeated windows/doors align to a facade grid or bay rhythm
- intentional modular contact is not the same thing as accidental collision
- floating gaps and bad penetrations still need bounded repair

Use `macro_cutout_recess` for bounded openings, `macro_relative_layout` for
module spacing, `macro_place_supported_pair` for supported pairs,
`macro_attach_part_to_surface` / `macro_align_part_with_contact` for seating and
contact repair, and inspect/assert tools before claiming completion.

## Prompt Template

```text
Use the active Blender MCP `llm-guided` profile to reconstruct a bounded
architectural target from references.

Reference files:
- PLAN_OR_TOP_REFERENCE_PATH=<ABSOLUTE_PATH_OR_EMPTY>
- FRONT_ELEVATION_REFERENCE_PATH=<ABSOLUTE_PATH_OR_EMPTY>
- SIDE_ELEVATION_REFERENCE_PATH=<ABSOLUTE_PATH_OR_EMPTY>
- PHOTO_OR_DETAIL_REFERENCE_PATH=<ABSOLUTE_PATH_OR_EMPTY>

Rules:
- work on the active `llm-guided` shaped surface
- treat `router_get_status().surface_profile` / `contract_version` plus the
  live `guided_flow_state` and `reference_orchestrator_feedback` as the active
  session authority line; if stale external memory or old tool schemas
  disagree, trust the live runtime contract
- prefer `reference_guided_architecture_build` when `recommended_prompts` or
  `guided_flow_state.required_prompts` names it for the active building goal
- do not use raw Blender Python or hidden/internal tools
- if a tool is not directly visible, use `search_tools(...)` before
  `call_tool(name=..., arguments=...)`
- never treat `call_tool(...)` as a bypass for hidden or phase-locked tools
- attach references with one `reference_images(action="attach", source_path=...)`
  call per file
- build footprint and wall shell before openings/supports
- place or cut openings against the wall shell, not as floating facade props
- seat the roof on the wall/main volume after the shell is stable
- keep columns/posts/supports explicit when the reference shows them
- after each stage, run the staged reference checkpoint and deterministic
  spatial checks before deciding the next correction
- when compare packets mention plan, elevation, facade rhythm, opening grid, or
  roofline evidence, treat those as advisory packet-local evidence and join them
  back to deterministic gates before marking the stage complete
```
