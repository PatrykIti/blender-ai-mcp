# TASK-166-01-02: Scope-First Packet Planner

**Parent:** [TASK-166-01](./TASK-166-01_View_And_Scope_Packet_Compare_Family.md)  
**Status:** ✅ Done
**Priority:** 🔴 High
**Objective:** Plan compare packets by active scope clusters such as `Body + Head`, `Tail`, and `Ears` instead of always comparing the full assembled model.

## Completion Summary

- scope packet planning now groups common creature seams into semantic scope
  clusters such as `Body + Head`, `Tail`, and `Ears`
- complex staged compare runs now preserve both view and scope on packet-local
  diagnostics instead of dropping secondary views once focus pairs are present
- when truth follow-up does not provide explicit focus pairs, packet planning can
  still derive bounded scope clusters from the assembled target scope instead of
  falling back to one whole-model compare

## Repository Touchpoints

- `server/adapters/mcp/areas/reference.py`
- `server/adapters/mcp/areas/reference_planner.py`
- `tests/unit/adapters/mcp/test_reference_images.py`

## Implementation Notes

- Scope packets should align with current guided step, gate blockers, and active
  target scope.
- Likely implementation shape:
  - one `build_scope_packets(...)` helper on the compare-plan seam
  - one mapping from existing truth-pair / object-cluster data into packet-local
    scope groups
- Scope packets should map back to existing truth pairs/object clusters instead
  of inventing a second scope graph beside the staged compare truth bundle.
- Packet planning must remain generic across domains.

## Acceptance Criteria

- compare packets can isolate one blocker cluster
- large assembled models no longer force every compare to include every part
- scope packets identify the object cluster / truth-pair slice they own so later
  synthesis and feedback can attribute findings without guessing

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_reference_images.py`
- packet-plan unit coverage for scope-cluster mapping and blocker-driven packet
  selection

## Docs To Update

- `_docs/_VISION/README.md`
- `_docs/_MCP_SERVER/README.md`
- `README.md`
- `_docs/AVAILABLE_TOOLS_SUMMARY.md`
- `_docs/_TESTS/README.md`

## Changelog Impact

- include in the umbrella `_docs/_CHANGELOG/` entry when scope-first packet
  planning ships

## Status / Board Update

- keep parent `TASK-166` and this leaf aligned when scope-first planning closes
  or splits into follow-on work

## Validation Commands

- `git diff --check`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_reference_images.py -q`
- `poetry run pytest ./tests/unit`
- `poetry run python scripts/run_e2e_tests.py`
