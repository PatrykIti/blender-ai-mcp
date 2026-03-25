# TASK-121-03: Before/After Capture and Macro Integration

**Parent:** [TASK-121](./TASK-121_Goal_Aware_Vision_Assist_And_Reference_Context.md)  
**Status:** ⏳ To Do  
**Priority:** 🔴 High

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

---

## Acceptance Criteria

- macro/workflow paths can produce stable visual comparison inputs
- vision integration happens on top of deterministic captures, not ad hoc screenshots
