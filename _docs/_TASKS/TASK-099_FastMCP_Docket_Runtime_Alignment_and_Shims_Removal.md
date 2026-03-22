# TASK-099: FastMCP-Docket Runtime Alignment and Shims Removal

**Priority:** 🔴 High  
**Category:** FastMCP Platform  
**Estimated Effort:** Medium  
**Dependencies:** TASK-083, TASK-088  
**Status:** ⬜ Planned

**Current State:** TASK-088 introduced a repo-local compatibility shim in `server/adapters/mcp/tasks/runtime_compat.py` to bridge the current `fastmcp` / `docket` symbol drift. The repo is usable with that shim, but upstream/runtime alignment is still technical debt and should be closed intentionally.

---

## Objective

Move the repo from “task mode works because we patch the runtime mismatch locally” to “task mode works on one explicitly supported FastMCP+Docket version pair without local compatibility shims.”

---

## Problem

The current repo baseline depends on a local compatibility patch:

- FastMCP 3.1.1 expects `current_execution`
- the installed Docket line exposes `CurrentExecution`
- the repo currently patches that drift locally to keep task mode usable

That is a pragmatic fix, not a clean platform baseline.

If we leave it unresolved:

- upgrades become harder to reason about
- failures may reappear when versions drift again
- maintainers have no single supported runtime contract to point to

### Current Code Reality

Today the runtime debt is visible in concrete repo seams:

- `server/adapters/mcp/tasks/runtime_compat.py` mutates `docket.dependencies` symbols at runtime
- `server/adapters/mcp/factory.py` calls `ensure_task_runtime_compatibility()` for every server build
- `pyproject.toml` declares broad `fastmcp (>=3.0,<4.0)` but does not express an explicit supported Docket pair at the project dependency level
- `poetry.lock` currently resolves `fastmcp 3.1.1`
- current tests only prove the shimmed alias exists, not that the upstream runtime pair is formally supported without the shim

---

## Business Outcome

Turn task runtime compatibility into a maintained platform baseline instead of an implicit local workaround.

This enables:

- clearer dependency policy
- safer upgrades
- simpler debugging when task runtime fails
- eventual removal of repo-local shims

---

## Proposed Solution

Treat runtime alignment as a dedicated platform task:

1. reproduce and document the current mismatch
2. add repo-side guards so unsupported version pairs fail clearly
3. choose and validate a supported FastMCP+Docket pair
4. remove the local shim once real runtime validation is green

---

## Implementation Constraints

Follow [FASTMCP_3X_IMPLEMENTATION_MODEL.md](./FASTMCP_3X_IMPLEMENTATION_MODEL.md).

This task must preserve the difference between:

- temporary compatibility containment
- final supported runtime alignment

Rules:

- do not normalize long-term reliance on repo-local shims
- do not remove the shim before a validated supported version pair exists
- fail fast on unsupported version pairs instead of silently degrading task-mode behavior
- any final “supported pair” decision must update repo dependency docs and runtime baseline docs, not only code

---

## Scope

This task covers:

- runtime compatibility audit for FastMCP+Docket task execution
- repo-side version guards and diagnostics
- dependency/version selection for a supported pair
- removal of repo-local task-runtime shims

This task does not cover:

- product-level task adoption for more tools
- redesign of the task bridge itself

---

## Why This Matters For Blender AI

Task mode is now part of the platform product surface.

That means runtime compatibility is no longer just an internal nuisance. If the repo only works because of a hidden shim, every future task-mode rollout inherits that fragility.

---

## Success Criteria

- the repo documents one explicitly supported FastMCP+Docket task-runtime pair
- unsupported version pairs fail clearly and early
- task mode works on the supported pair without local compatibility shims
- `runtime_compat.py` can be removed or reduced to zero behavioral importance

---

## Umbrella Execution Notes

This remains the umbrella task. The original scope stays unchanged.

### Atomic Delivery Waves

1. Audit the current compatibility matrix and build a reproduction harness.
2. Add repo-side guards and diagnostics for unsupported version pairs.
3. Choose and validate a supported upstream version pair.
4. Remove local shims and close the task with tests/docs/release notes.

Implementation is decomposed into:

| Order | Subtask | Purpose |
|------|---------|---------|
| 1 | [TASK-099-01](./TASK-099-01_Compatibility_Matrix_and_Reproduction_Harness.md) | Audit and reproduce runtime compatibility drift |
| 2 | [TASK-099-02](./TASK-099-02_Runtime_Guards_and_Shim_Containment.md) | Add repo-side guards and containment around the temporary shim |
| 3 | [TASK-099-03](./TASK-099-03_Upstream_Version_Alignment_and_Validation.md) | Select and validate a supported FastMCP+Docket pair |
| 4 | [TASK-099-04](./TASK-099-04_Shims_Removal_and_Release_Documentation.md) | Remove the shim and finalize docs/release notes |
