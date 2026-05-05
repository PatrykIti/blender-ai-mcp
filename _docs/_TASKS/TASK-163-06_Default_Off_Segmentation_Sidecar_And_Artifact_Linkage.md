# TASK-163-06: Default-Off Segmentation Sidecar And Artifact Linkage

**Status:** ⏳ To Do
**Priority:** 🔴 High
**Parent:** [TASK-163](./TASK-163_Vision_Orchestrator_Feedback_Strategy_Normalization_And_Optional_Perception_Adapters.md)
**Objective:** Add default-off RU segmentation artifact linkage without changing truth ownership or making the sidecar mandatory.
**Repository Touchpoints:** `server/adapters/mcp/vision/`, `server/adapters/mcp/contracts/reference.py`, `server/adapters/mcp/areas/reference_understanding.py`, `tests/unit/adapters/mcp/`, `tests/e2e/integration/`
**Acceptance Criteria:** missing sidecar stays non-fatal; segmentation artifacts remain advisory-only; no second public flow is introduced.

## Implementation Notes

- reuse the current sidecar philosophy already present on staged compare/iterate
- link artifact refs instead of embedding heavy blobs in normal payloads
- keep `part_segmentation` and `segmentation_artifacts` distinct: one is a
  staged compare payload, the other is RU-side support evidence
