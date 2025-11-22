# 3. Scene Tools Improvement

**Date:** 2025-11-22  
**Version:** 0.1.2  
**Tasks:** TASK-003 (Improvement)

## 🚀 Changes

### Scene Tools
- Updated `clean_scene` tool with `keep_lights_and_cameras` parameter (default `True`).
- Added "Hard Reset" logic: Setting the parameter to `False` deletes all objects (including cameras and lights) and clears unused collections. This allows starting work from a completely empty project ("Factory Reset" for the scene).