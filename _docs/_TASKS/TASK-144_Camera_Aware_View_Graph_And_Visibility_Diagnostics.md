# TASK-144: Camera-Aware View Graph and Visibility Diagnostics

**Status:** ⏳ To Do
**Priority:** 🔴 High
**Category:** Spatial Intelligence / View-Space Reasoning
**Estimated Effort:** Large
**Dependencies:** TASK-121-03-03, TASK-121-03-04, TASK-121-03-05, TASK-143

## Objective

Expose machine-readable view-space facts so an LLM can reason about what is
actually visible from the current camera or viewport instead of treating
rendered images as the only source of view information.

The target outcome is not "better screenshots". The target outcome is:

- better framing awareness
- explicit occlusion/visibility diagnostics
- explicit screen-space projection data
- stronger spatial context before later mesh or sculpt refinement

## Business Problem

Today the guided loop has:

- strong scene truth
- strong capture tools
- strong compare/iterate envelopes

But it still lacks one crucial layer:

- what is actually visible from this view?
- is the target fully on screen?
- is the relevant part occluded?
- is the current capture centered on the region we want to edit?

Without that layer:

- the model can ask vision to judge the wrong framing
- it can overcorrect based on occluded or partial views
- it cannot tell whether a local sculpt or mesh correction is even visible from
  the current capture family
- camera/viewport reasoning still depends on prose interpretation instead of
  typed facts

This umbrella also exists to make one boundary explicit:

- truth-space should answer whether two parts actually touch, overlap, detach,
  or align in 3D
- view-space should answer whether the current camera/viewport makes that fact
  visible, ambiguous, occluded, or off-frame

Example:

- truth-space may correctly report that an ear is still separated from the head
  even when bbox contact or a front view is misleading
- view-space should then help the model understand whether the active view is a
  bad place to judge that gap and whether it should reframe, orbit, isolate, or
  switch view family before asking vision for another interpretation

## Current Runtime Baseline

The repo already has the prerequisites this umbrella should build on:

- `scene_get_viewport(...)`
- `scene_camera_focus(...)`
- `scene_camera_orbit(...)`
- `scene_isolate_object(...)`
- user-view and named-camera capture semantics
- deterministic stage-capture presets

This matters because the follow-on should add view-space state on top of the
existing capture/control model, not reinvent the whole render path.

It should also preserve the core `llm-guided` constraint:

- the guided surface must stay small
- default compare/iterate payloads must stay bounded
- richer view-space diagnostics should be available on demand when the current
  task and goal actually need them

Actual runtime/code seams already in place:

- `server/domain/tools/scene.py`,
  `server/application/tool_handlers/scene_handler.py`, and
  `blender_addon/application/handlers/scene.py` already carry the
  named-camera vs `USER_PERSPECTIVE` split for `scene_get_viewport(...)`
- `blender_addon/application/handlers/scene.py` already exposes
  `get_view_state(...)`, `restore_view_state(...)`, and
  `set_standard_view(...)`, which the capture path reuses for bounded
  viewport mutations
- `server/adapters/mcp/vision/capture_runtime.py` already composes
  `scene_isolate_object(...)`, `scene_camera_focus(...)`,
  `scene_camera_orbit(...)`, `snapshot_state(...)`, and view-state restore for
  deterministic stage captures
- `server/adapters/mcp/areas/reference.py` already keeps
  `reference_compare_current_view(...)` as a thin capture-then-compare wrapper,
  while `reference_compare_stage_checkpoint(...)` /
  `reference_iterate_stage_checkpoint(...)` already carry dense truth/vision
  payloads that should not become the default home for a full view graph
- `server/adapters/mcp/transforms/visibility_policy.py` and
  `server/adapters/mcp/guided_mode.py` already own `llm-guided` surface
  shaping, so goal-aware disclosure belongs there rather than in the router or
  in prompt-only heuristics

## Business Outcome

If this umbrella is done correctly, the repo gains:

- one explicit machine-readable view graph / visibility report layer
- more reliable reasoning about off-screen, partially visible, or occluded
  targets
- better capture-targeting before compare and before local refinement
- a stronger substrate for later sculpt-region handoff and local-form work

## Implementation Direction

This umbrella should be implemented primarily as an extension of the current
camera / viewport / isolation stack, not as a heavy geometry-library project.

The intended posture is:

- start from the repo's current view-control and capture foundations:
  - `scene_get_viewport(...)`
  - `scene_camera_focus(...)`
  - `scene_camera_orbit(...)`
  - `scene_isolate_object(...)`
  - current named-camera and `USER_PERSPECTIVE` semantics
- derive view-space facts from Blender-side camera/view state and current
  capture/runtime semantics first
- keep heavier external geometry libraries out of the first implementation
  unless one specific view-space capability truly requires them

For the first wave, the implementation should therefore be framed as:

- **v1 baseline**:
  - current camera/viewport/isolation stack
  - current scene and capture contracts
- **possible later extensions if they become genuinely necessary**:
  - richer server-side projection helpers
  - heavier geometry/raycast tooling for specialized view queries

