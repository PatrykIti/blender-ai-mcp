# TASK-086-01-01: Core Public Surface Manifest and Naming Conventions

**Parent:** [TASK-086-01](./TASK-086-01_Public_Surface_Manifest_and_Naming_Conventions.md)  
**Status:** ✅ Done  
**Priority:** 🔴 High  
**Depends On:** [TASK-083-04](./TASK-083-04_Transform_Pipeline_Baseline.md), [TASK-084-01](./TASK-084-01_Tool_Inventory_Normalization_and_Discovery_Taxonomy.md)

---

## Objective

Implement the core code changes for **Public Surface Manifest and Naming Conventions**.

---

## Repository Touchpoints

- `server/adapters/mcp/areas/*.py`
- `server/adapters/mcp/dispatcher.py`

---

## Planned Work

- update `server/adapters/mcp/platform/capability_manifest.py`
- create `server/adapters/mcp/platform/public_contracts.py`
- create `server/adapters/mcp/platform/naming_rules.py`
- add `tests/unit/adapters/mcp/test_surface_manifest.py`

### Ownership Rule

Do not create a second standalone manifest that competes with the shared platform capability manifest created in TASK-084-01.
---

## Acceptance Criteria

- there is an explicit `internal name -> public name -> audience -> version` mapping
- naming decisions are no longer hidden inside scattered wrappers
---

## Atomic Work Items

1. Define naming rules for tools, arguments, and summaries.
2. Attach public contract metadata to the shared capability manifest.
3. Add tests for one capability exposing more than one public contract line.
