# TASK-092: Server-Side Sampling Assistants

**Priority:** 🟡 Medium  
**Category:** FastMCP LLM Reliability  
**Estimated Effort:** Medium  
**Dependencies:** TASK-083  
**Status:** ⬜ To Do

---

## Objective

Introduce controlled server-side LLM assistance for analysis, triage, and validation tasks that benefit from short internal reasoning loops.

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

