# TASK-099-03-02: Tests Upstream Version Alignment

**Parent:** [TASK-099-03](./TASK-099-03_Upstream_Version_Alignment_and_Validation.md)  
**Status:** ⬜ Planned  
**Priority:** 🔴 High  
**Depends On:** [TASK-099-03-01](./TASK-099-03-01_Core_Upstream_Version_Alignment.md)

---

## Objective

Add regression coverage and validation notes for the selected supported runtime pair.

---

## Repository Touchpoints

- `tests/unit/adapters/mcp/`
- `_docs/`

---

## Planned Work

- record validation commands and expected runtime behavior
- ensure the supported pair is regression-tested explicitly

### Test Detail

- document the exact validation command set for the supported pair
- add or refine tests so they prove real runtime behavior, not only shimmed symbol presence

---

## Acceptance Criteria

- the selected runtime pair is test-covered and documented
