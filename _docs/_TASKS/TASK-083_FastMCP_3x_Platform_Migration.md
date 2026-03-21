# TASK-083: FastMCP 3.x Platform Migration

**Priority:** 🔴 High  
**Category:** FastMCP Platform  
**Estimated Effort:** Large  
**Dependencies:** None  
**Status:** ⬜ To Do

---

## Objective

Move the MCP server foundation from the current 2.x-centered runtime model to a FastMCP 3.x platform baseline that is better suited for large, composable, LLM-facing tool ecosystems.

This task is about the platform base, not about adding new Blender functionality.

---

## Problem

The current project already has a large and growing MCP surface. That was the right decision for capability growth, but it creates a platform problem:

- the server is difficult to reshape for different client types
- the full tool catalog is too large to expose in one flat form
- visibility and discovery control are limited
- introducing safer, LLM-optimized API surfaces without breaking existing behavior is harder than it should be
- later improvements such as search-based discovery, versioned surfaces, or session-adaptive views become more expensive if the base stays on the old model

In practice, this means the project risks becoming harder to evolve exactly at the point where it needs better productization for LLM usage.

---

## Business Outcome

Create a durable FastMCP base that supports:

- large tool catalogs
- multiple client-facing surfaces
- safer migration of the public API
- composition of prompts, tools, resources, and future extensions
- better long-term operability for router-centric and inspection-heavy workflows

This gives the project a stronger platform to build on before expanding deeper into Blender-specific reliability features.

---

## Proposed Solution

Adopt FastMCP 3.x as the strategic platform layer and treat the MCP server as a composition system rather than only a decorator registry.

The server should be rebuilt conceptually around:

- providers as the source of components
- transforms as the place where visibility, naming, versioning, and discovery are controlled
- a cleaner separation between internal capabilities and the public LLM-facing product surface

The migration should preserve the current business capabilities while making later tasks cheaper and safer.

---

## FastMCP Features To Use

- **Provider Architecture** — **FastMCP 3.0.0**
- **Transforms Architecture** — **FastMCP 3.0.0**
- **LocalProvider** — **FastMCP 3.0.0**
- **Component Versioning foundation** — **FastMCP 3.0.0**
- **Session-Scoped State foundation** — **FastMCP 3.0.0**

---

## Scope

This task covers:

- the strategic FastMCP runtime baseline
- the server composition model
- future-proofing for discovery, filtering, and versioning
- alignment of the MCP platform with the repo’s next growth stage

This task does not cover:

- redesigning individual Blender tools
- introducing spatial reasoning features by itself
- changing workflow content

---

## Why This Matters For Blender AI

This repo is no longer a small MCP wrapper. It is becoming a platform for:

- building
- inspecting
- validating
- repairing
- reconstructing
- guiding users through Blender work

That requires a server base that can present different capabilities in different contexts without forcing one giant flat API on every client and every model turn.

---

## Success Criteria

- The project has a clear FastMCP 3.x baseline strategy.
- Later capabilities such as discovery, adaptive visibility, versioning, and prompt delivery can be added without another structural migration.
- Existing business capabilities remain intact during the platform transition.
- The platform becomes easier to evolve for both router-first and manual-tool workflows.

---

## Umbrella Execution Notes

This remains the umbrella task. The original business scope stays unchanged.

Implementation is decomposed into:

| Order | Subtask | Purpose |
|------|---------|---------|
| 1 | [TASK-083-01](./TASK-083-01_FastMCP_3x_Dependency_and_Runtime_Audit.md) | Audit current 2.x coupling and define migration readiness baseline |
| 2 | [TASK-083-02](./TASK-083-02_Provider_Based_Component_Inventory.md) | Split the current flat registry into reusable provider groups |
| 3 | [TASK-083-03](./TASK-083-03_Server_Factory_and_Composition_Root.md) | Replace the singleton runtime with a composition-root server factory |
| 4 | [TASK-083-04](./TASK-083-04_Transform_Pipeline_Baseline.md) | Establish the base transform pipeline for later discovery/visibility/versioning work |
| 5 | [TASK-083-05](./TASK-083-05_Context_Session_and_Execution_Bridge.md) | Normalize context/session/execution bridging for 3.x features |
| 6 | [TASK-083-06](./TASK-083-06_Platform_Regression_Harness_and_Docs.md) | Add regression coverage and architecture documentation for the new platform base |

### Repo-Specific Focus

- `pyproject.toml`
- `server/adapters/mcp/instance.py`
- `server/adapters/mcp/server.py`
- `server/adapters/mcp/areas/*.py`
- `server/infrastructure/di.py`
- `tests/unit/router/adapters/test_mcp_integration.py`
