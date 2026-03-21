# TASK-087-04-01: Core Session Persistence, Retry, and Cancel Semantics

**Parent:** [TASK-087-04](./TASK-087-04_Session_Persistence_Retry_and_Cancel_Semantics.md)  
**Status:** ⬜ Planned  
**Priority:** 🟡 Medium  
**Depends On:** [TASK-087-02](./TASK-087-02_Router_Parameter_Resolution_Integration.md)

---

## Objective

Implement the core code changes for **Session Persistence, Retry, and Cancel Semantics**.

---

## Repository Touchpoints

- `server/adapters/mcp/session_state.py`
- `server/adapters/mcp/context_utils.py`
- `server/adapters/mcp/areas/router.py`
- `server/application/tool_handlers/router_handler.py`
- `tests/unit/router/application/test_router_handler_parameters.py`
---

## Planned Work

- session state fields:
  - `pending_elicitation_id`
  - `pending_workflow_name`
  - `partial_answers`
  - `pending_question_set_id`
- helper logic for retry and cleanup
---

## Acceptance Criteria

- users can cancel or pause elicitation safely
- partial answers survive across the next interaction step when appropriate
---

## Atomic Work Items

1. Persist pending question-set identity and partial answers.
2. Implement retry, cancel, and cleanup transitions explicitly.
3. Add tests for cancel-and-resume and partial-answer retry flows.