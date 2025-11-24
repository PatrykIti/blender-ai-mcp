# 15. Extended Viewport Control

**Date:** 2025-11-24  
**Version:** 0.1.14  
**Tasks:** TASK-009

## 🚀 Key Changes

### Enhanced Visual Feedback
The `scene_get_viewport` tool has been significantly upgraded to give the AI precise control over what it sees. This is crucial for inspecting topology, materials, or specific details of a model.

### New Features
- **Shading Modes**: The AI can now request `WIREFRAME`, `SOLID`, `MATERIAL`, or `RENDERED` views. This allows for checking mesh topology (wireframe) vs final look (rendered).
- **Camera Control**:
  - **Specific Camera**: View through any existing camera object (e.g., `camera_name="Camera.001"`).
  - **Dynamic View**: If no camera is specified (or `USER_PERSPECTIVE` is used), a temporary camera is created.
- **Focus Targeting**:
  - When using the dynamic view, the AI can specify `focus_target="ObjectName"`. The viewport will automatically frame that object ("View Selected").
  - If no target is specified, it frames the entire scene ("View All").

### Technical Details
- **State Restoration**: The tool guarantees "side-effect free" operation. It saves the state of the viewport (shading, camera, selection) before rendering and restores it afterwards, ensuring the user's workspace is not disturbed.
- **Implementation**: Uses `bpy.context.temp_override` to manipulate the 3D View context safely during the RPC call.

### Testing
- Added `tests/test_viewport_control.py` covering complex mocking of Blender's Screen/Area/Region/Space structure to verify the context overrides and state restoration logic.
