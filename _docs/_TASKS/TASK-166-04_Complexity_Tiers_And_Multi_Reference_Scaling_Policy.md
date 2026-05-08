# TASK-166-04: Complexity Tiers And Multi-Reference Scaling Policy

**Parent:** [TASK-166](./TASK-166_Hierarchical_Reference_Compare_Perceived_Evidence_And_Budget_Control.md)  
**Status:** ⏳ To Do  
**Priority:** 🔴 High
**Objective:** Define how the compare family scales from simple models to complex and super-complex 6-12 image runs without one static request shape.

## Repository Touchpoints

- `server/adapters/mcp/areas/reference.py`
- `server/adapters/mcp/areas/reference_planner.py`
- `server/adapters/mcp/contracts/reference.py`
- `tests/unit/adapters/mcp/test_reference_images.py`
- `tests/e2e/vision/`

## Implementation Notes

- Complexity policy should choose:
  - packet count
  - packet size
  - synthesis strategy
  - optional sidecar usage threshold

## Current Flow Integration

- The current staged compare tools keep the same public names, but complexity
  policy determines how many packeted compare calls/slices happen under the
  hood before one final staged response is assembled.
- For 6-12 image sets, packeting should default to one image or one small
  paired packet at a time, then one short synthesis pass.
- Complexity policy should also determine how much packet detail is surfaced
  back to clients:
  - compact flows keep the orchestration read model short
  - rich or failure/uncertainty paths may surface additive packet diagnostics

## Acceptance Criteria

- simple, complex, and super-complex tiers use different packet/synthesis
  defaults
- 6-12 image runs no longer imply one monolithic compare request
- uncertainty from complex packet runs can propagate into the compact feedback
  layer without forcing raw packet replay

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_reference_images.py`
- packet-policy unit coverage in `reference_planner.py`
- selected `tests/e2e/vision/` or integration proof for multi-reference runtime
  scaling behavior

## Docs To Update

- `_docs/_VISION/README.md`
- `_docs/_MCP_SERVER/README.md`

## Changelog Impact

- include in the umbrella `_docs/_CHANGELOG/` entry when complexity-tier policy
  ships

## Status / Board Update

- keep parent `TASK-166` and this subtask aligned in `_docs/_TASKS/README.md`
- record whether simple/complex/super-complex policy all shipped together or
  whether any tier remains open as explicit follow-on work

## Validation Commands

- `git diff --check`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_reference_images.py -q`
- `PYTHONPATH=. poetry run pytest tests/e2e/integration/test_guided_gate_state_transport.py -q`
- `poetry run python scripts/run_e2e_tests.py`
