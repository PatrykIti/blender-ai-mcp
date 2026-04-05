# Reference-Guided Creature Build

Use this on the `llm-guided` surface when you want staged manual building with
reference images and bounded vision feedback after each checkpoint.

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
4. `router_set_goal("create a low-poly squirrel matching front and side reference images")`
5. if the router returns `continuation_mode="guided_manual_build"`, continue on
   the shaped manual build surface
6. if the router returns `needs_input`, answer that first and wait until
   `guided_reference_readiness.compare_ready == true`
7. build in short stages:
   - head + ears
   - face details
   - body + tail
   - paws + final cleanup
8. after each stage run:
   - `reference_iterate_stage_checkpoint(target_object="Squirrel", checkpoint_label="<stage>", preset_profile="compact")`
9. use the response in this order:
   - `loop_disposition`
   - `guided_reference_readiness`
   - `correction_candidates`
   - `truth_followup`
   - `correction_focus`
   - `shape_mismatches`
   - `proportion_mismatches`
   - `next_corrections`
10. repeat the next stage or correction step

## Prompt Template

```text
Use the active Blender MCP profile with MLX vision and build a low-poly
squirrel from two local reference images.

Reference files:
- FRONT_REFERENCE_PATH=<ABSOLUTE_PATH>
- SIDE_REFERENCE_PATH=<ABSOLUTE_PATH>

Rules:
- work on the active `llm-guided` shaped surface
- do not guess hidden/internal tool names
- use `call_tool(...)` only for tools that are directly visible or were just
  discovered through `search_tools(...)`
- keep parts as separate objects
- focus on low-poly shape match, not materials or fur detail
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
4. set the goal:
   `create a low-poly squirrel matching front and side reference images`
5. if the router returns `guided_manual_build`, continue manually on the
   shaped build surface
6. if the router returns `needs_input`, answer that first and wait until
   `guided_reference_readiness.compare_ready == true`
7. build in 4 stages:
   - stage 1: head + ears
   - stage 2: snout + eyes + nose
   - stage 3: body + tail
   - stage 4: paws + final proportion cleanup
8. after each stage call:
   `reference_iterate_stage_checkpoint(target_object="Squirrel", checkpoint_label="<stage_name>", preset_profile="compact")`
9. on the next iteration prioritize:
   - `loop_disposition`
   - `guided_reference_readiness`
   - `correction_candidates`
   - `truth_followup.focus_pairs`
   - `truth_followup.macro_candidates`
   - `correction_focus`
   - then `shape_mismatches`
   - then `proportion_mismatches`
   - then `next_corrections`
10. if `guided_reference_readiness.compare_ready == false`, execute
    `guided_reference_readiness.next_action` instead of trying to recover the
    session with `goal_override`
11. if `loop_disposition == "inspect_validate"`, stop free-form modeling and
    switch to inspect/measure/assert before making another large change

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
- `correction_focus` should be treated as the first action list, but only
  after checking whether `correction_candidates` or `truth_followup` carry a
  stronger truth-driven signal
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
- for the full multi-part squirrel, do not narrow the final iterations to only
  `Squirrel_Body`, because then the loop will evaluate only the torso
