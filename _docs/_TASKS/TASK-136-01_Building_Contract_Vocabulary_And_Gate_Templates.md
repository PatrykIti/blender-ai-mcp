# TASK-136-01: Building Contract, Vocabulary, And Gate Templates

**Status:** ⏳ To Do
**Priority:** 🔴 High
**Parent:** [TASK-136](./TASK-136_Reference_Guided_Architecture_And_Building_Reconstruction.md)
**Objective:** Extend the shipped generic building gate/reference substrate with architecture-specific target classes, vocabulary, stage vocabulary, and gate templates for shell, openings, supports, roof form, and facade rhythm on top of the existing `TASK-157` substrate.
**Repository Touchpoints:** `server/adapters/mcp/contracts/quality_gates.py`, `server/adapters/mcp/contracts/reference.py`, `server/adapters/mcp/transforms/quality_gate_verifier.py`, `server/adapters/mcp/areas/reference.py`, `server/adapters/mcp/areas/reference_understanding.py`, `server/adapters/mcp/areas/reference_truth.py`, `server/application/services/spatial_graph.py`, `server/adapters/mcp/areas/scene_spatial_graph.py`, `_docs/_PROMPTS/README.md`, likely new `_docs/_PROMPTS/REFERENCE_GUIDED_ARCHITECTURE_BUILD.md`, `tests/unit/adapters/mcp/test_quality_gate_contracts.py`, `tests/unit/adapters/mcp/test_quality_gate_intake.py`, `tests/unit/adapters/mcp/test_quality_gate_verifier.py`, `tests/unit/tools/scene/test_scene_contracts.py`, `tests/unit/tools/scene/test_spatial_graph_service.py`
**Acceptance Criteria:**
- building-oriented goal or RU intake can normalize shell/opening/roof/support/facade-rhythm expectations onto the existing generic gate vocabulary without inventing an architecture-only gate system
- the architecture templates explicitly reuse current gate types such as `required_part`, `attachment_seam`, `support_contact`, `opening_or_cut`, `shape_profile`, and `refinement_stage` where they already match the shipped verifier substrate
- staged checkpoint payloads can surface architecture blockers with typed gate ids, evidence requirements, and recommended bounded tools on the current checkpoint/truth envelopes
- unit owner lanes prove the new vocabulary, template merge behavior, and relation semantics on the existing contract/verifier/spatial seams

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
  - `opening_or_cut`
  - `shape_profile`
  - `proportion_ratio`
  - `symmetry_pair`
  - `refinement_stage`
- keep building-specific findings on the existing staged truth/checkpoint
  surfaces
- treat the current building templates and `opening_or_cut` verifier path as
  the baseline; this leaf extends and specializes them instead of replacing
  them with a parallel architecture-only contract

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
- add new building-specific schema fields only through typed contract
  extensions; keep public payloads schema-first and reject unknown fields where
  the contract is meant to stay strict
- limit compatibility shims to explicit legacy aliases already normalized by
  the intake helpers; do not add prose-only fallback keys for new
  architecture-specific fields

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_quality_gate_contracts.py`
- `tests/unit/adapters/mcp/test_quality_gate_intake.py`
- `tests/unit/adapters/mcp/test_quality_gate_verifier.py`
- `tests/unit/tools/scene/test_scene_contracts.py`
- `tests/unit/tools/scene/test_spatial_graph_service.py`

## Docs To Update

- `_docs/_PROMPTS/README.md`
- likely new `_docs/_PROMPTS/REFERENCE_GUIDED_ARCHITECTURE_BUILD.md`
- `_docs/_MCP_SERVER/README.md`
- `_docs/_TESTS/README.md`

## Changelog Impact

- Add a `_docs/_CHANGELOG/*` entry when the first architecture contract slice
  ships.

## Validation Commands

- `git diff --check`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_quality_gate_contracts.py tests/unit/adapters/mcp/test_quality_gate_intake.py tests/unit/adapters/mcp/test_quality_gate_verifier.py tests/unit/tools/scene/test_scene_contracts.py tests/unit/tools/scene/test_spatial_graph_service.py -q`

## Status / Board Update

- keep `_docs/_TASKS/README.md` unchanged while this leaf remains open
- when this leaf lands, update `TASK-136-01` and the parent `TASK-136`
  progress notes/status summary together so later leaves inherit the corrected
  contract baseline
