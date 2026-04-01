# TASK-098-04-01: Core Operations Rollback Documentation

**Parent:** [TASK-098-04](./TASK-098-04_Operations_Rollback_and_Documentation.md)  
**Status:** ✅ Done  
**Priority:** 🟡 Medium  
**Depends On:** [TASK-098-03](./TASK-098-03_Import_Image_As_Plane_and_Compatibility_Polish.md)

---

## Objective

Document the operating model and rollback boundaries for import/export task-mode rollout.

---

## Repository Touchpoints

- `README.md`
- `_docs/_MCP_SERVER/README.md`
- `_docs/_TESTS/README.md`
- `_docs/_TASKS/README.md`

---

## Planned Work

- document when import/export should use background task mode
- document how to fall back safely to foreground mode if runtime or surface constraints require it

### Required Outputs

- explicit rollout note for task-capable vs compatibility surfaces
- rollback note if import/export task mode must be disabled without removing the tools themselves
- validation command list that covers unit, RPC, and selective E2E layers

---

## Acceptance Criteria

- maintainers have clear operating and rollback guidance for the import/export extension
