# TASK-159-01-04: Reference Image Lifecycle And Staged Session Integration

**Parent:** [TASK-159-01](./TASK-159-01_Reference_Area_Modularization_And_Checkpoint_Assembly_Boundaries.md)
**Status:** ⏳ To Do
**Priority:** 🔴 High

## Objective

Separate `reference_images(...)` file-lifecycle and staged-session update logic
from the compare/iterate helper clusters so reference intake can evolve without
re-expanding the whole adapter file.

## Repository Touchpoints

- `server/adapters/mcp/areas/reference.py`
- likely new helper module such as `server/adapters/mcp/areas/reference_images_runtime.py`
- `server/adapters/mcp/session_capabilities.py`
- `server/infrastructure/tmp_paths.py`
- `tests/unit/adapters/mcp/test_reference_images.py`
- `tests/e2e/integration/test_guided_gate_state_transport.py`

## Current Code Anchors

- `reference_images(...)`
- `_validate_local_reference_path(...)`
- `_copy_reference_image(...)`
- `_delete_reference_files(...)`
- `replace_session_reference_images_async(...)`
- `replace_session_pending_reference_images_async(...)`

## Planned Code Shape

```python
stored_reference = ingest_reference_image(...)
session = await replace_session_reference_images_async(ctx, updated_images)
```

## Runtime / Security Contract Notes

- preserve current local-path validation, suffix allowlist, and file deletion
  safety
- keep active vs pending reference session semantics unchanged
- preserve current visibility/session updates on staged adoption/removal paths

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_reference_images.py`
- `tests/e2e/integration/test_guided_gate_state_transport.py`

## Validation Commands

- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_reference_images.py tests/e2e/integration/test_guided_gate_state_transport.py -q`

## Docs To Update

- inherit parent docs closeout unless reference image ownership wording in
  `_docs/_MCP_SERVER/README.md` or `_docs/_VISION/README.md` changes

## Changelog Impact

- include in the parent `TASK-159` changelog entry when shipped

## Acceptance Criteria

- reference image file lifecycle and session adoption logic no longer compete
  for space with checkpoint/truth/planner helpers
- active/pending reference semantics remain stable across attach/adopt/remove
  flows
- file/path validation rules remain explicit and test-covered

## Status / Board Update

- keep promoted tracking on parent `TASK-159`
