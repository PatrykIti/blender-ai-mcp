# 167 - 2026-03-30: Reference checkpoint compare surface

**Status**: ✅ Completed  
**Type**: Vision Integration / Reference Surface  
**Task**: TASK-121-07-01

---

## Summary

Added the first bounded checkpoint-vs-reference comparison surface for staged
manual/reference-guided work.

New tools:

- `reference_compare_checkpoint(...)`
- `reference_compare_current_view(...)`

They compare one current checkpoint (existing image path or current
viewport/camera capture) against the active goal plus attached reference
images, then return bounded `vision_assistant` interpretation for the next
correction step.
