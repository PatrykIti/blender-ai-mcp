# TASK-121-05-06-02: Explicit Manual Guided Build Handoff

**Parent:** [TASK-121-05-06](./TASK-121-05-06_Guided_Manual_Build_Handoff_After_Weak_Or_Irrelevant_Workflow_Match.md)  
**Status:** ✅ Done  
**Priority:** 🔴 High

---

**Completion Summary:** `router_set_goal()` now returns an explicit typed `guided_handoff`
contract on guided manual-build continuation paths, the session persists that
handoff for `router_get_status()`, and the payload names the intended phase plus
the first-choice direct/discovery tools on `llm-guided`.

## Objective

Give `llm-guided` an explicit, intended path for continuing manual guided
modeling after a workflow `no_match` or rejected workflow path.

---

## Implementation Direction

- define how guided sessions enter the curated build layer without relying on
  a successful workflow match
- avoid pushing the model toward workflow import/create unless the user
  explicitly wants that
- keep the handoff bounded and aligned with current guided visibility rules

Possible delivery shapes:

- one explicit router/session action for guided manual continuation
- or one clearer session-phase transition contract after `no_match`

---

## Repository Touchpoints

- `server/adapters/mcp/areas/router.py`
- `server/adapters/mcp/session_capabilities.py`
- `server/adapters/mcp/transforms/visibility_policy.py`
- `tests/unit/adapters/mcp/`
- `tests/e2e/router/`

---

## Acceptance Criteria

- the model can continue guided modeling after `no_match` without guessing or
  over-searching blindly
- manual guided continuation is an explicit product path, not an accidental side effect
