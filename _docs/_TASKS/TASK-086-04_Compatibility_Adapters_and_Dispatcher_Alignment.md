# TASK-086-04: Compatibility Adapters and Dispatcher Alignment

**Parent:** [TASK-086](./TASK-086_LLM_Optimized_API_Surfaces.md)  
**Status:** ✅ Done  
**Priority:** 🔴 High  
**Depends On:** [TASK-086-02](./TASK-086-02_Transform_Based_Tool_and_Parameter_Aliasing.md)

---

## Objective

Keep the aliased public surface compatible with router internals, dispatcher execution, and metadata alignment tests.

## Completion Summary

This slice is now closed.

- canonical-name resolution exists for public alias -> internal tool mapping
- dispatcher compatibility for aliased calls is covered by tests
- metadata alignment tests understand the public/internal distinction without breaking router internals

---

## Repository Touchpoints

- `server/adapters/mcp/dispatcher.py`
- `server/adapters/mcp/router_helper.py`
- `server/router/application/router.py`
- `tests/unit/router/infrastructure/test_mcp_tools_metadata_alignment.py`

---

## Planned Work

- add a canonical-name resolver
- maintain `public_name -> internal_name` mapping
- extend alignment tests to understand public/internal name pairs

---

## Layered Subtasks

| ID | Title | Focus |
|----|-------|-------|
| [TASK-086-04-01](./TASK-086-04-01_Core_Compatibility_Adapters_Dispatcher_Alignment.md) | Core Compatibility Adapters and Dispatcher Alignment | Core implementation layer |
| [TASK-086-04-02](./TASK-086-04-02_Tests_Compatibility_Adapters_Dispatcher_Alignment.md) | Tests and Docs Compatibility Adapters and Dispatcher Alignment | Tests, docs, and QA |

---

## Acceptance Criteria

- router continues to emit canonical internal tool names
- public aliases do not break dispatcher execution
