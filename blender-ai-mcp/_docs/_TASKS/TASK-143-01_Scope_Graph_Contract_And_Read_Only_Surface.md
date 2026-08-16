# TASK-143-01: Scope Graph Contract and Read-Only Surface

**Parent:** [TASK-143](./TASK-143_Guided_Spatial_Scope_And_Relation_Graphs.md)
**Status:** ✅ Done
**Priority:** 🔴 High

**Completion Summary:** Completed on 2026-04-07. Scope derivation moved into
the shared spatial graph service, `assembled_target_scope` gained explicit
object-role semantics, and `scene_scope_graph(...)` now exposes the same
compact structural scope artifact through a dedicated read-only scene surface.

## Objective

Turn the current private scope/anchor logic into one explicit reusable
scope-graph artifact and expose it through a separate read-only scene-facing
surface.

## Business Problem

`assembled_target_scope` already exists, but today it is mostly a checkpoint
payload assembled inside `server/adapters/mcp/areas/reference.py`. That makes
it hard to:

- reuse the same semantics outside stage compare / iterate
- expose object roles as a first-class product artifact
- keep MCP wrappers thin while scope logic keeps growing
- give the LLM a direct "what is the current structural scope?" answer without
  making the stage contracts heavier

The first TASK-143 slice should therefore formalize scope as a reusable
read-only product, not just a private adapter helper.

## Repository Touchpoints

- `server/adapters/mcp/areas/reference.py`
- `server/adapters/mcp/areas/scene.py`
- `server/adapters/mcp/contracts/scene.py`
- `server/adapters/mcp/dispatcher.py`
- `server/infrastructure/di.py`
- `server/application/services/`
- `server/router/infrastructure/tools_metadata/scene/`
- `tests/unit/adapters/mcp/test_reference_images.py`
- `tests/unit/adapters/mcp/test_structured_contract_delivery.py`
- `tests/unit/tools/scene/test_scene_contracts.py`
- `_docs/LLM_GUIDE_V2.md`
- `_docs/_MCP_SERVER/README.md`
- `_docs/AVAILABLE_TOOLS_SUMMARY.md`

## Acceptance Criteria

- the repo has one explicit scope-graph contract separate from the current
  stage-checkpoint response contracts
- scope derivation no longer lives only as private logic in
  `server/adapters/mcp/areas/reference.py`
- the scope artifact can represent at least:
  - `single_object`
  - `object_set`
  - `collection`
  - `scene`
- structural anchor and object-role semantics are explicit enough to reduce
  accessory-first edits
- the public read-only scope artifact is router/search aware without becoming
  bootstrap-visible on `llm-guided` by default

## Docs To Update

- `_docs/LLM_GUIDE_V2.md`
- `_docs/_MCP_SERVER/README.md`
- `_docs/AVAILABLE_TOOLS_SUMMARY.md`

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_reference_images.py`
- `tests/unit/adapters/mcp/test_structured_contract_delivery.py`
- `tests/unit/tools/scene/test_scene_contracts.py`

## Changelog Impact

- include in the parent `TASK-143` changelog entry when shipped

## Execution Structure

| Order | Leaf | Purpose |
|------|------|---------|
| 1 | [TASK-143-01-01](./TASK-143-01-01_Scope_Artifact_Role_Vocabulary_And_Shared_Builder.md) | Define the scope artifact, object-role vocabulary, and shared builder that replaces the current private helper-only posture |
| 2 | [TASK-143-01-02](./TASK-143-01-02_Public_Scene_Surface_And_Router_Metadata_For_Scope_Graph.md) | Expose the scope graph as a separate read-only scene surface with proper metadata and internal routing support |

## Status / Board Update

- keep board tracking on the parent `TASK-143`
- do not promote this slice independently unless scope-surface work becomes the
  only active TASK-143 branch
- this planning pass intentionally leaves `_docs/_TASKS/README.md` untouched
