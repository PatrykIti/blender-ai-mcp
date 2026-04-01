# TASK-121-05-06-01: Router No-Match and Irrelevant Workflow Guard

**Parent:** [TASK-121-05-06](./TASK-121-05-06_Guided_Manual_Build_Handoff_After_Weak_Or_Irrelevant_Workflow_Match.md)  
**Status:** 🚧 In Progress  
**Priority:** 🔴 High

**Progress Update:** The router/handler layer now short-circuits obvious meta capture-build goals away from irrelevant workflow matches and into `no_match` + `build` handoff semantics. Unit and E2E-style regression coverage now exist for the squirrel progressive-screenshot case. The next gap is to generalize this beyond the first explicit meta-test pattern set without reintroducing weak workflow matches.

---

## Objective

Improve router behavior so guided sessions get `no_match` instead of a weak or
obviously irrelevant workflow path when the catalog is not a good fit.

---

## Implementation Direction

- add stronger guards against domain-mismatched workflow selection
- prefer `no_match` over `needs_input` for clearly wrong workflow families
- ensure that meta-test wording does not dominate the true build intent
- add regression coverage using goals that should not drift into unrelated
  workflows such as phone/screen cutout paths

---

## Repository Touchpoints

- `server/router/application/`
- `server/application/tool_handlers/router_handler.py`
- `tests/unit/router/`
- `tests/e2e/router/`

---

## Acceptance Criteria

- irrelevant workflow families are rejected more aggressively
- guided manual-build goals can cleanly get `status="no_match"` when that is
  the correct outcome
