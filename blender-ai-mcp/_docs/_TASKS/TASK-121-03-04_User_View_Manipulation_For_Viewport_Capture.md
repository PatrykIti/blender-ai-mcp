# TASK-121-03-04: User-View Manipulation for Viewport Capture

**Parent:** [TASK-121-03](./TASK-121-03_Before_After_Capture_And_Macro_Integration.md)  
**Status:** ✅ Done  
**Priority:** 🟡 Medium

---

**Completion Summary:** `scene_get_viewport(...)` now supports a bounded
user-view adjustment path on `USER_PERSPECTIVE` captures through
`view_name`, `orbit_horizontal`, `orbit_vertical`, `zoom_factor`, and
`persist_view`. Named-camera capture remains semantically separate, the live
user-view path restores prior state by default, and both unit plus
Blender-backed E2E coverage exist for the branch behavior.

## Objective

Allow `scene_get_viewport(...)` to perform a small, bounded amount of
user-view manipulation before capture when that materially improves test and
vision-prep workflows.

The goal is convenience and determinism for capture, not to turn
`scene_get_viewport` into a replacement for the broader scene/view-control API.

---

## Business Problem

Right now `scene_get_viewport(...)` can:

- capture `USER_PERSPECTIVE`
- capture a named scene camera
- optionally focus on a target in the existing capture path

But it cannot express a compact “prepare view + capture” intent for the live
user viewport. That hurts practical workflows such as:

- take a quick top/front/right screenshot without manually chaining extra tools
- orbit slightly around the focused object before capture
- generate a stable small series of user-view screenshots for vision smoke
  comparisons

Without this, clients either:

- overuse separate utility tools for every small camera adjustment, or
- capture from a poor/friction-heavy user view

---

## Design Constraints

This leaf must preserve clean boundaries:

- **Domain / Application**
  - `server/domain/tools/scene.py` and
    `server/application/tool_handlers/scene_handler.py`
    define/transport the new bounded parameters
- **Addon**
  - actual viewport/view-state manipulation remains inside
    `blender_addon/application/handlers/scene.py`
- **MCP adapter**
  - `server/adapters/mcp/areas/scene.py` stays thin and only exposes the new
    bounded arguments

Do **not** turn this into an unbounded “do anything to the viewport” endpoint.

---

## Proposed Scope

Bounded optional arguments for the `USER_PERSPECTIVE` path only:

- `view_name`
  - standard view preset such as `FRONT`, `RIGHT`, `TOP`
- `orbit_horizontal`
  - small horizontal orbit in degrees before capture
- `orbit_vertical`
  - small vertical orbit in degrees before capture
- `zoom_factor`
  - optional zoom to combine with `focus_target`
- `persist_view`
  - whether the user viewport should stay changed after capture, or restore
    automatically

Rules:

- if `camera_name` points to an explicit camera, these user-view manipulation
  parameters should be ignored or rejected explicitly
- if `camera_name` is `USER_PERSPECTIVE` (or omitted), the tool may:
  - capture current user view unchanged
  - or apply the bounded user-view adjustments above before capture

---

## Implementation Direction

1. Extend the public `scene_get_viewport(...)` contract with bounded user-view
   capture arguments.
2. Keep the actual manipulation logic inside the addon handler.
3. Reuse existing internal viewport helpers where possible:
   - `get_view_state`
   - `restore_view_state`
   - `set_standard_view`
   - `camera_focus`
   - `camera_orbit`
4. Default to safe behavior:
   - no extra manipulation unless arguments are provided
   - avoid surprising permanent viewport mutations unless explicitly requested
5. Add:
   - unit tests for branch selection and restoration semantics
   - Blender-backed E2E for a changed user view vs default user view

---

## Repository Touchpoints

- `server/domain/tools/scene.py`
- `server/application/tool_handlers/scene_handler.py`
- `server/adapters/mcp/areas/scene.py`
- `blender_addon/application/handlers/scene.py`
- `tests/unit/tools/scene/test_viewport_control.py`
- `tests/unit/tools/scene/test_mcp_viewport_output.py`
- `tests/e2e/tools/scene/`

---

## Acceptance Criteria

- `scene_get_viewport(...)` can optionally apply bounded user-view changes
  before capture
- named-camera capture stays semantically separate from user-view capture
- unit and E2E coverage prove the bounded user-view path works
- the tool remains bounded and clean-architecture aligned
