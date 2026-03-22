# TASK-099-02-02: Tests Runtime Guards and Containment

**Parent:** [TASK-099-02](./TASK-099-02_Runtime_Guards_and_Shim_Containment.md)  
**Status:** ⬜ Planned  
**Priority:** 🔴 High  
**Depends On:** [TASK-099-02-01](./TASK-099-02-01_Core_Runtime_Guards_and_Containment.md)

---

## Objective

Add tests for guard behavior and shim containment.

---

## Repository Touchpoints

- `tests/unit/adapters/mcp/`
- `_docs/`

---

## Planned Work

- add positive/negative coverage for runtime guards
- verify shim activation is constrained to the known mismatch path

### Test Detail

- supported pair path stays green
- unsupported pair path fails clearly
- shim path only mutates missing symbols
- no-op path stays no-op when upstream symbols already exist

---

## Acceptance Criteria

- guard and containment behavior are regression-tested
