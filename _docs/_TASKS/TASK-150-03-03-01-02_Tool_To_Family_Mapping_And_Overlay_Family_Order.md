# TASK-150-03-03-01-02: Tool-To-Family Mapping And Overlay Family Order

**Parent:** [TASK-150-03-03-01](./TASK-150-03-03-01_Shared_Tool_Family_Vocabulary_And_Overlay_Mapping.md)
**Depends On:** [TASK-150-03-03-01-01](./TASK-150-03-03-01-01_Guided_Family_Literals_And_Flow_Contract_Extension.md)
**Status:** ⏳ To Do
**Priority:** 🔴 High

## Objective

Map existing tools/macros onto shared families and define per-overlay family
order without creating domain-specific tool families.

## Repository Touchpoints

- `server/adapters/mcp/session_capabilities.py`
- `server/adapters/mcp/transforms/visibility_policy.py`

## Current Code Anchors

- `session_capabilities.py` lines 252-314: current flow initialization
- `visibility_policy.py` lines 452-499: current build visibility shaping

## Planned Code Shape

```python
TOOL_FAMILY_MAP = {"modeling_create_primitive": "primary_masses", ...}
OVERLAY_FAMILY_ORDER = {"creature": (...), "building": (...)}
STEP_ALLOWED_FAMILIES = {("creature", "create_primary_masses"): ("primary_masses",)}
```

## Acceptance Criteria

- the repo has one deterministic tool-to-family map
- each overlay can define family order and allowed family windows

## Planned Unit Test Scenarios

- `macro_finish_form` resolves to `finish`
- `reference_iterate_stage_checkpoint` resolves to `checkpoint_iterate`
- `creature` and `building` overlays produce different allowed family windows
  for the same coarse build phase

## Planned E2E / Transport Scenarios

- guided creature session:
  - status payload shows `primary_masses` family active after spatial checks
- guided building session:
  - same coarse build phase but different family order / unlock sequence

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_visibility_policy.py`
- `tests/unit/adapters/mcp/test_guided_mode.py`
