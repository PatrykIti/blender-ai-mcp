# TASK-121-08: Session-Aware Reference Correction Auto Loop

**Parent:** [TASK-121](./TASK-121_Goal_Aware_Vision_Assist_And_Reference_Context.md)  
**Status:** ✅ Done  
**Priority:** 🔴 High

Added the first session-aware reference correction auto loop for staged manual
work.

Delivered:

- public bounded tool:
  - `reference_iterate_stage_checkpoint(...)`
- behavior:
  - captures deterministic stage views
  - compares them against the active references
  - persists the previous correction focus in session state
  - returns `loop_disposition`:
    - `continue_build`
    - `inspect_validate`
    - `stop`
  - escalates to `inspect_validate` when the same correction focus repeats
    across multiple stage iterations

Why this matters:

- the model no longer has to manually compare the new correction hints against
  the previous iteration
- the loop is still bounded and request-driven, but it now behaves like a
  practical auto loop controller instead of a stateless compare endpoint
