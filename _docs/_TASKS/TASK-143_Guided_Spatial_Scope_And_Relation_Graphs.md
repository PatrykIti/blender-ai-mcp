# TASK-143: Guided Spatial Scope and Relation Graphs

**Status:** ✅ Done
**Priority:** 🔴 High
**Category:** Spatial Intelligence / Scene Truth
**Estimated Effort:** Large
**Dependencies:** TASK-116, TASK-117, TASK-122, TASK-142
**Follow-on After:** [TASK-142](./TASK-142_Creature_Part_Seating_And_Organic_Attachment_Semantics.md)

**Completion Summary:** Completed on 2026-04-07. Shipped one explicit
read-only spatial-state layer on top of the current truth surface: reusable
scope/relation graph builders now live in `server/application/services/`,
public `scene_scope_graph(...)` / `scene_relation_graph(...)` artifacts are
available through the normal MCP/router metadata path, `assembled_target_scope`
now carries deterministic object-role hints, and the staged reference loop
reuses the same shared derivation layer without embedding a heavyweight graph
payload by default. Guided visibility/search stays bootstrap-small while still
allowing on-demand spatial graph access in inspect and goal-aware creature
handoff flows. Regression coverage, docs, and changelog history were updated in
the same branch.

## Objective

Add one explicit read-only spatial-state layer on top of the current truth
surface, so an LLM operating `llm-guided` can reason over:

- the current structural scope
- the current anchor/core object
- typed pair relations
- typed relation verdicts

instead of reconstructing those concepts from scattered bbox/measure/assert
calls and prose summaries.

## Business Problem

The repo already has strong truth primitives and a strong guided correction
loop:

- `assembled_target_scope`
- `truth_bundle`
- `truth_followup`
- `correction_candidates`
- `scene_measure_*`
- `scene_assert_*`

That is enough for deterministic correctness, but it is still too fragmented
for LLM spatial reasoning.

The model still has to infer too much:

- which object is the structural anchor
- which objects are accessories vs attached masses
- which pair relations matter right now
- which failures are really:
  - attachment
  - support
  - separation
  - overlap
  - symmetry

The result is predictable:

- wrong object gets edited first
- pair-level correction logic is rediscovered per step
- LLMs stay dependent on names and prose instead of typed spatial facts
- later mesh/sculpt handoffs remain weaker than they should be because the
  model lacks one compact "what is the current spatial state?" artifact

There is also an important product constraint here:

- `llm-guided` must stay small and legible
- the repo already learned that exposing 170+ atomic tools causes drift and
  confusion
- spatial intelligence therefore cannot mean "make the guided profile much
  bigger" or "stuff the current stage-checkpoint contract with another large
  default payload"

This umbrella must solve the spatial-state problem without regressing the core
guided-surface discipline that motivated the `llm-guided` profile in the first
place.

## Current Runtime Baseline

This umbrella should build on, not replace, the current architecture:

- `assembled_target_scope` already exposes one typed scope envelope
- `truth_bundle` already exposes pairwise measured/asserted state
- `truth_followup` and `correction_candidates` already expose bounded next-step
  handoff hints
- mesh-aware contact semantics already exist for supported scene pairs
- the current guided/reference loop already consumes typed state instead of
  relying only on vision prose

The missing layer is a stable, compact, read-only spatial graph view that
packages those facts in a way the LLM can reason over directly.

That should be delivered as:

- a small number of explicit read-only spatial tools or modules
- goal-aware and phase-aware disclosure on `llm-guided`
- optional/on-demand expansion when the current task genuinely needs richer
  spatial detail

It should **not** be delivered by turning stage compare / iterate responses
into the default carrier for yet another heavyweight graph payload.

Actual runtime/code seams already in place:

- `server/adapters/mcp/areas/reference.py` already owns the current
  `_assembled_target_scope(...)`, `_select_scope_primary_target(...)`,
  `_truth_bundle_pairs(...)`, `_build_correction_truth_bundle(...)`,
  `_build_truth_followup(...)`, and `_build_correction_candidates(...)`
  helpers, so the current spatial reasoning core is real code, not just doc
  intent
