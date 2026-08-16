# Fix Blender Tool Bugs (Mode Validation, Boolean Solver, Edit Mode Context)

## 🐛 Bug Fixes

### mesh_boolean - Invalid Solver Default (CRITICAL)
- **Fixed**: Changed default `solver` from 'FAST' (invalid in Blender 5.0+) to 'EXACT'
- **Impact**: `mesh_boolean` now works correctly with modern Blender versions
- **Files**: `mesh.py`, `server.py`

### scene_set_mode - Improved Validation
- **Fixed**: Added object type validation before switching to EDIT/SCULPT modes
- **Impact**: Prevents cryptic "enum not found" errors, provides clear validation messages
- **Files**: `scene.py`

### Edit Mode Operations - Context Consistency
- **Fixed**: Edit mode operations now restore previous mode after completion
- **Fixed**: `scene_clean_scene` ensures OBJECT mode before deleting objects
- **Impact**: Prevents "context is incorrect" errors, more predictable behavior
- **Files**: `mesh.py`, `scene.py`
