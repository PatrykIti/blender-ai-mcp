# Reference-Guided Creature Build

Stable MCP prompt asset name: `reference_guided_creature_build`

Use this on the `llm-guided` surface when you want staged manual building with
reference images and bounded vision feedback after each checkpoint, regardless
of whether the configured runtime is `mlx_local` or a supported external
vision path.

When the client tends to drift, prepend
[`GUIDED_SESSION_START.md`](./GUIDED_SESSION_START.md) first and treat that
asset as the generic search-first operating baseline.

## Best Fit

- low-poly animal / creature blockouts
- staged character-like models with separate parts
- front + side reference-driven work where exact realism is not required

## Recommended Flow

1. `router_get_status()`
2. `scene_clean_scene(...)` if needed
3. `reference_images(action="attach", ...)` for:
   - front reference
   - side reference
4. inspect/read the attached references as the primary grounding input for:
   - initial body/head/tail proportions
   - broad silhouette
   - rough part placement
5. `router_set_goal("create a low-poly creature matching front and side reference images")`
6. if the router returns `continuation_mode="guided_manual_build"`, continue on
   the shaped manual build surface
   - if `guided_handoff.recipe_id == "low_poly_creature_blockout"`, stay on the
     modeling/mesh-first creature blockout recipe instead of widening into the
     full generic build surface
7. if the router returns `needs_input`, answer that first and wait until
   `guided_reference_readiness.compare_ready == true`
   - if you only discover stale scene state after this point, `scene_clean_scene(...)`
     remains an allowed build-phase recovery hatch even though cleanup-before-goal
     is still the preferred path
   - once the goal is active, inspect `guided_flow_state` and treat
     `establish_spatial_context` plus its `required_checks` as a real gate
     before broad free-form modeling
8. build in short stages:
   - body + head primary masses
   - tail mass
   - snout + ears
   - forelegs + hindlegs + final proportion cleanup
9. after each stage run:
   - `reference_iterate_stage_checkpoint(target_object="Creature", checkpoint_label="<stage>", preset_profile="compact")`
10. use the response in this order:
   - `loop_disposition`
   - `guided_reference_readiness`
   - `correction_candidates`
   - `truth_followup`
   - `action_hints`
   - `correction_focus`
   - `silhouette_analysis.metrics`
   - `vision_assistant.result.shape_mismatches`
   - `vision_assistant.result.proportion_mismatches`
   - `vision_assistant.result.next_corrections`
11. repeat the next stage or correction step

## Prompt Template