This umbrella should not assume that `Open3D`, `trimesh`, or other heavy
geometry stacks are required to ship the first useful visibility/projection
layer.

## Dependency Policy

- if a new library gives the first version of a concrete visibility/projection
  capability a clear acceleration, it may be adopted
- otherwise, prefer building the first version from the repo's existing
  camera/viewport/control stack
- if new low-level view tools are needed, they should remain bounded and should
  not automatically become part of the default bootstrap-visible `llm-guided`
  set
- `LLM_GUIDE_V2.md` is the supporting design document for these choices; this
  umbrella remains the canonical delivery direction

## Product Design Requirements

### Lightweight Guided Exposure

- keep the default `llm-guided` visible surface small
- do not expose a broad new family of view-space atomics on bootstrap by
  default
- prefer one small number of read-only guided-facing entry tools or modules
- allow richer view-space detail only on demand
- do not enlarge `reference_compare_stage_checkpoint(...)` or
  `reference_iterate_stage_checkpoint(...)` with a full view graph by default;
  those contracts are already dense and should stay focused on
  compare/iterate results

### Goal-Aware View Disclosure

- view-space diagnostics should adapt to the active guided goal and phase
- example:
  - creature work may care about local part visibility, occluded attachments,
    and whether a target region is usable for later sculpt refinement
  - architecture or landmark work may care more about full-structure framing,
    vertical coverage, and silhouette occupancy in the frame
- goal-aware shaping should remain deterministic and metadata-driven where
  possible

### Delivery Model

- view-space diagnostics should be retrievable as explicit read-only products
  instead of being hidden inside larger compare contracts
- the guided loop may call or reference them when needed, but the
  view-graph/visibility module should remain conceptually separate from the
  checkpoint compare/iterate payloads
- if a lightweight summary is later added to loop responses, it should be a
  compact derivative rather than the full view graph

### Visibility Report

- expose whether requested objects are:
  - visible
  - partially visible
  - fully occluded
  - outside the current frame
- support both named-camera and `USER_PERSPECTIVE` paths

### Projection Data

- expose compact projected-screen data for selected objects or bounding boxes
- support center and coarse 2D extent at minimum
- keep the payload read-only and machine-readable

### Guided Loop Adoption

- allow the guided/reference loop to request or consume view-space diagnostics
  when current captures are insufficiently informative
- do not make view-space diagnostics a mandatory cost on every guided step;
  keep them bounded and selective
- use them to improve camera/framing decisions before another vision-assisted
  correction step, not to replace truth-space contact/attachment semantics

## Scope

This umbrella covers:

- camera-aware visibility diagnostics
- projected screen-space data for selected objects or scopes
- one lightweight guided-facing delivery model for those diagnostics
- goal-aware and phase-aware disclosure for those diagnostics on `llm-guided`
- view-target coverage diagnostics for guided capture families
- docs and regression coverage for the new view-space layer

This umbrella does **not** cover:

- semantic scene truth
- attachment/support/contact relation logic
- new render engines or photorealistic image generation
- segmentation as the primary view-state mechanism
- unrestricted general-purpose computer vision tooling
- exposing a broad new default tool family on `llm-guided` bootstrap
- turning `reference_compare_*` / `reference_iterate_*` into the default home
  for a full view-graph payload

## Acceptance Criteria

- the repo has one explicit machine-readable visibility/reporting layer for
  camera/viewport state
- the repo has one explicit machine-readable projection/view-space layer for
  selected objects or scopes
- the delivery model keeps `llm-guided` small:
  - no large new bootstrap-visible view-graph family
  - no default full view-graph embedding into the current stage-checkpoint
    payloads
- guided capture workflows can tell when the relevant target is off-screen,
  under-framed, or occluded
- the new view-space layer works with current named-camera and
  `USER_PERSPECTIVE` semantics instead of bypassing them
- the new layer remains clearly view-space, not a replacement for truth-space
  contact/attachment semantics
- graph access and summary detail can adapt to the active guided goal / phase
  instead of staying one fixed heavy payload for every domain
- focused regression coverage protects the new view-space contracts

## Repository Touchpoints

