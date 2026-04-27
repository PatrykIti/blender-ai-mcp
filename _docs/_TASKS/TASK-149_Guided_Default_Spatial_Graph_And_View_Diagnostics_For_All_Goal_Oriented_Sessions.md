# TASK-149: Guided Default Spatial Graph And View Diagnostics For All Goal-Oriented Sessions

**Status:** ✅ Done
**Priority:** 🔴 High
**Category:** Guided Runtime / Spatial Reasoning Reliability
**Estimated Effort:** Large
**Dependencies:** TASK-124, TASK-125, TASK-143, TASK-144
**Follow-on After:** [TASK-143](./TASK-143_Guided_Spatial_Scope_And_Relation_Graphs.md), [TASK-144](./TASK-144_Camera_Aware_View_Graph_And_Visibility_Diagnostics.md)

## Objective

Promote `scene_scope_graph(...)`, `scene_relation_graph(...)`, and
`scene_view_diagnostics(...)` from "optional on-demand helpers" to default
guided support tools on `llm-guided`, so the model always has direct access to
an explicit spatial-orientation layer while steering Blender.

The target outcome is simple:

- the LLM should not have to guess whether the session exposes structural
  scope, pair relations, or view-space diagnostics
- the model should always be able to reach explicit spatial-state helpers
  directly instead of reasoning blindly from names, screenshots, or partial
  truth payloads

**Completion Summary:** Completed on 2026-04-08. `llm-guided` now treats
`scene_scope_graph(...)`, `scene_relation_graph(...)`, and
`scene_view_diagnostics(...)` as standard directly visible spatial-support
tools instead of keeping them behind optional on-demand discovery. The scene
capability now pins those tools into the shaped search-first surface, the
visibility policy keeps them enabled across guided phases and creature
handoffs, and docs/tests were updated so the public contract matches the real
runtime behavior.

## Business Problem

`TASK-143` and `TASK-144` shipped the right read-only artifacts:

- `scene_scope_graph(...)`
- `scene_relation_graph(...)`
- `scene_view_diagnostics(...)`

But the current product posture still treats them as:

- off-bootstrap
- on-demand
- secondary to search/discovery

That design preserved a small guided surface, but it created a practical
failure in real sessions:

- an LLM that is already trying to build or repair something in 3D often does
  **not** know enough about the spatial state to realize it should first ask
  for scope/relation/view diagnostics
- the model therefore falls back to:
  - naming heuristics
  - raw screenshots
  - partial compare payloads
  - primitive-by-primitive guesswork
- the result is weaker structure, worse placement decisions, and lower-quality
  guided modeling even when the repo already has the right spatial tools

The current squirrel regression is the concrete symptom:

- the model entered a creature blockout recipe
- the loop and handoff did not make spatial graph/view diagnostics standard
  working tools
- the build devolved into low-information primitive placement and weak
  correction quality

For a goal-oriented 3D guided system, this is the wrong default.
Spatial orientation is not an optional luxury.

## Current Runtime Baseline

The repo already has the core spatial-state artifacts and session-shaping
machinery:

- `scene_scope_graph(...)`
- `scene_relation_graph(...)`
- `scene_view_diagnostics(...)`
- `guided_handoff`
- phase-aware `llm-guided` visibility rules
- guided prompt assets that already mention using these tools when richer
  spatial state is needed

The current mismatch is product-level:

- docs/tasks say the tools exist
- prompt guidance says to use them when spatial context is needed
- but default goal-aware guided visibility still does not treat them as
  standard support tools across all goal-oriented flows

This umbrella should close that mismatch.

## Business Outcome

If this umbrella is done correctly, the repo gains:

- one consistent rule: `llm-guided` always keeps direct access to
  spatial-state helpers
- stronger 3D orientation for LLM-driven modeling without reopening the full
  legacy tool catalog
- better structured use of:
  - anchor/core/accessory scope
  - pair relations
  - framing/occlusion diagnostics
- better build quality on manual/no-match and workflow-backed guided sessions
- less dependence on prompt luck for deciding when to ask for spatial facts

## Scope

This umbrella covers:

- visibility-policy changes so the spatial graph/view helpers are directly
  visible on `llm-guided`, including bootstrap and all active guided phases
- guided handoff changes so these tools are part of the default continuation
  contract, not optional side knowledge
- prompt and operator guidance changes so the model uses them as normal
  spatial orientation primitives
- regression coverage for direct visibility, search parity, and handoff parity
  across guided session states

This umbrella does **not** cover:

- making these tools mandatory payload fields inside every compare/iterate
  result
- replacing truth-layer measure/assert semantics with graph/view summaries

## Success Criteria

- the default visible `llm-guided` session directly exposes:
  - `scene_scope_graph`
  - `scene_relation_graph`
  - `scene_view_diagnostics`
- this remains true for all goal-oriented guided flows, including:
  - workflow-ready
  - `no_match` / `guided_manual_build`
  - creature blockout recipes
  - inspect/validate follow-up phases
- prompt assets and MCP docs present these tools as standard spatial
  orientation helpers, not hidden fallback aids
- direct visibility and search/call behavior stay aligned; the tools are not
  "mentioned in guidance" but hidden in the real session
- regression coverage proves the behavior end to end on the guided surface

## Repository Touchpoints

- `server/adapters/mcp/transforms/visibility_policy.py`
- `server/adapters/mcp/guided_mode.py`
- `server/adapters/mcp/session_capabilities.py`
- `server/adapters/mcp/areas/router.py`
- `_docs/_PROMPTS/README.md`
- `_docs/_PROMPTS/WORKFLOW_ROUTER_FIRST.md`
- `_docs/_PROMPTS/REFERENCE_GUIDED_CREATURE_BUILD.md`
- `README.md`
- `_docs/_MCP_SERVER/README.md`
- `tests/unit/adapters/mcp/`
- `tests/e2e/integration/`

## Docs To Update

- `README.md`
- `_docs/_MCP_SERVER/README.md`
- `_docs/_PROMPTS/README.md`
- `_docs/_PROMPTS/WORKFLOW_ROUTER_FIRST.md`
- `_docs/_PROMPTS/REFERENCE_GUIDED_CREATURE_BUILD.md`
- `_docs/_TASKS/README.md`

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_visibility_policy.py`
- `tests/unit/adapters/mcp/test_guided_mode.py`
- `tests/unit/adapters/mcp/test_public_surface_docs.py`
- `tests/e2e/integration/` transport-backed guided visibility coverage as needed

## Changelog Impact

- add a dedicated `_docs/_CHANGELOG/*` entry when the umbrella ships

## Execution Structure

| Order | Subtask | Purpose |
|------|---------|---------|
| 1 | [TASK-149-01](./TASK-149-01_Visibility_Policy_And_Guided_Handoff_Default_Spatial_Support.md) | Make the spatial graph/view tools directly visible on all active goal-oriented guided phases and handoffs |
| 2 | [TASK-149-02](./TASK-149-02_Prompt_And_Loop_Adoption_Of_Default_Spatial_Support.md) | Update prompt/loop guidance so these tools are treated as standard orientation helpers, not optional search trivia |
| 3 | [TASK-149-03](./TASK-149-03_Regression_Pack_And_Docs_For_Default_Spatial_Support.md) | Lock the behavior in with visibility/search parity tests, docs, and troubleshooting notes |

## Status / Board Update

- completed directly in the same branch as the runtime/docs/test changes
- closed as a board-level follow-on after TASK-143/TASK-144 because the
  original spatial artifacts now have a default guided delivery path
