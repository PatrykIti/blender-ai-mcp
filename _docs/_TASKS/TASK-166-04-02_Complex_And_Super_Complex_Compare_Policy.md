# TASK-166-04-02: Complex And Super-Complex Compare Policy

**Parent:** [TASK-166-04](./TASK-166-04_Complexity_Tiers_And_Multi_Reference_Scaling_Policy.md)  
**Status:** ✅ Done
**Priority:** 🔴 High
**Objective:** Define the packet scheduler and synthesis posture for complex and super-complex 6-12 image compare runs.

## Completion Summary

- complex and super-complex staged compare now resolves a packet image policy
  from the effective runtime `max_images` budget before executing packet-local
  vision requests
- super-complex runs split large same-view reference sets into bounded
  reference slices, keep per-packet image counts within `VISION_MAX_IMAGES`,
  and surface the split through additive `compare_diagnostics.budget_notes`
- tight image budgets preserve the focused stage capture before optional
  context captures, then mark impossible 1-image budgets as explicit packet
  uncertainty instead of silently overfilling the runner request
- mixed clean vs corrective/uncertain packet statuses now add a synthesis
  conflict note so clients do not treat packet synthesis as stronger than the
  bounded packet evidence

## Repository Touchpoints

- `server/adapters/mcp/areas/reference.py`
- `server/adapters/mcp/areas/reference_planner.py`
- `server/adapters/mcp/areas/reference_compare_packets.py`
- `tests/unit/adapters/mcp/test_reference_images.py`
- `tests/unit/adapters/mcp/test_reference_compare_packets.py`
- `README.md`
- `_docs/AVAILABLE_TOOLS_SUMMARY.md`
- `_docs/_MCP_SERVER/README.md`
- `_docs/_VISION/README.md`
- `_docs/_TESTS/README.md`

## Implementation Notes

- Large runs should default to:
  - one image or a small paired packet at a time
  - packet synthesis afterward
  - conflict/uncertainty reporting across packets
- Likely implementation shape:
  - one `resolve_complex_compare_policy(...)` / packet-scheduler helper on the
    complexity-policy seam
  - one synthesis path that can surface packet conflict into both additive
    staged diagnostics and compact `reference_orchestrator_feedback`
- The complex/super-complex packet scheduler must respect the live
  `runtime.max_images` limiter enforced by
  `server/adapters/mcp/vision/config.py` /
  `server/adapters/mcp/vision/runner.py`, or else land in lockstep with the
  `TASK-166-05` runtime budget changes.
- Error cases to call out:
  - packet budget overflow on 6-12 image runs
  - contradictory packet conclusions that must degrade into explicit
    uncertainty instead of silent merge
  - complex-tier ambiguity that should fall back to the more conservative
    packet schedule

## Acceptance Criteria

- 6-12 image runs stay bounded and explain packet conflicts explicitly
- synthesis remains short enough for generic LLM operators
- packet conflict/uncertainty reporting can feed both additive staged compare
  diagnostics and the compact `reference_orchestrator_feedback` summary

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_reference_images.py`
- `tests/unit/adapters/mcp/test_contract_payload_parity.py`
- `tests/unit/adapters/mcp/test_public_surface_docs.py`
- complex-tier packet-scheduler coverage for conflict/uncertainty projection
- `tests/e2e/integration/test_guided_gate_state_transport.py` when complex-tier
  packet conflict/uncertainty changes staged compare / iterate payloads
- add a dedicated staged multi-reference scaling lane under
  `tests/e2e/vision/`, likely `test_reference_stage_multi_reference_scaling.py`,
  before closeout
- the repo-supported Blender runner when the packet scheduler changes real
  multi-reference runtime behavior beyond those focused owner lanes
- optional harness/model-eval suites may remain supplementary smoke coverage,
  but they are not the primary staged-owner proof lane for this leaf

## Docs To Update

- `_docs/_VISION/README.md`
- `_docs/_MCP_SERVER/README.md`
- `README.md`
- `_docs/AVAILABLE_TOOLS_SUMMARY.md`
- `_docs/_TESTS/README.md`

## Changelog Impact

- shipped in `_docs/_CHANGELOG/335-2026-05-10-task-166-super-complex-packet-scheduling.md`

## Status / Board Update

- parent `TASK-166-04` is now ready to close because both simple and
  complex/super-complex policy leaves are complete
- later public transparency cleanup closed under `TASK-166-06`; changelog
  `336` closed the promoted `TASK-166` umbrella

## Validation Commands

- `git diff --check`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_reference_compare_packets.py -q`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_reference_images.py -q -k "super_complex_packets or deterministic_stage_set or packet_local_target"`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_reference_images.py tests/unit/adapters/mcp/test_reference_compare_packets.py tests/unit/adapters/mcp/test_contract_payload_parity.py tests/unit/adapters/mcp/test_public_surface_docs.py -q`
- `PYTHONPATH=. poetry run pytest ./tests/unit`
- `PYTHONPATH=. poetry run python scripts/run_e2e_tests.py`
- `poetry run ruff check server/adapters/mcp/areas/reference_compare_packets.py server/adapters/mcp/areas/reference.py server/adapters/mcp/areas/reference_planner.py tests/unit/adapters/mcp/test_reference_compare_packets.py tests/unit/adapters/mcp/test_reference_images.py`