```text
Use the active Blender MCP profile with the repo's configured bounded vision
runtime and build a low-poly creature from two local reference images.

Reference files:
- FRONT_REFERENCE_PATH=<ABSOLUTE_PATH>
- SIDE_REFERENCE_PATH=<ABSOLUTE_PATH>

Rules:
- work on the active `llm-guided` shaped surface
- prefer the exposed `reference_guided_creature_build` prompt path when
  `recommended_prompts` or prompt discovery surfaces suggest it for the active
  creature goal
- if the server exposes `guided_flow_state.required_prompts` or
  `guided_flow_state.preferred_prompts`, treat those as the current required prompt bundle and preferred prompt bundle for the creature flow
- do not assume MLX-only or provider-specific compare behavior; follow the
  runtime that is actually configured for this server
- do not guess hidden/internal tool names
- if a tool is not already directly visible, use `search_tools(...)` before
  `call_tool(...)`
- use `call_tool(...)` only for tools that are directly visible or were just
  discovered through `search_tools(...)`
- use the canonical `call_tool(name=..., arguments=...)` wrapper; legacy
  `tool=...` / `params=...` aliases are compatibility-only
- the same guided contract hardening now applies on directly visible tools too:
  batch-like `reference_images(...)` attach drift, legacy
  `collection_manage(..., name=...)`, legacy cleanup split flags, and
  unsupported primitive shortcuts return actionable guidance instead of raw
  schema noise
- keep parts as separate objects
- focus on low-poly shape match, not materials or fur detail
- attached reference images are the primary grounding input for how the first
  masses should look and sit; do not start from generic animal priors when the
  active guided session already has references
- attach references one at a time with
  `reference_images(action="attach", source_path=..., ...)`; do not pass
  batch shapes such as `images=[...]`
- use full semantic object names:
  - `Body`
  - `Head`
  - `Tail`
  - `ForeLeg_L`
  - `ForeLeg_R`
  - `HindLeg_L`
  - `HindLeg_R`
- avoid opaque abbreviations like `ForeL`, `ForeR`, `HindL`, `HindR` because
  guided seam/role heuristics are more reliable on full readable names
- on `llm-guided`, weak role-sensitive names can now produce explicit server
  warnings and clearly opaque placeholder names such as `Sphere` / `Object`
  can be blocked until you use a semantic part name
- use `collection_manage(action="create", collection_name=...)`, not
  `name=...`
- use `modeling_create_primitive(...)` only with its public shape:
  `primitive_type`, `radius`/`size`, `location`, `rotation`, optional `name`
- if you need non-uniform scale, create the primitive first and then call
  `modeling_transform_object(scale=...)`
- when the server needs semantic part roles for build enforcement, use the
  canonical `guided_register_part(object_name=..., role=...)` path
- optional `guided_role=...` on `modeling_create_primitive(...)` or
  `modeling_transform_object(...)` is a convenience path only; do not rely on
  it as a substitute for reading the active guided flow state
- if you need to place a new object into a collection, create it first and then
  call `collection_manage(action="move_object", collection_name=..., object_name=...)`
- after each stage use `reference_iterate_stage_checkpoint(...)`
- do not call `scene_scope_graph(...)` / `scene_relation_graph(...)` with no
  scope and assume that means “inspect the whole scene”
- `scene_view_diagnostics(...)` also requires explicit scope
- for stages with one clear primary mass you may use `target_object=...`
- for a full assembled silhouette use:
  - `target_objects=[...]`
  - or `collection_name="Squirrel"`
- on full assembled-creature checkpoints, treat `truth_followup.focus_pairs`
  as the required creature seam set for the current scope; one improved local
  pair does not mean the whole creature stage is done
- read seam outcomes using the explicit attachment verdict model:
  - `seated_contact`
  - `floating_gap`
  - `intersecting`
  - `misaligned_attachment`
- interpret seam verdicts explicitly:
  - `intersecting` can be acceptable for embedded seams such as ear/head or
    snout/head during blockout
  - `floating_gap` remains actionable for segment seams such as head/body,
    tail/body, or limb/body

Workflow:
1. `router_get_status()`
2. clean the scene but keep lights and cameras
3. attach both references through `reference_images(...)`
   - use one `source_path` per attach call, not `images=[...]`
4. inspect/read the attached reference set before deciding the first body/head
   masses and rough silhouette
5. set the goal:
   `create a low-poly creature matching front and side reference images`
6. if the router returns `guided_manual_build`, continue manually on the
   shaped build surface
   - if `guided_handoff.recipe_id == "low_poly_creature_blockout"`, use that
     smaller recipe as the default direct-tool surface
7. if the router returns `needs_input`, answer that first and wait until
   `guided_reference_readiness.compare_ready == true`
8. build in 4 stages:
   - stage 1: body + head primary masses
   - stage 2: tail mass
   - stage 3: snout + ears
   - stage 4: forelegs + hindlegs + final proportion cleanup
9. during the primary-mass stages, do not jump early to ears or legs
   - if the server reports `guided_flow_state.allowed_roles=["body_core","head_mass","tail_mass"]`, stay inside that role set
   - read `allowed_roles` and `missing_roles` literally from the active guided flow state before creating the next creature part
   - register semantic part roles with `guided_register_part(...)` or use the convenience hint `guided_role=...` on the build call
10. after each stage call:
   `reference_iterate_stage_checkpoint(target_object="Creature", checkpoint_label="<stage_name>", preset_profile="compact")`
11. on the next iteration prioritize:
   - `loop_disposition`
   - `guided_reference_readiness`
   - `correction_candidates`
   - `truth_followup.focus_pairs`
   - `truth_followup.macro_candidates`
   - `action_hints`
   - `correction_focus`
   - then `silhouette_analysis.metrics`
   - then `vision_assistant.result.shape_mismatches`
   - then `vision_assistant.result.proportion_mismatches`
   - then `vision_assistant.result.next_corrections`
12. if `guided_reference_readiness.compare_ready == false`, execute
    `guided_reference_readiness.next_action` instead of trying to recover the
    session with `goal_override`
13. if `loop_disposition == "inspect_validate"`, stop free-form modeling and
    switch to inspect/measure/assert before making another large change
    - bounded attachment repair macros and spatial re-check tools may still be
      available there; use that bounded surface instead of broad free-form
      modeling
14. if staged compare/iterate returns a vision error but still includes strong
    deterministic `truth_followup` / `correction_candidates`, use that as an
    inspect/measure/assert handoff instead of guessing another large free-form
    correction
15. if `part_segmentation.status == "disabled"`, stay on the silhouette-first
    path; the segmentation sidecar is optional and not part of the default
    guided baseline
16. if a build call is blocked because the family or role is wrong for the
    current step, do not try another guessed build tool name
    - inspect `guided_flow_state.allowed_families`
    - inspect `guided_flow_state.allowed_roles`
    - inspect `guided_flow_state.missing_roles`
17. when the current issue is an embedded organic seam such as snout/head or
    nose/snout, prefer `macro_attach_part_to_surface`
18. when the current issue is head/body, tail/body, or limb/body seating,
    prefer `macro_align_part_with_contact`
19. do not treat generic overlap cleanup as success for a creature seam unless
    the final attachment verdict has also moved to `seated_contact`
20. for segment seams such as head/body, tail/body, and limb/body, do not
    rationalize `floating_gap` as “expected blockout state”; it still needs
    correction

At the end of each stage, return only:
- what was done
- `loop_disposition`
- `correction_focus`
- what still does not match the references
- the next step
```

