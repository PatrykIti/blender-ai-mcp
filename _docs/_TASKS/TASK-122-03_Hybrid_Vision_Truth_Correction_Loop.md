# TASK-122-03: Hybrid Vision + Truth Correction Loop

**Parent:** [TASK-122](./TASK-122_Hybrid_Vision_Truth_And_Correction_Macro_Wave.md)  
**Status:** 🚧 In Progress  
**Priority:** 🔴 High

**Progress Update:** The first two hybrid-loop leaves are now complete. Stage compare / iterate responses expose a ranked `correction_candidates` list that preserves source boundaries between vision evidence, truth evidence, and bounded macro options, and `reference_iterate_stage_checkpoint(...)` now derives loop-facing `correction_focus` from those ranked candidates when available. The subtree remains open while disposition policy and real eval work land on top of that integration.

## Objective

Merge:

- visual mismatch interpretation
- truth/spatial correction bundles
- bounded correction macros

into one practical correction loop for assembled models.

## Business Problem

Today the repo can:

- compare current state to references
- remember prior correction focus
- stop or continue based on repeated vision findings

But it still cannot fully say:

- this part visually looks wrong
- and here is the deterministic proof that it floats/intersects/misaligns
- and here is the bounded macro that should fix it next

## Acceptance Criteria

- one loop contract can carry both vision and truth findings
- loop disposition can depend on both visual and geometric evidence
- the loop can hand off into bounded correction macros rather than raw atomics

## Repository Touchpoints

- `server/adapters/mcp/areas/reference.py`
- `server/adapters/mcp/contracts/vision.py`
- `server/adapters/mcp/contracts/router.py`
- `server/adapters/mcp/vision/`
- `server/adapters/mcp/session_capabilities.py`
- `tests/unit/adapters/mcp/`
- `tests/e2e/vision/`
- `_docs/_VISION/README.md`
- `_docs/_MCP_SERVER/README.md`

## Completion Update Requirements

- update loop-contract and vision/truth-boundary docs in `_docs/` when a leaf here ships
- add or update focused unit coverage for loop disposition, correction-candidate ranking, and truth-bundle handoff
- add or update E2E/reference-driven evaluation coverage when runtime loop behavior changes
- add the historical `_docs/_CHANGELOG/*` entry and sync the task board when this subtree changes promoted state

## Execution Structure

| Order | Leaf | Purpose |
|------|------|---------|
| 1 | [TASK-122-03-01](./TASK-122-03-01_Correction_Candidate_Contract_And_Priority_Model.md) | Define one merged correction-candidate contract and priority model |
| 2 | [TASK-122-03-02](./TASK-122-03-02_Reference_Iterate_Stage_Checkpoint_Truth_Bundle_Integration.md) | Feed truth bundles into `reference_iterate_stage_checkpoint(...)` |
| 3 | [TASK-122-03-03](./TASK-122-03-03_Loop_Disposition_From_Vision_And_Truth_Signal.md) | Recompute `loop_disposition` from both visual and geometric evidence |
| 4 | [TASK-122-03-04](./TASK-122-03-04_Real_Assembled_Creature_Eval_And_Prompting.md) | Validate the hybrid loop on real multi-part creature scenarios and prompts |
