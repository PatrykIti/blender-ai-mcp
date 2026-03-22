# TASK-087: Structured User Elicitation for Missing Parameters

**Priority:** 🔴 High  
**Category:** FastMCP Interaction UX  
**Estimated Effort:** Medium  
**Dependencies:** TASK-083  
**Status:** ⬜ To Do

---

## Objective

Turn missing-parameter handling into a first-class, structured interaction model instead of an ad hoc conversational fallback.

---

## Problem

In real Blender tasks, the model often lacks required decisions:

- exact dimensions
- style variant
- symmetry expectations
- poly budget
- material intent
- export target
- workflow modifier choices

If these are resolved only through improvised free-form conversation, the system becomes inconsistent across clients and models. The result is often loops, ambiguous replies, or missing values that arrive too late.

---

## Business Outcome

Make parameter resolution feel like part of the product:

- the server asks for missing information in a structured way
- the client can present that cleanly
- the model does not need to invent its own question format each time
- the router can depend on a more reliable missing-input workflow

This reduces friction and makes workflow-first usage significantly stronger.

---

## Proposed Solution

Adopt server-driven elicitation for missing values, clarifications, and constrained choices.

This should be especially useful for:

- router workflow parameters
- ambiguous build requests
- optional feature packs
- export settings
- style and budget selection

The system should treat elicitation as a standard interaction contract, not an exception path.

---

## Implementation Constraints

Follow [FASTMCP_3X_IMPLEMENTATION_MODEL.md](./FASTMCP_3X_IMPLEMENTATION_MODEL.md).

For this repo:

- native elicitation should live on async-capable LLM-guided surfaces
- legacy and tool-only surfaces must keep a typed `needs_input` fallback
- workflow context and partial answers must survive across the next interaction step
- elicitation must remain request-bound to an active MCP request (no out-of-band elicitation after request completion)

### Ownership Rule

For `router_set_goal` and similar missing-input flows:

- TASK-087 owns clarification semantics: question models, partial-answer persistence, native elicitation mapping, and the typed `needs_input` payload content
- TASK-089 owns the broader adapter-facing response envelopes, `outputSchema`, and execution-report contracts that carry those clarification payloads

Do not define a second, competing clarification-question schema in TASK-089.

---

## FastMCP Features To Use

- **User Elicitation** — **FastMCP 2.10.0**
- **Multi-select elicitation support via updated protocol adoption** — **FastMCP 2.14.0**

---

## Scope

This task covers:

- structured prompting for missing user inputs
- constrained choice collection
- better integration between router intent resolution and user clarification

This task does not cover:

- free-form product chat
- internal backend retries

---

## Why This Matters For Blender AI

This project is not only a tool executor. It is a guided build system.

When a user says “make a table,” the system often needs more than one unstated parameter to succeed well. A first-class elicitation layer makes that interaction more robust and easier to standardize across clients.

---

## Success Criteria

- Missing parameters are resolved through a structured server capability.
- Clients can present clarification requests consistently.
- Router and workflow usage become more reliable when the initial prompt is incomplete.
- The project reduces ambiguity-driven build failures and retry loops.

---

## Umbrella Execution Notes

This remains the umbrella task. The original scope stays unchanged.

### Atomic Delivery Waves

1. Define elicitation request and answer contracts derived from workflow parameter schemas.
2. Add an async-aware router entry path that can call `ctx.elicit(...)`.
3. Support constrained choice, booleans, and multi-select without free-form ambiguity.
4. Persist partial answers and cancellation state in session data.
5. Preserve a stable fallback payload for clients without elicitation support.
6. Add test coverage for both native elicitation and compatibility mode.

Implementation is decomposed into:

| Order | Subtask | Purpose |
|------|---------|---------|
| 1 | [TASK-087-01](./TASK-087-01_Elicitation_Domain_Model_and_Response_Contracts.md) | Define typed elicitation request and response contracts |
| 2 | [TASK-087-02](./TASK-087-02_Router_Parameter_Resolution_Integration.md) | Integrate `router_set_goal` with structured elicitation |
| 3 | [TASK-087-03](./TASK-087-03_Constrained_Choice_and_Multi_Select_Flows.md) | Support enums, booleans, and multi-select flows cleanly |
| 4 | [TASK-087-04](./TASK-087-04_Session_Persistence_Retry_and_Cancel_Semantics.md) | Preserve partial answers and cancellation semantics |
| 5 | [TASK-087-05](./TASK-087-05_Tool_Only_Fallback_and_Compatibility_Mode.md) | Provide a fallback for clients without elicitation support |
| 6 | [TASK-087-06](./TASK-087-06_Elicitation_Tests_and_Docs.md) | Add test coverage and docs for both interaction modes |
