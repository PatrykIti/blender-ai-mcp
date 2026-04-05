# TASK-139-02-01: Profile-Aware Prompting Abstraction

**Parent:** [TASK-139-02](./TASK-139-02_Prompt_Schema_And_Request_Routing_By_Contract_Profile.md)
**Status:** ⏳ To Do
**Priority:** 🔴 High

## Objective

Replace provider-only prompt/schema gating in the vision prompting helpers with
contract-profile-aware selection.

## Technical Direction

The current code path:

- detects reference-guided compare requests
- but only enables the narrow compare prompt/schema when
  `provider_name == "google_ai_studio"`

This task should separate:

- request kind detection
- selected contract profile
- prompt/schema template choice

so downstream code can reuse the narrow compare contract for any compatible
profile.

## Repository Touchpoints

- `server/adapters/mcp/vision/prompting.py`
- `tests/unit/adapters/mcp/test_vision_prompting.py`

## Acceptance Criteria

- prompt/schema selection is driven by contract profile and request kind
- narrow compare prompt/schema generation is reusable outside the
  Google-AI-Studio-only gate
- local-model prompt behavior is not regressed by the abstraction

## Leaf Work Items

- replace provider-only compare-contract helper gates
- add one explicit prompt/schema profile selection seam
- keep canonical expected-key helpers aligned with the selected profile

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
  contract seam is described at the slice level
