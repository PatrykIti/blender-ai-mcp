# TASK-084: Dynamic Tool Discovery for Large Catalogs

**Priority:** 🔴 High  
**Category:** FastMCP Tool UX  
**Estimated Effort:** Medium  
**Dependencies:** TASK-083  
**Status:** ⬜ To Do

---

## Objective

Replace flat, full-catalog tool discovery with an on-demand discovery model that is more natural for LLMs using a large Blender server.

---

## Problem

The project exposes a large number of tools. Even when the tools are well designed, a very large flat catalog creates predictable issues:

- the model spends context budget just reading the catalog
- tool selection quality gets worse when too many options are visible at once
- nearby tools compete semantically and cause confusion
- the model overuses familiar tools instead of the best tool
- adding more tools can paradoxically reduce overall reliability

For Blender workflows, this is especially painful because the model must already reason about geometry, hierarchy, mode, selection, and spatial relationships.

---

## Business Outcome

Make the MCP server discoverable in stages:

- the model sees only a minimal entry surface
- it searches for relevant tools when needed
- it inspects only the matching subset
- it executes only the tools that matter for the current task

This reduces token waste and improves selection quality without shrinking the true capability set.

---

## Proposed Solution

Adopt search-based tool discovery as the default experience for large-surface clients.

The public tool surface should shift from:

- “here is the whole Blender API”

to:

- “here are a few core entry points and a discovery mechanism”

Core tools such as router entry, status, prompt access, and essential help can remain directly visible, while the rest of the catalog is discovered on demand.

---

## FastMCP Features To Use

- **Tool Search** — **FastMCP 3.1.0**
- **Transforms Architecture** — **FastMCP 3.0.0**
- **Always-visible pinned tools within search transform** — **FastMCP 3.1.0**

---

## Scope

This task covers:

- search-first discovery for large tool catalogs
- deciding which tools stay always visible
- designing a small public “entry layer” for the server
- improving LLM tool selection quality at catalog scale

This task does not cover:

- changing the semantics of existing Blender tools
- replacing the router

---

## Why This Matters For Blender AI

For this repo, large-tool-catalog management is not a nice-to-have. It is central to product quality.

Search-based discovery directly helps with:

- tool choice
- context budget
- model focus
- future expansion of the toolset

It is one of the most important FastMCP 3.1 features for this project.

---

## Success Criteria

- LLM-facing clients no longer need the full tool catalog up front.
- The server exposes a smaller, more focused discovery entry point.
- Tool selection quality improves for complex Blender tasks.
- The project can keep growing its tool catalog without linearly increasing model confusion.

