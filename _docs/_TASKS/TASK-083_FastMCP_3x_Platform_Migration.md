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

The implementation should move incrementally, not as one wide cut-over:

- first establish inventory and registration seams
- then migrate provider composition area by area
- then flip bootstrap and transform composition
- only then layer discovery, visibility, and versioned public surfaces on top

---

## Implementation Constraints

Follow the shared platform model in [FASTMCP_3X_IMPLEMENTATION_MODEL.md](./FASTMCP_3X_IMPLEMENTATION_MODEL.md).

For this task series, the migration baseline must establish:

- one canonical platform manifest seam and minimal scaffold outside router metadata
- a clear distinction between surface profile, contract version, and session phase
- provider-based composition as the runtime source of truth
- built-in FastMCP transforms as the default shaping mechanism before custom wrappers are considered
- reusable `LocalProvider` groups and registration seams as the default migration path before introducing repo-specific custom provider abstractions

Interpretation for this umbrella:

- TASK-083 establishes the runtime-owned manifest seam and bootstrap scaffold
- TASK-084 populates and normalizes that scaffold for discovery inventory use
- TASK-086 attaches public naming and contract metadata to the same shared manifest

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

### Atomic Delivery Waves

1. Audit current 2.x coupling, supported Python/runtime baseline, and missing inventory coverage.
2. Extract reusable `LocalProvider` groups / registrars and remove side-effect-only registration assumptions.
3. Replace the singleton bootstrap with a server factory, surface profiles, and a minimal platform manifest scaffold owned by the MCP platform layer.
4. Lock a deterministic transform order that later tasks extend rather than bypass.
5. Normalize context, session, and execution reporting for async-capable platform features.
6. Add regression coverage for profiles, providers, transforms, and bootstrap behavior.

Migration should stay area-oriented:

- `scene`, `mesh`, and `modeling` first, because they dominate the public catalog
- `router` and `workflow_catalog` next, because later 3.x interaction work depends on them
- remaining families after the provider and factory pattern is proven

YAGNI rule for this umbrella:

- do not introduce a broad custom-provider subsystem unless a concrete FastMCP limitation appears
- prefer registration functions bound to `LocalProvider` instances over inventing repo-specific provider hierarchies
- keep the first migration focused on factory, profiles, transforms, and reusable provider groups

### Migration Gates (Blocking For TASK-084+)

Before starting broad implementation of TASK-084 through TASK-097, the following gates must pass:

- **Gate 0 (after TASK-083-01): Runtime Baseline Gate**
  - `pyproject.toml` pins FastMCP to a stable 3.0+ baseline (`>=3.0,<4.0` unless explicitly revised)
  - `pyproject.toml`, docs, and smoke-test assumptions agree on the practical supported Python baseline for this task series (`3.11+` unless explicitly revised)
  - a runtime/dependency matrix explains which capabilities are baseline-supported vs degraded/disabled on older interpreters, and Gate 0 is evaluated against the supported baseline rather than an arbitrary local interpreter
  - migration docs explain that 3.1+ is a feature gate for downstream tasks that require it (`BM25SearchTransform`, `Code Mode`)
  - smoke tests confirm runtime boots on the selected FastMCP baseline and on the supported Python/runtime matrix used by gated tasks
- **Gate A (after TASK-083-03): Composition Root Gate**
  - bootstrap uses `build_server(surface_profile=...)` instead of global side-effect registration
  - profile selection is explicit in config (`legacy-flat`, `llm-guided`, `internal-debug`, `code-mode-pilot`)
  - unit smoke tests prove at least two profiles can boot from the same provider set
  - one minimal platform manifest scaffold exists outside router metadata and is wired into the platform bootstrap as the future source of public capability metadata
- **Gate B (after TASK-083-04): Transform Pipeline Gate**
  - transform order is deterministic and covered by snapshot/regression tests
  - naming/visibility/version shaping happens in the transform chain, not in ad hoc adapter wrappers
  - provider-level and server-level transform layering is documented and verified in tests

If either gate is red, downstream FastMCP platform tasks are blocked except for doc-only preparation.
If Gate 0 is green but runtime is still below 3.1, tasks that require FastMCP 3.1+ features (notably TASK-084 and TASK-094) are blocked except for doc-only preparation.

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
