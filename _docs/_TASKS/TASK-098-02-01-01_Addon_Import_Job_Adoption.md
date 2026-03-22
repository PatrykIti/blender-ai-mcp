# TASK-098-02-01-01: Addon Import Job Adoption

**Parent:** [TASK-098-02-01](./TASK-098-02-01_Core_Import_Task_Mode_Adoption.md)  
**Status:** ✅ Done  
**Priority:** 🔴 High  
**Depends On:** [TASK-098-02](./TASK-098-02_Import_Task_Mode_Adoption.md)

---

## Objective

Make addon-side import handlers usable through the existing background job lifecycle.

---

## Repository Touchpoints

- `blender_addon/application/handlers/system.py`
- `blender_addon/__init__.py`
- `blender_addon/infrastructure/rpc_server.py`

---

## Planned Work

- add cooperative progress/cancel hooks to import handlers
- register import commands as background-capable addon jobs
- keep existing foreground RPC behavior intact

### Tool-Specific Detail

- `import_obj`:
  - preserve file-existence validation
  - preserve imported-object delta reporting
- `import_fbx`:
  - preserve file-existence validation
  - preserve imported-object delta reporting
- `import_glb`:
  - preserve file-existence validation
  - preserve imported-object delta reporting

Progress stages should align with the real handler flow:

1. validate file
2. run importer
3. compute/imported object delta

---

## Acceptance Criteria

- import handlers can be launched as addon background jobs
- cancellation and timeout checks are cooperative rather than ad hoc
