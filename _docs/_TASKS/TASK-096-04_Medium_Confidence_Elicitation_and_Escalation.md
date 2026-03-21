# TASK-096-04: Medium-Confidence Elicitation and Escalation

**Parent:** [TASK-096](./TASK-096_Confidence_Policy_for_Auto_Correction.md)  
**Status:** ⬜ Planned  
**Priority:** 🔴 High  
**Depends On:** [TASK-087-02](./TASK-087-02_Router_Parameter_Resolution_Integration.md), [TASK-096-03](./TASK-096-03_Auto_Fix_Ask_Block_Policy_Engine.md)

---

## Objective

Route medium-confidence interpretation paths into structured clarification instead of silent auto-rewrites.

---

## Layered Subtasks

| ID | Title | Focus |
|----|-------|-------|
| [TASK-096-04-01](./TASK-096-04-01_Core_Medium_Confidence_Elicitation_Escalation.md) | Core Medium-Confidence Elicitation and Escalation | Core implementation layer |
| [TASK-096-04-02](./TASK-096-04-02_Tests_Medium_Confidence_Elicitation_Escalation.md) | Tests and Docs Medium-Confidence Elicitation and Escalation | Tests, docs, and QA |

---

## Acceptance Criteria

- medium-confidence reinterpretation does not happen without an explicit clarification path
