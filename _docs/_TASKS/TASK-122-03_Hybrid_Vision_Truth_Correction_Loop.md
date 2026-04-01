# TASK-122-03: Hybrid Vision + Truth Correction Loop

**Parent:** [TASK-122](./TASK-122_Hybrid_Vision_Truth_And_Correction_Macro_Wave.md)  
**Status:** ⏳ To Do  
**Priority:** 🔴 High

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

## Success Criteria

- one loop contract can carry both vision and truth findings
- loop disposition can depend on both visual and geometric evidence
- the loop can hand off into bounded correction macros rather than raw atomics

## Execution Structure

| Order | Leaf | Purpose |
|------|------|---------|
| 1 | [TASK-122-03-01](./TASK-122-03-01_Correction_Candidate_Contract_And_Priority_Model.md) | Define one merged correction-candidate contract and priority model |
| 2 | [TASK-122-03-02](./TASK-122-03-02_Reference_Iterate_Stage_Checkpoint_Truth_Bundle_Integration.md) | Feed truth bundles into `reference_iterate_stage_checkpoint(...)` |
| 3 | [TASK-122-03-03](./TASK-122-03-03_Loop_Disposition_From_Vision_And_Truth_Signal.md) | Recompute `loop_disposition` from both visual and geometric evidence |
| 4 | [TASK-122-03-04](./TASK-122-03-04_Real_Assembled_Creature_Eval_And_Prompting.md) | Validate the hybrid loop on real multi-part creature scenarios and prompts |
