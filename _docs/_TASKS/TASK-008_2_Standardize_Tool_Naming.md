---
type: task
id: TASK-008_2
title: Standardize Tool Naming (Prefixing)
status: todo
priority: medium
assignee: unassigned
depends_on: TASK-008_1
---

# 🎯 Objective
Standardize tool names by adding domain prefixes (`scene_`, `modeling_`). This improves organization in MCP clients (like Cline) by grouping related tools together, which is crucial as the number of tools grows (planned 30-50 tools).

# 📋 Scope of Work

## 1. Update Adapter Layer (`server/adapters/mcp/server.py`)
- Rename existing tools with prefixes:
  - `list_objects` -> `scene_list_objects`
  - `delete_object` -> `scene_delete_object`
  - `clean_scene` -> `scene_clean_scene`
  - `duplicate_object` -> `scene_duplicate_object`
  - `set_active_object` -> `scene_set_active_object`
  - `get_viewport` -> `scene_get_viewport`
  - `create_primitive` -> `modeling_create_primitive`
  - `transform_object` -> `modeling_transform_object`
  - `add_modifier` -> `modeling_add_modifier`
  - `apply_modifier` -> `modeling_apply_modifier`
  - `convert_to_mesh` -> `modeling_convert_to_mesh`
  - `join_objects` -> `modeling_join_objects`
  - `separate_object` -> `modeling_separate_object`
  - `set_origin` -> `modeling_set_origin`
  - `list_modifiers` -> `modeling_list_modifiers`

## 2. Update Documentation
- Update `README.md` (including `autoApprove` list).
- Update `_docs/_ADDON/README.md` and `_docs/_MCP_SERVER/README.md`.

## 3. Backward Compatibility Check
- Ensure internal RPC calls in `server/application` don't need changes (they shouldn't, as they call `ModelingHandler` methods directly, and RPC commands strings can remain as is or be updated for consistency - preferable to keep RPC names consistent with MCP tool names if possible, but not strictly required for this task. Let's keep RPC names as is for now to minimize backend churn, just rename the @mcp.tool exposure).

# ✅ Acceptance Criteria
- All MCP tools visible to the user start with `scene_` or `modeling_`.
- Tools are sorted logically in the client UI.
- Functionality remains unchanged.
