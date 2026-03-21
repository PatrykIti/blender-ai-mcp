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

## Implementation Constraints

Follow [FASTMCP_3X_IMPLEMENTATION_MODEL.md](./FASTMCP_3X_IMPLEMENTATION_MODEL.md).

Visibility work in this task must preserve the distinction between:

- surface profile selected at bootstrap
- session phase selected at runtime
- contract version selected through version filters

The router may emit hints, but FastMCP remains the owner of what is visible.

Initial rollout rule:

- start with a very small async-capable entry surface (`router_*`, `workflow_catalog`, prompt/help/status entrypoints where applicable)
- start with coarse phases only
- do not attempt whole-catalog phase orchestration in the first pass

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

---

## Umbrella Execution Notes

This remains the umbrella task. The original business goal stays unchanged.

### Atomic Delivery Waves

1. Define explicit session state keys and the minimal coarse phase model.
2. Bind visibility rules to platform tags and profile defaults instead of ad hoc wrapper logic.
3. Feed router-generated phase hints into session state without moving ownership into the router.
4. Apply adaptive visibility first to the small guided entry surface, not to the whole catalog.
5. Add guided presets for `llm-guided` work while preserving deeper access through search or debug surfaces.
6. Add observability so maintainers can see which profile and phase shaped the active surface.

Implementation is decomposed into:

| Order | Subtask | Purpose |
|------|---------|---------|
| 1 | [TASK-085-01](./TASK-085-01_Session_State_Model_and_Capability_Phases.md) | Define session state and capability phases |
| 2 | [TASK-085-02](./TASK-085-02_Visibility_Policy_Engine_and_Tagged_Providers.md) | Build visibility filtering around phase/profile tags |
| 3 | [TASK-085-03](./TASK-085-03_Router_Driven_Phase_Transitions.md) | Feed router phase hints into session state without mixing responsibilities |
| 4 | [TASK-085-04](./TASK-085-04_Client_Profiles_and_Guided_Mode_Presets.md) | Add guided mode and client profile presets |
| 5 | [TASK-085-05](./TASK-085-05_Visibility_Observability_Tests_and_Docs.md) | Add visibility diagnostics, tests, and docs |

### Repo-Specific Focus

- `server/router/application/router.py`
- `server/application/tool_handlers/router_handler.py`
- `server/adapters/mcp/context_utils.py`
- `server/adapters/mcp/router_helper.py`
