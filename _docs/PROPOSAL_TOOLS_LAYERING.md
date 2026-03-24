# Blender AI MCP — Tool Layering, Macro Tools, Workflow Tools, and Multiview Vision Strategy

## Purpose

This document describes a practical architecture for scaling a Blender AI MCP server that already has a large tool surface (for example 161 tools), while improving reliability, tool selection quality, and vision-based scene understanding.

The goal is **not** to expose every low-level capability directly to the model at all times.

The goal is to:

- reduce tool-selection chaos
- keep low-level power available
- expose a smaller, more meaningful action space to the LLM
- support reusable workflows
- improve visual understanding of the Blender scene through structured multiview capture
- let higher-level tools orchestrate lower-level tools without turning the whole system into one giant ambiguous megatool

---

# Core Principle

Do **not** build one giant tool that does everything.

Instead, use:

1. **Atomic tools** — low-level, precise actions
2. **Macro tools** — higher-level task tools built from atomic tools
3. **Workflow tools** — bounded multi-step process tools that orchestrate macros and atomic tools
4. **Supervisor / router logic** — decides when to use workflow, macro, or atomic tools

This gives the system a controlled public surface while preserving internal flexibility.

---

# Why This Is Needed

When the MCP server grows to 161 tools, the problem changes.

The challenge is no longer only “can the server do many things?”

The real challenge becomes:

- can the model discover the right tool?
- can the model avoid drowning in the full catalog?
- can the model avoid jumping into low-level tools too early?
- can the system keep workflows consistent and testable?
- can the model inspect and verify visual results reliably?

A large flat tool catalog usually harms reliability.

A layered architecture improves:

- discoverability
- correctness
- repeatability
- debugging
- maintainability
- prompt-to-action mapping

---

# Layer 1 — Atomic Tools

## Definition

Atomic tools are small, precise, focused operations.

Each atomic tool should ideally do one thing only.

These tools are still very important, but they should **not always be the primary interface exposed to the LLM**.

## Properties

Atomic tools should be:

- narrow in scope
- deterministic
- easy to validate
- individually testable
- low-level enough to be reusable
- explicit about preconditions and outputs

## Examples

### Scene / object state
- `scene.get_state`
- `scene.resolve_target`
- `scene.compute_bounds`
- `object.get_state`
- `object.get_transform`
- `object.get_dimensions`

### Selection / mode helpers
- `selection.get_active`
- `selection.get_selected`
- `selection.set_active`
- `selection.select_object`
- `mode.get_current`
- `mode.set_object`
- `mode.set_edit`

### Camera helpers
- `camera.create_temp_camera`
- `camera.look_at_target`
- `camera.set_projection`
- `camera.compute_pose_from_bounds`
- `camera.fit_bounds`

### Capture helpers
- `capture.viewport_image`
- `capture.render_view`
- `capture.render_pass`
- `capture.crop_to_region`

### Modeling helpers
- `mesh.extrude`
- `mesh.inset`
- `mesh.bevel`
- `mesh.subdivide`
- `mesh.delete_selected`
- `modeling.add_modifier`
- `modeling.apply_boolean`

### Internal support helpers
- `scene.create_temp_collection`
- `scene.cleanup_temp_artifacts`
- `metadata.package_snapshot`
- `analysis.build_view_specs`

---

# Layer 2 — Macro Tools

## Definition

Macro tools combine several atomic tools into one meaningful task-level operation.

A macro tool should still represent **one clear responsibility**, not an entire open-ended workflow.

## Why Macro Tools Matter

This is usually the best default layer for LLM interaction.

Macro tools reduce the burden on the model because the model no longer needs to know every tiny implementation detail.

The LLM should mostly think in terms of:

- inspect scene
- capture object
- create panel cut
- align object
- verify result

instead of:

- create temp camera
- compute bounds
- render pass
- crop image
- switch mode
- restore selection
- cleanup helpers

## Properties

Macro tools should be:

- task-oriented
- easy to describe in one sentence
- composed internally from atomic tools
- safe and predictable
- often used
- more semantically meaningful than atomic tools

## Examples

### Scene / capture macros
- `scene.capture_multiview`
- `scene.capture_focus_region`
- `scene.capture_diagnostic_multiview`
- `scene.inspect_target_visual`

