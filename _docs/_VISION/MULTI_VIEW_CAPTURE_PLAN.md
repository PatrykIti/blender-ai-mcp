# Multi-View Capture Plan

Design notes for the deterministic multi-view capture path used by `TASK-121`.

## Goal

Move the vision layer away from "one screenshot guessing" toward a stable,
bounded multi-view comparison bundle that can be attached to macro/workflow
reports.

The long-term target is not "create permanent camera objects everywhere in the
scene". The better product shape is:

- deterministic capture pipeline
- temporary/reversible view manipulation
- repeatable view presets
- no scene pollution from helper cameras unless a later implementation truly
  needs them

## Current Runtime State

Already implemented:

- deterministic capture bundle contract
- runtime capture helpers
- current preset scaffold:
  - `context_wide`
  - `target_focus`
  - `target_oblique`
- goal-scoped reference images
- request-bound macro MCP attachment of `capture_bundle` and `vision_assistant`

## Existing Atomics We Already Have

The current repo already exposes enough scene-side building blocks to compose a
good first multi-view capture path:

- `scene_get_viewport`
- `scene_camera_focus`
- `scene_camera_orbit`
- `scene_isolate_object`
- `scene_show_all_objects`
- `scene_get_bounding_box`
- `scene_measure_dimensions`
- `reference_images`

This means the near-term path should prefer composition over inventing a large
new Blender-side subsystem too early.

## What Still Must Be Created

To reach the real long-term target, the repo still needs one deliberate capture
orchestration layer on top of the existing atomics.

Recommended shape:

- first build an internal bounded capture orchestrator for:
  - isolate/focus/orbit/capture/restore
  - deterministic preset sequencing
  - before/after bundle assembly
- only later decide whether that becomes a public MCP tool

Important clarification:

- a full `before/after capture bundle` is naturally tied to a change boundary
  (for example a macro or workflow step), not to one static instant
- because of that, the most natural first implementation is:
  - internal helper / bounded macro-path orchestration
  - not a broad free-floating public tool that pretends to own both "before"
    and "after" without controlling the change in between

## Missing Low-Level Capabilities

What we can already do well enough with current atomics:

- focus a target
- orbit deterministically
- capture viewport images
- isolate/show objects
- collect truth summaries

What is still weak for the true long-term target:

- exact save/restore of viewport/view state
- exact save/restore of prior visibility state without lossy fallback

Current implementation note:

- the repo now has a first internal capture-state scaffold that can snapshot and
  restore visibility from scene snapshot data
- stage capture now also replays a best-effort saved view state after bounded
  capture execution when the internal helper is available
- view-state restoration is still intentionally marked as the next missing
  helper, not solved prematurely with a weak public API

So the practical implementation path is:

1. keep using current scene atomics for the first bounded multi-view path
2. add internal save/restore helpers where state fidelity is insufficient
3. only later decide whether those helpers deserve public MCP exposure

## Recommended Product Shape

### Near-Term

Use the existing viewport/camera atomics to generate deterministic bundles.

That means:

- focus the viewport on the target object when needed
- orbit deterministically for selected angled views
- capture images with fixed resolution/shading
- store them in a capture bundle
- attach the bundle to macro/workflow reports

### Long-Term

The target visual evidence bundle should be closer to an 8-image set:

1. `context_wide`
2. `target_focus`
3. `target_oblique_left`
4. `target_oblique_right`
5. `target_front`
6. `target_side`
7. `target_top`
8. `target_detail` or another object-critical focused angle

Reference images should be selected and attached alongside this bundle using
goal/object/view-aware filtering.

## Camera Strategy

Preferred default:

- do **not** leave persistent helper camera objects in the user scene
- use reversible viewport/camera positioning first
- only introduce temporary generated cameras if later evaluation proves the
  viewport path is insufficient for determinism/quality

Why:

- avoids scene pollution
- reduces cleanup complexity
- keeps the feature aligned with bounded macro/workflow execution
- makes before/after comparisons easier to keep stable

## Truth Pairing

Every multi-view bundle should carry structured truth context next to images:

- target object
- goal text / goal id
- preset names
- bounding box / dimensions summary
- later: selected gap/contact/alignment summaries where relevant

Vision should interpret the images in that frame, not replace it.

## Suggested Implementation Order

1. Keep extending deterministic preset coverage on top of the existing
   viewport/camera atomics.
2. Improve target/view-aware reference selection.
3. Add internal save/restore helpers for view/visibility state where the
   current atomics are insufficient.
4. Prove stable before/after bundle generation in unit tests.
5. Only then consider a richer dedicated scene capture surface or temporary
   camera-backed implementation if needed.

## Non-Goals

- persistent multi-camera rig creation as the default capture path
- ad hoc screenshots without preset discipline
- letting vision reason without capture bundles or truth summaries
