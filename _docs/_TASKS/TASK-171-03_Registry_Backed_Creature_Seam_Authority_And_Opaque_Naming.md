# TASK-171-03: Registry-Backed Creature Seam Authority And Opaque Naming

**Parent:** [TASK-171](./TASK-171_Creature_Attachment_First_Build_Contract_And_Structured_Vision_Handoff.md)
**Status:** ⏳ To Do
**Priority:** 🔴 High
**Objective:** Move required creature seam inference and attachment-pair matching toward `guided_part_registry` roles so guided creature truth still works when object names are opaque, abbreviated, or drift from the current heuristics, while preserving the already-shipped registry-first required-part gate matching path.
**Repository Touchpoints:** `server/application/services/spatial_graph.py`, `server/adapters/mcp/areas/reference.py`, `server/adapters/mcp/areas/reference_truth.py`, `server/adapters/mcp/transforms/quality_gate_verifier.py`, `server/adapters/mcp/guided_naming_policy.py`, `tests/unit/tools/scene/test_spatial_graph_service.py`, `tests/unit/adapters/mcp/test_quality_gate_verifier.py`, `tests/unit/adapters/mcp/test_router_elicitation.py`, `tests/unit/tools/test_handler_rpc_alignment.py`, `tests/e2e/tools/scene/test_scene_measure_tools.py`, `tests/e2e/vision/test_reference_stage_assembled_creature_attachment_truth.py`
**Acceptance Criteria:**
- required creature seams can be derived from registry-backed creature roles in guided sessions
- lexical name heuristics remain available as fallback for unguided or weakly registered scenes
- the already-shipped registry-first required-part gate matching path remains intact while seam inference stops depending entirely on lexical names
- gate verification and truth follow-up can still match attachment pairs correctly when object names do not spell out `head`, `body`, `tail`, `snout`, or limb names

## Implementation Notes

- required-part gate verification is already registry-first on the current
  verifier seam; do not reopen that landed path here
- the still-open gap is earlier:
  - the deterministic seam planner still classifies most creature parts from
    object names
  - required seam planning and attachment-pair inference do not consistently
    consume registry-backed creature roles
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
- `tests/unit/adapters/mcp/test_router_elicitation.py`
- `tests/unit/tools/test_handler_rpc_alignment.py`
- `tests/e2e/tools/scene/test_scene_measure_tools.py`
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
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_router_elicitation.py -q`
- `PYTHONPATH=. poetry run pytest tests/unit/tools/test_handler_rpc_alignment.py -q`
- `PYTHONPATH=. poetry run pytest tests/e2e/tools/scene/test_scene_measure_tools.py -q`
- `PYTHONPATH=. poetry run pytest tests/e2e/vision/test_reference_stage_assembled_creature_attachment_truth.py -q`
- `PYTHONPATH=. poetry run pytest ./tests/unit`
- `poetry run python scripts/run_e2e_tests.py`

## Validation Category

- deterministic seam inference and gate-matching proof
