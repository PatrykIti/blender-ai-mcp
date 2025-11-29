# TASK-014-15: Fix Blender Tool Bugs (Mode Validation, Boolean Solver, Edit Mode Context)

**Status:** ✅ Completed
**Priority:** 🔴 Critical
**Phase:** Phase 7 - Bug Fixes & Quality Improvements
**Created:** 2025-11-27
**Completed:** 2025-11-28

## 🎯 Objective
Fix 3 critical bugs identified in Blender MCP tools:
1. **mesh_boolean**: CRITICAL - Invalid default solver='FAST' (removed in Blender 5.0+)
2. **Edit mode operations**: Context consistency issues causing "context is incorrect" errors
3. **scene_set_mode**: Improve validation to prevent cryptic "enum not found" errors

## 🐛 Bug Analysis

### Bug 1: mesh_boolean - Invalid Default Solver ⚠️ CRITICAL
**Files:**
- `blender_addon/application/handlers/mesh.py:207-220`
- `server/adapters/mcp/server.py:1285-1308`

**Problem:**
- Default `solver='FAST'` is INVALID in Blender 5.0+
- Valid values: 'EXACT' (modern, recommended) or 'FLOAT' (legacy)
- This causes immediate failure on EVERY boolean operation

**Root Cause:** Outdated default parameter referencing removed Blender API enum value

### Bug 2: Edit Mode Context Consistency
**Files:**
- `blender_addon/application/handlers/mesh.py:7-16` (_ensure_edit_mode helper)
- `blender_addon/application/handlers/mesh.py:242-259` (smooth_vertices)
- `blender_addon/application/handlers/mesh.py:261-298` (flatten_vertices)
- `blender_addon/application/handlers/scene.py:30-57` (clean_scene)

**Problems:**
- `_ensure_edit_mode()` switches to EDIT mode but doesn't restore previous mode
- Operations like `mesh_smooth`, `mesh_flatten` leave objects in EDIT mode
- `scene_clean_scene()` doesn't ensure OBJECT mode before deleting objects
- Causes "context is incorrect" errors from Blender operators

**Root Cause:** Missing mode restoration logic in edit mode helpers

### Bug 3: scene_set_mode - Insufficient Validation
**File:** `blender_addon/application/handlers/scene.py:531-557`

**Problem:**
- Checks if active_object exists
- Does NOT validate object type before switching to EDIT/SCULPT modes
- Blender API throws cryptic "enum 'EDIT' not found in ('OBJECT')" when trying to switch non-MESH objects to EDIT mode

**Root Cause:** Missing object type validation before mode switch

## 🏗️ Implementation Plan

### Task 1: Fix mesh_boolean Solver Default (CRITICAL - Do First)

**1.1 Update Handler**
File: `blender_addon/application/handlers/mesh.py:207-220`

Change default:
```python
# BEFORE:
def boolean(self, object_name: str, target_name: str, operation: str, solver='FAST') -> str:

# AFTER:
def boolean(self, object_name: str, target_name: str, operation: str, solver='EXACT') -> str:
```

**1.2 Update MCP Tool**
File: `server/adapters/mcp/server.py:1285-1308`

Update schema:
```python
"solver": {
    "type": "string",
    "enum": ["EXACT", "FLOAT"],  # Remove FAST
    "default": "EXACT",  # Change from FAST
    "description": "Boolean solver algorithm. EXACT (modern, recommended), FLOAT (legacy)."
}
```

**1.3 Update Docstring**
Document that EXACT is modern/recommended, FLOAT is legacy, FAST was removed in Blender 5.0.

### Task 2: Fix Edit Mode Context Consistency

**2.1 Update _ensure_edit_mode() Helper**
File: `blender_addon/application/handlers/mesh.py:7-16`

Return previous mode:
```python
def _ensure_edit_mode(obj) -> str:
    """
    Ensure object is in EDIT mode.
    Returns the previous mode so it can be restored.
    """
    import bpy

    bpy.context.view_layer.objects.active = obj
    previous_mode = bpy.context.object.mode

    if previous_mode != 'EDIT':
        bpy.ops.object.mode_set(mode='EDIT')

    return previous_mode
```

**2.2 Update smooth_vertices() to Restore Mode**
File: `blender_addon/application/handlers/mesh.py:242-259`

