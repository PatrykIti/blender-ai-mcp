# TASK-011-7: Scene Tool Docstring Standardization

## 🎯 Objective
Define and apply concise semantic tags in docstrings for all `scene_*` tools so LLMs clearly understand which operations are safe (non-destructive) and which modify or clear the scene.

## 📋 Scope
- Tools under **Scene API** (`scene_*`) on the MCP server side (and any corresponding addon handlers if applicable).
- Focus mainly on **destructiveness** and **side-effects** (e.g. deleting, resetting, heavy changes).

## 🧩 Requirements

1. **Define Tagging Scheme for Scene Tools**
   - Propose a small tag vocabulary, for example:
     - `[SCENE][SAFE]` for tools that only query or non-destructively adjust context, e.g.:
       - `scene_list_objects`
       - `scene_set_active_object`
       - `scene_get_viewport`
       - `scene_create_light`
       - `scene_create_camera`
       - `scene_create_empty`
       - `scene_set_mode`
     - `[SCENE][DESTRUCTIVE]` for tools that remove or heavily modify scene contents, e.g.:
       - `scene_delete_object`
       - `scene_clean_scene`
   - Tags should appear on the **first line** of each docstring.

2. **Apply Tags to All Scene Tools (Server Side)**
   - File: `server/adapters/mcp/server.py`
   - Tools to tag:
     - `scene_list_objects`
     - `scene_delete_object`
     - `scene_clean_scene`
     - `scene_duplicate_object`
     - `scene_set_active_object`
     - `scene_get_viewport`
     - `scene_create_light`
     - `scene_create_camera`
     - `scene_create_empty`
     - `scene_set_mode`

3. **Clarify Destructive Semantics**
   - In `scene_clean_scene` docstring:
     - Explicitly tag as `[SCENE][DESTRUCTIVE]`.
     - Short, clear sentence about `keep_lights_and_cameras=False` meaning **hard reset** of the scene.
   - In `scene_delete_object` docstring:
     - Tag as `[SCENE][DESTRUCTIVE]` and clearly say this permanently removes the object from the scene.

4. **Keep It Token-Cheap & Consistent**
   - 1–2 short lines per tool beyond the tag line.
   - Reuse `[SCENE][SAFE]` / `[SCENE][DESTRUCTIVE]` combinations to minimize token diversity.

## ✅ Checklist
- [x] Define final tag vocabulary for scene tools.
- [x] Tag all `scene_*` tool docstrings in `server/adapters/mcp/server.py`.
- [x] Ensure destructive tools (`scene_clean_scene`, `scene_delete_object`) have very explicit, short warnings.
- [x] Update `_docs/_TASKS/README.md` statistics and To Do section.
