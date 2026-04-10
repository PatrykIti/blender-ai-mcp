# TASK-152-01-02: Reference Image Grounding In Guided Blockout Prompts

**Parent:** [TASK-152-01](./TASK-152-01_Spatial_Tool_Prompting_And_Seam_Interpretation_Guidance.md)
**Depends On:** [TASK-152-01-01](./TASK-152-01-01_Valid_Spatial_Scope_Preconditions_In_LLM_Guides.md)
**Status:** ✅ Done
**Priority:** 🔴 High

## Objective

Make the `llm-guided` prompt assets explicit that attached reference images are
not passive session metadata. They are the primary grounding input for how the
model should begin the blockout.

## Repository Touchpoints

- `_docs/_PROMPTS/GUIDED_SESSION_START.md`
- `_docs/_PROMPTS/REFERENCE_GUIDED_CREATURE_BUILD.md`
- `_docs/_PROMPTS/WORKFLOW_ROUTER_FIRST.md`
- `_docs/_PROMPTS/README.md`
- `README.md`
- `tests/unit/adapters/mcp/test_public_surface_docs.py`

## Planned Guidance Shape

- explicitly say:
  - after `reference_images(action="attach", ...)`, the model must inspect/read
    the attached reference set before deciding on:
    - initial mass proportions
    - broad silhouette
    - relative head/body/tail placement
  - do not start “guess-first” blockout from generic animal priors when the
    active guided session already has attached references
- add one short positive sequence such as:
  1. attach references
  2. set goal
  3. read the attached reference set as the grounding input
  4. start primary masses

## Planned Code / Doc Shape

```text
Prompt rule:
- If reference_images are attached for the active guided goal, inspect/read
  them before deciding:
  - body/head/tail relative scale
  - broad silhouette
  - initial placement
- Do not start from generic animal priors when active references already exist.
```

## Planned Unit Test Scenarios

- docs parity asserts wording equivalent to:
  - “attached references are the primary grounding input”
  - “read/inspect the attached references before initial mass decisions”
  - “do not start guess-first when references already exist”

## Acceptance Criteria

- prompt assets no longer let the model behave as if attached references are
  optional context before the first meaningful build decisions

## Docs To Update

- `_docs/_PROMPTS/GUIDED_SESSION_START.md`
- `_docs/_PROMPTS/REFERENCE_GUIDED_CREATURE_BUILD.md`
- `_docs/_PROMPTS/WORKFLOW_ROUTER_FIRST.md`
- `_docs/_PROMPTS/README.md`
- `README.md`

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_public_surface_docs.py`

## Planned E2E Scenarios

- transport scenarios should later verify that the revised prompt/docs contract
  is exercised in guided creature benchmark/playbook runs, but this leaf itself
  is prompt/docs focused

## Changelog Impact

- include in the parent TASK-152 changelog entry

## Completion Summary

- prompt assets now describe attached `reference_images(...)` as the primary
  grounding input for first-pass mass proportions, silhouette, and placement
