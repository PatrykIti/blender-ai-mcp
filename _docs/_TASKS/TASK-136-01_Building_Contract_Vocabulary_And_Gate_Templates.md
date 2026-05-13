# TASK-136-01: Building Contract, Vocabulary, And Gate Templates

**Status:** ✅ Done
**Priority:** 🔴 High
**Parent:** [TASK-136](./TASK-136_Reference_Guided_Architecture_And_Building_Reconstruction.md)
**Objective:** Extend the shipped generic building gate/reference substrate with architecture-specific target classes, vocabulary, stage vocabulary, and gate templates for shell, openings, supports, roof form, and facade rhythm on top of the existing `TASK-157` substrate.
**Repository Touchpoints:** `server/adapters/mcp/contracts/quality_gates.py`, `server/adapters/mcp/contracts/reference.py`, `server/adapters/mcp/contracts/scene.py`, `server/adapters/mcp/guided_naming_policy.py`, `server/adapters/mcp/transforms/quality_gate_verifier.py`, `server/adapters/mcp/areas/reference.py`, `server/adapters/mcp/areas/reference_compare_packets.py`, `server/adapters/mcp/areas/reference_checkpoint_compare.py`, `server/adapters/mcp/areas/reference_feedback.py`, `server/adapters/mcp/areas/reference_images_runtime.py`, `server/adapters/mcp/areas/reference_silhouette.py`, `server/adapters/mcp/areas/reference_understanding.py`, `server/adapters/mcp/areas/reference_truth.py`, `server/adapters/mcp/session_capabilities_bootstrap.py`, `server/adapters/mcp/session_capabilities_state.py`, `server/adapters/mcp/session_capabilities_runtime_glue.py`, `server/application/services/spatial_graph.py`, `server/adapters/mcp/areas/scene_spatial_graph.py`, `_docs/_PROMPTS/README.md`, `_docs/_PROMPTS/REFERENCE_GUIDED_ARCHITECTURE_BUILD.md`, `tests/unit/adapters/mcp/test_quality_gate_contracts.py`, `tests/unit/adapters/mcp/test_quality_gate_intake.py`, `tests/unit/adapters/mcp/test_quality_gate_verifier.py`, `tests/unit/adapters/mcp/test_guided_naming_policy.py`, `tests/unit/adapters/mcp/test_reference_compare_packets.py`, `tests/unit/adapters/mcp/test_reference_images.py`, `tests/unit/adapters/mcp/test_contract_payload_parity.py`, `tests/e2e/vision/test_reference_understanding_runtime_surface.py`, `tests/e2e/vision/test_reference_stage_truth_handoff.py`, `tests/e2e/vision/test_reference_stage_silhouette_contract.py`, `tests/e2e/vision/test_reference_stage_multi_reference_scaling.py`, `tests/unit/tools/scene/test_scene_contracts.py`, `tests/unit/tools/scene/test_spatial_graph_service.py`
**Acceptance Criteria:**
- building-oriented goal or RU intake can normalize shell/opening/roof/support/facade-rhythm expectations onto the existing generic gate vocabulary without inventing an architecture-only gate system
- the architecture templates explicitly reuse current gate types such as `required_part`, `attachment_seam`, `support_contact`, `opening_or_cut`, `shape_profile`, and `refinement_stage` where they already match the shipped verifier substrate
- staged checkpoint payloads can surface architecture blockers with typed gate ids, evidence requirements, and recommended bounded tools on the current checkpoint/truth envelopes
- the new vocabulary, template merge behavior, and relation semantics fit the current contract/verifier/spatial seams without requiring ad hoc building-only fallback paths
- the staged checkpoint/truth contract changes stay aligned across the public reference/checkpoint payload surfaces instead of landing only in internal helper types

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
  the baseline; this subtask extends and specializes them instead of replacing
  them with a parallel architecture-only contract
- keep guided naming in sync when adding or renaming shell/opening/support/roof
  roles by updating `server/adapters/mcp/guided_naming_policy.py` and
  `tests/unit/adapters/mcp/test_guided_naming_policy.py`
