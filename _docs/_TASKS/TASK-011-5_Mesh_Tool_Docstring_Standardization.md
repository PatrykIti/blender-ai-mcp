# TASK-011-5: Mesh Tool Docstring Standardization

## 🎯 Objective
Introduce concise, consistent semantic tags in docstrings for all `mesh_*` tools so LLMs clearly understand their mode, selection semantics, and destructiveness.

## 📋 Scope
- Tools under **Edit Mode Mesh API** (`mesh_*`) on both MCP server and Blender Addon side.
- Focus on **token-cheap** tags that strongly influence LLM behavior.
- Optional follow-up (separate task): extend the same pattern to `modeling_*` and other tool groups.

## 🧩 Requirements

1. **Define Tagging Scheme**
   - For all `mesh_*` tools use a short header line in docstrings, e.g.:
     - `[EDIT MODE][SELECTION-BASED][DESTRUCTIVE]` for tools that:
       - Operate only in Edit Mode.
       - Act on the current selection.
       - Modify geometry in-place.
   - For `mesh_boolean` add an additional semantic hint:
     - `[UNSELECTED - SELECTED for DIFFERENCE]`.
   - Keep tags on the **first line** of the docstring so LLMs see them immediately.

2. **Apply Tags to All Mesh Tools**
   - MCP server adapter (`server/adapters/mcp/server.py`):
     - `mesh_select_all`
     - `mesh_delete_selected`
     - `mesh_select_by_index`
     - `mesh_extrude_region`
     - `mesh_fill_holes`
     - `mesh_bevel`
     - `mesh_loop_cut`
     - `mesh_inset`
     - `mesh_boolean`
     - `mesh_merge_by_distance`
     - `mesh_subdivide`
   - Blender Addon (`blender_addon/application/handlers/mesh.py`):
     - Ensure corresponding methods carry matching tags in their docstrings.

3. **Clarify Recommended Usage vs. Alternatives**
   - In `mesh_boolean` docstrings (server + addon):
     - Add one short line pointing to the safer, object-level alternative:
       - Example: `Prefer 'modeling_add_modifier(BOOLEAN)' for standard object-level booleans.`
   - Make sure this line is **short** and follows the tag line.

4. **Keep It Token-Cheap**
   - No long paragraphs; use **1–2 short lines** per tool at most, beyond the tags.
   - Reuse the same tag patterns across tools for maximum repetition and minimal token cost.

5. **(Optional / Future) Modeling Tools**
   - Document in this file a recommended pattern for `modeling_*` tools, but do **not** implement in this task:
     - Example tags: `[OBJECT MODE][SAFE][NON-DESTRUCTIVE]` for modifier-based or transform tools.
   - Leave a short "Future Work" note so a separate task can expand this to other groups.

## ✅ Checklist
- [ ] Define final tag vocabulary for mesh tools.
- [ ] Create example docstrings for 2 key tools as templates (see Examples below).
- [ ] Update all `mesh_*` tool docstrings in MCP server.
- [ ] Update all `mesh_*` handler docstrings in Blender Addon.
- [ ] Add boolean-specific guidance towards `modeling_add_modifier(BOOLEAN)`.
- [ ] Document suggested tag scheme for `modeling_*` tools (future task).
- [ ] Update `_docs/_TASKS/README.md` statistics and tables.

---

## 📝 Example Docstrings (Templates)

### Example 1: `mesh_extrude_region` (MCP Server)
```python
@mcp.tool()
def mesh_extrude_region(ctx: Context, move: List[float] = None) -> str:
    """
    [EDIT MODE][SELECTION-BASED][DESTRUCTIVE] Extrudes selected geometry.
    WARNING: If 'move' is None, new geometry is created in-place (overlapping).
    Always provide 'move' vector or follow up with transform.
    
    Args:
        move: Optional [x, y, z] vector to move extruded region.
    """
```

### Example 2: `mesh_boolean` (MCP Server)
```python
@mcp.tool()
def mesh_boolean(ctx: Context, operation: str = 'DIFFERENCE', solver: str = 'FAST') -> str:
    """
    [EDIT MODE][SELECTION-BASED][DESTRUCTIVE] Boolean operation on selected geometry.
    Formula: Unselected - Selected (for DIFFERENCE).
    TIP: For object-level booleans, prefer 'modeling_add_modifier(BOOLEAN)' (safer).
    
    Workflow:
      1. Select 'Cutter' geometry.
      2. Deselect 'Base' geometry.
      3. Run tool.
    
    Args:
        operation: 'INTERSECT', 'UNION', 'DIFFERENCE'.
        solver: 'FAST' or 'EXACT'.
    """
```

### Example 3: `mesh_select_by_index` (Blender Addon Handler)
```python
def select_by_index(self, indices, type='VERT', selection_mode='SET'):
    """
    [EDIT MODE][SELECTION-BASED][DESTRUCTIVE] Select geometry elements by index.
    Uses BMesh for precise indexing. Indices are 0-based.
    
    Args:
        indices: List of integer indices.
        type: 'VERT', 'EDGE', 'FACE'.
        selection_mode: 'SET' (replace), 'ADD' (extend), 'SUBTRACT' (deselect).
    """
```

### Pattern Summary
- **First Line:** Tags `[MODE][BEHAVIOR][SAFETY]` + ultra-short description.
- **Second Line:** Key warning or workflow tip (if critical).
- **Third+ Lines:** Optional workflow steps or Args (keep under 3 lines total if possible).
- **Consistency:** Reuse exact same tags across all `mesh_*` tools to minimize token diversity.
