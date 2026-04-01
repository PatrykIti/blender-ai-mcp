# TASK-090: Prompt Layer and Tool-Compatible Prompt Delivery

**Priority:** 🟡 Medium  
**Category:** FastMCP Prompt UX  
**Estimated Effort:** Medium  
**Dependencies:** TASK-083  
**Status:** ✅ Done

**Completion Summary:** This task is now closed. The repo has a curated prompt catalog, native FastMCP prompt components, canonical bridge tools (`list_prompts`, `get_prompt`) for tool-only clients, a dynamic `recommended_prompts` product that reacts to surface profile and session phase, and tests/docs covering prompt access across prompt-capable and tool-only clients.

---

## Objective

Turn prompt guidance into a first-class server product surface that works across both prompt-capable and tool-only MCP clients.

---

## Problem

This repo already contains strong prompt guidance and workflow usage patterns. That is valuable product knowledge, but today it mostly lives as documentation and templates outside the live server surface.

This creates a consistency problem:

- some clients can use prompts directly
- some clients support only tools
- some users know how to configure system prompts well
- some do not

As a result, the quality of the LLM experience depends too much on external setup quality.

---

## Business Outcome

Deliver prompt guidance as part of the server product itself.

This should let the project distribute:

- modeling mode guidance
- workflow-first guidance
- manual-tool guidance
- validation guidance
- troubleshooting guidance

through the MCP server in a client-compatible way.

---

## Proposed Solution

Promote prompt assets to first-class server components and bridge them to tool-only clients when needed.

The goal is for clients to access the project’s best guidance through the server instead of relying only on copied markdown templates.

This strengthens consistency across ChatGPT, Claude, Codex, and other MCP consumers.

---

## Implementation Constraints

Follow [FASTMCP_3X_IMPLEMENTATION_MODEL.md](./FASTMCP_3X_IMPLEMENTATION_MODEL.md).

Native prompts should remain the primary mechanism on prompt-capable surfaces.
Prompt bridge tools exist for compatibility, not as the default public abstraction.

---

## FastMCP Features To Use

- **Prompt components in the FastMCP 3.x platform model** — **FastMCP 3.0.0**
- **Prompts as Tools** — **FastMCP 3.0.0**

---

## Scope

This task covers:

- productized prompt delivery
- prompt access for prompt-capable clients
- fallback prompt access for tool-only clients
- server-distributed guidance for different operating modes

This task does not cover:

- writing all final prompts in implementation detail
- replacing the router

---

## Why This Matters For Blender AI

Prompt quality is part of the product here.

Your server already benefits from good behavioral scaffolding. This task makes that scaffolding:

- reusable
- client-compatible
- standardized
- easier to maintain

instead of leaving it fragmented across external instructions.

---

## Success Criteria

- Prompt guidance becomes a formal part of the server surface.
- Tool-only clients can still access prompt products.
- Users need less manual prompt setup to get strong behavior.
- The project’s best operating guidance becomes easier to distribute consistently.

---

## Umbrella Execution Notes

This remains the umbrella task. The original scope stays unchanged.

### Atomic Delivery Waves

1. Inventory prompt assets and tag them by phase, audience, and operating mode.
2. Expose them as native FastMCP prompts.
3. Add a prompt bridge for tool-only surfaces.
4. Make prompt recommendations depend on session phase and profile.
5. Add QA examples and docs so prompt products stay curated instead of drifting.

Implementation is decomposed into:

| Order | Subtask | Purpose |
|------|---------|---------|
| 1 | [TASK-090-01](./TASK-090-01_Prompt_Asset_Inventory_and_Taxonomy.md) | Inventory prompt assets and assign operating modes |
| 2 | [TASK-090-02](./TASK-090-02_FastMCP_Prompt_Provider_and_Rendering.md) | Expose prompts as native FastMCP prompt components |
| 3 | [TASK-090-03](./TASK-090-03_Prompts_As_Tools_Bridge.md) | Bridge prompts to tool-only clients |
| 4 | [TASK-090-04](./TASK-090-04_Session_Aware_Prompt_Selection.md) | Make prompt selection phase and profile aware |
| 5 | [TASK-090-05](./TASK-090-05_Prompt_QA_Examples_and_Documentation.md) | Add prompt QA coverage and docs |
