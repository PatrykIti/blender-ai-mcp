# TASK-128-02-04: Iterate-Stage Integration, Docs, and Regression Pack

**Parent:** [TASK-128-02](./TASK-128-02_Deterministic_Silhouette_Analysis_And_Typed_Action_Hints.md)
**Status:** ✅ Done
**Priority:** 🟠 High

## Objective

Adopt the silhouette metrics and typed `action_hints` into the staged
reference-guided loop and document the resulting prioritization order against
the current contract-profile-aware vision baseline.

## Repository Touchpoints

- `server/adapters/mcp/areas/reference.py`
- `tests/unit/adapters/mcp/test_reference_images.py`
- `tests/e2e/vision/`
- `_docs/_VISION/README.md`
- `_docs/_PROMPTS/REFERENCE_GUIDED_CREATURE_BUILD.md`

## Acceptance Criteria

- iterate-stage docs explain where `action_hints` sit relative to
  `correction_candidates`, `truth_followup`, and `correction_focus`
- regression coverage protects the new staged-loop output shape
- the operator prompt/docs describe the new order cleanly
- the reading order stays the same across the current MLX-local and external
  contract-profile-aware compare paths

## Docs To Update

- `_docs/_VISION/README.md`
- `_docs/_PROMPTS/REFERENCE_GUIDED_CREATURE_BUILD.md`

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_reference_images.py`
- `tests/e2e/vision/`

## Changelog Impact

- include in the parent slice changelog entry when shipped

## Execution Structure

| Order | Subtask | Purpose |
|------|---------|---------|
| 1 | [TASK-128-02-04-01](./TASK-128-02-04-01_Iterate_Stage_Adoption_And_Prioritization_Order.md) | Define the staged-loop adoption order for the new perception outputs |
| 2 | [TASK-128-02-04-02](./TASK-128-02-04-02_Silhouette_Regression_Pack_And_Vision_Docs.md) | Lock the behavior with focused regressions and updated docs |
