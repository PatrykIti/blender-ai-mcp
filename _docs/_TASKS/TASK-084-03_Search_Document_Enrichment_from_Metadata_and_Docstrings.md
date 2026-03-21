# TASK-084-03: Search Document Enrichment from Metadata and Docstrings

**Parent:** [TASK-084](./TASK-084_Dynamic_Tool_Discovery.md)  
**Status:** ⬜ Planned  
**Priority:** 🔴 High  
**Depends On:** [TASK-084-01](./TASK-084-01_Tool_Inventory_Normalization_and_Discovery_Taxonomy.md)

---

## Objective

Build rich search documents from metadata, docstrings, parameter names, and parameter descriptions so discovery works on intent-level language rather than tool names alone.

---

## Repository Touchpoints

- `server/router/infrastructure/tools_metadata/**`
- `server/adapters/mcp/areas/*.py`
- `server/domain/tools/*.py`
- `tests/unit/router/infrastructure/test_mcp_tools_metadata_alignment.py`

---

## Planned Work

- create `server/adapters/mcp/discovery/search_documents.py`
- generate search text from:
  - tool name
  - public aliases
  - description
  - docstring summary
  - parameter names
  - parameter descriptions
  - tags and category
- add tests proving that mega tools such as `mesh_inspect` are discoverable by action-level intent

---

## Pseudocode

```python
def build_search_document(tool_def, metadata):
    return " ".join([
        tool_def.name,
        metadata.description,
        " ".join(metadata.keywords),
        " ".join(tool_def.param_names),
        " ".join(tool_def.param_descriptions),
    ])
```

---

## Layered Subtasks

| ID | Title | Focus |
|----|-------|-------|
| [TASK-084-03-01](./TASK-084-03-01_Core_Search_Document_Enrichment_Metadata.md) | Core Search Document Enrichment from Metadata and Docstrings | Core implementation layer |
| [TASK-084-03-02](./TASK-084-03-02_Tests_Search_Document_Enrichment_Metadata.md) | Tests and Docs Search Document Enrichment from Metadata and Docstrings | Tests, docs, and QA |

---

## Acceptance Criteria

- search quality does not depend only on tool names
- mega tools and router tools are discoverable through intent-level phrasing