```python
def smooth_vertices(self, object_name: str, factor: float = 0.5, iterations: int = 1) -> str:
    obj = bpy.data.objects.get(object_name)
    if not obj or obj.type != 'MESH':
        raise ValueError(f"Object '{object_name}' not found or is not a MESH")

    previous_mode = _ensure_edit_mode(obj)  # Store previous mode

    # ... existing smooth logic ...

    # Restore previous mode
    if previous_mode != 'EDIT':
        bpy.ops.object.mode_set(mode=previous_mode)

    return f"Smoothed vertices on '{object_name}' (factor={factor}, iterations={iterations})"
```

**2.3 Update flatten_vertices() to Restore Mode**
File: `blender_addon/application/handlers/mesh.py:261-298`

Same pattern as smooth_vertices - store and restore previous mode.

**2.4 Update scene_clean_scene() to Ensure OBJECT Mode**
File: `blender_addon/application/handlers/scene.py:30-57`

Add mode check at start:
```python
def clean_scene(self, keep_lights_and_cameras: bool = False) -> str:
    """Clean scene by removing objects."""
    # Ensure we're in OBJECT mode before deleting
    if bpy.context.mode != 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')

    # ... existing deletion logic ...
```

### Task 3: Improve scene_set_mode Validation

**3.1 Update set_mode() Method**
File: `blender_addon/application/handlers/scene.py:531-557`

Add object type validation:
```python
def set_mode(self, mode: str) -> str:
    """Switch Blender context mode."""
    valid_modes = ['OBJECT', 'EDIT', 'SCULPT', 'VERTEX_PAINT', 'WEIGHT_PAINT', 'TEXTURE_PAINT']

    if mode not in valid_modes:
        raise ValueError(f"Invalid mode '{mode}'. Valid: {valid_modes}")

    current_mode = bpy.context.mode

    if current_mode == mode or current_mode.startswith(mode):
        return f"Already in {mode} mode"

    active_obj = bpy.context.active_object

    # NEW: Validate object type for modes that require specific types
    if mode in ['EDIT', 'SCULPT'] and active_obj:
        if active_obj.type not in ['MESH', 'CURVE', 'SURFACE', 'META', 'FONT', 'LATTICE']:
            raise ValueError(
                f"Cannot enter {mode} mode: active object '{active_obj.name}' "
                f"is type '{active_obj.type}'. Supported types: MESH, CURVE, SURFACE, META, FONT, LATTICE"
            )
    elif mode in ['EDIT', 'SCULPT'] and not active_obj:
        raise ValueError(f"Cannot enter {mode} mode: no active object")

    bpy.ops.object.mode_set(mode=mode)
    return f"Switched to {mode} mode"
```

**3.2 Update MCP Tool Error Handling**
File: `server/adapters/mcp/server.py:681-692`

Catch ValueError separately from RuntimeError:
```python
@mcp.tool(...)
async def scene_set_mode(mode: str) -> str:
    try:
        return scene_handler.set_mode(mode)
    except ValueError as e:
        return f"Validation error: {str(e)}"
    except RuntimeError as e:
        return f"Runtime error: {str(e)}"
```

### Task 4: Update Tests

**4.1 Update test_mesh_boolean**
File: `tests/test_modeling_tools.py`

Verify EXACT is default solver in test assertions.

**4.2 Add Test for Mode Validation**
File: `tests/test_scene_mode.py`

```python
def test_set_mode_edit_wrong_object_type(self):
    """Test that EDIT mode rejects non-editable object types."""
    camera = MagicMock()
    camera.name = "Camera"
    camera.type = "CAMERA"
    self.mock_bpy.context.active_object = camera

    with pytest.raises(ValueError, match="Cannot enter EDIT mode"):
        self.handler.set_mode('EDIT')
```

**4.3 Add Test for Mode Restoration**
File: `tests/test_modeling_tools.py`

```python
def test_smooth_vertices_restores_mode(self):
    """Test that smooth_vertices restores previous mode."""
    mock_obj = MagicMock()
    mock_obj.type = 'MESH'
    self.mock_bpy.data.objects = {"Cube": mock_obj}
    self.mock_bpy.context.object.mode = 'OBJECT'

    self.handler.smooth_vertices("Cube", factor=0.5)

    calls = self.mock_bpy.ops.object.mode_set.call_args_list
    assert len(calls) == 2
    assert calls[0][1]['mode'] == 'EDIT'
    assert calls[1][1]['mode'] == 'OBJECT'
```

