# TASK-159: Modularize Oversized Guided Runtime And Scene Owner Files

**Status:** ⏳ To Do
**Priority:** 🔴 High
**Category:** Architecture / Maintainability
**Estimated Effort:** Large
**Dependencies:** TASK-143, TASK-144, TASK-145, TASK-150, TASK-157, TASK-158
**Follow-on After:** [TASK-143](./TASK-143_Guided_Spatial_Scope_And_Relation_Graphs.md), [TASK-145](./TASK-145_Spatial_Repair_Planner_And_Sculpt_Handoff_Context.md), [TASK-157](./TASK-157_Goal_Derived_Quality_Gates_And_Deterministic_Verification.md), [TASK-158](./TASK-158_Vision_And_Creature_Gate_Boundary_Doc_Alignment.md)

## Objective

Split the repo's oversized guided-runtime and scene owner files into smaller,
bounded modules so the current architecture can keep expanding without
reintroducing parallel flows, duplicated logic, or unsafe cross-layer coupling.

The target is not "small files for aesthetics." The target is:

- clearer ownership per concern
- safer extension points for the next spatial-intelligence wave
- lower-risk edits in guided/reference/runtime code
- preserved public MCP, router, addon, and RPC contracts

## Business Problem

Recent work intentionally built strong foundations instead of a second flow:

- `scene_scope_graph(...)`
- `scene_relation_graph(...)`
- `scene_view_diagnostics(...)`
- staged reference compare / iterate
- planner / handoff contracts
- goal-derived quality gates
- guided state, visibility, and prompt-bundle shaping

That foundation is correct, but several owner files now absorb too many
responsibilities at once:

- `server/adapters/mcp/areas/reference.py`
- `server/adapters/mcp/areas/scene.py`
- `blender_addon/application/handlers/scene.py`
- `server/adapters/mcp/session_capabilities.py`

This creates a predictable delivery risk for the next waves:

- small changes force broad diff surfaces
- unrelated concerns drift together inside one file
- review becomes slower because every change looks cross-cutting
- contract work, planner work, spatial work, and transport work become harder
  to separate cleanly
- future domains that depend on higher-precision spatial reasoning or stronger
  verification will amplify the problem rather than reuse the foundation safely

The repo already paid the cost to unify behavior around one guided/runtime
substrate. If the oversized files remain monolithic, later expansions will
start to feel like a second architecture even if the public surface stays the
same.

## Current Runtime Baseline

The current implementation already has the right high-level product model:

- MCP adapters stay the public surface
- addon handlers stay the Blender owner layer
- guided/reference state remains session-owned
- spatial truth stays deterministic
- vision/perception remains advisory

The issue is not that the architecture is wrong. The issue is that too much of
that architecture is packed into a few large owner files.

Current large-file pressure points include:

- `server/adapters/mcp/areas/reference.py`
  - staged compare / iterate assembly
  - truth bundle shaping
  - correction-candidate shaping
  - silhouette and view-diagnostics hints
  - planner / handoff assembly
  - reference intake and staged orchestration
- `server/adapters/mcp/areas/scene.py`
  - public MCP tool registration
  - inspect/configure flows
  - create/manage flows
  - viewport/view diagnostics
  - spatial graph access
  - measure/assert tool family
- `blender_addon/application/handlers/scene.py`
  - scene CRUD helpers
  - hierarchy / bbox / origin inspection
  - viewport and render orchestration
  - mesh-aware measure/assert logic
  - world/render configuration
  - topology inspection helpers
- `server/adapters/mcp/session_capabilities.py`
  - guided-flow state model
  - visibility-refresh behavior
  - spatial freshness / rearm bookkeeping
  - quality-gate projection hooks
  - required/preferred prompt-bundle shaping

The runtime should keep these capabilities. The delivery goal is to separate
their ownership seams.

## Business Outcome

If this umbrella is done correctly, the repo gains:

- a cleaner extension path for deeper spatial-intelligence work
- a safer base for high-precision or domain-specific guided consumers
- smaller, more reviewable change slices
- lower risk that one runtime fix regresses visibility, planner, reference, and
  scene behavior all at once
- clearer places to put new logic without inventing a second flow or shadow
  service layer

## Non-Goals

This umbrella deliberately does not:

- create a second guided/reference/runtime flow
- rename public MCP tools, addon RPC methods, or session-contract fields
- widen or redesign the current public compare / iterate / scene contracts
- rewrite the repo into a package-per-tool architecture
- move Blender logic out of `blender_addon/`
- move FastMCP or router imports into domain/application layers that should stay
  framework-free
- bundle product changes with maintainability refactors unless the behavior
  change is required to preserve the existing contract safely

## Refactor Principles

- Keep the public import and call surface stable first; extract internals behind
  facades before considering broader path changes.
- Preserve Clean Architecture direction. If logic becomes framework-free and
  reusable, prefer application-service extraction over leaving it trapped in an
  MCP adapter forever.
- Keep MCP adapter files as the registration / translation layer, not the
  permanent home of every helper.
- Keep addon-side Blender logic in addon modules; do not "helpfully" mirror it
  into the server.
- Prefer sibling helper modules and re-exports over sweeping path changes in
  one pass.
