# TASK-121-03: Before/After Capture and Macro Integration

**Parent:** [TASK-121](./TASK-121_Goal_Aware_Vision_Assist_And_Reference_Context.md)  
**Status:** 🚧 In Progress  
**Priority:** 🔴 High

**Progress Update:** Deterministic capture-bundle contracts and initial runtime presets now exist, macro reports can already carry `capture_bundle`, and MCP macro adapters now build bounded vision requests from before/after captures plus goal-scoped reference images when vision is enabled.

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

---

## Acceptance Criteria

- macro/workflow paths can produce stable visual comparison inputs
- vision integration happens on top of deterministic captures, not ad hoc screenshots
