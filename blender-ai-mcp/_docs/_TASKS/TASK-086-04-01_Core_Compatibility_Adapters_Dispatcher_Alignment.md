# TASK-086-04-01: Core Compatibility Adapters and Dispatcher Alignment

**Parent:** [TASK-086-04](./TASK-086-04_Compatibility_Adapters_and_Dispatcher_Alignment.md)  
**Status:** ✅ Done  
**Priority:** 🔴 High  
**Depends On:** [TASK-086-02](./TASK-086-02_Transform_Based_Tool_and_Parameter_Aliasing.md)

---

## Objective

Implement the core code changes for **Compatibility Adapters and Dispatcher Alignment**.

---

## Repository Touchpoints

- `server/adapters/mcp/dispatcher.py`
- `server/adapters/mcp/router_helper.py`
- `server/router/application/router.py`

---

## Planned Work

- add a canonical-name resolver
- maintain `public_name -> internal_name` mapping
- extend alignment tests to understand public/internal name pairs
---

## Acceptance Criteria

- router continues to emit canonical internal tool names
- public aliases do not break dispatcher execution
---

## Atomic Work Items

1. Implement the leaf scope in the listed touchpoints.
2. Keep the implementation aligned with the parent task boundaries and the existing runtime call path.
