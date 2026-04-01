# TASK-121-03-02: Macro/Workflow Vision Integration Path

**Parent:** [TASK-121-03](./TASK-121-03_Before_After_Capture_And_Macro_Integration.md)  
**Status:** ✅ Done  
**Priority:** 🔴 High

**Progress Update:** Macro MCP adapters now have the first request-bound vision attachment path: when a macro report carries a capture bundle, the adapter builds a `VisionRequest`, includes goal-scoped reference images from session state, filters them toward the current target object before attaching them, and attaches the resulting `vision_assistant` envelope back onto the macro report. The path now also passes the macro's existing deterministic verification tools into the vision prompt hint and folds vision-driven follow-up checks/mismatch signals back into `verification_recommended` plus `requires_followup`, so the report remains correction-oriented instead of ending at a detached summary blob.

---

## Objective

Integrate vision assistance into macro/workflow paths rather than exposing it as
an isolated free-floating tool first.

---

## Implementation Direction

- attach vision assistance to bounded macro/workflow reports using:
  - active goal
  - reference images
  - capture bundles
  - optional inspect/measure/assert summaries
- do not call vision first on arbitrary viewport images; integrate it after deterministic capture-bundle creation
- vision output should recommend deterministic next checks where needed
- keep request-bound execution; do not turn vision into a background authority

---

## Repository Touchpoints

- macro/report contracts from `TASK-120`
- `server/adapters/mcp/sampling/`
- `server/adapters/mcp/contracts/`
- `tests/unit/adapters/mcp/`
- `tests/e2e/`

---

## Acceptance Criteria

- macro/workflow reports can carry bounded visual interpretation
- deterministic follow-up checks remain the preferred way to confirm correctness
- macro/workflow integrations use stable before/after comparisons rather than one-shot image guessing
