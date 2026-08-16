# 250. Guided scope validation, unavailable view checks, and sidecar status

Date: 2026-04-22

## Summary

Fixed four guided/runtime correctness gaps:

- unavailable `scene_view_diagnostics(...)` payloads no longer satisfy guided
  spatial checks
- explicit target names must exist before a guided scope can bind
- enabled-but-unexecuted segmentation sidecar config now surfaces as
  `part_segmentation.status="unavailable"` on staged compare/iterate payloads
- named-camera view diagnostics now reject non-camera objects

## What Changed

- in `server/adapters/mcp/areas/scene.py`:
  - gated guided spatial-check completion for `scene_view_diagnostics(...)` on
    real available view-space evidence instead of any non-error payload
- in `server/application/services/spatial_graph.py`:
  - validated explicit `target_object` / `target_objects` names against Blender
    truth before producing a bindable scope payload
- in `server/adapters/mcp/areas/reference.py`:
  - changed staged compare payloads to honor enabled segmentation-sidecar
    config by returning `status="unavailable"` when the sidecar is configured
    but not executed on that path
- in `blender_addon/application/handlers/scene.py`:
  - enforced that explicit `camera_name` resolves to a camera object, not just
    any object with a matching name
- updated public docs in:
  - `README.md`
  - `_docs/_MCP_SERVER/README.md`
  so the guided scope/view/segmentation story matches the shipped runtime

## Validation

- `PYTHONPATH=. poetry run pytest tests/unit -q`
  - result on this machine: `3058 passed`
- `PRE_COMMIT_HOME=/tmp/pre-commit-cache poetry run pre-commit run --all-files --show-diff-on-failure`
  - result on this machine: passed
