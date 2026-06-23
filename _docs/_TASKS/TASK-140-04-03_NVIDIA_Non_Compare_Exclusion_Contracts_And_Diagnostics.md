# TASK-140-04-03: NVIDIA Non-Compare Exclusion Contracts and Diagnostics

**Parent:** [TASK-140-04](./TASK-140-04_NVIDIA_VLM_Support_And_Exclusion_Policy.md)
**Depends On:** [TASK-140-04-02](./TASK-140-04-02_Selected_NVIDIA_Family_Routing_And_Compare_Path.md)
**Status:** ⏭️ Superseded
**Priority:** 🟠 High
**Superseded By:** [TASK-187](./TASK-187_External_Vision_Model_Evidence_And_Profile_Promotion_Governance.md)
**Superseded Reason:** Replaced by the capability-first OpenRouter metadata, fallback capability registry, and request-policy model. Family-specific profiles return under `TASK-187` only when harness/operator evidence shows a real contract delta.

## Objective

Make the NVIDIA exclusion boundary explicit in runtime behavior, diagnostics,
and docs so non-compare models do not appear "partially supported" by accident.

## Repository Touchpoints

- `server/adapters/mcp/vision/runtime.py`
- `server/adapters/mcp/vision/parsing.py`
- `tests/unit/adapters/mcp/test_vision_runtime_config.py`
- `tests/unit/adapters/mcp/test_vision_parsing.py`
- `_docs/_VISION/README.md`

## Acceptance Criteria

- excluded NVIDIA visual families have explicit runtime or docs-visible
  exclusion semantics
- diagnostics make it clear when a model is outside the compare-support matrix
- diagnostics preserve the `TASK-139` fallback story by making it clear when a
  non-matching NVIDIA-family id stayed on `generic_full`
- the repo does not conflate document/retrieval capability with compare
  capability

## Implementation Notes

- use this leaf to make non-compare NVIDIA behavior explicit in runtime
  selection, diagnostics, and docs
- keep exclusions and fallback diagnostics aligned so operators can distinguish
  “generic fallback” from “known non-compare family”
- coordinate the final wording with the selected-family routing leaf so the
  support matrix remains coherent

## Runtime / Security Contract Notes

- excluded NVIDIA families must not appear partially supported by accident
- diagnostics should stay bounded and explicit without surfacing raw provider
  payloads unnecessarily

## Docs To Update

- `_docs/_VISION/README.md`

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_vision_runtime_config.py`
- `tests/unit/adapters/mcp/test_vision_parsing.py`

## Changelog Impact

- include in the parent slice changelog entry when shipped

## Validation Commands

- `git diff --check`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_vision_runtime_config.py tests/unit/adapters/mcp/test_vision_parsing.py -q`
- `PYTHONPATH=. poetry run pytest ./tests/unit`

## Status / Board Update

- remains nested under `TASK-140-04`
- should close only after selected-family routing is explicit
