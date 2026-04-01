# TASK-121-06-03: Utility Tool Router Bypass for Guided Sessions

**Parent:** [TASK-121-06](./TASK-121-06_Guided_Goal_Recovery_And_Reference_Semantics.md)  
**Status:** ✅ Done  
**Priority:** 🔴 High

Public `scene_*` helper tools now bypass router workflow triggering on direct
user calls, so cleanup/viewport/inspection/visibility actions do not execute an
unrelated pending workflow.
