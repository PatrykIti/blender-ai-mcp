# TASK-163-06: Default-Off Segmentation Sidecar And Artifact Linkage

**Status:** ✅ Done
**Priority:** 🔴 High
**Parent:** [TASK-163](./TASK-163_Vision_Orchestrator_Feedback_Strategy_Normalization_And_Optional_Perception_Adapters.md)
**Objective:** Add default-off RU segmentation artifact linkage without changing truth ownership or making the sidecar mandatory.
**Repository Touchpoints:** `server/infrastructure/config.py`, `server/adapters/mcp/vision/config.py`, `server/adapters/mcp/vision/runtime.py`, `server/adapters/mcp/contracts/reference.py`, `server/adapters/mcp/areas/reference_understanding.py`, `server/adapters/mcp/areas/reference.py`, `tests/unit/adapters/mcp/test_vision_runtime_config.py`, `tests/unit/adapters/mcp/test_reference_images.py`, `tests/e2e/integration/test_guided_gate_state_transport.py`
**Acceptance Criteria:** missing sidecar stays non-fatal; segmentation artifacts remain advisory-only; no second public flow is introduced.

## Completion Summary

- reused the existing `VISION_SEGMENTATION_*` runtime seam so RU can
  optionally fetch support-only `segmentation_artifacts` without adding a new
  registry or public tool
- kept RU artifact linkage bounded to ids, kinds, reference ids, and summaries;
  normal payloads still avoid raw mask bytes and private local paths
- preserved the staged compare/iterate `part_segmentation` contract as the
  separate default-off runtime envelope while RU-side `segmentation_artifacts`
  stay support evidence only
- surfaced segmentation support summaries and unavailable notes through the
  existing compact orchestrator-feedback path instead of inventing a second
  discovery/read surface

## Implementation Notes

- reuse the current sidecar philosophy already present on staged compare/iterate
- link artifact refs instead of embedding heavy blobs in normal payloads
- keep `part_segmentation` and `segmentation_artifacts` distinct: one is a
  staged compare payload, the other is RU-side support evidence
- keep the implementation on the current `VISION_SEGMENTATION_*` seam from
  `TASK-158-05`, not on a new adapter registry

## Pseudocode

```python
sidecar = build_vision_runtime_config(config).active_segmentation_sidecar
if sidecar is None or not sidecar.enabled:
    return []

return [
    {
        "artifact_id": "mask_tail_front",
        "artifact_kind": "mask",
        "reference_id": "ref_front",
        "summary": "Support-only tail mask for RU follow-up.",
    }
]
```

## Runtime / Security Contract Notes

- default-off only; no implicit sidecar startup
- RU artifact linkage is advisory-only and must not mutate gate status
- sidecar timeouts/resource limits stay on the current runtime config seam
- raw mask bytes and local private paths must not be exposed in client-facing
  payloads

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_vision_runtime_config.py`
- `tests/unit/adapters/mcp/test_reference_images.py`
- `tests/e2e/integration/test_guided_gate_state_transport.py` when transport-visible RU artifact linkage changes

## Docs To Update

- `_docs/_VISION/REFERENCE_UNDERSTANDING_ROADMAP.md`
- `_docs/_VISION/README.md`
- `_docs/_MCP_SERVER/README.md` if RU artifact linkage becomes client-visible outside the existing payload family

## Changelog Impact

- covered by [319. TASK-163 optional RU support adapters](../_CHANGELOG/319-2026-05-05-task-163-optional-ru-support-adapters.md)

## Status / Board Update

- closed historically under `TASK-163`; future related work should use an
  explicit follow-on task
- does not become its own board row unless the sidecar wave is later promoted separately

## Validation Commands

- `git diff --check`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_vision_runtime_config.py tests/unit/adapters/mcp/test_reference_images.py -q`
- `PYTHONPATH=. poetry run pytest tests/e2e/integration/test_guided_gate_state_transport.py -k "reference_understanding" -q` when transport-visible RU artifacts change
