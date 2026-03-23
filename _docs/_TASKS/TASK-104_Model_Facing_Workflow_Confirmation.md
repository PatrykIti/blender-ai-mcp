# TASK-104: Model-Facing Workflow Confirmation Boundary

**Priority:** 🟡 Medium  
**Category:** Router / LLM UX  
**Estimated Effort:** Small  
**Dependencies:** TASK-087, TASK-096  
**Status:** ✅ Done

**Completion Summary:** `workflow_confirmation` no longer triggers native human elicitation on `llm-guided`. Medium-confidence workflow-choice clarification now stays model-facing: the outer LLM receives a typed `needs_input` response and can answer with a follow-up `router_set_goal(..., resolved_params={"workflow_confirmation": ...})`. Human elicitation remains reserved for user-intent gaps and true missing business inputs.

---

## Objective

Keep workflow-choice ambiguity in the model/orchestration loop instead of escalating it directly to the human operator.

---

## Problem

`workflow_confirmation` is not a natural user-facing business question.
It is an execution-path confirmation about which workflow the router should use.

When native elicitation asked the human to confirm it directly, the product blurred two responsibilities:

- human intent selection
- model-side workflow/orchestration choice

This created a weaker UX for agentic clients and made the human arbitrate technical workflow selection that the outer LLM is better positioned to handle.

---

## Solution

Treat `workflow_confirmation` as model-facing clarification:

- do **not** trigger native `ctx.elicit(...)` for that field
- return typed `needs_input` to the outer LLM instead
- let the outer LLM answer through a follow-up `router_set_goal(..., resolved_params=...)`

Human/native elicitation remains available for actual missing user/business inputs.

---

## Repository Touchpoints

- `server/adapters/mcp/areas/router.py`
- `server/application/tool_handlers/router_handler.py`
- `tests/unit/adapters/mcp/test_router_elicitation.py`
- `tests/unit/router/application/test_router_handler_parameters.py`
- `README.md`

---

## Acceptance Criteria

- `workflow_confirmation` does not trigger native human elicitation on `llm-guided`
- valid workflow confirmations are consumed on follow-up without looping
- invalid workflow confirmations stay in typed clarification
- docs explain the boundary between human-facing clarification and model-facing workflow selection
