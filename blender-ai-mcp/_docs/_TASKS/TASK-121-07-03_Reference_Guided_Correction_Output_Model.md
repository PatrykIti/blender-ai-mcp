# TASK-121-07-03: Reference-Guided Correction Output Model

**Parent:** [TASK-121-07](./TASK-121-07_Vision_Guided_Iterative_Correction_Loop.md)  
**Status:** ✅ Done  
**Priority:** 🔴 High

Specialized the checkpoint comparison output so shape/proportion mismatches and
bounded next corrections are directly useful for iterative creature/reference
work.

Delivered:

- added `correction_focus` as an ordered 1-3 item summary of the highest-value
  mismatch targets to fix next
- tightened prompt semantics for reference-guided checkpoint comparison modes
- parser now backfills `correction_focus` from existing mismatch/correction
  fields when the request is a reference-guided checkpoint compare
- parser now prunes clearly unhelpful unchanged-fact items from correction
  lists and bounds the correction-oriented lists to a small usable set
