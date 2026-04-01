# TASK-121-07-02: Manual Stage Checkpoint Capture Path

**Parent:** [TASK-121-07](./TASK-121-07_Vision_Guided_Iterative_Correction_Loop.md)  
**Status:** ✅ Done  
**Priority:** 🟡 Medium

Added a practical deterministic checkpoint capture path for staged/manual
guided builds without requiring a full workflow or macro bundle first.

Delivered surface:

- `reference_compare_stage_checkpoint(...)`

Behavior:

- captures one deterministic multi-view stage checkpoint for `target_object`
- uses the existing `compact` / `rich` preset profile system
- compares that stage checkpoint set against the active goal plus attached
  references
- returns bounded vision output together with the capture artifacts used for
  the comparison
