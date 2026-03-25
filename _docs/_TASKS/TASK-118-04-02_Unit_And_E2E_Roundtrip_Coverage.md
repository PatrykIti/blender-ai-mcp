# TASK-118-04-02: Unit and E2E Roundtrip Coverage

**Parent:** [TASK-118-04](./TASK-118-04_Metadata_Docs_And_Roundtrip_Coverage.md)  
**Status:** 🚧 In Progress  
**Priority:** 🟡 Medium

**Progress Update:** Grouped configure action coverage, contract delivery checks, router metadata alignment, and addon-side unit coverage are now in place for `scene_configure`. Blender-backed read/apply/read E2E coverage is still outstanding.

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
