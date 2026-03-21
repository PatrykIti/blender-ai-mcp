# TASK-092: Server-Side Sampling Assistants

**Priority:** 🟡 Medium  
**Category:** FastMCP LLM Reliability  
**Estimated Effort:** Medium  
**Dependencies:** TASK-083, TASK-089, TASK-095  
**Status:** ⬜ To Do

---

## Objective

Introduce controlled, server-orchestrated, client-mediated LLM assistance for analysis, triage, and validation tasks that benefit from short internal reasoning loops.

---

## Problem

Not every decision should be pushed back to the client LLM as another outer-loop turn.

Some parts of the system would benefit from small, controlled internal reasoning helpers, for example:

- deciding which subset of tools is relevant
- summarizing inspection results
- turning large raw diagnostics into compact next-step guidance
- evaluating whether a workflow result matches an expected pattern
- generating structured repair suggestions after a failed step

Without this, the outer client model bears all orchestration cost and context burden.

---

## Business Outcome

Give the server the ability to run bounded, product-specific reasoning helpers where that improves overall reliability and reduces outer-loop friction.

This should help the system become more assistive without making the client experience heavier.

---

## Proposed Solution

Use FastMCP sampling capabilities for tightly scoped internal assistants, especially where:

- the task is analytical rather than directly geometry-destructive
- the result can be structured and validated
- the server can bound the scope clearly

These helpers should complement the router, not replace it.

---

## Implementation Constraints

Follow [FASTMCP_3X_IMPLEMENTATION_MODEL.md](./FASTMCP_3X_IMPLEMENTATION_MODEL.md).

Terminology note for this repo:

- the server orchestrates sampling
- the client still owns the model call
- sampling remains request-bound and capability-dependent

Do not design this task as autonomous background reasoning detached from an active MCP request.

---

## FastMCP Features To Use

- **Sampling with tools** — **FastMCP 2.14.1**
- **`sample_step()` for controlled loops** — **FastMCP 2.14.1**
- **Structured output via `result_type`** — **FastMCP 2.14.1**

---

## Scope

This task covers:

- bounded internal reasoning helpers
- structured analytical assistants
- server-side summarization and validation flows

This task does not cover:

- unrestricted autonomous modeling
- replacing the main router with a free-form agent

---

## Why This Matters For Blender AI

This project has reached the point where not all intelligence should sit in the client prompt.

Some intelligence belongs in the server because it is:

- repeatable
- product-specific
- easier to constrain
- easier to validate

That is where sampling-based assistants can create value.

---

## Success Criteria

- The server can host bounded reasoning helpers for high-value analytical tasks.
- Internal assistants return structured, dependable outputs.
- Outer client loops become lighter where server-local reasoning is a better fit.
- The project gains a path to smarter validation and recovery without fully agentic sprawl.

---

## Umbrella Execution Notes

This remains the umbrella task. The original scope stays unchanged.

### Atomic Delivery Waves

1. Define hard boundaries for where sampling assistants are allowed.
2. Build a typed assistant runner with explicit fallback behavior when sampling is unavailable.
3. Add a very small first set of analytical assistants.
4. Integrate them with router and inspection flows under budget and masking rules.
5. Add tests and docs focused on bounded behavior, not agentic expansion.

Implementation is decomposed into:

| Order | Subtask | Purpose |
|------|---------|---------|
| 1 | [TASK-092-01](./TASK-092-01_Sampling_Assistant_Governance_and_Safety_Boundaries.md) | Define where sampling assistants are allowed and where they are not |
| 2 | [TASK-092-02](./TASK-092-02_Assistant_Runner_with_Typed_Result_Wrappers.md) | Build the bounded assistant runner with typed outputs |
| 3 | [TASK-092-03](./TASK-092-03_Inspection_Summarizer_and_Repair_Suggester_Assistants.md) | Add the first analytical assistants |
| 4 | [TASK-092-04](./TASK-092-04_Router_Integration_Masking_and_Budget_Control.md) | Integrate assistants with router flows and budgets |
| 5 | [TASK-092-05](./TASK-092-05_Sampling_Assistant_Tests_and_Documentation.md) | Add tests and documentation for assistant usage |
