# TASK-166-04: Complexity Tiers And Multi-Reference Scaling Policy

**Parent:** [TASK-166](./TASK-166_Hierarchical_Reference_Compare_Perceived_Evidence_And_Budget_Control.md)  
**Status:** ✅ Done
**Priority:** 🔴 High
**Objective:** Define how the compare family scales from simple models to complex and super-complex 6-12 image runs without one static request shape.

## Completion Summary

- simple-tier compare keeps lightweight one-view or two-view packet plans and
  skips synthesis when a clean compact single packet is enough
- complex collection/object-set compare uses scope/view packets so active seam
  failures remain local to their target scope
- super-complex 6-12 image compare now slices large same-view reference sets
  into bounded packet-local chunks based on the effective runtime
  `VISION_MAX_IMAGES` limit before packet execution
- packet synthesis now reports mixed clean/corrective packet conclusions as
  explicit conflict uncertainty instead of silently collapsing them into one
  stronger verdict

## Repository Touchpoints

- `server/adapters/mcp/areas/reference.py`
- `server/adapters/mcp/areas/reference_planner.py`
- `server/adapters/mcp/contracts/reference.py`
- `server/adapters/mcp/areas/reference_compare_packets.py`
- `tests/unit/adapters/mcp/test_reference_images.py`
- `tests/unit/adapters/mcp/test_reference_compare_packets.py`

## Implementation Notes

- Complexity policy should choose:
  - packet count
  - packet size
  - synthesis strategy
  - optional sidecar usage threshold
- Tier resolution and packet-policy selection should live in a dedicated
  staged-compare helper seam once the policy stops being trivial; do not let
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

- shipped through incremental TASK-166 entries including
  `_docs/_CHANGELOG/335-2026-05-10-task-166-super-complex-packet-scheduling.md`

## Status / Board Update

- `TASK-166-04` is closed; no open direct complexity-tier leaves remain
- promoted `TASK-166` remains open for `TASK-166-06`

## Validation Commands

- `git diff --check`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_reference_compare_packets.py -q`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_reference_images.py -q -k "super_complex_packets or deterministic_stage_set or packet_local_target"`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_reference_images.py -q`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_contract_payload_parity.py -q`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_public_surface_docs.py -q`
- `PYTHONPATH=. poetry run pytest ./tests/unit`
- `PYTHONPATH=. poetry run python scripts/run_e2e_tests.py`
- `poetry run ruff check server/adapters/mcp/areas/reference_compare_packets.py server/adapters/mcp/areas/reference.py server/adapters/mcp/areas/reference_planner.py tests/unit/adapters/mcp/test_reference_compare_packets.py tests/unit/adapters/mcp/test_reference_images.py`
