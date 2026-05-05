# TASK-163-05: Default-Off CLIP Or SigLIP Classification Support

**Status:** ⏳ To Do
**Priority:** 🔴 High
**Parent:** [TASK-163](./TASK-163_Vision_Orchestrator_Feedback_Strategy_Normalization_And_Optional_Perception_Adapters.md)
**Objective:** Add default-off classifier support that can contribute `classification_scores` to RU without becoming a second authority.
**Repository Touchpoints:** `server/adapters/mcp/vision/`, `server/infrastructure/config.py`, `server/adapters/mcp/contracts/reference.py`, `tests/unit/adapters/mcp/`
**Acceptance Criteria:** classifier path stays optional, typed, and advisory-only; disabled/unavailable states do not break guided sessions.

## Implementation Notes

- do not silently download or enable heavy classifier runtimes
- keep classifier support evidence distinct from `TASK-157` verifier authority
- preserve the current RU and transport seams instead of inventing a new tool

## Tests To Add/Update

- config/default-off coverage
- unavailable-path coverage on RU payload projection
- harness fixtures for at least creature, hard-surface, and architectural classes
