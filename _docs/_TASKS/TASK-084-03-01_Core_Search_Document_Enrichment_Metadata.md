# TASK-084-03-01: Core Search Document Enrichment from Metadata and Docstrings

**Parent:** [TASK-084-03](./TASK-084-03_Search_Document_Enrichment_from_Metadata_and_Docstrings.md)  
**Status:** ✅ Done  
**Priority:** 🔴 High  
**Depends On:** [TASK-084-01](./TASK-084-01_Tool_Inventory_Normalization_and_Discovery_Taxonomy.md)

---

## Objective

Implement the core code changes for **Search Document Enrichment from Metadata and Docstrings**.

## Completion Summary

This slice is now closed.

- `server/adapters/mcp/discovery/search_documents.py` builds enriched search text from the public discovery inventory, docstrings, metadata, and parameter schemas
- the preview search transform indexes those enriched documents on the shaped public surface

---

## Repository Touchpoints

- `server/router/infrastructure/tools_metadata/**`
- `server/adapters/mcp/areas/*.py`
- `server/domain/tools/*.py`

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

## Acceptance Criteria

- search quality does not depend only on tool names
- mega tools and router tools are discoverable through intent-level phrasing
---

## Atomic Work Items

1. Implement the leaf scope in the listed touchpoints.
2. Keep the implementation aligned with the parent task boundaries and the existing runtime call path.
