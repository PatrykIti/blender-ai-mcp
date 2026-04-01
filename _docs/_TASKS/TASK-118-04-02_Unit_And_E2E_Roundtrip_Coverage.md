# TASK-118-04-02: Unit and E2E Roundtrip Coverage

**Parent:** [TASK-118-04](./TASK-118-04_Metadata_Docs_And_Roundtrip_Coverage.md)  
**Status:** ✅ Done  
**Priority:** 🟡 Medium

**Completion Summary:** Grouped configure action coverage, contract delivery checks, router metadata alignment, addon-side unit coverage, and Blender-backed read/apply/read roundtrip validation are now in place for `scene_configure`.

---

## Objective

Protect the new scene-surface wave with read/apply/read regression coverage.

---

## Required Test Areas

- grouped inspect action coverage
- grouped configure action coverage
- roundtrip comparison of inspected vs reapplied settings
- Blender-backed tests for representative render/world cases

---

## Acceptance Criteria

- read/apply/read semantics are caught by tests before scene-surface regressions ship
- grouped scene config stays stable across contracts and addon behavior
