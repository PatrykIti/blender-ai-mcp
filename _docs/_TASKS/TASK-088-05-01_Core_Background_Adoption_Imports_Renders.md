# TASK-088-05-01: Core Background Adoption for Imports, Renders, Extraction, and Workflow Import

**Parent:** [TASK-088-05](./TASK-088-05_Background_Adoption_for_Imports_Renders_Extraction_and_Workflow_Import.md)  
**Status:** ✅ Done  
**Priority:** 🔴 High  
**Depends On:** [TASK-088-03](./TASK-088-03_Progress_Cancellation_and_Result_Retrieval.md), [TASK-088-04](./TASK-088-04_RPC_and_Blender_Main_Thread_Adaptation.md)

---

## Objective

Implement the core code changes for **Background Adoption for Imports, Renders, Extraction, and Workflow Import**.

---

## Repository Touchpoints

- `server/adapters/mcp/areas/scene.py`
- `server/adapters/mcp/areas/extraction.py`
- `server/adapters/mcp/areas/workflow_catalog.py`
- `server/adapters/mcp/areas/system.py`
- `server/application/tool_handlers/extraction_handler.py`
- `server/application/tool_handlers/workflow_catalog_handler.py`
- `tests/e2e/tools/extraction/`
- `tests/e2e/tools/scene/`
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
- selected entrypoints are exposed as async task-capable adapters (`async def`, `task=True`) on task-enabled surfaces
---

## Acceptance Criteria

- at least one render path, one extraction path, and one workflow-import path support task mode
---

## Atomic Work Items

1. Convert selected candidates to explicit async MCP entrypoints with `task=True` on task-enabled surfaces.
2. Preserve or document sync fallback behavior for non-task/legacy surfaces.
3. Keep the implementation aligned with the parent task boundaries and the existing runtime call path.
