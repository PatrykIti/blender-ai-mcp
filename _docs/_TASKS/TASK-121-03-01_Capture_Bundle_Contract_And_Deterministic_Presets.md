# TASK-121-03-01: Capture Bundle Contract and Deterministic Presets

**Parent:** [TASK-121-03](./TASK-121-03_Before_After_Capture_And_Macro_Integration.md)  
**Status:** 🚧 In Progress  
**Priority:** 🔴 High

**Progress Update:** The repo now has a first deterministic capture-bundle scaffold with current runtime presets (`context_wide`, `target_focus`, `target_oblique`) and a documented path toward a richer multi-view bundle assembled from existing scene camera/viewport atomics without leaving persistent helper cameras in the scene.

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
- prefer first implementation as a bounded internal orchestration path around
  macro/workflow execution rather than a broad free-floating public tool that
  has to invent both "before" and "after" in isolation
- add internal save/restore helpers for view and visibility state if current
  scene atomics are not enough to keep capture side effects bounded
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