### Modeling macros
- `modeling.create_panel_cut`
- `modeling.create_screen_inset`
- `object.center_on_target`
- `object.align_to_reference`
- `object.place_on_surface`

### Validation / analysis macros
- `vision.analyze_multiview`
- `vision.verify_goal`
- `vision.compare_snapshots`
- `vision.locate_issue`

---

# Layer 3 — Workflow Tools

## Definition

Workflow tools represent bounded, reusable multi-step processes.

A workflow tool is not “do anything.”
A workflow tool is a defined slice of work with a clear entry, clear steps, and a clear output.

A workflow tool can call:

- macro tools
- atomic tools
- vision analysis
- validation logic
- compare steps
- decision branches

## Why Workflow Tools Matter

Workflow tools are useful when common work repeatedly follows the same pattern.

For example:

1. inspect scene
2. capture views
3. analyze
4. perform action
5. re-capture
6. verify
7. report result

This is not one simple macro anymore.
It is a mini-process.

## Properties

Workflow tools should be:

- bounded
- intentional
- reusable
- auditable
- able to return a structured report
- not open-ended “everything tools”

## Examples

- `workflow.capture_analyze_verify`
- `workflow.inspect_and_fix_alignment`
- `workflow.create_and_verify_screen_inset`
- `workflow.prepare_model_for_export`
- `workflow.detect_and_report_visual_issues`

---

# Layer 4 — Supervisor / Router Logic

## Definition

The supervisor or router is the policy layer that decides what class of tool should be used.

This is not necessarily exposed as a public tool.
Often it should be internal orchestration logic.

## Responsibility

The router should determine:

- whether a workflow tool already exists for the request
- whether a macro tool is enough
- whether the system needs to drop to atomic tools
- whether more visual context is needed before acting
- whether confidence is too low and more observations are required

## Good Routing Policy

Recommended decision order:

1. try a workflow tool
2. if none matches, try a macro tool
3. if no macro fits, compose from atomic tools
4. if uncertainty is high, inspect/capture/analyze first
5. only use internal tools indirectly unless absolutely necessary

---

# The Main Architectural Rule

## Expose intent, hide mechanics

This is one of the most important design rules.

The model should mostly see tools that represent **what it wants to achieve**, not **how the system internally implements it**.

### Good public tool
- `scene.capture_multiview`

### Bad direct public surface for the same task
- `camera.create_temp_camera`
- `camera.look_at_target`
- `camera.fit_bounds`
- `capture.render_view`
- `scene.cleanup_temp_artifacts`

The second list is implementation detail.
The first tool expresses intent.

---

# What to Hide, What to Expose

## Public / primary tools

These should be the most visible tools to the LLM.

They should usually include:

- common scene inspection tools
- common capture tools
- common modeling macros
- common validation tools
- common workflow tools

Typical size:
- around 20–40 primary tools

## Secondary tools

These are useful, but should not always be in the main discovery surface.

Examples:
- rare mesh operations
- specialized diagnostics
- advanced internal helpers
- unusual technical utilities

These can be:
- selectively exposed
- available in special modes
- accessible through router logic

## Internal tools

These should usually not be directly used by the LLM.

Examples:
- temp collection creation
- cleanup helpers
- metadata normalization
- camera rig internals
- snapshot packaging
- low-level staging operations

These tools are for system composition, not for user-level or LLM-level reasoning.

---

# The Correct Use of a “Megatool”

## Should there be a megatool?

Yes — but only if by “megatool” you mean a **bounded workflow tool**.

No — if by “megatool” you mean one huge universal tool with endless action flags.

### Good megatool pattern
A workflow tool that handles a clearly defined slice of work.

Example:
- `workflow.capture_analyze_fix_alignment`

### Bad megatool pattern
A giant catch-all interface like:
- `mega_tool(action="anything", subaction="...", mode="...", maybe_do_capture=true, maybe_analyze=true, maybe_fix=true, maybe_export=true)`

This becomes:

- ambiguous
- hard to document
- hard to test
- hard for the model to choose correctly
- hard to validate
- difficult to maintain

## Correct interpretation

