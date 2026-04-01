# TASK-084-01-01: Core Tool Inventory Normalization and Discovery Taxonomy

**Parent:** [TASK-084-01](./TASK-084-01_Tool_Inventory_Normalization_and_Discovery_Taxonomy.md)  
**Status:** ✅ Done  
**Priority:** 🔴 High  
**Depends On:** [TASK-083-02](./TASK-083-02_Provider_Based_Component_Inventory.md)

---

## Objective

Implement the core code changes for **Tool Inventory Normalization and Discovery Taxonomy**.

## Completion Summary

This slice is now closed.

- `server/adapters/mcp/discovery/tool_inventory.py` and `taxonomy.py` provide the canonical inventory/taxonomy layer
- manifest-owned discovery metadata replaces ad hoc discovery ownership
- metadata loader enrichment coverage now includes the previously-missing router areas needed for discovery docs

---

## Repository Touchpoints

- `server/router/infrastructure/metadata_loader.py`
- `server/router/infrastructure/tools_metadata/**`
- `server/adapters/mcp/areas/*.py`
- `server/adapters/mcp/dispatcher.py`

---

## Planned Work

### New Files To Create

- `server/adapters/mcp/platform/capability_manifest.py`
- `server/adapters/mcp/discovery/tool_inventory.py`
- `server/adapters/mcp/discovery/taxonomy.py`
- `tests/unit/adapters/mcp/test_tool_inventory.py`

### Existing Files To Update

- `server/router/infrastructure/metadata_loader.py`
  - include every router-callable family that needs search enrichment data
- `server/router/infrastructure/tools_metadata/_schema.json`
  - keep router-focused fields router-focused; do not make it the canonical audience/visibility registry

### Ownership Rule

The canonical source for:

- audience
- phase tags
- public aliases
- pinned defaults
- hidden-from-search defaults

belongs in the platform capability manifest, not in router metadata.
---

## Layered Subtasks

| ID | Title | Focus |
|----|-------|-------|
| [TASK-084-01-01-01](./TASK-084-01-01-01_Capability_Manifest_Schema_and_Tags.md) | Capability Manifest Schema and Tags | Core slice |
| [TASK-084-01-01-02](./TASK-084-01-01-02_Inventory_Builder_and_Enrichment.md) | Inventory Builder and Enrichment | Core slice |

---

## Acceptance Criteria

- discovery inventory covers all public and router-callable tools
- discovery grouping is no longer fragmented across docstrings, metadata, and ad hoc lists
---

## Atomic Work Items

1. Define the shared platform manifest for public capability metadata.
2. Build discovery inventory from manifest + docstrings + schemas + optional router hints.
3. Keep router metadata as enrichment only.
4. Add tests proving every public and router-callable capability is represented exactly once.
