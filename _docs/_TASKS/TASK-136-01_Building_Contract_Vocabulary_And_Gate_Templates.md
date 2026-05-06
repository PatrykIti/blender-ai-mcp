# TASK-136-01: Building Contract, Vocabulary, And Gate Templates

**Status:** ⏳ To Do
**Priority:** 🔴 High
**Parent:** [TASK-136](./TASK-136_Reference_Guided_Architecture_And_Building_Reconstruction.md)
**Objective:** Define the first bounded architecture target classes, reference vocabulary, stage vocabulary, and gate templates for shell, openings, supports, and roof form on the existing `TASK-157` substrate.
**Repository Touchpoints:** `server/adapters/mcp/contracts/quality_gates.py`, `server/adapters/mcp/contracts/reference.py`, `server/adapters/mcp/areas/reference.py`, `server/adapters/mcp/areas/reference_truth.py`, `server/application/services/spatial_graph.py`, `server/adapters/mcp/areas/scene_spatial_graph.py`, `_docs/_PROMPTS/DEMO_TASK_LOW_POLY_MEDIEVAL_WELL.md`, likely new `_docs/_PROMPTS/REFERENCE_GUIDED_ARCHITECTURE_BUILD.md`, `tests/unit/adapters/mcp/test_quality_gate_contracts.py`, `tests/unit/adapters/mcp/test_quality_gate_intake.py`, `tests/unit/tools/scene/test_scene_contracts.py`, `tests/unit/tools/scene/test_spatial_graph_service.py`
**Acceptance Criteria:** building goals can declare shell/opening/roof/support/facade-rhythm expectations through normalized gate templates; staged checkpoint payloads can express those blockers without inventing a building-only gate system.

## Implementation Notes

- start with a bounded target class:
  - facade-only reconstruction
  - small standalone building shell
  - modular opening/support rhythm
- define reusable building nouns and relations:
  - wall shell
  - opening
  - roof mass
  - support/post/beam
  - seated on
  - cut into
  - supported by
  - aligned to grid
- map them onto existing generic gates such as:
  - `required_part`
  - `attachment_seam`
  - `support_contact`
  - `symmetry_pair`
  - `refinement_stage`
- keep building-specific findings on the existing staged truth/checkpoint
  surfaces

## Pseudocode

```python
target_class = select_building_target_class(goal, references)
building_vocab = build_architecture_vocabulary(target_class)
gate_templates = derive_building_gate_templates(building_vocab)

checkpoint_contract = extend_reference_checkpoint_contract(
    required_parts=gate_templates.required_parts,
    interface_relations=gate_templates.interface_relations,
    staged_blockers=gate_templates.stage_blockers,
)
```

## Runtime / Security Contract Notes

- keep verifier authority on the closed `TASK-157` path
- architecture interpretation is bounded reconstruction guidance, not CAD/BIM
  or survey-grade measurement
- do not add a new public architecture-only gate tool

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_quality_gate_contracts.py`
- `tests/unit/adapters/mcp/test_quality_gate_intake.py`
- `tests/unit/tools/scene/test_scene_contracts.py`
- `tests/unit/tools/scene/test_spatial_graph_service.py`

## Docs To Update

- `_docs/_PROMPTS/DEMO_TASK_LOW_POLY_MEDIEVAL_WELL.md`
- likely new `_docs/_PROMPTS/REFERENCE_GUIDED_ARCHITECTURE_BUILD.md`
- `_docs/_MCP_SERVER/README.md`
- `_docs/_TESTS/README.md`

## Changelog Impact

- Add a `_docs/_CHANGELOG/*` entry when the first architecture contract slice
  ships.

## Validation Commands

- `git diff --check`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_quality_gate_contracts.py tests/unit/adapters/mcp/test_quality_gate_intake.py tests/unit/tools/scene/test_scene_contracts.py tests/unit/tools/scene/test_spatial_graph_service.py -q`