So yes:
- workflow tools may call macro tools
- workflow tools may call atomic tools
- workflow tools may include decision logic
- workflow tools may produce reports

But they should still remain bounded and purpose-specific.

---

# Recommended Architecture for a 161-Tool MCP Server

## Suggested exposure model

### Internal / foundation layer
Hidden or minimally exposed:
- selection utilities
- naming helpers
- temp rig creation
- bounding-box math
- camera pose calculations
- cleanup helpers
- metadata packaging

### Atomic public-safe layer
Exposed selectively:
- scene state
- object state
- safe transforms
- common modeling actions
- single-view capture
- render pass tools

### Macro primary layer
Main surface for LLM usage:
- capture multiview
- inspect target
- align object
- create common modeling features
- compare snapshots
- verify result

### Workflow layer
For structured multi-step tasks:
- inspect + diagnose
- capture + analyze + verify
- create + validate
- repair + compare + report

## Approximate distribution

A practical target could look like this:

- **20–30 primary macro tools**
- **10–20 workflow tools**
- remainder as atomic/internal/supporting tools

This is much better than exposing all 161 tools equally.

---

# Multiview Vision Strategy

## Problem

If the system only provides one viewport screenshot to the LLM, the model has too little context.

The model may not know:

- which object is active
- what is selected
- what mode Blender is in
- which geometry is relevant
- what the scene is supposed to achieve
- whether the observed shape is correct from other angles

## Correct Solution

Use **multiview capture + structured state + goal-aware vision analysis**.

---

# Multiview Capture Strategy

## Main idea

Instead of capturing only one viewport view, the system should:

1. detect the target object or target group
2. compute world-space bounds
3. generate multiple views based on the target
4. optionally generate additional diagnostic passes
5. package everything into a structured snapshot
6. feed this to vision analysis tools or the supervisor

---

# Target Resolution Strategy

A multiview tool should first determine what to observe.

## Recommended target priority

1. explicit target name
2. active object
3. selected objects as a group
4. named collection
5. largest visible mesh
6. all visible geometry as fallback

## Why this matters

Without target resolution, multiview capture becomes inconsistent and often frames the wrong thing.

## Recommended metadata

The system should return not only the selected target, but also the reason.

Example:
- `resolution_reason: "used active object"`
- `resolution_reason: "used selected objects because no active object was set"`
- `resolution_reason: "fallback to largest visible mesh"`

This helps debugging and routing.

---

# Bounds-Based Framing

After resolving the target, compute:

- world-space bounding box
- center point
- extents / size
- diagonal / effective radius
- dominant axes
- aspect ratio characteristics

This enables repeatable camera placement.

## Why bounds matter

Camera positions should not be hardcoded blindly.
They should be computed relative to the target size and orientation.

Basic idea:

- camera position = `center + direction * distance`
- distance depends on:
  - target size
  - field of view
  - framing padding
  - whether the shot is orthographic or perspective

---

# Capture Rig Pattern

Instead of permanently cluttering the Blender scene with many extra cameras, create a temporary multiview capture rig.

## Recommended structure

A technical collection such as:
- `_mcp_capture`

Inside it:
- temporary cameras
- helper empties if needed
- metadata anchors
- temporary visual-analysis artifacts

After capture:
- either clean it up automatically
- or preserve it in debug mode

This is cleaner and easier to manage than ad hoc scene modifications.

---

# View Patterns

## Why patterns are needed

Do not invent random camera angles each time.
Use reusable view patterns.

## Recommended presets

### 1. Inspect
Basic quick inspection:
- front
- side
- top
- current-style perspective

### 2. Validation
Better for checking modeling results:
- front orthographic
- side orthographic
- top orthographic
- perspective three-quarter
- reverse three-quarter
- target close-up

### 3. Diagnostic
For difficult or error-prone cases:
- clean shaded
- wireframe
- face orientation
- object mask
- depth pass
- normals pass

---

# View Specification Pattern

Instead of storing raw camera logic everywhere, define each capture view as a reusable spec.

Example:

```json
{
  "view_id": "front_ortho",
  "projection": "orthographic",
  "direction": [0, -1, 0],
  "up": [0, 0, 1],
  "frame_target": "bbox",
  "padding": 1.15,
  "render_style": "solid_clean"
}