# TASK-092-02-01: Core Assistant Runner with Typed Result Wrappers

**Parent:** [TASK-092-02](./TASK-092-02_Assistant_Runner_with_Typed_Result_Wrappers.md)  
**Status:** ⬜ Planned  
**Priority:** 🟡 Medium  
**Depends On:** [TASK-092-02](./TASK-092-02_Assistant_Runner_with_Typed_Result_Wrappers.md)  

---

## Objective

Implement the core code changes for **Assistant Runner with Typed Result Wrappers**.

---

## Repository Touchpoints

- `server/adapters/mcp/sampling/assistant_runner.py`
- `server/adapters/mcp/sampling/result_types.py`
- `server/adapters/mcp/context_utils.py`
- `server/adapters/mcp/contracts/base.py`
- `tests/unit/adapters/mcp/test_assistant_runner.py`

---

## Planned Work

- Implement the primary code changes described in the parent task.
- Keep responsibilities aligned with Clean Architecture and `RESPONSIBILITY_BOUNDARIES.md`.
- Avoid introducing new bootstrap side effects outside the platform composition root.

---

## Acceptance Criteria

- Core implementation is complete and aligned with the parent scope.

---

## Atomic Work Items

1. Implement one bounded runner around `ctx.sample()` / `ctx.sample_step()` with explicit capability detection and request-bound execution context.
2. Return typed result envelopes for `success`, `unavailable`, `masked_error`, and `rejected_by_policy` instead of free-form text blobs.
3. Keep the runner generic and adapter-scoped so router policy, semantic retrieval, and inspection truth remain separate concerns.