- `server/adapters/mcp/contracts/scene.py` and
  `server/adapters/mcp/contracts/reference.py` already define the typed
  envelopes that this follow-on must extend without turning
  `reference_compare_stage_checkpoint(...)` /
  `reference_iterate_stage_checkpoint(...)` into default graph carriers
- `blender_addon/application/handlers/scene.py` already exposes
  `get_bounding_box(...)`, `measure_gap(...)`, `measure_alignment(...)`,
  `measure_overlap(...)`, and `assert_contact(...)`, including mesh-surface
  semantics backed by Blender-side `BVHTree` where possible
- `server/adapters/mcp/transforms/visibility_policy.py` already owns
  `llm-guided` phase/handoff shaping, so goal-aware disclosure belongs there
  rather than in prompt-only heuristics
- `server/router/infrastructure/tools_metadata/scene/` already covers
  inspect/measure/assert/macro tools, but it does not yet expose explicit
  scope-graph or relation-graph artifacts

## Business Outcome

If this umbrella is done correctly, the repo gains:

- one explicit machine-readable spatial scope artifact for guided sessions
- one explicit machine-readable relation graph for the active object set /
  collection / scene scope
- more reliable anchor selection and pair selection for later correction steps
- less prompt-level guesswork around "which object is the core mass?" and "how
  are these parts related?"
- a stronger substrate for later camera-aware reasoning and sculpt handoff
- a more scalable way to enrich guided spatial reasoning without reopening the
  large-catalog problem that `llm-guided` was created to fix

## Implementation Direction

This umbrella should be implemented as a **lightweight spatial-state layer**
above the current truth surface, not as a dependency-heavy geometry rewrite.

The intended posture is:

- start from the repo's existing spatial/truth foundations:
  - Blender-side `bmesh`
  - Blender-side `BVHTree`
  - Blender-side `KDTree`
  - current measure/assert tools
  - current `assembled_target_scope` / `truth_bundle` / `truth_followup`
- allow small implementation accelerators when they give immediate value to the
  first shipped version of the module
- keep heavier geometry libraries as explicit follow-on extensions, not as a
  blocker for the first useful product version

For the first wave, the implementation should therefore be framed as:

- **v1 baseline**:
  - current Blender-side spatial primitives plus current typed MCP contracts
- **optional v1 accelerators when justified**:
  - `scipy.spatial`
  - `networkx`
- **later extensions, not v1 requirements**:
  - `trimesh`
  - `Open3D`
  - `shapely`
  - `libigl`

This umbrella should not assume that heavy geometry dependencies must land
before the first scope/relation graph contracts ship.

One implementation constraint from the current code baseline should stay
explicit:

- the current scope/relation derivation logic is still mostly private helper
  logic inside `server/adapters/mcp/areas/reference.py`
- the intended follow-on direction is to turn that into a reusable shared
  derivation layer or service instead of letting the MCP wrapper become the
  long-term home for graph-building logic

## Dependency Policy

- if a new library clearly accelerates or simplifies the first version of the
  module, it is acceptable to adopt it
- if a new library is only useful for a richer later wave, treat it as an
  explicit future extension rather than a baseline requirement
- if a new low-level spatial tool or bounded macro is needed to expose one
  stable Blender fact or one bounded spatial action, that is acceptable, but it
  does not automatically become bootstrap-visible on `llm-guided`
- `LLM_GUIDE_V2.md` is the supporting design document for these library and
  layering choices; this umbrella remains the canonical delivery direction

## Product Design Requirements

### Lightweight Guided Exposure

- keep the default `llm-guided` visible surface small
- do not expose a large family of new spatial atomics on bootstrap by default
- prefer one small number of read-only guided-facing entry tools or modules,
  with richer detail available on demand