- `server/domain/tools/scene.py`
- `server/application/tool_handlers/scene_handler.py`
- `server/adapters/mcp/areas/scene.py`
- `server/adapters/mcp/contracts/scene.py`
- `server/adapters/mcp/vision/capture_runtime.py`
- `server/adapters/mcp/areas/reference.py`
- `server/adapters/mcp/contracts/reference.py`
- `server/adapters/mcp/transforms/visibility_policy.py`
- `server/adapters/mcp/guided_mode.py`
- `server/router/infrastructure/tools_metadata/scene/`
- `server/router/infrastructure/tools_metadata/reference/`
- `blender_addon/application/handlers/scene.py`
- `blender_addon/__init__.py`
- `blender_addon/infrastructure/rpc_server.py`
- `tests/unit/tools/scene/test_scene_contracts.py`
- `tests/unit/tools/scene/test_scene_mcp_tools_batch.py`
- `tests/unit/tools/scene/test_view_state.py`
- `tests/unit/tools/scene/test_viewport_control.py`
- `tests/unit/tools/scene/test_mcp_viewport_output.py`
- `tests/unit/tools/scene/test_camera_focus.py`
- `tests/unit/tools/scene/test_camera_orbit.py`
- `tests/unit/tools/scene/test_isolate_object.py`
- `tests/unit/adapters/mcp/test_reference_images.py`
- `tests/unit/adapters/mcp/test_guided_mode.py`
- `tests/unit/adapters/mcp/test_guided_surface_benchmarks.py`
- `tests/unit/adapters/mcp/test_provider_inventory.py`
- `tests/unit/adapters/mcp/test_tool_inventory.py`
- `tests/unit/adapters/mcp/test_public_surface_docs.py`
- `tests/e2e/tools/scene/test_scene_get_viewport.py`
- `tests/e2e/tools/scene/test_scene_get_viewport_camera.py`
- `tests/e2e/tools/scene/test_camera_focus.py`
- `tests/e2e/tools/scene/test_camera_orbit.py`
- `tests/e2e/tools/scene/test_isolate_object.py`
- `tests/e2e/vision/`
- `_docs/LLM_GUIDE_V2.md`
- `_docs/AVAILABLE_TOOLS_SUMMARY.md`
- `_docs/_MCP_SERVER/README.md`
- `_docs/_PROMPTS/README.md`
- `_docs/_VISION/README.md`
- `_docs/_TESTS/README.md`

## Docs To Update

- `_docs/LLM_GUIDE_V2.md`
- `_docs/AVAILABLE_TOOLS_SUMMARY.md`
- `_docs/_MCP_SERVER/README.md`
- `_docs/_PROMPTS/README.md`
- `_docs/_VISION/README.md`
- `_docs/_TESTS/README.md`
- `_docs/_TASKS/README.md` when the execution branch is allowed to sync the
  board state

## Tests To Add/Update

- `tests/unit/tools/scene/test_mcp_viewport_output.py`
- `tests/unit/tools/scene/test_scene_contracts.py`
- `tests/unit/tools/scene/test_scene_mcp_tools_batch.py`
- `tests/unit/tools/scene/test_view_state.py`
- `tests/unit/tools/scene/test_viewport_control.py`
- `tests/unit/tools/scene/test_camera_focus.py`
- `tests/unit/tools/scene/test_camera_orbit.py`
- `tests/unit/tools/scene/test_isolate_object.py`
- `tests/unit/adapters/mcp/test_reference_images.py`
- `tests/unit/adapters/mcp/test_visibility_policy.py`
- `tests/unit/adapters/mcp/test_guided_mode.py`
- `tests/unit/adapters/mcp/test_guided_surface_benchmarks.py`
- `tests/unit/adapters/mcp/test_provider_inventory.py`
- `tests/unit/adapters/mcp/test_tool_inventory.py`
- `tests/unit/adapters/mcp/test_public_surface_docs.py`
- `tests/e2e/tools/scene/test_scene_get_viewport.py`
- `tests/e2e/tools/scene/test_scene_get_viewport_camera.py`
- `tests/e2e/tools/scene/test_camera_focus.py`
- `tests/e2e/tools/scene/test_camera_orbit.py`
- `tests/e2e/tools/scene/test_isolate_object.py`
- `tests/e2e/vision/`

## Changelog Impact

- add a dedicated `_docs/_CHANGELOG/*` entry when this umbrella ships

## Execution Structure

| Order | Subtask | Depends On | Purpose |
|------|---------|------------|---------|
| 1 | [TASK-144-01](./TASK-144-01_Projection_View_Space_Contract_And_Runtime_Foundation.md) | TASK-121-03-03, TASK-121-03-04, TASK-121-03-05 | Reuse the existing named-camera / `USER_PERSPECTIVE` capture stack to define one typed view-space seam and Blender-side projection foundation |
| 2 | [TASK-144-02](./TASK-144-02_Visibility_Report_Contract_And_Read_Surface.md) | TASK-144-01 | Build the actual visibility-report contract and narrow read-only MCP surface without turning compare/iterate into the default carrier |
| 3 | [TASK-144-03](./TASK-144-03_Goal_Aware_Disclosure_Guided_Adoption_And_Regression_Pack.md) | TASK-144-01, TASK-144-02 | Keep `llm-guided` small, wire view diagnostics into guided/reference flows only on demand, and lock the behavior with docs/regressions |

Deliberate split:

- projection/view-space foundation lands before visibility verdicts so the
  report is derived from one explicit runtime seam instead of ad hoc adapter
  logic
- visibility reporting remains separate from guided adoption so the repo can
  enforce the `reference_compare_*` / `reference_iterate_*` payload boundary
- guided adoption remains a FastMCP visibility/discovery concern plus bounded
  reference-loop integration, not a new router authority layer

## Status / Board Update

- this planning pass decomposes TASK-144 into execution-ready children aligned
  to the current code seams in `scene`, `reference`, and `visibility_policy`
- `_docs/_TASKS/README.md` is intentionally unchanged in this branch per
  operator constraint; board sync is deferred to the first implementation
  branch that is allowed to touch the task board
