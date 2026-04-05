# TASK-139-02-01: Vision-Contract-Profile-Aware Prompting Abstraction

**Parent:** [TASK-139-02](./TASK-139-02_Prompt_Schema_And_Request_Routing_By_Contract_Profile.md)
**Status:** ⏳ To Do
**Priority:** 🔴 High

## Objective

Replace provider-only prompt/schema gating in the vision prompting helpers with
vision-contract-profile-aware selection.

## Technical Direction

The current code path:

- detects reference-guided compare requests
- but only enables the narrow compare prompt/schema when
  `provider_name == "google_ai_studio"`

This task should separate:

- request kind detection
- selected `vision_contract_profile`
- prompt/schema template choice

so downstream code can reuse the narrow compare contract for any compatible
profile.

This leaf owns the helper-selection seam in `prompting.py`.

It should decide:

- how request kind and selected `vision_contract_profile` combine into one
  prompt/schema choice
- which helper(s) expose that choice to callers
- how expected-key/schema behavior stays aligned with the selected
  `vision_contract_profile`

Backend request assembly and transport-specific consumption of that seam stay on
`TASK-139-02-02`.

## Repository Touchpoints

- `server/adapters/mcp/vision/prompting.py`
- `tests/unit/adapters/mcp/test_vision_prompting.py`

## Acceptance Criteria

- prompt/schema selection is driven by `vision_contract_profile` and request
  kind
- narrow compare prompt/schema generation is reusable outside the
  Google-AI-Studio-only gate
- `prompting.py` is the single owner of the prompt/schema
  vision-contract-profile-selection seam
- local-model prompt behavior is not regressed by the abstraction

## Leaf Work Items

- replace provider-only compare-contract helper gates
- add one explicit `vision_contract_profile` prompt/schema selection seam in
  `prompting.py`
- keep canonical expected-key helpers aligned with the selected
  `vision_contract_profile`
- add or update prompt-focused regression coverage only for the helper seam

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_vision_prompting.py`

## Docs To Update

- `_docs/_VISION/README.md`

## Changelog Impact

- include in the parent follow-on changelog entry when shipped

## Status / Board Update

- keep board tracking on the parent prompt/schema slice unless this leaf is
  promoted independently
- when this leaf closes, update the parent task summary so the prompt/schema
  contract seam is described at the slice level and clearly separated from
  backend request assembly
