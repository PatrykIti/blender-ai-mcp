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

