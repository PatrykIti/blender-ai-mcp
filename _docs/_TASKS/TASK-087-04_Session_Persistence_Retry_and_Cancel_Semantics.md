# TASK-087-04: Session Persistence, Retry, and Cancel Semantics

**Parent:** [TASK-087](./TASK-087_Structured_User_Elicitation.md)  
**Status:** ⬜ Planned  
**Priority:** 🟡 Medium  
**Depends On:** [TASK-087-02](./TASK-087-02_Router_Parameter_Resolution_Integration.md)

---

## Objective

Handle partial answers, re-prompting, and cancellation without losing workflow context or corrupting router session state.

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
