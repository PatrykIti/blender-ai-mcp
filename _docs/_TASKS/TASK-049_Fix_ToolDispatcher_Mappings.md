# TASK-049: Fix ToolDispatcher Missing and Incorrect Mappings

**Priority:** 🔴 High (blocking Router functionality)
**Category:** Infrastructure / Bug Fix
**Estimated Effort:** Small (1-2 hours)
**Dependencies:** None
**Status:** ✅ Done (2025-12-07)

---

## Overview

The `server/adapters/mcp/dispatcher.py` has multiple issues causing "tool not found" errors when the Router tries to dispatch tool calls. The dispatcher maps MCP tool names to handler method names, but several mappings are missing or incorrect.

**Problem Symptoms:**
- Router logs show "Tool not found in dispatcher: {tool_name}"
- Export/import tools fail to dispatch
- Metaball/skin tools fail to dispatch
- Some mesh tools fail due to wrong method names

**Root Cause:**
The dispatcher was not updated when new tools were added (TASK-026, TASK-035, TASK-038), and some original mappings have incorrect method names.

---

## Architecture

```
server/adapters/mcp/
├── dispatcher.py              # FIX: Add missing mappings, fix incorrect ones
```

No new files needed - this is a bug fix in existing code.

---

## Issues to Fix

### Issue 1: Missing Export/Import Tools (7 mappings)

**Location:** `dispatcher.py` lines 95-103 (System section)

**Handler:** `SystemToolHandler` (verified at `server/application/tool_handlers/system_handler.py` lines 85-200)

**Missing Mappings:**
| MCP Tool Name | Handler Method |
|---------------|----------------|
| `export_glb` | `export_glb` |
| `export_fbx` | `export_fbx` |
| `export_obj` | `export_obj` |
| `import_obj` | `import_obj` |
| `import_fbx` | `import_fbx` |
| `import_glb` | `import_glb` |
| `import_image_as_plane` | `import_image_as_plane` |

**Fix:** Add to system tools section after line 103:
```python
self._safe_update(system, {
    # ... existing mappings ...
    "export_glb": "export_glb",
    "export_fbx": "export_fbx",
    "export_obj": "export_obj",
    "import_obj": "import_obj",
    "import_fbx": "import_fbx",
    "import_glb": "import_glb",
    "import_image_as_plane": "import_image_as_plane",
})
```

---

### Issue 2: Missing Metaball/Skin Tools (5 mappings)

**Location:** `dispatcher.py` lines 106-117 (Modeling section)

**Handler:** `ModelingToolHandler` (verified at `server/application/tool_handlers/modeling_handler.py` lines 106-199)

**Missing Mappings:**
| MCP Tool Name | Handler Method |
|---------------|----------------|
| `metaball_create` | `metaball_create` |
| `metaball_add_element` | `metaball_add_element` |
| `metaball_to_mesh` | `metaball_to_mesh` |
| `skin_create_skeleton` | `skin_create_skeleton` |
| `skin_set_radius` | `skin_set_radius` |

**Fix:** Add to modeling tools section after line 117:
```python
self._safe_update(modeling, {
    # ... existing mappings ...
    "metaball_create": "metaball_create",
    "metaball_add_element": "metaball_add_element",
    "metaball_to_mesh": "metaball_to_mesh",
    "skin_create_skeleton": "skin_create_skeleton",
    "skin_set_radius": "skin_set_radius",
})
```

---

### Issue 3: Incorrect Mesh Tool Method Names (3 fixes)

**Location:** `dispatcher.py` lines 138, 141, 142 (Mesh section)

**Handler:** `MeshToolHandler` (verified at `server/application/tool_handlers/mesh_handler.py`)

**Incorrect Mappings:**
| Line | Current (Wrong) | Should Be |
|------|-----------------|-----------|
| 138 | `"mesh_boolean": "boolean_operation"` | `"mesh_boolean": "boolean"` |
| 141 | `"mesh_smooth": "smooth"` | `"mesh_smooth": "smooth_vertices"` |
| 142 | `"mesh_flatten": "flatten"` | `"mesh_flatten": "flatten_vertices"` |

**Verification from handler source:**
- Line 61: `def boolean(self, operation: str, solver: str = 'FAST') -> str:`
- Line 82: `def smooth_vertices(self, iterations: int = 1, factor: float = 0.5) -> str:`
- Line 89: `def flatten_vertices(self, axis: str) -> str:`

**Fix:** Update these three lines in the mesh section.

---

### Issue 4: Invalid Collection Tool Mappings (4 removals)

**Location:** `dispatcher.py` lines 206-209 (Collection section)

