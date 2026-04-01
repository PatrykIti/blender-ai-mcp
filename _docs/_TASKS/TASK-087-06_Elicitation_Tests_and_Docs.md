# TASK-087-06: Elicitation Tests and Docs

**Parent:** [TASK-087](./TASK-087_Structured_User_Elicitation.md)  
**Status:** ✅ Done  
**Priority:** 🟡 Medium  
**Depends On:** [TASK-087-03](./TASK-087-03_Constrained_Choice_and_Multi_Select_Flows.md), [TASK-087-04](./TASK-087-04_Session_Persistence_Retry_and_Cancel_Semantics.md), [TASK-087-05](./TASK-087-05_Tool_Only_Fallback_and_Compatibility_Mode.md)

---

## Objective

Add test coverage and documentation for both native elicitation mode and tool-only fallback mode.

---

## Planned Work

### Regression Scenarios (Required)

1. native elicitation happy path resolves missing workflow parameters and continues execution.
2. accept/decline/cancel responses are persisted and replayed correctly across retries.
3. tool-only fallback path returns typed `needs_input` contracts with equivalent decision semantics.
4. mixed-client regression path shows no divergence between native and fallback behavior under identical inputs.

### Metrics To Capture

- elicitation contract schema pass rate
- fallback/native parity mismatch count (target: 0)
- average rounds-to-resolution for unresolved parameter sets

### Documentation Deliverables

- update `_docs/_MCP_SERVER/README.md` with interaction-mode matrix and examples
- update `_docs/_PROMPTS/README.md` with elicitation-aware prompting recommendations
- update `README.md` with high-level clarification flow and compatibility notes

---

## Layered Subtasks

| ID | Title | Focus |
|----|-------|-------|
| [TASK-087-06-01](./TASK-087-06-01_Core_Elicitation_Tests_Docs.md) | Core Elicitation Tests and Docs | Core implementation layer |
| [TASK-087-06-02](./TASK-087-06-02_Tests_Elicitation_Tests_Docs.md) | Tests and Docs Elicitation Tests and Docs | Tests, docs, and QA |

---

## Acceptance Criteria

- all required elicitation regression scenarios are implemented and passing
- metrics are captured with baseline vs post-change values and linked in task notes
- native and fallback modes are both documented with explicit expected behavior
- no undocumented divergence remains between tested and documented interaction flows
