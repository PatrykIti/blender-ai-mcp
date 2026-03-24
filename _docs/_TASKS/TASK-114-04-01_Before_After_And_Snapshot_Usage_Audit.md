# TASK-114-04-01: Before/After and Snapshot Usage Audit

**Parent:** [TASK-114-04](./TASK-114-04_Verification_And_Truth_Model_Audit.md)  
**Status:** ✅ Done  
**Priority:** 🔴 High

**Completion Summary:** The before/after verification pattern is already present in several high-signal places, but not yet expressed as a full platform-level operational habit in existing tool families.

---

## Objective

Audit where the current docs/tools already encourage before/after or snapshot usage, and where they still do not.

---

## Exact Audit Targets

- `scene_snapshot_state`
- `scene_compare_snapshot`
- `scene_get_viewport`
- `extraction_render_angles`
- prompt docs and examples

---

## Acceptance Criteria

- the repo has an explicit map of where before/after verification already exists vs where it is missing

## Audit Result

### Already Present

- prompt guidance in `_docs/_PROMPTS/MANUAL_TOOLS_NO_ROUTER.md`
- prompt guidance in `_docs/_PROMPTS/WORKFLOW_ROUTER_FIRST.md`
- tool surface:
  - `scene_snapshot_state`
  - `scene_compare_snapshot`
  - `scene_get_viewport`
  - `extraction_render_angles`
  - `system_snapshot`

### Still Missing

- explicit before/after hooks in many tool descriptions
- compact structured “visual verification step” guidance in more user-facing examples
- a direct bridge from before/after capture to deterministic assertions
