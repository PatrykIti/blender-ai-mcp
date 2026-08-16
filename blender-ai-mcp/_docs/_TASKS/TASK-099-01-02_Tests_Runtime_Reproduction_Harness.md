# TASK-099-01-02: Tests Runtime Reproduction Harness

**Parent:** [TASK-099-01](./TASK-099-01_Compatibility_Matrix_and_Reproduction_Harness.md)  
**Status:** ✅ Done  
**Priority:** 🔴 High  
**Depends On:** [TASK-099-01-01](./TASK-099-01-01_Core_Runtime_Version_Audit.md)

---

## Objective

Add tests or harness coverage that reproduces the runtime mismatch without relying on accidental breakage.

---

## Repository Touchpoints

- `tests/unit/adapters/mcp/`
- `_docs/`

---

## Planned Work

- isolate one negative-path reproduction for the current mismatch
- keep the reproduction stable enough to validate future alignment work

### Reproduction Targets

- import/lookup path for `current_execution`
- progress reporting path used by `ctx.report_progress(...)`
- one background task submission path under a real FastMCP server context

---

## Acceptance Criteria

- runtime drift can be reproduced intentionally in tests/harness docs
