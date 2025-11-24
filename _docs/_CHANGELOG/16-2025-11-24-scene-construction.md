# 16. Scene Construction Tools

**Date:** 2025-11-24  
**Version:** 0.1.15  
**Tasks:** TASK-010

## 🚀 Key Changes

### New Scene Tools
Added essential tools for scene composition, enabling the AI to create:
1.  **Lights (`scene_create_light`)**:
    *   Types: POINT, SUN, SPOT, AREA.
    *   Control over Energy (Watts) and Color (RGB).
2.  **Cameras (`scene_create_camera`)**:
    *   Control over Lens (focal length), Clipping, Position, and Rotation.
3.  **Empties (`scene_create_empty`)**:
    *   Helpers for hierarchy organization.
    *   Visual types: PLAIN_AXES, CUBE, SPHERE, etc.

### Implementation Details
- Tools directly create `bpy.data` blocks (Lights, Cameras) and link them to new Objects.
- Objects are automatically linked to the active scene collection.

### Testing
- Added `tests/test_scene_construction.py` verifying correct object creation and property assignment using mocks.
