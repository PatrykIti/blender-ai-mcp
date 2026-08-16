# TASK-085-02-01-01: Visibility Tags and Manifest Wiring

**Parent:** [TASK-085-02-01](./TASK-085-02-01_Core_Visibility_Engine_Tagged_Providers.md)  
**Status:** ✅ Done  
**Priority:** 🔴 High  

**Administrative Note:** Closed with the completed parent implementation wave. The planning sections below are retained as historical slice notes.

**Depends On:** [TASK-085-02](./TASK-085-02_Visibility_Policy_Engine_and_Tagged_Providers.md)  

---

## Objective

Implement the **Visibility Tags and Manifest Wiring** slice of the parent task.

---

## Repository Touchpoints

- `server/adapters/mcp/platform/capability_manifest.py`
- `server/adapters/mcp/visibility/tags.py`

---

## Planned Work

### Slice Outputs

- define canonical manifest/taxonomy fields required for discovery and visibility
- implement deterministic inventory/enrichment build path from declared sources
- ensure manifest data can be consumed by search/visibility transforms without router coupling

### Implementation Checklist

- touch `server/adapters/mcp/platform/capability_manifest.py` with explicit change notes and boundary rationale
- touch `server/adapters/mcp/visibility/tags.py` with explicit change notes and boundary rationale
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
