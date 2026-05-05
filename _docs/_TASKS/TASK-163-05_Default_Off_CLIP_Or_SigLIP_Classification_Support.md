# TASK-163-05: Default-Off CLIP Or SigLIP Classification Support

**Status:** ⏳ To Do
**Priority:** 🔴 High
**Parent:** [TASK-163](./TASK-163_Vision_Orchestrator_Feedback_Strategy_Normalization_And_Optional_Perception_Adapters.md)
**Objective:** Add default-off classifier support that can contribute `classification_scores` to RU without becoming a second authority.
**Repository Touchpoints:** `server/infrastructure/config.py`, `server/adapters/mcp/vision/config.py`, `server/adapters/mcp/vision/runtime.py`, `server/adapters/mcp/areas/reference_understanding.py`, `server/adapters/mcp/contracts/reference.py`, `tests/unit/adapters/mcp/test_vision_runtime_config.py`, `tests/unit/adapters/mcp/test_reference_images.py`, `tests/unit/scripts/test_script_tooling.py`
**Acceptance Criteria:** classifier path stays optional, typed, and advisory-only; disabled/unavailable states do not break guided sessions.

## Implementation Notes

- do not silently download or enable heavy classifier runtimes
- keep classifier support evidence distinct from `TASK-157` verifier authority
- preserve the current RU and transport seams instead of inventing a new tool
- reuse the existing default-off optional-perception seam from `TASK-158-05`
  instead of creating a second runtime registry or env-family
- introduce the classifier seam explicitly in `server/adapters/mcp/vision/config.py`
  and `server/adapters/mcp/vision/runtime.py`; do not pretend a ready-made
  `VisionRuntimeConfig` classifier accessor already exists

## Pseudocode

```python
runtime = build_vision_runtime_config(config)
classifier_cfg = runtime.reference_classifier  # introduced by this leaf
if classifier_cfg is None or not classifier_cfg.enabled:
    return []

return [
    {
        "label": "low_poly_faceted",
        "score": 0.91,
    }
]
```

## Runtime / Security Contract Notes

- default-off only; no implicit downloads or background startup
- classifier output is support evidence only and must not pass gates
- unavailable classifier state must degrade to typed empty/unavailable RU data,
  not runtime failure
- any provider key or model id must stay out of client-facing logs unless
  already redacted through the shared vision diagnostics path

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_vision_runtime_config.py` for default-off
  config/runtime wiring
- `tests/unit/adapters/mcp/test_reference_images.py` for unavailable-path RU
  projection
- `tests/unit/scripts/test_script_tooling.py` if harness CLI or fixture-only RU
  classification flow changes
- harness fixtures for at least creature, hard-surface, and architectural
  classes

## Docs To Update

- `_docs/_VISION/REFERENCE_UNDERSTANDING_ROADMAP.md`
- `_docs/_VISION/README.md`
- `_docs/_TESTS/README.md` when new fixture or harness lanes are added

## Changelog Impact

- add a dedicated `_docs/_CHANGELOG/*` entry when this leaf lands

## Status / Board Update

- stays under the open `TASK-163` umbrella
- does not become its own board row unless the optional adapter wave is later
  promoted separately

## Validation Commands

- `git diff --check`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_vision_runtime_config.py tests/unit/adapters/mcp/test_reference_images.py -q`
- exact harness command pair to record when this leaf is implemented:
  - local: `poetry run python scripts/vision_harness.py --fixture-only reference-understanding --backend mlx_local`
  - external: `poetry run python scripts/vision_harness.py --fixture-only reference-understanding --backend openai_compatible_external`
