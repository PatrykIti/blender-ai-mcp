# TASK-090: Prompt Layer and Tool-Compatible Prompt Delivery

**Priority:** 🟡 Medium  
**Category:** FastMCP Prompt UX  
**Estimated Effort:** Medium  
**Dependencies:** TASK-083  
**Status:** ⬜ To Do

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

