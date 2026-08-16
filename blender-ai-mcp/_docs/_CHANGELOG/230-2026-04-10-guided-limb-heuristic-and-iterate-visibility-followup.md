# 230. Guided limb heuristic and iterate visibility follow-up

Date: 2026-04-10

## Summary

Applied a focused follow-up after TASK-152 to restore two regressions around
guided creature/reference flows:

- prefixed abbreviated limb names such as `E2E_Abbrev_ForeL` /
  `E2E_Abbrev_HindR` now again produce limb/body seam planning
- `reference_iterate_stage_checkpoint(...)` test doubles now provide the
  native visibility API expected by guided session visibility sync

## What Changed

- widened the abbreviated limb-name fallback in:
  - `server/application/services/spatial_graph.py`
  - `server/adapters/mcp/areas/reference.py`
  so directional + side token recognition no longer depends on a very short
  token list and still works for prefixed test/runtime object names
- updated the staged silhouette E2E fake context in:
  - `tests/e2e/vision/test_reference_stage_silhouette_contract.py`
  to expose no-op `reset_visibility(...)`, `enable_components(...)`, and
  `disable_components(...)` methods required by the post-TASK-152 guided
  visibility refresh path
- added a regression unit case in:
  - `tests/unit/tools/test_handler_rpc_alignment.py`
  to keep prefixed `ForeL` / `HindR` naming coverage from drifting again

## Why

TASK-152 intentionally expanded guided naming heuristics and visibility sync,
but two residual gaps remained:

- the abbreviated limb fallback still failed once extra prefix tokens were
  present in object names
- one staged reference E2E path still used a fake context that predated the
  newer FastMCP visibility application contract

## Validation

- `PYTHONPATH=. poetry run pytest tests/unit/tools/test_handler_rpc_alignment.py -q -k 'prefixed_forel_hindr or forel_hindr'`
- `poetry run pytest tests/e2e/tools/scene/test_scene_measure_tools.py tests/e2e/vision/test_reference_stage_silhouette_contract.py -ra -s`
  - result on this machine: `1 passed, 4 skipped`
  - the four skips were Blender-backed scene E2E cases requiring an active
    Blender RPC server
