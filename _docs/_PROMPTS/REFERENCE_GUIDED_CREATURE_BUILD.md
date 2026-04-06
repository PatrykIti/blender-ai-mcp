# Reference-Guided Creature Build

Stable MCP prompt asset name: `reference_guided_creature_build`

Use this on the `llm-guided` surface when you want staged manual building with
reference images and bounded vision feedback after each checkpoint, regardless
of whether the configured runtime is `mlx_local` or a supported external
vision path.

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
4. `router_set_goal("create a low-poly creature matching front and side reference images")`
5. if the router returns `continuation_mode="guided_manual_build"`, continue on
   the shaped manual build surface
   - if `guided_handoff.recipe_id == "low_poly_creature_blockout"`, stay on the
     modeling/mesh-first creature blockout recipe instead of widening into the
     full generic build surface
6. if the router returns `needs_input`, answer that first and wait until
   `guided_reference_readiness.compare_ready == true`
7. build in short stages:
   - head + ears
   - snout + face mass
   - body + tail
   - paws + final proportion cleanup
8. after each stage run:
   - `reference_iterate_stage_checkpoint(target_object="Creature", checkpoint_label="<stage>", preset_profile="compact")`
9. use the response in this order:
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
10. repeat the next stage or correction step

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
- do not assume MLX-only or provider-specific compare behavior; follow the
  runtime that is actually configured for this server
- do not guess hidden/internal tool names
- use `call_tool(...)` only for tools that are directly visible or were just
  discovered through `search_tools(...)`
- use the canonical `call_tool(name=..., arguments=...)` wrapper; legacy
  `tool=...` / `params=...` aliases are compatibility-only
- keep parts as separate objects
- focus on low-poly shape match, not materials or fur detail
- attach references one at a time with
  `reference_images(action="attach", source_path=..., ...)`; do not pass
  batch shapes such as `images=[...]`
- use `collection_manage(action="create", collection_name=...)`, not
  `name=...`
- use `modeling_create_primitive(...)` only with its public shape:
  `primitive_type`, `radius`/`size`, `location`, `rotation`, optional `name`
- if you need non-uniform scale, create the primitive first and then call
  `modeling_transform_object(scale=...)`
- if you need to place a new object into a collection, create it first and then
  call `collection_manage(action="move_object", collection_name=..., object_name=...)`
- after each stage use `reference_iterate_stage_checkpoint(...)`
- for stages with one clear primary mass you may use `target_object=...`
- for a full assembled silhouette use:
  - `target_objects=[...]`
  - or `collection_name="Squirrel"`
  - or no explicit scope if you want to compare the whole assembled
    scene/silhouette

Workflow:
1. `router_get_status()`
2. clean the scene but keep lights and cameras
3. attach both references through `reference_images(...)`
   - use one `source_path` per attach call, not `images=[...]`
4. set the goal:
   `create a low-poly creature matching front and side reference images`
5. if the router returns `guided_manual_build`, continue manually on the
   shaped build surface
   - if `guided_handoff.recipe_id == "low_poly_creature_blockout"`, use that
     smaller recipe as the default direct-tool surface
6. if the router returns `needs_input`, answer that first and wait until
   `guided_reference_readiness.compare_ready == true`
7. build in 4 stages:
   - stage 1: head + ears
   - stage 2: snout + face mass
   - stage 3: body + tail
   - stage 4: paws + final proportion cleanup
8. after each stage call:
   `reference_iterate_stage_checkpoint(target_object="Creature", checkpoint_label="<stage_name>", preset_profile="compact")`
9. on the next iteration prioritize:
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
10. if `guided_reference_readiness.compare_ready == false`, execute
    `guided_reference_readiness.next_action` instead of trying to recover the
    session with `goal_override`
11. if `loop_disposition == "inspect_validate"`, stop free-form modeling and
    switch to inspect/measure/assert before making another large change
12. if staged compare/iterate returns a vision error but still includes strong
    deterministic `truth_followup` / `correction_candidates`, use that as an
    inspect/measure/assert handoff instead of guessing another large free-form
    correction
13. if `part_segmentation.status == "disabled"`, stay on the silhouette-first
    path; the segmentation sidecar is optional and not part of the default
    guided baseline

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
- the optional part-segmentation sidecar is separate from
  `vision_contract_profile` and is disabled by default
- for the full multi-part creature, do not narrow the final iterations to only
  one torso/body object, because then the loop will evaluate only that local
  mass instead of the assembled silhouette
