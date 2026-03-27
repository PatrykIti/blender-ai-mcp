# TASK-121-05-01: Router Utility Goal Boundary and Workflow Trigger Hygiene

**Parent:** [TASK-121-05](./TASK-121-05_Guided_Utility_Capture_Prep_And_Goal_Boundary.md)  
**Status:** 🚧 In Progress  
**Priority:** 🔴 High

**Progress Update:** A first pass of this fix is implemented. `RouterToolHandler.set_goal(...)` now short-circuits obvious utility/capture requests into `status="no_match"` instead of letting them fall into unrelated build workflows, the workflow registry no longer uses raw substring matching for trigger keywords, and `screen_cutout_workflow` trigger keywords have been narrowed away from broad one-word hits such as `screen`/`display`. The remaining work is to decide whether utility-goal classification should stay in the handler only or also become a deeper router/ensemble concept.

---

## Objective

Ensure `router_set_goal(...)` distinguishes utility/capture requests from
actual build/workflow goals before the router commits to a workflow match.

---

## Business Problem

The current router path can treat requests like:

- `"capture viewport screenshot save to file"`
- `"take a viewport image"`
- `"clean the scene and save a screenshot"`

as if they were workflow build goals. This is especially dangerous when a
single loose keyword, such as `screen`, can trigger a workflow like
`screen_cutout_workflow`.

That creates:

- false-positive workflow matches
- `needs_input` loops for irrelevant modeling parameters
- guided sessions that feel broken even though the user asked for a simple
  utility action

---

## Implementation Direction

- add a utility/capture-goal guard before ensemble workflow commitment in the
  router goal path
- treat intents like screenshot/viewport/capture/clean/reset as:
  - `no_match`, or
  - an explicit utility disposition that does **not** create `pending_workflow`
- tighten workflow keyword matching so one generic token does not count as an
  exact workflow hit
- narrow overly broad workflow trigger keywords where necessary, especially for
  workflows like `screen_cutout_workflow`

---

## Repository Touchpoints

- `server/router/application/router.py`
- `server/router/application/matcher/ensemble_matcher.py`
- `server/router/application/matcher/ensemble_aggregator.py`
- `server/router/application/workflows/registry.py`
- `server/router/application/workflows/custom/screen_cutout.yaml`
- `tests/unit/router/`
- `tests/unit/adapters/mcp/`

---

## Acceptance Criteria

- screenshot/viewport/scene-reset goals do not resolve to unrelated modeling
  workflows
- a utility/capture request leaves the router in a sane non-workflow state
- broad one-token workflow triggers are no longer enough to create these false
  positives
