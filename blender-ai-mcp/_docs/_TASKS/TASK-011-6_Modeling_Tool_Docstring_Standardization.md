# TASK-011-6: Modeling Tool Docstring Standardization

## 🎯 Objective
Define and apply concise semantic tags in docstrings for all `modeling_*` tools so LLMs clearly understand that these are high-level, object-mode, generally safer operations compared to `mesh_*` tools.

## 📋 Scope
- Tools under **Object Mode Modeling API** (`modeling_*`) on both MCP server and Blender Addon side.
- Emphasize:
  - Object Mode vs Edit Mode.
  - Safe vs destructive operations.
  - Recommended usage patterns ("preferred" layer for AI over raw mesh tools).

## 🧩 Requirements

1. **Define Tagging Scheme for Modeling Tools**
   - Propose a small, reusable vocabulary of tags, for example:
     - `[OBJECT MODE][SAFE][NON-DESTRUCTIVE]` for tools that do not irreversibly alter mesh topology, e.g.:
       - `modeling_create_primitive`
       - `modeling_transform_object`
       - `modeling_add_modifier`
       - `modeling_list_modifiers`
     - `[OBJECT MODE][DESTRUCTIVE]` for tools that apply or bake changes into geometry, e.g.:
       - `modeling_apply_modifier`
       - `modeling_convert_to_mesh`
       - `modeling_join_objects`
       - `modeling_separate_object`
       - `modeling_set_origin` (changes origin, not topology, but is irreversible in a simple way).
   - Tags should appear on the **first line** of each docstring.

2. **Apply Tags to All Modeling Tools (Server Side)**
   - File: `server/adapters/mcp/server.py`
   - Tools to tag:
     - `modeling_create_primitive`
     - `modeling_transform_object`
     - `modeling_add_modifier`
     - `modeling_apply_modifier`
     - `modeling_convert_to_mesh`
     - `modeling_join_objects`
     - `modeling_separate_object`
     - `modeling_list_modifiers`
     - `modeling_set_origin`

3. **Align Blender Addon Handler Docstrings**
   - File: `blender_addon/application/handlers/modeling.py`
   - Ensure each public method corresponding to a `modeling_*` tool has matching tags in its docstring, using the same vocabulary.

4. **Clarify Relationship to Mesh Tools**
   - In one or two key modeling tools (documentation only, not behavior), briefly hint that:
     - Modeling tools are the **preferred** entry point for high-level operations.
     - `mesh_*` tools are low-level, Edit Mode, destructive building blocks.
   - Keep this to **one short line** to stay token-cheap.

5. **Keep It Token-Cheap & Consistent**
   - 1–2 short lines per tool beyond the tag line.
   - Reuse tag combinations across tools as much as possible to minimize token diversity.

## ✅ Checklist
- [x] Finalize modeling tag vocabulary (`SAFE`, `NON-DESTRUCTIVE`, `DESTRUCTIVE`, etc.).
- [x] Tag all `modeling_*` tool docstrings in `server/adapters/mcp/server.py`.
- [x] Tag all corresponding methods in `blender_addon/application/handlers/modeling.py`.
- [x] Add a brief note in 1–2 modeling tools explaining that `modeling_*` is preferred over raw `mesh_*` for high-level AI workflows.
- [x] Update `_docs/_TASKS/README.md` statistics and To Do section.