- new atomics, grouped tools, or bounded macros are allowed when they provide:
  - one stable spatial fact from Blender
  - or one bounded spatial action that later guided modules genuinely need
  but adding such building blocks must not automatically make them default
  bootstrap-visible on `llm-guided`
- keep disclosure adaptive:
  - surface the minimal spatial artifact set needed for the current goal,
    phase, and handoff
  - allow richer expansion only when the current task actually needs it
- do not enlarge `reference_compare_stage_checkpoint(...)` or
  `reference_iterate_stage_checkpoint(...)` with a full graph payload by
  default; current stage-checkpoint contracts are already dense and should stay
  focused on compare/iterate results

### Goal-Aware Spatial Disclosure

- the spatial-state layer should adapt to the active guided goal and shaped
  handoff, not behave as one fixed universal payload
- example:
  - creature work should bias toward anchor/body-part/attachment relations
  - landmark or monument work may care more about symmetry, vertical
    alignment, support, and stacked landmark structure
- goal-aware shaping should remain deterministic and metadata-driven where
  possible; do not solve this by scraping arbitrary chat history

### Delivery Model

- spatial artifacts should be retrievable as explicit read-only products
  instead of being hidden inside larger compare contracts
- the guided loop may reference or call those artifacts when needed, but the
  graph/module itself should remain conceptually separate from the checkpoint
  compare/iterate payloads
- if a lightweight summary field is later added to loop responses, it should be
  a compact derivative of the graph/module rather than the full graph itself

### Scope Graph

- expose the current scope kind, anchor, object roles, and target set as a
  stable typed artifact
- keep the graph derived from measured/runtime state; do not create a second
  fuzzy authority layer
- support at least:
  - `single_object`
  - `object_set`
  - `collection`
  - `scene`

### Relation Graph

- expose typed pair relations derived from the truth layer, not from prompt
  heuristics
- support at least the current high-value relations already implicit in the
  repo:
  - contact / gap
  - overlap
  - alignment
  - attachment
  - support
  - symmetry-oriented pair interpretation
- keep the relation graph compact enough for frequent guided-loop use
- keep pair expansion bounded and goal-aware / phase-aware; the current
  anchor-first `primary_to_others` baseline should not silently turn into an
  unbounded all-to-all graph

### Guided Loop Adoption

- let the guided loop call or reference spatial graph artifacts when they add
  decision value, without displacing the existing `truth_bundle` /
  `truth_followup` contracts
- keep the graph useful to `correction_candidates` and future repair-planner
  work, not just a detached debug payload
- keep default loop payload growth tightly bounded; prefer separate read-only
  access over unconditional payload expansion

## Scope

This umbrella covers:

- a typed scope-graph contract for active guided spatial targets
- a typed relation-graph contract derived from current truth-layer facts
- one lightweight guided-facing delivery model for those artifacts
- structural anchor and object-role exposure for multi-object scopes
- goal-aware and phase-aware disclosure for those artifacts on `llm-guided`
- adoption of those graph artifacts in the current guided/reference loop only
  where they add decision value
- docs and regression coverage for the new graph layer

This umbrella does **not** cover:

- camera-aware visibility / occlusion / screen projection
- a new free-form "scene graph AI" planner
- using vision as the authority for scene truth
- automatic write-side scene graph execution
- exposing a broad new default tool family on `llm-guided` bootstrap
- turning `reference_compare_*` / `reference_iterate_*` into the default home
  for a full graph payload
- sculpt-specific handoff policy beyond the graph substrate required to support
  it later

## Acceptance Criteria

- the repo has one explicit read-only scope-graph artifact for guided spatial
  reasoning
- the repo has one explicit read-only relation-graph artifact for guided
  spatial reasoning
- the delivery model keeps `llm-guided` small:
  - no large new bootstrap-visible graph family
  - no default full graph embedding into the current stage-checkpoint payloads
- the graph artifacts are clearly derived from measured/asserted state rather
  than prompt-only inference
- multi-object guided scopes expose a structural anchor/object-role story
  strong enough to reduce accessory-first corrections