- Do not hide behavior drift behind refactor language. If a contract changes,
  document it as a contract change.

## Execution Structure

| Order | Subtask | Purpose |
|------|---------|---------|
| 1 | [TASK-159-01](./TASK-159-01_Reference_Area_Modularization_And_Checkpoint_Assembly_Boundaries.md) | Split `reference.py` into planner, truth, silhouette, view-diagnostics, and checkpoint ownership slices while keeping the staged public surface stable |
| 2 | [TASK-159-02](./TASK-159-02_Scene_MCP_Area_Modularization_And_Surface_Slices.md) | Split `scene.py` into inspect, create/manage, spatial-graph, measure/assert, and view slices while preserving MCP tool names and surface behavior |
| 3 | [TASK-159-03](./TASK-159-03_Addon_Scene_Handler_Modularization_And_Blender_Ownership_Boundaries.md) | Split addon `SceneHandler` by inspection, measure/assert, viewport, and world/render responsibility without changing RPC behavior |
| 4 | [TASK-159-04](./TASK-159-04_Session_Capabilities_Modularization_And_Guided_State_Boundaries.md) | Split `session_capabilities.py` into guided-state, visibility-refresh, quality-gate projection, and prompt-bundle ownership slices while preserving the current facade |

## Repository Touchpoint Table

| Path / Module | Scope | Why It Is In Scope |
|---------------|-------|--------------------|
| `server/adapters/mcp/areas/reference.py` | MCP staged reference surface | Current assembler for compare / iterate, truth, planner, and perception-side helpers |
| `server/adapters/mcp/areas/scene.py` | MCP scene surface | Current public owner of scene tool families that now mix multiple read/write concerns |
| `blender_addon/application/handlers/scene.py` | Blender truth / scene handler | Current addon owner for scene inspection, viewport, world, and measure/assert behavior |
| `server/adapters/mcp/session_capabilities.py` | Guided runtime state | Current owner of guided-flow persistence, visibility refresh, and gate/prompt shaping |
| `server/application/services/` | Service promotion | Target home for framework-free logic that should not stay trapped in adapter modules |
| `server/adapters/mcp/contracts/` | Contract stability | Public response shapes must remain stable while internal ownership changes |
| `tests/unit/adapters/mcp/` | MCP regressions | Protect public surface and adapter behavior during extraction |
| `tests/unit/tools/scene/` | Scene truth / RPC alignment | Protect scene and addon behavior while splitting handlers |
| `tests/e2e/vision/` | Hybrid loop regressions | Protect staged compare / iterate behavior during `reference.py` extraction |
| `tests/e2e/integration/` | Guided transport/state regressions | Protect session-state and guided transport semantics during session-capabilities extraction |
| `_docs/_TASKS/README.md` | Board sync | Promote and track the internal architecture umbrella coherently |

## Test Matrix

| Slice | Primary Validation Lane | Why |
|-------|-------------------------|-----|
| `reference.py` split | unit + guided/vision integration | public staged response shape and planner/truth assembly are contract-sensitive |
| `scene.py` split | unit + scene tool integration/e2e | public tool surface and scene behavior must stay identical |
| addon `scene.py` split | unit + Blender-backed scene tests | Blender truth path and viewport behavior are runtime-sensitive |
| `session_capabilities.py` split | unit + guided transport/integration | visibility, stale-state, and prompt-bundle regressions can hide until session-level flows run |

## Pseudocode

```python
for owner_file in oversized_owner_files:
    concerns = identify_private_helper_clusters(owner_file)
    for concern in concerns:
        target_module = choose_target_module(owner_file, concern)
        move_private_helpers(owner_file, target_module)
        keep_public_facade_stable(owner_file, target_module)
        run_targeted_contract_and_runtime_tests(owner_file, concern)

    if pure_logic_outgrew_adapter(owner_file):
        promote_to_application_service()
        keep_adapter_translation_local()
```

## Docs To Update

- `_docs/_TASKS/README.md`
- `ARCHITECTURE.md` if the final extraction changes the documented ownership map
- `_docs/_ADDON/README.md` if addon-scene internals become explicitly documented
- `_docs/_MCP_SERVER/README.md` only if public/tool/runtime ownership wording needs a maintenance note
- `_docs/_TESTS/README.md` if test-lane ownership or commands change materially

## Changelog Impact

- add one dedicated `_docs/_CHANGELOG/*` entry when the umbrella ships
- use that entry to record structural extraction and ownership-boundary changes,
  not as a cover label for unrelated product behavior changes

## Acceptance Criteria

- the repo has one active modularization umbrella covering the four oversized
  owner files
- each branch names the target ownership split clearly enough for one focused
  implementation pass
- the planned refactor preserves the current public MCP/addon/session surface
  rather than opening a second architecture
- the board tracks this as a promoted internal follow-on before the next deeper
  spatial/runtime expansion wave

## Status / Board Update

- promote as a board-level open task because the work spans MCP adapters,
  addon handlers, guided runtime state, and regression ownership
- treat this as an internal follow-on that prepares the repo for the next
  spatial-intelligence and domain-expansion waves without changing product
  direction