**Handler:** `CollectionToolHandler` (verified at `server/application/tool_handlers/collection_handler.py`)

**Handler only has 3 methods:**
- `list_collections`
- `list_objects`
- `manage_collection` (takes `action` parameter)

**Invalid Mappings to Remove:**
```python
# DELETE these lines - these methods don't exist:
"collection_create": "create",
"collection_delete": "delete",
"collection_rename": "rename",
"collection_move_object": "move_object",
```

The MCP layer's `collection_manage` tool already routes through `manage_collection` correctly with an `action` parameter.

---

## Implementation Checklist

### Step 1: Fix System Section (lines 95-103)
- [ ] Add 7 export/import mappings after existing system mappings

### Step 2: Fix Modeling Section (lines 106-117)
- [ ] Add 5 metaball/skin mappings after existing modeling mappings

### Step 3: Fix Mesh Section (lines 138, 141, 142)
- [ ] Change `"boolean_operation"` → `"boolean"` on line 138
- [ ] Change `"smooth"` → `"smooth_vertices"` on line 141
- [ ] Change `"flatten"` → `"flatten_vertices"` on line 142

### Step 4: Fix Collection Section (lines 206-209)
- [ ] Remove 4 invalid individual action mappings

### Step 5: Verify
- [ ] Run dispatcher's `list_tools()` and count mappings
- [ ] Test Router with tools that were previously failing

---

## Files to Modify

| File | Action |
|------|--------|
| `server/adapters/mcp/dispatcher.py` | Add 12 mappings, fix 3 names, remove 4 invalid |

---

## Summary of Changes

| Section | Action | Count |
|---------|--------|-------|
| System | Add missing export/import | +7 |
| Modeling | Add missing metaball/skin | +5 |
| Mesh | Fix wrong method names | 3 fixes |
| Collection | Remove invalid mappings | -4 |

**Total:** 12 new mappings, 3 fixes, 4 removals

---

## Testing Requirements

- [ ] Verify Router can dispatch `export_glb` tool
- [ ] Verify Router can dispatch `import_obj` tool
- [ ] Verify Router can dispatch `metaball_create` tool
- [ ] Verify Router can dispatch `skin_create_skeleton` tool
- [ ] Verify `mesh_boolean` dispatches correctly (was failing)
- [ ] Verify `mesh_smooth` dispatches correctly (was failing)
- [ ] Verify `mesh_flatten` dispatches correctly (was failing)
- [ ] Verify `collection_manage` still works (should be unaffected)

---

## Documentation Updates Required

After fixing dispatcher, update:

| File | What to Update |
|------|----------------|
| `_docs/_TASKS/TASK-049_Fix_ToolDispatcher_Mappings.md` | Mark as ✅ Done |
| `_docs/_TASKS/README.md` | Add TASK-049, update statistics |
| `_docs/_CHANGELOG/{NN}-{date}-fix-dispatcher-mappings.md` | Create changelog entry |

---

## Verification Script

After implementation, run this to verify all mappings:

```python
from server.adapters.mcp.dispatcher import get_dispatcher

dispatcher = get_dispatcher()
tools = dispatcher.list_tools()

print(f"Total registered tools: {len(tools)}")

# Check specific tools that were missing
required_tools = [
    "export_glb", "export_fbx", "export_obj",
    "import_obj", "import_fbx", "import_glb", "import_image_as_plane",
    "metaball_create", "metaball_add_element", "metaball_to_mesh",
    "skin_create_skeleton", "skin_set_radius",
    "mesh_boolean", "mesh_smooth", "mesh_flatten",
]

for tool in required_tools:
    if dispatcher.has_tool(tool):
        print(f"✅ {tool}")
    else:
        print(f"❌ {tool} - MISSING!")
```

---

## Root Cause Analysis

These issues occurred because:

1. **TASK-026 (Export Tools)** and **TASK-035 (Import Tools)** added tools to `SystemToolHandler` but didn't update dispatcher
2. **TASK-038 (Organic Modeling Tools)** added metaball/skin tools to `ModelingToolHandler` but didn't update dispatcher
3. Original mesh tool mappings had typos: handler uses `smooth_vertices`/`flatten_vertices` but dispatcher mapped to `smooth`/`flatten`
4. Collection tools were mapped to non-existent individual methods instead of the unified `manage_collection`

**Prevention:** Future tasks should include dispatcher update as part of implementation checklist.

---

## Relation to Other Tasks

This fix is required for proper Router functionality:

```
TASK-039 (Router Implementation)
    ↓ uses
TASK-049 (Dispatcher Fix) ← THIS TASK
    ↓ enables
Router to dispatch all 156 MCP tools correctly
```
