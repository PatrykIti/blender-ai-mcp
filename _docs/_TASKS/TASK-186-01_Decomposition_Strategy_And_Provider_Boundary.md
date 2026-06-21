# TASK-186-01: Decomposition Strategy And Provider Boundary

**Parent:** [TASK-186](./TASK-186_Semantic_Part_Decomposition_And_Registry_Materialization.md)
**Status:** ⏳ To Do
**Priority:** 🔴 High
**Objective:** Choose and document the first semantic part decomposition strategy without binding the repo to stale provider claims or confusing advisory segmentation with deterministic truth.

**Repository Touchpoints:** `server/infrastructure/config.py`, `server/adapters/mcp/contracts/`, `server/adapters/mcp/vision/config.py`, `server/adapters/mcp/vision/runtime.py`, `_docs/_MCP_SERVER/README.md`, `_docs/_VISION/README.md`

## Implementation Notes

- Compare viable strategies before code lands:
  - local geometric heuristics and mesh islands
  - reference/image-conditioned segmentation sidecars
  - mesh/point/3D segmentation sidecars
  - operator-assisted seed labels
- Record provider license, model size, runtime cost, input/output shape, and
  failure modes.
- Prefer a fixture-backed local path first if it can prove the contract.

## Runtime / Security Contract Notes

- external provider choices require current official-source verification during
  implementation
- provider keys and source assets must stay redacted from logs
- sidecar outputs are advisory until materialized and verified

## Tests To Add/Update

- config validation tests for disabled/unavailable/provider-missing states
- contract tests for provider-neutral output shape
- negative tests for unsupported provider and unknown fields

## Docs To Update

- `_docs/_MCP_SERVER/README.md`
- `_docs/_VISION/README.md`

## Acceptance Criteria

- one first-wave strategy is selected with explicit non-goals and fallback path
- provider-specific behavior stays behind a provider-neutral contract
- no task or doc claims current object-ID masks can provide semantic parts

## Validation Commands

- `git diff --check`
- targeted unit tests added by the implementation
