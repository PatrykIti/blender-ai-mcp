# TASK-121-05-03: Guided Discovery, Prompts, and Docs for Utility Capture Flows

**Parent:** [TASK-121-05](./TASK-121-05_Guided_Utility_Capture_Prep_And_Goal_Boundary.md)  
**Status:** ⏳ To Do  
**Priority:** 🟡 Medium

---

## Objective

Align guided discovery, prompts, and docs so LLM clients know how to handle
utility/capture requests without abusing `router_set_goal(...)`.

---

## Business Problem

Even after router/visibility fixes, guided clients will still behave poorly if
the product guidance continues to imply that every request should start from
`router_set_goal(...)`.

The product needs a clear rule:

- build/workflow goals start from `router_set_goal(...)`
- utility/capture/scene-prep requests use the guided utility path instead

Without that distinction, the same bad behavior will keep reappearing in model
prompts, demos, and user sessions.

---

## Implementation Direction

- update guided prompts/instructions so utility capture requests are framed as
  utility actions, not build goals
- bias search/discovery toward the guided utility path for queries such as:
  - screenshot
  - viewport
  - capture image
  - clean scene
  - reset scene
- update docs/examples to show:
  - build-goal flow
  - utility-capture flow
  - mixed flow where a guided session prepares a scene, runs a workflow/macro,
    then captures before/after images

---

## Repository Touchpoints

- `README.md`
- `_docs/_MCP_SERVER/README.md`
- `_docs/_PROMPTS/README.md`
- `_docs/_PROMPTS/WORKFLOW_ROUTER_FIRST.md`
- `_docs/_VISION/README.md`
- `tests/unit/adapters/mcp/test_public_surface_docs.py`

---

## Acceptance Criteria

- guided product docs clearly distinguish build-goal flow from utility-capture
  flow
- prompts and discovery guidance stop nudging models toward `router_set_goal`
  for screenshot/reset requests
- examples exist for using guided mode to prepare vision test inputs
