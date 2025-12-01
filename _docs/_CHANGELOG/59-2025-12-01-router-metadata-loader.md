# Changelog: Router Metadata Loader

**Date:** 2025-12-01
**Task:** TASK-039-4
**Type:** Feature

---

## Summary

Implemented the MetadataLoader for loading tool metadata from modular per-tool JSON files.

---

## New/Updated Files

| File | Description |
|------|-------------|
| `server/router/infrastructure/metadata_loader.py` | Full MetadataLoader implementation |
| `tools_metadata/mesh/mesh_extrude.json` | Sample mesh tool metadata |
| `tools_metadata/mesh/mesh_bevel.json` | Sample mesh tool metadata |
| `tools_metadata/mesh/mesh_inset.json` | Sample mesh tool metadata |
| `tools_metadata/modeling/modeling_create_primitive.json` | Sample modeling tool |
| `tools_metadata/scene/scene_list_objects.json` | Sample scene tool |
| `tools_metadata/system/system_set_mode.json` | Sample system tool |
| `tests/unit/router/infrastructure/test_metadata_loader.py` | 20 unit tests |

---

## Features

- **ToolMetadata dataclass** - Represents tool metadata with all fields
- **MetadataLoader class** with methods:
  - `load_all()` - Load all metadata
  - `load_by_area(area)` - Load by category
  - `get_tool(name)` - Get specific tool
  - `validate_all()` - Validate against schema
  - `search_by_keyword()` - Search tools
  - `get_tools_by_mode()` - Filter by mode
  - `get_tools_requiring_selection()` - Tools needing selection
  - `get_all_sample_prompts()` - For classifier training
- **Caching** - Loaded metadata is cached
- **Validation** - Required fields, valid category/mode

---

## Tests

20 unit tests covering:
- ToolMetadata creation and serialization
- Loading all metadata
- Loading by area
- Getting specific tools
- Filtering by mode/category
- Keyword search
- Validation errors
- Caching

---

## Next Steps

- TASK-039-5: Router Configuration (expand existing config)
