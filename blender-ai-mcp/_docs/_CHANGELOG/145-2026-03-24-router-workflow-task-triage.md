# 145 - 2026-03-24: Router/workflow task triage against new tool strategy

**Status**: ✅ Completed  
**Type**: Docs / Task Board Cleanup  
**Task**: TASK-113 follow-up

---

## Summary

Cleaned up the router/workflow task cluster in the board after introducing the new
tool-layering and goal-first strategy.

The goal of this cleanup is to stop old workflow/router tasks from being mistaken
for the new public MCP surface strategy.

---

## Changes

- removed `TASK-055-FIX-7` from active board sections and placed it in `Done`, matching its actual task-file status
- kept `TASK-058`, `TASK-054`, and `TASK-042` open
- added explicit alignment notes explaining that:
  - `TASK-058` is internal workflow DSL work
  - `TASK-054` is router internal observability/performance work
  - `TASK-042` is internal workflow-authoring/extraction work
- clarified that the public tool-surface strategy is now governed by `TASK-113`

---

## Files Modified (high level)

- `_docs/_TASKS/README.md`
- `_docs/_TASKS/TASK-058_Loop_System_String_Interpolation.md`
- `_docs/_TASKS/TASK-054_Ensemble_Matcher_Enhancements.md`
- `_docs/_TASKS/TASK-042_Automatic_Workflow_Extraction_System.md`
