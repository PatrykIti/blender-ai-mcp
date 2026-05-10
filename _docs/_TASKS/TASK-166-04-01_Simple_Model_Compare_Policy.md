# TASK-166-04-01: Simple Model Compare Policy

**Parent:** [TASK-166-04](./TASK-166-04_Complexity_Tiers_And_Multi_Reference_Scaling_Policy.md)  
**Status:** ✅ Done
**Priority:** 🔴 High
**Objective:** Define the minimal compare strategy for simple models so easy cases do not pay the overhead of a super-complex packet pipeline.

## Completion Summary

- simple-tier staged compare now emits one bounded packet per captured view,
  typically one front packet or one front + one side packet
- clean compact single-packet runs can stay slim again by omitting additive
  `compare_diagnostics`, while ranking/extraction uncertainty still forces that
  surface back on demand
- simple-tier planning no longer invents mixed front+side packets from
  reference-only view coverage when the current staged capture set does not
  contain those views

## Repository Touchpoints

- `server/adapters/mcp/areas/reference_planner.py`
- `server/adapters/mcp/areas/reference.py`
- `tests/unit/adapters/mcp/test_reference_images.py`

## Implementation Notes

- The simple tier should stay on the existing staged compare path with the
  smallest packet plan that still preserves deterministic truth + compare
  provenance.
- Likely implementation shape:
  - one `resolve_simple_compare_policy(...)` helper on the complexity-policy
    seam
  - one fast path that keeps packet count minimal and skips synthesis unless the
    first packet produces conflict or uncertainty
- Prefer one view packet or one small paired packet first; avoid introducing a
  synthesis pass unless packet conflict or ambiguity makes it necessary.
- Keep the emitted staged response shape identical to larger tiers so callers do
  not need a second contract path for simple runs.
- Error cases to call out:
  - ambiguous tier classification should fall upward to the more conservative
    packet policy
  - a single clean packet should not still pay for a synthesis pass just because
    richer tiers need one

## Acceptance Criteria

- one or two reference images can stay on a lightweight packet plan
- simple models do not require unnecessary synthesis stages
- simple runs may omit rich packet diagnostics on clean paths while still
  surfacing failure/uncertainty additively when needed

## Validation Commands

- `git diff --check`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_reference_images.py -q`
- `poetry run pytest ./tests/unit`
- `poetry run python scripts/run_e2e_tests.py`

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_reference_images.py`
- simple-tier packet-policy coverage for minimal packet count and synthesis skip
  behavior

## Docs To Update

- `_docs/_VISION/README.md`
- `_docs/_MCP_SERVER/README.md`
- `README.md`
- `_docs/AVAILABLE_TOOLS_SUMMARY.md`
- `_docs/_TESTS/README.md`

## Changelog Impact

- include in the umbrella `_docs/_CHANGELOG/` entry when the simple compare
  tier ships

## Status / Board Update

- keep parent `TASK-166` and this leaf aligned when the simple compare policy
  closes or is superseded by a refined tier split
