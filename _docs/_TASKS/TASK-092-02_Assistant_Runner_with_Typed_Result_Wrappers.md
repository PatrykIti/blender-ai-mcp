# TASK-092-02: Assistant Runner with Typed Result Wrappers

**Parent:** [TASK-092](./TASK-092_Server_Side_Sampling_Assistants.md)  
**Status:** ⬜ Planned  
**Priority:** 🟡 Medium  
**Depends On:** [TASK-089-01](./TASK-089-01_Contract_Catalog_and_Response_Guidelines.md)

---

## Objective

Build the bounded assistant runner around `ctx.sample()` or `sample_step()` with typed result wrappers.

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

## Layered Subtasks

| ID | Title | Focus |
|----|-------|-------|
| [TASK-092-02-01](./TASK-092-02-01_Core_Assistant_Runner_Typed_Result.md) | Core Assistant Runner with Typed Result Wrappers | Core implementation layer |
| [TASK-092-02-02](./TASK-092-02-02_Tests_Assistant_Runner_Typed_Result.md) | Tests and Docs Assistant Runner with Typed Result Wrappers | Tests, docs, and QA |

---

## Acceptance Criteria

- assistants return typed results instead of free-form text blobs

---

## Atomic Work Items

1. Build one bounded runner around `ctx.sample()` / `ctx.sample_step()`.
2. Add capability detection and fallback return shapes.
3. Add tests for typed success, unavailable-capability fallback, and masked-error behavior.
