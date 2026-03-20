# TASK-089: Typed Contracts and Structured Responses

**Priority:** 🔴 High  
**Category:** FastMCP LLM Reliability  
**Estimated Effort:** Large  
**Dependencies:** TASK-083  
**Status:** ⬜ To Do

---

## Objective

Move critical server responses from prose-heavy outputs toward explicit, typed, machine-readable contracts that are easier for LLMs to consume reliably.

---

## Problem

The project already has many strong inspection and context tools, but if their outputs are too string-oriented, the model has to parse human-oriented prose while also reasoning about geometry and workflow state.

That increases the chance of:

- partial parsing
- missed values
- inconsistent follow-up logic
- silent misinterpretation of scene state
- errors in spatial reasoning and validation

This is one of the core reasons an LLM can be “almost correct” but still drift.

---

## Business Outcome

Make server outputs easier to trust, automate against, and reuse in downstream reasoning.

Typed contracts should especially improve:

- context checks
- inspection flows
- validation steps
- repair and retry behavior
- workflow state handling

---

## Proposed Solution

Adopt structured response design as a product principle for critical tools and internal reasoning helpers.

The desired behavior is:

- important inspection tools return structured, stable payloads
- the LLM no longer depends on brittle text parsing for key state
- internal server-side reasoning helpers can also use validated structured output when sampling is involved

This should begin with high-value context and inspection surfaces and then expand outward.

---

## FastMCP Features To Use

- **Tool output schemas / structured content support in the current FastMCP server tools surface** — **3.x baseline**
- **Structured output via `result_type` for server-side sampling** — **FastMCP 2.14.1**

---

## Scope

This task covers:

- structured response contracts for critical tools
- machine-readable state exchange
- reduction of prose parsing in important decision points

This task does not cover:

- adding new geometry operations
- introducing Code Mode or tool discovery by itself

---

## Why This Matters For Blender AI

Blender work is state-heavy and spatially sensitive.

If the model misunderstands:

- mode
- selection
- object bounds
- origin
- topology state
- workflow resolution state

then the next action may be logically consistent but still wrong in practice.

Structured response contracts reduce that gap.

---

## Success Criteria

- Critical server outputs become easier for LLMs to consume deterministically.
- Inspection and validation flows rely less on natural-language parsing.
- The project gains a cleaner foundation for spatial assertions and automated QA.
- The model’s follow-up decisions improve because the state contract is clearer.