### Task 5: Update Documentation

**5.1 Update CHANGELOG**
File: `_docs/_CHANGELOG/CHANGELOG.md`

Add bug fix entries:
```markdown
## Bug Fixes (2025-11-27)

### mesh_boolean - Invalid Solver Default (CRITICAL)
- **Fixed**: Changed default `solver` from 'FAST' (invalid in Blender 5.0+) to 'EXACT'
- **Impact**: mesh_boolean now works correctly with modern Blender versions
- **Files**: mesh.py:207, server.py:1285

### scene_set_mode - Improved Validation
- **Fixed**: Added object type validation before switching to EDIT/SCULPT modes
- **Impact**: Prevents cryptic "enum not found" errors, provides clear validation messages
- **Files**: scene.py:531

### Edit Mode Operations - Context Consistency
- **Fixed**: Edit mode operations now restore previous mode after completion
- **Fixed**: scene_clean_scene ensures OBJECT mode before deleting objects
- **Impact**: Prevents "context is incorrect" errors, more predictable behavior
- **Files**: mesh.py:7-16, 242-298; scene.py:30-57
```

**5.2 Update Tool Documentation**
File: `_docs/_MCP_SERVER/README.md`

Update mesh_boolean section with correct solver options and note about FAST removal.

## ✅ Deliverables
- [x] Fix mesh_boolean solver default (CRITICAL) - Changed to 'EXACT'
- [x] Update _ensure_edit_mode() to return previous mode - Returns tuple (obj, previous_mode)
- [x] Update smooth_vertices() to restore mode - Restores previous_mode
- [x] Update flatten_vertices() to restore mode - Restores previous_mode
- [x] Update scene_clean_scene() to ensure OBJECT mode - Added mode check
- [x] Improve scene_set_mode validation - Added object type validation
- [x] Update MCP tool error handling - ValueError handling added
- [x] Add/update unit tests - Tests updated
- [x] Update CHANGELOG - Entry #35 created
- [x] Update tool documentation - Documentation updated

## 🧪 Testing Strategy

### Unit Tests
Run: `pytest tests/test_modeling_tools.py tests/test_scene_mode.py -v`

Expected results:
- All existing tests pass
- New validation test passes
- New mode restoration test passes

### Integration Tests (with real Blender)
1. Create CAMERA object, try `scene_set_mode EDIT` → should see clear validation error
2. Create two MESH cubes, run `mesh_boolean` with default solver → should succeed
3. Run `mesh_smooth` → verify object returns to OBJECT mode
4. Switch to EDIT mode, run `scene_clean_scene` → should not error

## 📊 Rollout Order

1. **CRITICAL FIRST**: Fix mesh_boolean solver (Task 1) - breaks every boolean operation
2. **Medium Priority**: Fix edit mode context (Task 2) - affects workflow but not blocking
3. **Low Priority**: Improve set_mode validation (Task 3) - better error messages
4. **After All Fixes**: Update tests (Task 4) and documentation (Task 5)

## 📁 Files to Modify

1. `blender_addon/application/handlers/mesh.py` (Tasks 1, 2)
2. `server/adapters/mcp/server.py` (Tasks 1, 3)
3. `blender_addon/application/handlers/scene.py` (Tasks 2, 3)
4. `tests/test_modeling_tools.py` (Task 4)
5. `tests/test_scene_mode.py` (Task 4)
6. `_docs/_CHANGELOG/CHANGELOG.md` (Task 5)
7. `_docs/_MCP_SERVER/README.md` (Task 5)

## 📚 Risk Assessment

- **Risk Level**: Low - all changes are isolated to specific methods
- **Impact**: High - fixes critical boolean operation failure
- **Backward Compatibility**: Safe - FAST solver doesn't work anyway, EXACT is the correct default
- **Test Coverage**: Existing 79 passing tests will catch any regressions

## 📚 References
- Blender 5.0+ Boolean Modifier API documentation
- Previous bug reports from LLM analysis
- `_docs/TOOLS_ARCHITECTURE_DEEP_DIVE.md` for testing guidelines
