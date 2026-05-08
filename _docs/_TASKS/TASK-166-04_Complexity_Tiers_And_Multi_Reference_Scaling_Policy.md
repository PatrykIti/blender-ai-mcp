# TASK-166-04: Complexity Tiers And Multi-Reference Scaling Policy

**Parent:** [TASK-166](./TASK-166_Hierarchical_Reference_Compare_Perceived_Evidence_And_Budget_Control.md)  
**Status:** ⏳ To Do  
**Priority:** 🔴 High
**Objective:** Define how the compare family scales from simple models to complex and super-complex 6-12 image runs without one static request shape.

## Repository Touchpoints

- `server/adapters/mcp/areas/reference.py`
- `server/adapters/mcp/areas/reference_planner.py`
- `server/adapters/mcp/contracts/reference.py`
- `server/application/services/`
- `server/adapters/mcp/vision/config.py`
- `server/adapters/mcp/vision/runner.py`
- `tests/unit/adapters/mcp/test_reference_images.py`
- `tests/e2e/vision/`

## Implementation Notes

- Complexity policy should choose:
  - packet count
  - packet size
  - synthesis strategy
  - optional sidecar usage threshold
- Tier resolution and packet-policy selection should live in a dedicated helper
  or application-service seam once the policy stops being trivial; do not let
  `reference_compare_stage_checkpoint(...)` absorb the long-term policy matrix.
- Packet scheduling for 6-12 image runs must stay within `runtime.max_images`
  from `server/adapters/mcp/vision/config.py` /
  `server/adapters/mcp/vision/runner.py` or explicitly coordinate with
  `TASK-166-05` before widening runtime limits.

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

## Pseudocode

```text
tier = resolve_compare_complexity(selected_references, assembled_scope, captures)
policy = resolve_compare_policy_for_tier(tier)
packet_plan = build_packet_plan(policy, selected_references, assembled_scope)
staged_compare = assemble_compare_from_packet_plan(packet_plan)
```

## Runtime / Security Contract Notes

- Tier selection must stay deterministic and server-owned; the public staged
  response shape remains one family regardless of tier.
- Multi-reference scaling proof must validate the real staged compare owner
  seam, not only the compact transport wrapper.
- When rich packet detail is omitted, failure/uncertainty still needs an
  explicit surfaced path through the existing staged contracts.

## Acceptance Criteria

- simple, complex, and super-complex tiers use different packet/synthesis
  defaults
- 6-12 image runs no longer imply one monolithic compare request
- uncertainty from complex packet runs can propagate into the compact feedback
  layer without forcing raw packet replay

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_reference_images.py`
- `tests/unit/adapters/mcp/test_contract_payload_parity.py`
- `tests/unit/adapters/mcp/test_public_surface_docs.py`
- `tests/unit/router/application/test_router_contracts.py`
- packet-policy unit coverage in `reference_planner.py`
- add a dedicated staged multi-reference scaling lane under
  `tests/e2e/vision/`, likely `test_reference_stage_multi_reference_scaling.py`,
  plus any supporting fixtures needed for 6-12 image packet scheduling proof
- integration proof when tiered packet scaling changes staged compare / iterate
  payloads
- optional harness/model-eval suites such as
  `test_reference_guided_creature_comparison.py` and
  `test_real_view_variant_model_comparison.py` may remain supplementary smoke
  coverage, but they are not the primary staged-owner proof lane for closeout

## Docs To Update

- `_docs/_VISION/README.md`
- `_docs/_MCP_SERVER/README.md`
- `README.md`
- `_docs/AVAILABLE_TOOLS_SUMMARY.md`
- `_docs/_TESTS/README.md`

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
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_contract_payload_parity.py -q`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_public_surface_docs.py -q`
- `PYTHONPATH=. poetry run pytest tests/unit/router/application/test_router_contracts.py -q`
- `PYTHONPATH=. poetry run pytest tests/e2e/integration/test_guided_gate_state_transport.py -q`
- after adding the dedicated multi-reference scaling lane, run:
  `PYTHONPATH=. poetry run pytest tests/e2e/vision/test_reference_stage_multi_reference_scaling.py -q`
- `poetry run pytest ./tests/unit`
- `poetry run python scripts/run_e2e_tests.py`
