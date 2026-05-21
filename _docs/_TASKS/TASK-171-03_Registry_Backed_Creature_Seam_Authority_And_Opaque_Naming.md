# TASK-171-03: Registry-Backed Creature Seam Authority And Opaque Naming

**Parent:** [TASK-171](./TASK-171_Creature_Attachment_First_Build_Contract_And_Structured_Vision_Handoff.md)
**Status:** ⏳ To Do
**Priority:** 🔴 High
**Objective:** Move required creature seam inference and attachment-pair matching toward `guided_part_registry` roles so guided creature truth and gate matching still work when object names are opaque, abbreviated, or drift from the current heuristics.
**Repository Touchpoints:** `server/application/services/spatial_graph.py`, `server/adapters/mcp/areas/reference.py`, `server/adapters/mcp/areas/reference_truth.py`, `server/adapters/mcp/transforms/quality_gate_verifier.py`, `tests/unit/tools/scene/test_spatial_graph_service.py`, `tests/unit/adapters/mcp/test_quality_gate_verifier.py`, `tests/e2e/vision/test_reference_stage_assembled_creature_attachment_truth.py`
**Acceptance Criteria:**
- required creature seams can be derived from registry-backed creature roles in guided sessions
- lexical name heuristics remain available as fallback for unguided or weakly registered scenes
- gate verification and truth follow-up can still match attachment pairs correctly when object names do not spell out `head`, `body`, `tail`, `snout`, or limb names

## Implementation Notes

- the current deterministic seam path still classifies most creature parts from
  object names
- registry-backed creature role data already exists elsewhere in guided state,
  but required seam planning and gate matching do not consistently consume it
- the task should introduce one explicit precedence rule:
  1. registry-backed role/object mapping in active guided creature sessions
  2. lexical-name heuristics as fallback
- keep this creature-specific; do not inject fuzzy semantic matching into the
  general verifier
- preserve the current building and non-creature paths

## Pseudocode

```python
role_map = guided_registry_role_map(session.guided_part_registry)
creature_parts = resolve_creature_parts(
    object_names=scope.object_names,
    role_map=role_map,
    fallback=name_heuristics,
)
required_seams = build_required_creature_seams(creature_parts)
gate_match = resolve_gate_targets_with_registry_first(required_seams, gate_plan)
```

## Runtime / Security Contract Notes

- registry-backed seam authority only applies when a guided creature session has
  trustworthy part-role state
- fallback heuristics must remain deterministic and bounded; do not replace
  them with embedding- or prose-based matching
- do not let registry-backed role aliases create cross-domain ambiguity for
  buildings or unguided scenes

## Tests To Add/Update

- `tests/unit/tools/scene/test_spatial_graph_service.py`
- `tests/unit/adapters/mcp/test_quality_gate_verifier.py`
- `tests/e2e/vision/test_reference_stage_assembled_creature_attachment_truth.py`

## Docs To Update

- `_docs/_MCP_SERVER/README.md`
- `_docs/_VISION/README.md`

## Changelog Impact

- add/update the historical `_docs/_CHANGELOG/*` entry when this slice lands

## Validation Commands

- `git diff --check`
- `PYTHONPATH=. poetry run pytest tests/unit/tools/scene/test_spatial_graph_service.py -q`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_quality_gate_verifier.py -q`
- `PYTHONPATH=. poetry run pytest tests/e2e/vision/test_reference_stage_assembled_creature_attachment_truth.py -q`

## Validation Category

- deterministic seam inference and gate-matching proof
