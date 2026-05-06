# TASK-137-02: Guided Organ Loop, Relation Semantics, And Bounded Surface

**Status:** ⏳ To Do
**Priority:** 🟠 High
**Parent:** [TASK-137](./TASK-137_Anatomy_Aware_Reference_Guided_Organ_Reconstruction.md)
**Depends On:** [TASK-137-01](./TASK-137-01_Organ_Domain_Boundary_Vocabulary_And_Fidelity_Tiers.md)
**Objective:** Turn the organ contract into a usable guided path with staged organ loops, organ-specific relation semantics, and a bounded modeling/sculpt/lattice surface.
**Repository Touchpoints:** `server/adapters/mcp/session_capabilities_state.py`, `server/adapters/mcp/session_capabilities_flow.py`, `server/adapters/mcp/session_capabilities_runtime_glue.py`, `server/adapters/mcp/transforms/visibility_policy.py`, `server/adapters/mcp/discovery/search_surface.py`, `server/adapters/mcp/areas/reference.py`, `server/adapters/mcp/areas/reference_feedback.py`, `server/adapters/mcp/areas/modeling.py`, `server/adapters/mcp/areas/mesh.py`, `server/adapters/mcp/areas/sculpt.py`, `server/adapters/mcp/areas/lattice.py`, `server/router/infrastructure/tools_metadata/mesh/`, `server/router/infrastructure/tools_metadata/sculpt/`, `server/router/infrastructure/tools_metadata/lattice/`, `tests/unit/adapters/mcp/test_guided_flow_state_contract.py`, `tests/unit/adapters/mcp/test_visibility_policy.py`, `tests/unit/adapters/mcp/test_search_surface.py`, `tests/unit/tools/sculpt/test_sculpt_tools.py`, `tests/unit/tools/lattice/test_lattice_handler.py`
**Acceptance Criteria:** organ work can move through bounded stages such as primary mass, lobe/chamber definition, cavity/port landmarks, and final validation; the public surface stays bounded and does not collapse into unrestricted sculpt.

## Implementation Notes

- stage organ work explicitly instead of treating it as generic organic blob
  sculpting
- distinguish fused, embedded, attached, and paired relations in the staged
  loop and correction policy
- keep sculpt, lattice, and modeling families bounded and role-aware
- preserve the current session-state and gate-transport model
- keep staged organ blockers and loop-facing summaries on the existing
  `reference.py` / `reference_feedback.py` delivery seams instead of inventing a
  second organ-only reporting surface

## Pseudocode

```python
if domain_profile == "organ":
    guided_flow_state = seed_organ_flow(primary_mass_then_lobes_then_cavities)
    relation_policy = map_organ_relations_to_gate_semantics()
    visibility_rules = expose_bounded_organic_surface_for(guided_flow_state.current_step)
```

## Runtime / Security Contract Notes

- no default public path to unrestricted high-resolution sculpt
- organ relation hints remain advisory; verifier authority stays unchanged
- any new anatomy-facing helper must stay bounded and documented as
  visualization-oriented only

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_guided_flow_state_contract.py`
- `tests/unit/adapters/mcp/test_visibility_policy.py`
- `tests/unit/adapters/mcp/test_search_surface.py`
- `tests/unit/tools/sculpt/test_sculpt_tools.py`
- `tests/unit/tools/lattice/test_lattice_handler.py`

## Docs To Update

- likely new `_docs/_PROMPTS/REFERENCE_GUIDED_ORGAN_BUILD.md`
- `_docs/_MCP_SERVER/README.md`
- `_docs/AVAILABLE_TOOLS_SUMMARY.md`

## Changelog Impact

- Add a `_docs/_CHANGELOG/*` entry when the first organ guided-surface slice
  ships.

## Validation Commands

- `git diff --check`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_guided_flow_state_contract.py tests/unit/adapters/mcp/test_visibility_policy.py tests/unit/adapters/mcp/test_search_surface.py tests/unit/tools/sculpt/test_sculpt_tools.py tests/unit/tools/lattice/test_lattice_handler.py -q`
