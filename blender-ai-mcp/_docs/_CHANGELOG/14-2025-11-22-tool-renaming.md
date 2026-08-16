# 14. Standardize Tool Naming (Prefixing)

**Date:** 2025-11-22  
**Version:** 0.1.13  
**Tasks:** TASK-008_2

## 🚀 Key Changes

This release introduces standardized naming conventions for all MCP tools by adding domain prefixes (`scene_`, `modeling_`). This improves organization and clarity, especially as the toolset expands.

### Adapters Layer (`server/adapters/mcp/server.py`)
- **Renamed Tools:**
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

### Documentation
- **`README.md`**: Updated `autoApprove` configuration with new tool names.
- **`_docs/_MCP_SERVER/README.md`**: Updated "Available Tools" table with new names.

### Backend Stability
- The internal RPC logic (`application` and `domain` layers) remains unchanged, ensuring backward compatibility for the core logic. Only the exposed MCP interface names have changed.
