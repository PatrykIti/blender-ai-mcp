# TASK-169-04: Viewport Verification Contract Recovery And Client Alias Hardening

**Parent:** [TASK-169](./TASK-169_Reference_Guided_Quality_Drift_Regression_And_Runtime_Authority.md)
**Status:** ✅ Done
**Completed:** 2026-05-19
**Priority:** 🟠 High
**Objective:** Restore reliable viewport-based verification for guided creature runs by hardening safe client alias recovery and clarifying the canonical `scene_get_viewport(...)` contract.
**Repository Touchpoints:** `server/adapters/mcp/areas/scene.py`, `server/adapters/mcp/areas/scene_viewport.py`, `server/adapters/mcp/guided_contract.py`, `server/adapters/mcp/discovery/search_surface.py`, `server/router/infrastructure/tools_metadata/scene/scene_get_viewport.json`, `tests/unit/tools/scene/test_mcp_viewport_output.py`, `tests/unit/adapters/mcp/test_search_surface.py`, `tests/e2e/tools/scene/test_scene_get_viewport.py`, `tests/e2e/tools/scene/test_scene_get_viewport_camera.py`
**Acceptance Criteria:**
- common safe client drift such as `output_mode=\"IMAGE_PATH\"` no longer breaks viewport verification when the recovery path is unambiguous
- unrecoverable drift still fails with one explicit correction path using the canonical public field names and values
- prompt/docs/examples stop teaching stale viewport arguments on the guided/reference surfaces

## Implementation Notes

- keep the public contract narrow:
  - `output_mode`: `IMAGE`, `BASE64`, `FILE`, `MARKDOWN`
  - `view_name`: `FRONT`, `RIGHT`, `TOP`
  - `camera_name=\"USER_PERSPECTIVE\"` for the live viewport path
- likely safe recovery candidates:
  - `PATH` -> `FILE` is already tolerated
  - evaluate whether `IMAGE_PATH` can safely normalize to `FILE`
- today alias tolerance is narrow and proxy-only:
  - `guided_contract.py` hardens guided `call_tool(...)` calls
  - direct visible-tool calls still hit the strict FastMCP/Pydantic signature
- do not introduce broad or ambiguous aliases such as `view=\"perspective\"`
  unless they map deterministically to an existing public contract
- keep the recovery logic on the current `guided_contract.py` / scene facade
  seam rather than teaching every client separately
- if proxy-only tolerance remains the final posture, improve the surfaced error
  so clients get one immediate canonical correction path

## Pseudocode

```python
mode = str(arguments.get("output_mode") or "").strip().upper()
if mode in {"PATH", "IMAGE_PATH"}:
    arguments["output_mode"] = "FILE"
elif mode and mode not in {"IMAGE", "BASE64", "FILE", "MARKDOWN"}:
    raise ValueError(canonical_scene_get_viewport_error(...))
```

## Runtime / Security Contract Notes

- only normalize aliases when the recovery is deterministic and low-risk
- keep named-camera vs user-perspective semantics explicit
- do not silently reinterpret arbitrary free-form `view` values

## Tests To Add/Update

- `tests/unit/tools/scene/test_mcp_viewport_output.py`
- `tests/unit/adapters/mcp/test_search_surface.py`
- `tests/e2e/tools/scene/test_scene_get_viewport.py`
- `tests/e2e/tools/scene/test_scene_get_viewport_camera.py`

## Docs To Update

- `_docs/_MCP_SERVER/README.md`
- `_docs/_PROMPTS/MANUAL_TOOLS_NO_ROUTER.md`
- `_docs/_PROMPTS/README.md`

## Changelog Impact

- add/update the historical `_docs/_CHANGELOG/*` entry when this slice lands

## Completion Summary

- guided contract hardening now accepts safe viewport aliases such as legacy
  `shading_mode` and `output_mode=\"PATH\"` while keeping the public canonical
  surface on `shading` and `output_mode=\"FILE\"`
- the regression is pinned on the current guided call-tool/search-surface
  tests instead of relying on operator memory

## Status / Board Update

- closed with parent `TASK-169`

## Validation Commands

- `git diff --check`
- `PYTHONPATH=. poetry run pytest tests/unit/tools/scene/test_mcp_viewport_output.py tests/unit/adapters/mcp/test_search_surface.py -q`
- `PYTHONPATH=. poetry run pytest tests/e2e/tools/scene/test_scene_get_viewport.py tests/e2e/tools/scene/test_scene_get_viewport_camera.py -q`

## Validation Category

- scene viewport contract and guided alias recovery proof
