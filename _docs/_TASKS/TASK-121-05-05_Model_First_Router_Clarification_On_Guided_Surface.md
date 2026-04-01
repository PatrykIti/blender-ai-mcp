# TASK-121-05-05: Model-First Router Clarification on Guided Surface

**Parent:** [TASK-121-05](./TASK-121-05_Guided_Utility_Capture_Prep_And_Goal_Boundary.md)  
**Status:** ✅ Done  
**Priority:** 🔴 High

**Completion Summary:** `router_set_goal(...)` on `llm-guided` now keeps ordinary missing workflow parameters model-facing by default: the server builds a typed clarification payload and returns `needs_input` to the outer model without triggering native human elicitation first.

---

## Objective

Keep workflow parameter clarification model-facing by default on
`llm-guided`, instead of prompting the human operator first on every
`needs_input` workflow resolution step.

---

## Business Problem

Today `router_set_goal(...)` still tries native human elicitation for normal
missing workflow parameters on `llm-guided`. That creates an awkward guided
experience:

- the model starts a workflow
- the server asks the human directly
- only after cancel/escape does the typed clarification become visible to the
  outer LLM

This fights the intended agentic control loop. Earlier work already moved
`workflow_confirmation` into a model-facing path; the same principle needs to
extend to ordinary workflow parameter gaps unless there is a true user/business
decision that only the human can answer.

---

## Implementation Direction

- stop native human elicitation from being the default first step for normal
  `router_set_goal(...)` missing parameters on `llm-guided`
- return typed `needs_input` clarification to the model/orchestrator first
- reserve native human elicitation for actual last-resort cases or explicit
  product decisions
- keep `workflow_confirmation` model-facing as already established
- update docs/tests so the boundary is explicit

---

## Repository Touchpoints

- `server/adapters/mcp/areas/router.py`
- `server/adapters/mcp/session_capabilities.py`
- `tests/unit/adapters/mcp/test_router_elicitation.py`
- `tests/unit/adapters/mcp/test_session_phase.py`
- `_docs/_MCP_SERVER/README.md`
- `_docs/_PROMPTS/README.md`
- `_docs/_PROMPTS/WORKFLOW_ROUTER_FIRST.md`

---

## Acceptance Criteria

- `llm-guided` no longer prompts the human first for ordinary missing workflow
  parameters
- typed `needs_input` goes to the model/orchestrator first
- docs clearly describe human elicitation as a later/fallback path rather than
  the default workflow-resolution loop
