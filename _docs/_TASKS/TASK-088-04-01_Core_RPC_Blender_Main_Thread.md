# TASK-088-04-01: Core RPC and Blender Main-Thread Adaptation

**Parent:** [TASK-088-04](./TASK-088-04_RPC_and_Blender_Main_Thread_Adaptation.md)  
**Status:** ⬜ Planned  
**Priority:** 🔴 High  
**Depends On:** None

---

## Objective

Implement the core code changes for **RPC and Blender Main-Thread Adaptation**.

---

## Repository Touchpoints

- `blender_addon/infrastructure/rpc_server.py`
- `server/adapters/rpc/client.py`
- `blender_addon/application/handlers/extraction.py`
- `blender_addon/application/handlers/system.py`

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

1. Apply the core changes in the relevant adapters/handlers.
2. Verify the core flow still matches the expected execution path.
