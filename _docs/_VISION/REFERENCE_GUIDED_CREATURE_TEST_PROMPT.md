# Reference-Guided Creature Test Prompt

This file is a manual/operator test prompt for the hybrid creature correction
loop.

It intentionally lives outside `_docs/_PROMPTS/` so it does not become part of
the MCP-served prompt catalog. Use it as a local eval/playbook document when
you want a fuller test prompt than the production prompt assets.

## When To Use It

Use this prompt when you want to validate the current hybrid loop on a staged
low-poly creature build with:

- goal-scoped front + side references
- `reference_iterate_stage_checkpoint(...)`
- truth-driven follow-up payloads
- ranked `correction_candidates`
- optional viewport/camera review captures between iterations

## Updated Test Prompt

```text
Use the active `blender-ai-mcp-guided-docker-openrouter` profile and build a low-poly squirrel from two local references.

Reference files:
- FRONT_REFERENCE_PATH=/tmp/squirrel-front.png
- SIDE_REFERENCE_PATH=/tmp/squirrel-side.png

Rules:
- work on the active `llm-guided` shaped surface
- do not guess hidden/internal tool names
- use `call_tool(...)` only for tools that are directly visible or were just discovered through `search_tools(...)`
- keep parts as separate objects
- focus on low-poly shape match, not materials or fur detail
- after each stage use `reference_iterate_stage_checkpoint(...)`
- for stages with one clear primary mass you may use `target_object=...`
- for a full assembled silhouette use:
  - `target_objects=[...]`
  - or `collection_name="Squirrel"`
  - or nothing if you want to compare the whole assembled scene/silhouette
- if you need an operator review capture from the viewport or a specific camera, also use `scene_get_viewport(...)`:
  - `camera_name="USER_PERSPECTIVE"` for the live user viewport
  - or a named camera for a stable camera shot
  - keep framing and focus on `Squirrel` consistent across review captures

Workflow:
1. `router_get_status()`
2. clean the scene but keep lights and cameras
3. attach both references through `reference_images(...)`
4. set the goal:
   `create a low-poly squirrel matching front and side reference images`
5. if the router returns `guided_manual_build`, continue manually on the shaped build surface
6. build in 4 stages:
   - stage 1: head + ears
   - stage 2: snout + eyes + nose
   - stage 3: body + tail
   - stage 4: paws + final proportion cleanup
7. after each stage call:
   `reference_iterate_stage_checkpoint(target_object="Squirrel", checkpoint_label="<stage_name>", preset_profile="compact")`
8. optionally add a review capture after each stage:
   - `scene_get_viewport(camera_name="USER_PERSPECTIVE", focus_target="Squirrel", output_mode="IMAGE")`
   - or `scene_get_viewport(camera_name="<named_camera>", output_mode="IMAGE")`
9. on each next iteration prioritize:
   - `loop_disposition`
   - `correction_candidates`
   - `truth_followup`
   - `truth_followup.focus_pairs`
   - `truth_followup.macro_candidates`
   - `correction_focus`
   - then `shape_mismatches`
   - then `proportion_mismatches`
   - then `next_corrections`
10. if `loop_disposition == "inspect_validate"`, stop free-form modeling and switch to inspect/measure/assert before making another large change

At the end of each stage, return only:
- what was done
- `loop_disposition`
- `correction_candidates`
- `truth_followup`
- `correction_focus`
- what still does not match the references
- the next step
```

## Practical Notes

- `reference_iterate_stage_checkpoint(...)` remains the primary hybrid-loop
  signal. `scene_get_viewport(...)` is supplemental operator review, not the
  main loop oracle.
- For stable human review, named cameras are better than `USER_PERSPECTIVE`.
- For quick manual validation during iterative building, `USER_PERSPECTIVE`
  is often faster and closer to the live modeling workflow.
- Review outputs in this order:
  - `loop_disposition`
  - `correction_candidates`
  - `truth_followup`
  - `correction_focus`
- Treat `truth_followup.macro_candidates` as bounded next-step options, not as
  proof that auto-apply should happen.
