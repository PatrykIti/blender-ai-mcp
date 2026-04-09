# TASK-150-05-02: Public Docs, Troubleshooting, And Changelog Closeout

**Parent:** [TASK-150-05](./TASK-150-05_Regression_Pack_And_Docs_For_Server_Driven_Guided_Flows.md)
**Depends On:** [TASK-150-05-01](./TASK-150-05-01_Unit_And_Transport_Regression_Matrix_For_Flow_State_And_Gating.md)
**Status:** ✅ Done
**Priority:** 🔴 High

## Objective

Update public docs and troubleshooting guidance so the new server-driven guided
flow model is understandable to operators and future contributors.

## Repository Touchpoints

- `README.md`
- `_docs/_MCP_SERVER/README.md`
- `_docs/_PROMPTS/README.md`
- `_docs/_CHANGELOG/`
- `_docs/_TASKS/README.md`

## Planned File Work

- Modify:
  - `README.md`
  - `_docs/_MCP_SERVER/README.md`
  - `_docs/_PROMPTS/README.md`
  - `_docs/_TASKS/README.md`
- Create:
  - one `_docs/_CHANGELOG/*` entry for TASK-150

## Detailed Implementation Notes

- this closeout leaf should not invent new runtime semantics; it should only
  document the behavior shipped by earlier leaves
- troubleshooting should be written from the operator's point of view using
  `router_get_status()` and visible MCP behavior, not internal implementation
  names only

## Planned Docs/Test Shape

- README:
  - one high-level section on server-driven guided flows
  - one short section on domain overlays
- MCP server docs:
  - one machine-readable field summary for `guided_flow_state`
  - one troubleshooting subsection for blocked/hidden-by-step behavior
- Prompt docs:
  - explain how prompt bundles relate to the server-driven flow instead of
    replacing it
- Docs parity tests:
  - assert `guided_flow_state`
  - assert `domain_profile`
  - assert step-gating wording
  - assert required/preferred prompt bundle wording

## Acceptance Criteria

- docs explain:
  - what `guided_flow_state` is
  - how domain profiles work
  - how step gating affects visible tools
  - how prompt bundles relate to the flow
- troubleshooting guidance distinguishes:
  - goal unset
  - wrong domain profile
  - step not yet complete
  - hidden/blocked-by-flow tool family
- the task board and changelog are updated in the same branch

## Pseudocode Sketch

```text
Troubleshooting:
- If a needed tool is not visible:
  1. check router_get_status().guided_flow_state
  2. inspect current_step and required_checks
  3. complete the required step instead of guessing tool names
```

## Docs To Update

- `README.md`
- `_docs/_MCP_SERVER/README.md`
- `_docs/_PROMPTS/README.md`
- `_docs/_TASKS/README.md`

## Tests To Add/Update

- docs parity tests as needed

## Changelog Impact

- create the parent TASK-150 changelog entry here

## Completion Summary

- README, MCP docs, prompt docs, task tree, and changelog are now aligned with
  the shipped execution-enforcement model
