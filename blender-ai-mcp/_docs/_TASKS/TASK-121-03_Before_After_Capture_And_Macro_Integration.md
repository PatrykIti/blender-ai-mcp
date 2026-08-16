# TASK-121-03: Before/After Capture and Macro Integration

**Parent:** [TASK-121](./TASK-121_Goal_Aware_Vision_Assist_And_Reference_Context.md)  
**Status:** ✅ Done  
**Priority:** 🔴 High

**Completion Summary:** Deterministic capture-bundle contracts and initial runtime presets are now in place, macro reports can carry `capture_bundle`, MCP macro adapters build bounded vision requests from before/after captures plus goal-scoped reference images when vision is enabled, and the viewport-capture path keeps `USER_PERSPECTIVE` plus named-camera visibility semantics aligned for staged real-model screenshot flows.

---

## Objective

Create a deterministic before/after capture bundle and integrate it into
macro/workflow reporting.

---

## Repository Touchpoints

- `server/adapters/mcp/areas/scene.py`
- `server/adapters/mcp/contracts/`
- `server/application/`
- `tests/unit/tools/scene/`
- `tests/e2e/tools/scene/`

---

## Leaf Breakdown

| Leaf | Purpose |
|------|---------|
| [TASK-121-03-01](./TASK-121-03-01_Capture_Bundle_Contract_And_Deterministic_Presets.md) | Define capture bundle shape and deterministic viewport presets for comparison |
| [TASK-121-03-02](./TASK-121-03-02_Macro_Workflow_Vision_Integration_Path.md) | Attach before/after captures and vision results to macro/workflow reports |
| [TASK-121-03-03](./TASK-121-03-03_Camera_Faithful_Viewport_Capture_Semantics.md) | Make camera-based viewport capture actually follow the named camera instead of the live user viewport |
| [TASK-121-03-04](./TASK-121-03-04_User_View_Manipulation_For_Viewport_Capture.md) | Add bounded user-view manipulation options to viewport capture without blurring the line between capture and broad scene-control APIs |
| [TASK-121-03-05](./TASK-121-03-05_Render_Visibility_Consistency_For_Viewport_Capture.md) | Align `USER_PERSPECTIVE`, named-camera capture, and scene visibility helpers so staged screenshots do not require render-visibility reset workarounds |

---

## Acceptance Criteria

- macro/workflow paths can produce stable visual comparison inputs
- vision integration happens on top of deterministic captures, not ad hoc screenshots
