# TASK-117-04-02: Unit and E2E Regression Coverage

**Parent:** [TASK-117-04](./TASK-117-04_Metadata_Docs_And_Regression_Coverage.md)  
**Status:** ✅ Done  
**Priority:** 🔴 High

**Completion Summary:** Unit coverage now protects the full first assertion family, and Blender-backed E2E files were added for the new scene assertion tools.

---

## Objective

Add regression coverage for assertion semantics, not only for wrapper plumbing.

---

## Required Test Areas

- contract/result-shape validation
- tolerance edge cases
- expected vs actual payload correctness
- Blender-backed happy-path geometry checks where practical

---

## Acceptance Criteria

- unit tests catch semantic drift in assertion pass/fail logic
- E2E tests cover at least the first high-frequency assertion flows
