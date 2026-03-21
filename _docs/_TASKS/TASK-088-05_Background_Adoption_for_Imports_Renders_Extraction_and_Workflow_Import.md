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

### Adoption Rule

Adopt task mode in vertical slices:

1. one render path
2. one extraction path
3. one workflow-import path
4. only then optional import/export extensions

Each slice must prove:

- task launch works
- progress and cancellation are observable
- result retrieval is explicit
- the synchronous fallback remains understandable

### Async Gate

Each adopted candidate must include an explicit async MCP entrypoint on task-capable surfaces:

- `async def ...` adapter signature
- `task=True` enablement at the MCP boundary
- explicit fallback behavior for legacy/sync surfaces where required

---

## Layered Subtasks

| ID | Title | Focus |
|----|-------|-------|
| [TASK-088-05-01](./TASK-088-05-01_Core_Background_Adoption_Imports_Renders.md) | Core Background Adoption for Imports, Renders, Extraction, and Workflow Import | Core implementation layer |
| [TASK-088-05-02](./TASK-088-05-02_Tests_Background_Adoption_Imports_Renders.md) | Tests and Docs Background Adoption for Imports, Renders, Extraction, and Workflow Import | Tests, docs, and QA |

---

## Acceptance Criteria

- at least one render path, one extraction path, and one workflow-import path support task mode
- adopted paths are explicitly async task-capable on selected surfaces, with documented fallback on non-task surfaces
