# TASK-171-02: Active Workset Expansion And Secondary Compare Precedence

**Parent:** [TASK-171](./TASK-171_Creature_Attachment_First_Build_Contract_And_Structured_Vision_Handoff.md)
**Status:** ⏳ To Do
**Priority:** 🔴 High
**Objective:** Ensure `guided_register_part(...)` widens the active workset soon enough for omitted-target compare/iterate to see the new part, and let registered secondary-part blocker/focus evidence outrank broad primary-mass compare earlier during `place_secondary_parts`.
**Repository Touchpoints:** `server/adapters/mcp/session_capabilities_registry.py`, `server/adapters/mcp/session_capabilities_flow.py`, `server/adapters/mcp/areas/reference.py`, `tests/unit/adapters/mcp/test_guided_flow_state_contract.py`, `tests/unit/adapters/mcp/test_reference_images.py`, `tests/e2e/vision/test_reference_guided_squirrel_quality_regression.py`
**Acceptance Criteria:**
- registering a new guided part can widen or rebind the active workset without waiting for an unrelated later manual state patch
- omitted-target compare/iterate can include newly registered parts in the same loop when they belong to the active creature workset
- broad-first creature compare still protects unresolved body/head/tail form, but registered non-detail secondary focus can override it sooner than today

## Implementation Notes

- today the registry and role summary update, but `active_target_scope` does
  not
- the current spatial refresh completion path also refuses to bind a wider scope
  once `active_target_scope` already exists
- omitted-target compare scope then resolves role/blocker/focus/last-mutation
  candidates only through the stale active-scope name set
- keep the existing broad-first rule for truly early creature silhouette work,
  but stop using it as a blanket override once:
  - a registered non-detail secondary part already exists
  - a blocker cluster targets that registered secondary part
  - a focus pair or last mutation points to that registered secondary part
- treat `ear_pair` and `eye_pair` differently from `snout_mass`,
  `foreleg_pair`, and `hindleg_pair` where needed; local-detail suppression
  should not become a forever-broad policy

## Pseudocode

```python
state = register_guided_part(...)
state.guided_flow_state.active_target_scope = merge_registered_object_into_scope(
    state.guided_flow_state.active_target_scope,
    object_name,
)

scope = resolve_active_compare_scope(...)
if current_step == "place_secondary_parts" and registered_secondary_focus_exists(scope, gate_plan, loop_state):
    scope = prefer_registered_secondary_focus(scope)
elif coarse_primary_form_still_unresolved(scope, gate_plan):
    scope = primary_mass_workset(scope)
```

## Runtime / Security Contract Notes

- scope widening must stay bounded to the current active creature workset; do
  not let arbitrary unrelated objects leak into the guided compare scope
- if the low-level pure state helper remains intentionally scene-agnostic,
  document where validated object-name expansion must happen on the public async
  path
- preserve spatial refresh/fingerprint safety; widening scope must not silently
  mark stale checks as completed for a different object set

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_guided_flow_state_contract.py`
- `tests/unit/adapters/mcp/test_reference_images.py`
- `tests/e2e/vision/test_reference_guided_squirrel_quality_regression.py`

## Docs To Update

- `_docs/_PROMPTS/REFERENCE_GUIDED_CREATURE_BUILD.md`
- `_docs/_MCP_SERVER/README.md`

## Changelog Impact

- add/update the historical `_docs/_CHANGELOG/*` entry when this slice lands

## Validation Commands

- `git diff --check`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_guided_flow_state_contract.py -q`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_reference_images.py -q`
- `PYTHONPATH=. poetry run pytest tests/e2e/vision/test_reference_guided_squirrel_quality_regression.py -q`

## Validation Category

- guided scope binding and compare-precedence proof
