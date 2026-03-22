# TASK-099-04-02: Tests Shims Removal and Release Documentation

**Parent:** [TASK-099-04](./TASK-099-04_Shims_Removal_and_Release_Documentation.md)  
**Status:** ⬜ Planned  
**Priority:** 🟡 Medium  
**Depends On:** [TASK-099-04-01](./TASK-099-04-01_Core_Shims_Removal.md)

---

## Objective

Validate the no-shim runtime baseline and document it for maintainers/releases.

---

## Repository Touchpoints

- `tests/unit/adapters/mcp/`
- `README.md`
- `_docs/_MCP_SERVER/README.md`
- `CHANGELOG.md`

---

## Planned Work

- run the final no-shim validation suite
- update release and platform docs to reflect the aligned runtime baseline

### Final Validation Detail

- prove the supported pair is green without `runtime_compat.py`
- update `README.md`, `_docs/_MCP_SERVER/README.md`, runtime baseline docs, and release notes to remove shim-era caveats

---

## Acceptance Criteria

- final runtime baseline is validated and documented without depending on the shim
