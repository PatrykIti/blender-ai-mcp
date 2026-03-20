# TASK-085: Session-Adaptive Tool Visibility

**Priority:** 🔴 High  
**Category:** FastMCP Tool UX  
**Estimated Effort:** Medium  
**Dependencies:** TASK-083  
**Status:** ⬜ To Do

---

## Objective

Adapt the visible tool surface dynamically to the current session, user intent, workflow phase, and Blender operation context.

---

## Problem

Today, one client session effectively sees one server shape.

That is a poor fit for Blender AI work, because the ideal tool surface changes across phases:

- onboarding and planning
- workflow selection
- object creation
- mesh editing
- inspection and validation
- export and handoff
- recovery after a failed step

Showing the same capability set at every stage increases noise and makes the model more likely to call the wrong category of tool.

---

## Business Outcome

Turn the MCP server into an adaptive product surface where the visible capabilities change with the job being done.

This should let the server feel smaller and more guided without actually becoming less powerful.

---

## Proposed Solution

Use session-level state and session-level visibility control to expose different capability subsets over time.

Examples of desired business behavior:

- early session: show router, prompts, help, status, workflow search
- active build phase: show only the relevant build and inspect surfaces
- repair phase: elevate validation, diff, snapshot, and recovery tools
- export phase: hide low-level modeling tools and show packaging/output tools

This should work as a dynamic product behavior, not as a static documentation recommendation.

---

## FastMCP Features To Use

- **Session-Scoped State** — **FastMCP 3.0.0**
- **Per-session component visibility control** — **FastMCP 3.0.0**
- **Tag-based component filtering / component control lineage** — **FastMCP 2.8.0**, carried into **3.x transform-based visibility**

---

## Scope

This task covers:

- session-aware exposure of tools, prompts, and future resources
- workflow-phase-based visibility
- client-specific and use-case-specific surface shaping

This task does not cover:

- authoring new Blender domain tools
- spatial verification logic itself

---

## Why This Matters For Blender AI

LLMs work better when the active action space is small and relevant.

In Blender, the same model may need to:

- choose a workflow
- reason about scene state
- build geometry
- inspect topology
- export results

Those are different tasks and should not all compete equally in one flat visible surface.

---

## Success Criteria

- The visible server surface can change during a session.
- Different workflow phases expose different capability subsets.
- The model receives less irrelevant tool noise.
- The project gains a practical mechanism for “guided mode” without removing deeper capabilities.

