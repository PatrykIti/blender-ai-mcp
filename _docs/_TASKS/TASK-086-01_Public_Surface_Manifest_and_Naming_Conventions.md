# TASK-086-01: Public Surface Manifest and Naming Conventions

**Parent:** [TASK-086](./TASK-086_LLM_Optimized_API_Surfaces.md)  
**Status:** ⬜ Planned  
**Priority:** 🔴 High  
**Depends On:** [TASK-083-04](./TASK-083-04_Transform_Pipeline_Baseline.md)

---

## Objective

Define which tools and parameters are public, how they should be named for LLM consumption, and which audience or version each surface element belongs to.

---

## Repository Touchpoints

- `server/adapters/mcp/areas/*.py`
- `server/adapters/mcp/dispatcher.py`
- `_docs/AVAILABLE_TOOLS_SUMMARY.md`

---

## Planned Work

- create `server/adapters/mcp/surface_manifest.py`
- create `server/adapters/mcp/naming_rules.py`
- add `tests/unit/adapters/mcp/test_surface_manifest.py`

---

## Acceptance Criteria

- there is an explicit `internal name -> public name -> audience -> version` mapping
- naming decisions are no longer hidden inside scattered wrappers
