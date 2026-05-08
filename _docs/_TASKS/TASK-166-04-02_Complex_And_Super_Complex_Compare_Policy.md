# TASK-166-04-02: Complex And Super-Complex Compare Policy

**Parent:** [TASK-166-04](./TASK-166-04_Complexity_Tiers_And_Multi_Reference_Scaling_Policy.md)  
**Status:** ⏳ To Do  
**Priority:** 🔴 High
**Objective:** Define the packet scheduler and synthesis posture for complex and super-complex 6-12 image compare runs.

## Repository Touchpoints

- `server/adapters/mcp/areas/reference.py`
- `server/adapters/mcp/areas/reference_feedback.py`
- `server/adapters/mcp/areas/reference_planner.py`
- `server/adapters/mcp/contracts/reference.py`
- `server/adapters/mcp/vision/config.py`
- `server/adapters/mcp/vision/runner.py`
- `tests/unit/adapters/mcp/test_reference_images.py`
- `tests/e2e/integration/test_guided_gate_state_transport.py`
- `tests/e2e/vision/`

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
- `tests/unit/router/application/test_router_contracts.py`
- complex-tier packet-scheduler coverage for conflict/uncertainty projection
- `tests/e2e/integration/test_guided_gate_state_transport.py` when complex-tier
  packet conflict/uncertainty changes staged compare / iterate payloads
- create a dedicated staged multi-reference scaling lane, for example
  `tests/e2e/vision/test_reference_stage_multi_reference_scaling.py`, before
  closeout
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

- include in the umbrella `_docs/_CHANGELOG/` entry when complex and
  super-complex compare policy ships

## Status / Board Update

- keep parent `TASK-166` and this leaf aligned when complex-tier packet policy
  closes or splits into follow-on runtime work

## Validation Commands

- `git diff --check`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_reference_images.py -q`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_contract_payload_parity.py -q`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_public_surface_docs.py -q`
- `PYTHONPATH=. poetry run pytest tests/unit/router/application/test_router_contracts.py -q`
- `PYTHONPATH=. poetry run pytest tests/e2e/integration/test_guided_gate_state_transport.py -q`
- `poetry run python scripts/run_e2e_tests.py`
