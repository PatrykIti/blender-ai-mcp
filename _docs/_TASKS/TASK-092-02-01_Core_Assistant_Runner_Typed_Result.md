# TASK-092-02-01: Core Assistant Runner with Typed Result Wrappers

**Parent:** [TASK-092-02](./TASK-092-02_Assistant_Runner_with_Typed_Result_Wrappers.md)  
**Status:** ⬜ Planned  
**Priority:** 🟡 Medium  
**Depends On:** [TASK-089-01](./TASK-089-01_Contract_Catalog_and_Response_Guidelines.md)

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

- create:
  - `server/adapters/mcp/sampling/assistant_runner.py`
  - `server/adapters/mcp/sampling/result_types.py`

### Capability Rule

The runner must:

- detect sampling capability availability
- degrade cleanly when sampling is unavailable
- keep every assistant request bound to the originating MCP request
---

## Acceptance Criteria

- assistants return typed results instead of free-form text blobs
---

## Atomic Work Items

1. Implement one bounded runner around `ctx.sample()` / `ctx.sample_step()` with explicit capability detection and request-bound execution context.
2. Return typed result envelopes for `success`, `unavailable`, `masked_error`, and `rejected_by_policy` instead of free-form text blobs.
3. Keep the runner generic and adapter-scoped so router policy, semantic retrieval, and inspection truth remain separate concerns.
