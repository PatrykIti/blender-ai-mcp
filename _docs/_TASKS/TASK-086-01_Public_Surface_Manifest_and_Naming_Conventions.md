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
