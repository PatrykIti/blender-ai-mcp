# TASK-159-01-01: Reference Public Facade, Registration, And Checkpoint Orchestrator Split

**Parent:** [TASK-159-01](./TASK-159-01_Reference_Area_Modularization_And_Checkpoint_Assembly_Boundaries.md)
**Status:** ⏳ To Do
**Priority:** 🔴 High

## Objective

Stabilize the public `reference.py` facade by isolating registration and
checkpoint orchestration helpers before moving deeper truth/planner/perception
logic out of the file.

## Repository Touchpoints

- `server/adapters/mcp/areas/reference.py`
- likely new helper module such as `server/adapters/mcp/areas/reference_checkpoint.py`
- `server/adapters/mcp/providers/core_tools.py`
- `server/adapters/mcp/platform/capability_manifest.py`
- `tests/unit/adapters/mcp/test_provider_inventory.py`
- `tests/unit/adapters/mcp/test_surface_manifest.py`
- `tests/unit/adapters/mcp/test_public_surface_docs.py`

## Current Code Anchors

- `REFERENCE_PUBLIC_TOOL_NAMES`
- `register_reference_tools(...)`
- `_run_checkpoint_compare(...)`
- `_run_stage_checkpoint_compare(...)`
- `reference_compare_checkpoint(...)`
- `reference_compare_stage_checkpoint(...)`
- `reference_iterate_stage_checkpoint(...)`

## Planned Code Shape

```python
from .reference_checkpoint import (
    run_checkpoint_compare,
    run_stage_checkpoint_compare,
)

def register_reference_tools(target):
    return {name: _register_existing_tool(target, name) for name in REFERENCE_PUBLIC_TOOL_NAMES}
```

## Runtime / Security Contract Notes

- keep `REFERENCE_PUBLIC_TOOL_NAMES`, `register_reference_tools(...)`, and the
  provider/manifest import seam unchanged
- preserve checkpoint response envelopes and public tool docstrings
- do not let helper extraction change which staged tools are discoverable or
  pinned through the current provider/manifest surface

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_provider_inventory.py`
- `tests/unit/adapters/mcp/test_surface_manifest.py`
- `tests/unit/adapters/mcp/test_public_surface_docs.py`

## Validation Commands

- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_provider_inventory.py tests/unit/adapters/mcp/test_surface_manifest.py tests/unit/adapters/mcp/test_public_surface_docs.py -q`

## Docs To Update

- none directly unless facade ownership wording in `_docs/_MCP_SERVER/README.md`
  needs maintenance after extraction

## Changelog Impact

- include in the parent `TASK-159` changelog entry when shipped

## Acceptance Criteria

- checkpoint orchestration no longer lives inline with every other reference
  helper cluster
- public tool registration and manifest-backed discovery for the reference
  family remain unchanged
- provider/manifest regressions fail if the facade drifted

## Status / Board Update

- keep promoted tracking on parent `TASK-159`
