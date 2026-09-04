# TASK-084-01-01-02: Inventory Builder and Enrichment

**Parent:** [TASK-084-01-01](./TASK-084-01-01_Core_Inventory_Normalization_Discovery_Taxonomy.md)  
**Status:** ✅ Done  
**Priority:** 🔴 High  

**Administrative Note:** Closed with the completed parent implementation wave. The planning sections below are retained as historical slice notes.

**Depends On:** [TASK-084-01](./TASK-084-01_Tool_Inventory_Normalization_and_Discovery_Taxonomy.md)  

---

## Objective

Implement the **Inventory Builder and Enrichment** slice of the parent task.

---

## Repository Touchpoints

- `server/adapters/mcp/discovery/tool_inventory.py`
- `server/adapters/mcp/discovery/search_documents.py`
- `server/router/infrastructure/metadata_loader.py`

---

## Planned Work

### Slice Outputs

- define canonical manifest/taxonomy fields required for discovery and visibility
- implement deterministic inventory/enrichment build path from declared sources
- ensure manifest data can be consumed by search/visibility transforms without router coupling

### Implementation Checklist

- touch `server/adapters/mcp/discovery/tool_inventory.py` with explicit change notes and boundary rationale
- touch `server/adapters/mcp/discovery/search_documents.py` with explicit change notes and boundary rationale
- touch `server/router/infrastructure/metadata_loader.py` with explicit change notes and boundary rationale
- add or update focused regression coverage for the slice behavior
- capture before/after evidence tied to the slice outputs

### Review Notes To Attach

- rationale per changed touchpoint and any explicit no-change decisions
- exact test commands and profile/config context used during validation
- deferred work list with safety rationale

---

## Acceptance Criteria

- manifest schema and inventory output are deterministic and versionable
- all required discovery fields are present or explicitly defaulted
- inventory build detects missing/invalid entries with explicit errors
- slice output is ready for TASK-084 search transform rollout

---

## Atomic Work Items

1. Implement manifest/taxonomy structures and enrichment logic in listed touchpoints.
2. Add regression tests for schema validity, enrichment completeness, and missing data handling.
3. Capture inventory before/after sample for at least one profile.
4. Document ownership split between platform manifest and router metadata.