## Practical Notes

- `compact` is a good default for frequent checkpoints
- `rich` makes sense only when one stage is already fairly stable and you want
  a wider multi-view comparison
- this flow is runtime-agnostic:
  - `mlx_local` is a valid local path
  - supported external compare runtimes are also valid when they honor the
    bounded staged-checkpoint contract
- on external runtimes, `vision_contract_profile` explains whether the active
  compare path is using the narrow Google-family compare contract or the full
  generic contract; use that field for diagnosis instead of inferring behavior
  from provider name alone
- `correction_focus` should be treated as the first action list, but only
  after checking whether `correction_candidates`, `truth_followup`, or typed
  `action_hints` carry a stronger bounded signal
- `silhouette_analysis` is deterministic perception evidence:
  - use it for contour/ratio drift, not for scene truth
  - `action_hints` are typed tool suggestions derived from those metrics
- `loop_disposition="inspect_validate"` means the system is detecting repeated
  focus or a high-priority truth signal, so it is better to pause free-form
  correction and switch briefly to truth-layer verification
- `correction_candidates` is the primary ranked handoff for the hybrid loop:
  - `vision_only` means the issue is visible mainly on the vision side
  - `truth_only` means the issue is deterministically confirmed by truth tools
  - `hybrid` means vision and truth signals converge on the same issue
- `truth_followup.focus_pairs` and `truth_followup.macro_candidates` still
  carry the detailed context when you need to understand which object pair and
  which bounded macro should be the next move
- for assembled creatures, the seam set should cover at least face/head,
  torso/body, and limb attachments when those masses are present in the
  current target scope
- the optional part-segmentation sidecar is separate from
  `vision_contract_profile` and is disabled by default
- for the full multi-part creature, do not narrow the final iterations to only
  one torso/body object, because then the loop will evaluate only that local
  mass instead of the assembled silhouette
