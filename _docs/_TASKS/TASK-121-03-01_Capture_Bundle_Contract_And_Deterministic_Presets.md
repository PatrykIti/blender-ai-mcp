# TASK-121-03-01: Capture Bundle Contract and Deterministic Presets

**Parent:** [TASK-121-03](./TASK-121-03_Before_After_Capture_And_Macro_Integration.md)  
**Status:** ⏳ To Do  
**Priority:** 🔴 High

---

## Objective

Define one deterministic capture bundle format for before/after visual comparison.

---

## Implementation Direction

- define capture bundle fields such as:
  - `bundle_id`
  - `goal_id`
  - `captures_before`
  - `captures_after`
  - `target_object`
  - `preset_names`
  - `truth_summary`
- define deterministic viewport presets, for example:
  - isometric
  - front
  - side
  - focus-target
- keep a deliberate view mix instead of one generic screenshot:
  - at least one wider framing view
  - at least one target-object-focused view/crop
  - optional overlay/mask variants if later evaluation needs them
- keep rendering/capture parameters stable:
  - fixed shading mode
  - fixed framing policy
  - no UI clutter
  - no random orbit noise
- keep capture presets reproducible enough for later visual evaluation/goldens

---

## Repository Touchpoints

- `server/adapters/mcp/contracts/`
- `server/adapters/mcp/areas/scene.py`
- `tests/unit/tools/scene/`
- `tests/e2e/tools/scene/`

---

## Acceptance Criteria

- before/after capture packaging is stable and reusable
- later vision/evaluation work can rely on deterministic capture presets
- capture bundles give the vision layer enough structured evidence to compare change, not just describe a single viewport
