# 140 - 2026-03-23: Programmatic sculpt replacement policy

**Status**: ✅ Completed  
**Type**: Task Planning / Product Direction  
**Task**: TASK-112

---

## Summary

Updated the sculpt planning track so the repo no longer carries a compatibility
story for non-deterministic brush tools that are not suitable for LLM
automation.

The direction is now explicit:

- keep `sculpt_auto`
- add deterministic programmatic sculpt-region tools
- replace brush-dependent sculpt tools where needed instead of preserving them as a long-term compatibility path

---

## Changes

- rewrote the TASK-112 umbrella to use a replacement posture instead of a compatibility posture
- updated the deform/grab replacement subtask accordingly
- replaced the old compatibility-boundary subtask with a replacement-boundary subtask
- updated the task board summary note

---

## Files Modified (high level)

- `_docs/_TASKS/TASK-112_Programmatic_Sculpt_Region_Tools.md`
- `_docs/_TASKS/TASK-112-02_Programmatic_Deform_And_Grab_Replacement.md`
- `_docs/_TASKS/TASK-112-04_Surface_Metadata_Docs_And_Replacement_Boundary.md`
- `_docs/_TASKS/README.md`
