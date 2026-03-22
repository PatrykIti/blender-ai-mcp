# TASK-098-01-01-01: Addon Export Job Adoption

**Parent:** [TASK-098-01-01](./TASK-098-01-01_Core_Export_Task_Mode_Adoption.md)  
**Status:** ⬜ Planned  
**Priority:** 🔴 High  
**Depends On:** [TASK-098-01](./TASK-098-01_Export_Task_Mode_Adoption.md)

---

## Objective

Make addon-side export handlers usable through the existing background job lifecycle.

---

## Repository Touchpoints

- `blender_addon/application/handlers/system.py`
- `blender_addon/__init__.py`
- `blender_addon/infrastructure/rpc_server.py`

---

## Planned Work

- add cooperative progress/cancel hooks to export handlers
- register export commands as background-capable addon jobs
- keep existing foreground RPC behavior intact

### Tool-Specific Detail

- `export_glb`:
  - preserve `.glb` / `.gltf` extension normalization
  - staged progress can stay coarse: validate path -> export call -> done
- `export_fbx`:
  - preserve `mesh_smooth_type` normalization
  - staged progress can stay coarse: validate path -> export call -> done
- `export_obj`:
  - preserve writable-directory check
  - preserve mesh-object presence guard
  - preserve exporter-result and file-existence verification
  - progress should include a final verification stage, not only the exporter call

---

## Acceptance Criteria

- export handlers can be launched as addon background jobs
- cancellation and timeout checks are cooperative rather than ad hoc
