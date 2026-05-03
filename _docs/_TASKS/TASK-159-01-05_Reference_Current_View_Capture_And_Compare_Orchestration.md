# TASK-159-01-05: Reference Current-View Capture And Compare Orchestration

**Parent:** [TASK-159-01](./TASK-159-01_Reference_Area_Modularization_And_Checkpoint_Assembly_Boundaries.md)
**Status:** ⏳ To Do
**Priority:** 🔴 High

## Objective

Separate the live current-view capture and compare orchestration from
`reference.py` so `reference_compare_current_view(...)` is not left as an
implicit remainder under the checkpoint or image-lifecycle leaves.

This leaf owns the viewport-backed compare path that captures one live
viewport/camera frame, stores a bounded checkpoint artifact, and feeds it
through the same compare response contract used by the staged reference loop.

## Repository Touchpoints

- `server/adapters/mcp/areas/reference.py`
- likely new helper module such as `server/adapters/mcp/areas/reference_current_view.py`
- `server/adapters/mcp/contracts/reference.py`
- `server/adapters/mcp/session_capabilities.py`
- `tests/unit/adapters/mcp/test_reference_images.py`
- `tests/unit/adapters/mcp/test_public_surface_docs.py`
- `tests/unit/adapters/mcp/test_provider_inventory.py`
- `tests/unit/adapters/mcp/test_tool_inventory.py`

## Current Code Anchors

- `reference_compare_current_view(...)`
- `_compare_response(...)`
- current-view capture call through `get_scene_handler().get_viewport(...)`
- `comparison_mode=current_view_checkpoint` prompt-hint shaping

## Planned Code Shape

```python
from .reference_current_view import run_current_view_compare

async def reference_compare_current_view(...):
    return await run_current_view_compare(ctx, ...)
```

## Runtime / Security Contract Notes

- preserve the current goal precondition: an active guided goal or
  `goal_override` is still required before capture/compare proceeds
- preserve checkpoint filename uniqueness, current-view prompt-hint semantics,
  and compact off-frame diagnostics hints
- do not double-apply persisted viewport adjustments or silently widen capture
  authority beyond the active request/session
- keep the public `reference_compare_current_view(...)` tool name, response
  envelope, and discovery surface unchanged

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_reference_images.py`
- `tests/unit/adapters/mcp/test_public_surface_docs.py`
- `tests/unit/adapters/mcp/test_provider_inventory.py`
- `tests/unit/adapters/mcp/test_tool_inventory.py`

## Validation Commands

- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_reference_images.py tests/unit/adapters/mcp/test_public_surface_docs.py tests/unit/adapters/mcp/test_provider_inventory.py tests/unit/adapters/mcp/test_tool_inventory.py -q`

## Docs To Update

- inherit parent docs closeout unless staged/current-view compare ownership
  wording changes in `_docs/_MCP_SERVER/README.md` or `_docs/_VISION/README.md`

## Changelog Impact

- include in the parent `TASK-159` changelog entry when shipped

## Acceptance Criteria

- `reference_compare_current_view(...)` has an explicit owner instead of being
  inferred from the checkpoint or image-lifecycle leaves
- current-view capture, bounded checkpoint persistence, and compare response
  assembly no longer share one anonymous edit zone with unrelated staged helper
  clusters
- current-view compare keeps the same public tool name, inventory/discovery
  surface, and response contract
- targeted unit/docs/inventory lanes still prove the same current-view compare
  behavior

## Status / Board Update

- keep promoted tracking on parent `TASK-159`
