# TASK-086-04: Compatibility Adapters and Dispatcher Alignment

**Parent:** [TASK-086](./TASK-086_LLM_Optimized_API_Surfaces.md)  
**Status:** ⬜ Planned  
**Priority:** 🔴 High  
**Depends On:** [TASK-086-02](./TASK-086-02_Transform_Based_Tool_and_Parameter_Aliasing.md)

---

## Objective

Keep the aliased public surface compatible with router internals, dispatcher execution, and metadata alignment tests.

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

## Acceptance Criteria

- router continues to emit canonical internal tool names
- public aliases do not break dispatcher execution