- keep plan/elevation/facade checkpoint evidence on the existing `TASK-166`
  packet path by extending `server/adapters/mcp/areas/reference_compare_packets.py`
  and staged `compare_diagnostics` only when architecture changes affect packet
  planning, evidence refs, or synthesis

## Completion Summary

Completed on 2026-05-12. The shipped slice keeps architecture vocabulary on the
existing building/gate/truth seams:

- added building templates for `wall_shell`, `roof_wall`, facade openings,
  facade rhythm, and optional support contact in `quality_gates.py`
- extended guided naming for `wall_shell`, `opening_grid`, expanded roof
  wording, and architecture support terms
- added `opening_wall` to the scene contract and to spatial/staged truth
  attachment semantics
- extended architecture packet labels for facade/opening, roofline, and support
  scopes on `reference_compare_packets.py`

## Intended Owner Flow

```python
templates = templates_for_domain_profile("building")
templates.extend(architecture_domain_templates_for_target_class(target_class))

plan = normalize_gate_plan(proposal, domain_profile="building", templates=templates)
verified_plan = verify_gate_plan_with_relation_graph(
    plan,
    scene_relation_graph_payload,
    guided_part_registry=session.guided_part_registry,
)
```

If this slice needs new helper functions, define them in the owning modules above
instead of introducing prose-only helper names. Likely additions are a small
architecture template builder in `quality_gates.py`, building-role naming specs
in `guided_naming_policy.py`, and relation/truth helpers in
`spatial_graph.py` / `reference_truth.py`.

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
- `tests/unit/adapters/mcp/test_guided_naming_policy.py`
- `tests/unit/adapters/mcp/test_reference_compare_packets.py`
- `tests/unit/adapters/mcp/test_reference_images.py`
- `tests/unit/adapters/mcp/test_contract_payload_parity.py`
- `tests/e2e/vision/test_reference_understanding_runtime_surface.py`
- `tests/e2e/vision/test_reference_stage_truth_handoff.py`
- `tests/e2e/vision/test_reference_stage_silhouette_contract.py`
- `tests/e2e/vision/test_reference_stage_multi_reference_scaling.py`
- `tests/unit/tools/scene/test_scene_contracts.py`
- `tests/unit/tools/scene/test_spatial_graph_service.py`

## Docs To Update

- `_docs/_PROMPTS/README.md`
- `_docs/_PROMPTS/REFERENCE_GUIDED_ARCHITECTURE_BUILD.md`
- `_docs/_MCP_SERVER/README.md`
- `_docs/_TESTS/README.md`
- `_docs/_CHANGELOG/README.md`

## Changelog Impact

- Historical closeout entry
  `_docs/_CHANGELOG/348-2026-05-12-task-136-architecture-guided-reconstruction.md`
  was added and indexed.

## Validation Commands

- `git diff --check`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_quality_gate_contracts.py tests/unit/adapters/mcp/test_quality_gate_intake.py tests/unit/adapters/mcp/test_quality_gate_verifier.py tests/unit/adapters/mcp/test_reference_images.py tests/unit/adapters/mcp/test_contract_payload_parity.py tests/unit/tools/scene/test_scene_contracts.py tests/unit/tools/scene/test_spatial_graph_service.py -q`
- `poetry run pytest ./tests/unit`
- `poetry run pre-commit run --all-files --show-diff-on-failure`
- `poetry run python scripts/run_e2e_tests.py`
- `PYTHONPATH=. poetry run pytest tests/e2e/vision/test_reference_understanding_runtime_surface.py tests/e2e/vision/test_reference_stage_truth_handoff.py tests/e2e/vision/test_reference_stage_silhouette_contract.py -q` (supplemental focused Blender-backed lane while iterating; closeout still uses the full repo-supported runner above)

## Status / Board Update

- closed with parent `TASK-136` on 2026-05-12
- validation is recorded in `TASK-136-03` and changelog entry
  `348-2026-05-12-task-136-architecture-guided-reconstruction.md`
