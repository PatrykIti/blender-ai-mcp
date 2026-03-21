# TASK-088-05: Background Adoption for Imports, Renders, Extraction, and Workflow Import

**Parent:** [TASK-088](./TASK-088_Background_Tasks_and_Progress.md)  
**Status:** ⬜ Planned  
**Priority:** 🔴 High  
**Depends On:** [TASK-088-03](./TASK-088-03_Progress_Cancellation_and_Result_Retrieval.md), [TASK-088-04](./TASK-088-04_RPC_and_Blender_Main_Thread_Adaptation.md)

---

## Objective

Roll task mode into the first set of concrete heavy tools.

---

## Planned Work

- initial candidates:
  - `scene_get_viewport`
  - `extraction_render_angles`
  - `workflow_catalog(import_finalize)`
  - selected import or export paths

---

## Acceptance Criteria

- at least one render path, one extraction path, and one workflow-import path support task mode
