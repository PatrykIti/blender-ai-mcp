# 04 - Metadata Loader

**Task:** TASK-039-4
**Status:** ✅ Done
**Layer:** Infrastructure

---

## Overview

The MetadataLoader loads tool metadata from modular per-tool JSON files. This enables the router to understand tool requirements, keywords, and sample prompts for intent classification.

---

## Directory Structure

```
server/router/infrastructure/tools_metadata/
├── _schema.json           # JSON Schema for validation
├── mesh/
│   ├── mesh_extrude.json
│   ├── mesh_bevel.json
│   └── mesh_inset.json
├── modeling/
│   └── modeling_create_primitive.json
├── scene/
│   └── scene_list_objects.json
├── system/
│   └── system_set_mode.json
└── ... (other areas)
```

---

## Tool Metadata Format

Each tool has a JSON file with this structure:

```json
{
  "tool_name": "mesh_extrude",
  "category": "mesh",
  "mode_required": "EDIT",
  "selection_required": true,
  "keywords": ["extrude", "pull", "extend"],
  "sample_prompts": [
    "extrude the selected faces",
    "pull out the top face"
  ],
  "parameters": {
    "value": {
      "type": "float",
      "default": 0.0,
      "range": [-100.0, 100.0]
    }
  },
  "related_tools": ["mesh_inset", "mesh_bevel"],
  "patterns": ["phone_like:screen_cutout"],
  "description": "Extrudes selected geometry."
}
```

---

## Classes

### ToolMetadata

Dataclass representing tool metadata.

```python
@dataclass
class ToolMetadata:
    tool_name: str
    category: str
    mode_required: str = "ANY"
    selection_required: bool = False
    keywords: List[str]
    sample_prompts: List[str]
    parameters: Dict[str, Any]
    related_tools: List[str]
    patterns: List[str]
    description: str
```

### MetadataLoader

Main loader class.

```python
class MetadataLoader:
    # Load all tools
    def load_all() -> Dict[str, ToolMetadata]

    # Load by area
    def load_by_area(area: str) -> Dict[str, ToolMetadata]

    # Get specific tool
    def get_tool(tool_name: str) -> Optional[ToolMetadata]

    # Reload from disk
    def reload() -> None

    # Validate all files
    def validate_all() -> List[ValidationError]

    # Query methods
    def get_tools_by_mode(mode: str) -> List[ToolMetadata]
    def get_tools_by_category(category: str) -> List[ToolMetadata]
    def get_tools_requiring_selection() -> List[str]
    def search_by_keyword(keyword: str) -> List[ToolMetadata]
    def get_all_sample_prompts() -> Dict[str, List[str]]
```

---

## Usage

```python
from server.router.infrastructure.metadata_loader import MetadataLoader

# Load all metadata
loader = MetadataLoader()
metadata = loader.load_all()

# Get specific tool
extrude = loader.get_tool("mesh_extrude")
print(extrude.mode_required)  # "EDIT"
print(extrude.selection_required)  # True

# Search by keyword
results = loader.search_by_keyword("extrude")

# Get tools requiring selection
selection_tools = loader.get_tools_requiring_selection()

# Get sample prompts for classifier training
prompts = loader.get_all_sample_prompts()
```

---

## Validation

Files are validated against schema:

```python
errors = loader.validate_all()
for error in errors:
    print(f"{error.file_path}: {error.message}")
```

Validation checks:
- Required fields (tool_name, category, mode_required)
- Valid category (must be in AREAS list)
- Valid mode (OBJECT, EDIT, SCULPT, etc., or ANY)

---

## Sample Metadata Files

Created sample files for:
- `mesh_extrude.json` - Edit mode, selection required
- `mesh_bevel.json` - Edit mode, selection required
- `mesh_inset.json` - Edit mode, selection required
- `modeling_create_primitive.json` - Object mode
- `scene_list_objects.json` - Any mode
- `system_set_mode.json` - Any mode

---

## Tests

- `tests/unit/router/infrastructure/test_metadata_loader.py` - 20 tests

---

## See Also

- [03-domain-interfaces.md](./03-domain-interfaces.md)
- [05-configuration.md](./05-configuration.md) (next)