- graph access and summary detail can adapt to the active guided goal / phase
  instead of staying one fixed heavy payload for every domain
- the new graph layer fits the current `assembled_target_scope` /
  `truth_bundle` / `truth_followup` model instead of creating a competing
  authority
- focused regression coverage proves the graph layer stays aligned with current
  truth semantics

## Repository Touchpoints

- `server/domain/tools/scene.py`
- `server/application/tool_handlers/scene_handler.py`
- `server/adapters/mcp/areas/scene.py`
- `server/adapters/mcp/contracts/scene.py`
- `server/adapters/mcp/areas/reference.py`
- `server/adapters/mcp/contracts/reference.py`
- `server/adapters/mcp/transforms/visibility_policy.py`
- `server/adapters/mcp/dispatcher.py`
- `server/infrastructure/di.py`
- `server/application/services/`
- `server/router/infrastructure/tools_metadata/scene/`
- `blender_addon/application/handlers/scene.py`
- `tests/unit/tools/scene/test_scene_contracts.py`
- `tests/unit/tools/scene/test_scene_measure_tools.py`
- `tests/unit/adapters/mcp/test_reference_images.py`
- `tests/unit/adapters/mcp/test_structured_contract_delivery.py`
- `tests/unit/adapters/mcp/test_visibility_policy.py`
- `tests/unit/tools/test_handler_rpc_alignment.py`
- `tests/e2e/tools/scene/test_scene_measure_tools.py`
- `tests/e2e/vision/test_reference_stage_truth_handoff.py`
- `_docs/LLM_GUIDE_V2.md`
- `_docs/_MCP_SERVER/README.md`
- `_docs/_PROMPTS/README.md`
- `_docs/_VISION/README.md`
- `_docs/AVAILABLE_TOOLS_SUMMARY.md`

## Docs To Update

- `_docs/LLM_GUIDE_V2.md`
- `_docs/_MCP_SERVER/README.md`
- `_docs/_PROMPTS/README.md`
- `_docs/_VISION/README.md`
- `_docs/AVAILABLE_TOOLS_SUMMARY.md`
- `_docs/_TASKS/README.md` when the execution branch is allowed to sync the
  board state

## Tests To Add/Update

- `tests/unit/tools/scene/test_scene_contracts.py`
- `tests/unit/tools/scene/test_scene_measure_tools.py`
- `tests/unit/adapters/mcp/test_reference_images.py`
- `tests/unit/adapters/mcp/test_structured_contract_delivery.py`
- `tests/unit/adapters/mcp/test_visibility_policy.py`
- `tests/unit/tools/test_handler_rpc_alignment.py`
- `tests/e2e/tools/scene/test_scene_measure_tools.py`
- `tests/e2e/vision/test_reference_stage_truth_handoff.py`

## Changelog Impact

- add a dedicated `_docs/_CHANGELOG/*` entry when this umbrella ships

## Execution Structure

| Order | Subtask | Purpose |
|------|---------|---------|
| 1 | [TASK-143-01](./TASK-143-01_Scope_Graph_Contract_And_Read_Only_Surface.md) | Extract and formalize the current scope/anchor logic into one reusable scope-graph contract plus a separate read-only scene surface |
| 2 | [TASK-143-02](./TASK-143-02_Relation_Graph_Derivation_And_Truth_Layer_Convergence.md) | Derive a compact relation graph from the existing truth primitives and align truth-followup / candidate semantics with that graph model |
| 3 | [TASK-143-03](./TASK-143-03_Goal_Aware_Disclosure_Guided_Adoption_And_Regression_Pack.md) | Gate the new graph layer behind goal/phase-aware disclosure, keep it on-demand, and lock the story with regression/docs coverage |

## Status / Board Update

- promote this as a board-level umbrella for spatial-state artifacts that make
  the current guided product surface easier for LLMs to reason about
- keep board tracking on this parent task until scope graph, relation graph,
  docs, and regression coverage are aligned
- this planning pass intentionally does **not** modify `_docs/_TASKS/README.md`
  per explicit user constraint
