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

---

## Acceptance Criteria

- assistants return typed results instead of free-form text blobs
