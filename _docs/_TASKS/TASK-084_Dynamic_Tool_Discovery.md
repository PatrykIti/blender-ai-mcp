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

## Implementation Constraints

Follow [FASTMCP_3X_IMPLEMENTATION_MODEL.md](./FASTMCP_3X_IMPLEMENTATION_MODEL.md).

For this repo, the preferred default is:

- built-in `BM25SearchTransform` for `llm-guided` discovery
- a very small pinned visible set
- native synthetic `search_tools` and `call_tool`

Hard gate:

- TASK-084 implementation is blocked until TASK-083 Gate 0 is green (3.0+ baseline) and the runtime for this surface is moved to a FastMCP 3.1+ feature line (`>=3.1,<4.0` unless explicitly revised).

Do not introduce a custom search proxy unless the built-in call path proves insufficient.

Discovery must preserve auth/visibility parity:

- `search_tools` results and `call_tool` execution must respect the same authorization and visibility pipeline as direct tool listing/calls
- session-level visibility changes (`ctx.enable_components()` / `ctx.disable_components()`) must be reflected in discovery results

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

---

## Umbrella Execution Notes

This remains the umbrella task. The original product objective stays unchanged.

### Atomic Delivery Waves

1. Define one platform-owned discovery manifest and taxonomy.
2. Roll out BM25 search with pinned entry tools on the LLM-guided surface.
3. Enrich search text from docstrings, schemas, aliases, and capability metadata.
4. Prove discovered-tool execution stays on the same router and dispatcher path.
5. Prove auth/visibility parity for `search_tools` / `call_tool` vs direct paths.
6. Measure payload reduction and search quality before making discovery-first the default.

Implementation is decomposed into:

| Order | Subtask | Purpose |
|------|---------|---------|
| 1 | [TASK-084-01](./TASK-084-01_Tool_Inventory_Normalization_and_Discovery_Taxonomy.md) | Build one canonical discovery inventory and taxonomy |
| 2 | [TASK-084-02](./TASK-084-02_Search_Transform_and_Pinned_Entry_Surface.md) | Introduce search-first discovery with pinned entry tools |
| 3 | [TASK-084-03](./TASK-084-03_Search_Document_Enrichment_from_Metadata_and_Docstrings.md) | Enrich search documents from metadata, docstrings, and schemas |
| 4 | [TASK-084-04](./TASK-084-04_Search_Execution_and_Router_Aware_Call_Path.md) | Keep search execution aligned with router and dispatcher behavior |
| 5 | [TASK-084-05](./TASK-084-05_Discovery_Tests_Benchmarks_and_Docs.md) | Add discovery regression tests, benchmarks, and docs |

### Repo-Specific Focus

- `server/router/infrastructure/tools_metadata/**`
- `server/router/infrastructure/metadata_loader.py`
- `server/adapters/mcp/areas/*.py`
- `server/adapters/mcp/dispatcher.py`
- `server/adapters/mcp/areas/workflow_catalog.py`
