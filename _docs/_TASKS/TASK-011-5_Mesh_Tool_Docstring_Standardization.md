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
- [ ] Update all `mesh_*` tool docstrings in MCP server.
- [ ] Update all `mesh_*` handler docstrings in Blender Addon.
- [ ] Add boolean-specific guidance towards `modeling_add_modifier(BOOLEAN)`.
- [ ] Document suggested tag scheme for `modeling_*` tools (future task).
- [ ] Update `_docs/_TASKS/README.md` statistics and tables.
