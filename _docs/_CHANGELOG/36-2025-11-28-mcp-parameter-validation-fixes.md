# Changelog #36 - MCP Parameter Validation Fixes

**Date:** 2025-11-28
**Branch:** fix/errors
**PR:** #14

---

## 📋 Summary

Fixed Pydantic validation errors occurring when MCP clients send coordinate and dictionary parameters as JSON strings instead of proper arrays/objects. Created centralized parsing utilities and added mode safeguards to prevent context errors.

---

## 🐛 Bug Fixes

### MCP Parameter Validation - Coordinate Parsing
- **Issue**: MCP clients (Claude Code, Cline) sent coordinate parameters as JSON strings `'[0.0, 0.0, 2.0]'` instead of proper lists, causing Pydantic validation errors.
- **Fix**: Created `parse_coordinate()` utility function that accepts `Union[str, List[float]]` and parses JSON strings to actual Python lists.
- **Impact**: All coordinate-based tools now work reliably regardless of how MCP clients serialize array parameters.
- **Tools Fixed**:
  - `modeling_transform_object` (location, rotation, scale)
  - `modeling_create_primitive` (location, rotation)
  - `scene_duplicate_object` (translation)
  - `scene_create_light` (location)
  - `scene_create_camera` (location)
  - `scene_create_empty` (location)
  - `mesh_extrude_region` (move)

### MCP Parameter Validation - Dictionary Parsing
- **Issue**: MCP clients sent dictionary parameters as JSON strings `'{"levels": 2}'` instead of proper dicts, causing Pydantic validation errors.
- **Fix**: Created `parse_dict()` utility function that accepts `Union[str, Dict[str, Any]]` and parses JSON strings to actual Python dictionaries.
- **Impact**: Modifier properties and other dictionary parameters now work correctly.
- **Tools Fixed**:
  - `modeling_add_modifier` (properties parameter)

### Context Mode Safeguards
- **Issue**: Calling `scene_duplicate_object` or `scene_set_active_object` from EDIT mode caused "Operator poll() failed, context is incorrect" errors.
- **Fix**: Added automatic mode switching to OBJECT mode before executing object-level operations.
- **Impact**: Object manipulation tools now work regardless of current Blender mode.
- **Files Modified**:
  - `blender_addon/application/handlers/scene.py`

---

## ✨ Features Added

### Utility Module
- **`server/adapters/mcp/utils.py`** (NEW FILE)
  - `parse_coordinate(value: Union[str, List[float], None]) -> Optional[List[float]]`
    - Parses coordinate parameters from JSON strings or lists
    - Converts all elements to float
    - Handles None values gracefully
    - Provides clear error messages for invalid formats
  - `parse_dict(value: Union[str, Dict[str, Any], None]) -> Optional[Dict[str, Any]]`
    - Parses dictionary parameters from JSON strings or dicts
    - Handles None values gracefully
    - Provides clear error messages for invalid formats

### Updated Tool Signatures
- All coordinate-accepting tools now use `Union[str, List[float]]` type hints
- All dictionary-accepting tools now use `Union[str, Dict[str, Any]]` type hints
- Parse utilities called before passing parameters to handlers

---

## 🧪 Testing

### Test File
- **`tests/test_mcp_utils.py`** (NEW FILE)
  - **TestParseCoordinate** (10 tests)
    - String parsing with floats, integers, negative values
    - Direct list handling with type conversion
    - None handling
    - Error cases: invalid JSON, non-list types, empty strings
    - Tuple support
  - **TestParseDict** (9 tests)
    - String parsing with single/multiple keys
    - Nested dictionary support
    - Direct dict handling
    - None handling
    - Error cases: invalid JSON, non-dict types, empty strings
    - Empty dict support

**Test Results:** All tests passing ✅

---

## 📚 Documentation Updates

### Roadmap Updates
- **`README.md`**
  - Added **Phase 2.1: Advanced Selection** section
  - Documented tools needed for mesh_boolean and mesh_fill_holes workflows:
    - `mesh_get_vertex_data`: Get vertex positions for programmatic selection
    - `mesh_select_by_location`: Select vertices by coordinate range
    - `mesh_select_boundary`: Select boundary edges (critical for mesh_fill_holes)
    - `mesh_select_linked`: Select connected geometry islands (critical for multi-part operations)
    - `mesh_select_loop`: Select edge loops
    - `mesh_select_ring`: Select edge rings
    - `mesh_select_more` / `mesh_select_less`: Grow/Shrink selection

---

## 🔨 Technical Details

### Before (Broken)
```python
@mcp.tool()
def modeling_transform_object(
    ctx: Context,
    name: str,
    location: List[float] = None,  # ❌ Fails when MCP sends string
    rotation: List[float] = None,
    scale: List[float] = None
) -> str:
    handler = get_modeling_handler()
    return handler.transform_object(name, location, rotation, scale)
```

### After (Fixed)
```python
@mcp.tool()
def modeling_transform_object(
    ctx: Context,
    name: str,
    location: Union[str, List[float], None] = None,  # ✅ Accepts both
    rotation: Union[str, List[float], None] = None,
    scale: Union[str, List[float], None] = None
) -> str:
    handler = get_modeling_handler()
    try:
        parsed_location = parse_coordinate(location)
        parsed_rotation = parse_coordinate(rotation)
        parsed_scale = parse_coordinate(scale)
        return handler.transform_object(name, parsed_location, parsed_rotation, parsed_scale)
    except (RuntimeError, ValueError) as e:
        return str(e)
```

### Design Decisions
- **Centralized Utilities**: Created `utils.py` module instead of duplicating parsing logic across multiple files (DRY principle)
- **Union Types**: Maintained backward compatibility - tools accept both strings and native types
- **Explicit Parsing**: Parse at adapter layer, keep domain/application layers type-safe
- **Clear Error Messages**: Validation errors include examples of expected format

---

## 🚀 Deployment

### Git Commits (6 total)
1. `feat: add parse_coordinate utility for MCP parameter handling`
2. `feat: add parse_dict utility and update modeling tools`
3. `feat: update scene tools with coordinate parsing`
4. `feat: update mesh tools with coordinate parsing`
5. `test: add comprehensive tests for MCP utils`
6. `fix: add OBJECT mode safeguards to scene operations`

### Docker Build
- Built new Docker image: `ghcr.io/patrykiti/blender-ai-mcp:latest`
- Tagged as: `blender-ai-mcp:local` for testing

### Pull Request
- **PR #14**: "feat: Fix MCP Parameter Validation & Add Mode Safeguards"
- Branch: `fix/errors` → `main`

---

## 🔍 User Testing Feedback

### Issues Discovered During Testing
1. **mesh_boolean unusable after join_objects**
   - Root cause: No way to programmatically select specific geometry after joining
   - Solution: Planned Phase 2.1 selection tools (`mesh_select_linked`, `mesh_select_by_location`)

2. **mesh_fill_holes fills wrong hole**
   - Root cause: `mesh_select_all` selects everything, can't target specific hole
   - Solution: Planned `mesh_select_boundary` to select only hole edges

3. **mesh_select_linked needed for advanced scenarios**
   - Use case: Selecting connected geometry islands for multi-part boolean operations
   - Status: Promoted to Phase 2.1 roadmap as critical tool

---

**Status:** ✅ Complete
**PR Status:** Merged to main
**Version Impact:** Patch version bump recommended (bug fixes)
