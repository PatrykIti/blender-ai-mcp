# TASK-099-03-01-02: Real Task Runtime Validation

**Parent:** [TASK-099-03-01](./TASK-099-03-01_Core_Upstream_Version_Alignment.md)  
**Status:** ⬜ Planned  
**Priority:** 🔴 High  
**Depends On:** [TASK-099-03-01-01](./TASK-099-03-01-01_FastMCP_Docket_Version_Selection.md)

---

## Objective

Validate background task runtime on the selected supported version pair before removing the repo-local shim.

---

## Repository Touchpoints

- `tests/unit/adapters/mcp/`
- `tests/unit/adapters/rpc/`
- `_docs/`

---

## Planned Work

- validate task submission, progress, and result handling on the selected pair
- prove the runtime behaves correctly without depending on the compatibility shim

### Validation Detail

- registration guard still works
- background task submission works under a real server/session context
- progress reporting path works without symbol patching
- result/cancel lifecycle remains green on the selected pair

---

## Acceptance Criteria

- task runtime validation is green on the supported pair
