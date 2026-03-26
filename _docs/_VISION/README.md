# Vision Layer Docs

Working documentation for the `TASK-121` vision-assist layer.

This folder is the canonical place to describe:

- pluggable vision backend strategy (`transformers_local` / `openai_compatible_external`)
- request-bound runtime behavior
- deterministic capture-bundle inputs
- goal-scoped reference image context
- macro/workflow integration of `capture_bundle` and `vision_assistant`
- evaluation constraints and model-comparison notes

## Current State

The repo now has the first implementation scaffolding for the vision layer:

- lazy, optional vision runtime config and backend resolution
- local and external backend families
- bounded `VisionAssistContract` / `VisionAssistantContract`
- deterministic capture-bundle contracts and initial runtime presets:
  - default `compact` profile:
    - `context_wide`
    - `target_front`
    - `target_side`
    - `target_top`
  - available `rich` profile scaffold:
    - `context_wide`
    - `target_focus`
    - `target_oblique_left`
    - `target_oblique_right`
    - `target_front`
    - `target_side`
    - `target_top`
    - `target_detail`
- focus-oriented presets now isolate the target object when the scene helper
  can do so, then restore prior visibility after capture
- goal-scoped `reference_images` session surface
- request-bound attachment of `vision_assistant` to macro MCP reports when a
  `capture_bundle` exists

Current reference-selection behavior:

- prefer references targeting the current object and current target view
- otherwise prefer object-specific references
- otherwise fall back to generic references for the requested view
- otherwise fall back to generic session references

Current image-budget assumption:

- the default bounded runtime now assumes up to `8` images per request
- this leaves room for before/after capture sets plus a small number of
  goal-scoped reference images

## Boundary Rules

The vision layer is not the truth source.

- vision interprets visible change
- measure/assert tooling remains the correctness layer
- router policy remains the policy layer
- FastMCP platform controls discovery/visibility/public surface behavior

Use these docs together with:

- [Tool Layering Policy](../_MCP_SERVER/TOOL_LAYERING_POLICY.md)
- [Router / Runtime Responsibility Boundaries](../_ROUTER/RESPONSIBILITY_BOUNDARIES.md)
- [MCP Server Docs](../_MCP_SERVER/README.md)
- [TASK-121](../_TASKS/TASK-121_Goal_Aware_Vision_Assist_And_Reference_Context.md)
- [Multi-View Capture Plan](./MULTI_VIEW_CAPTURE_PLAN.md)

## Implementation Notes

Current code-level anchors:

- `server/adapters/mcp/vision/`
- `server/adapters/mcp/contracts/vision.py`
- `server/adapters/mcp/contracts/reference.py`
- `server/adapters/mcp/areas/reference.py`
- `server/application/tool_handlers/macro_handler.py`

## Validation

Focused local validation for the current vision/runtime/capture/reference slice:

```bash
poetry run pytest tests/unit/adapters/mcp/test_reference_images.py tests/unit/adapters/mcp/test_vision_runtime_config.py tests/unit/adapters/mcp/test_vision_result_types.py tests/unit/adapters/mcp/test_vision_external_backend.py tests/unit/adapters/mcp/test_vision_local_backend.py tests/unit/adapters/mcp/test_vision_capture_bundle.py tests/unit/adapters/mcp/test_vision_capture_runtime.py tests/unit/adapters/mcp/test_vision_runner.py tests/unit/adapters/mcp/test_vision_macro_reporting.py tests/unit/adapters/mcp/test_vision_macro_mcp_integration.py tests/unit/adapters/mcp/test_vision_macro_reference_integration.py tests/unit/infrastructure/test_vision_di.py tests/unit/adapters/mcp/test_assistant_runner.py tests/unit/adapters/mcp/test_sampling_assistant_docs.py -q
```
