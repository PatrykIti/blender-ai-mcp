# TASK-089-01: Contract Catalog and Response Guidelines

**Parent:** [TASK-089](./TASK-089_Typed_Contracts_and_Structured_Responses.md)  
**Status:** ✅ Done  
**Priority:** 🔴 High  
**Depends On:** [TASK-083-04](./TASK-083-04_Transform_Pipeline_Baseline.md)

---

## Objective

Define the shared contract catalog and the rules for when tools return:

- native object / model payloads for structured MCP delivery
- optional short human summaries only where they add real compatibility value
- legacy text-only output only as an explicit compatibility exception

## Completion Summary

This slice is now closed.

- shared contract helpers, output-schema generation, and compatibility policy are in place
- contract-enabled adapters no longer depend on ad hoc per-tool response conventions

---

## Planned Work

- create:
  - `server/adapters/mcp/contracts/__init__.py`
  - `server/adapters/mcp/contracts/base.py`
  - `server/adapters/mcp/contracts/output_schema.py`
  - `server/adapters/mcp/contracts/compat.py`
  - `tests/unit/adapters/mcp/test_contract_base.py`

First-pass goal:

- define how adapter tools return native dict / dataclass / Pydantic objects
- define when `outputSchema` is required
- define where existing stringified JSON responses must be removed

Do not start by building a custom response-renderer framework.

---

## Layered Subtasks

| ID | Title | Focus |
|----|-------|-------|
| [TASK-089-01-01](./TASK-089-01-01_Core_Contract_Catalog_Response_Guidelines.md) | Core Contract Catalog and Response Guidelines | Core implementation layer |
| [TASK-089-01-02](./TASK-089-01-02_Tests_Contract_Catalog_Response_Guidelines.md) | Tests and Docs Contract Catalog and Response Guidelines | Tests, docs, and QA |

---

## Acceptance Criteria

- the adapter layer has one shared response-design policy instead of per-tool conventions
- contract-enabled adapters no longer need `json.dumps(...)` to expose machine-readable state

---

## Atomic Work Items

1. Define the base contract envelope and native adapter return rules.
2. Define when to return plain object-like payloads versus typed models with explicit `outputSchema`.
3. Identify and remove existing JSON-string return paths in contract-enabled tools.
4. Add tests proving object-like returns surface as structured MCP payloads on FastMCP without custom renderers.
