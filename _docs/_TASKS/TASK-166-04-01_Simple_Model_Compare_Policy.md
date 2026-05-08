# TASK-166-04-01: Simple Model Compare Policy

**Parent:** [TASK-166-04](./TASK-166-04_Complexity_Tiers_And_Multi_Reference_Scaling_Policy.md)  
**Status:** ⏳ To Do  
**Priority:** 🔴 High
**Objective:** Define the minimal compare strategy for simple models so easy cases do not pay the overhead of a super-complex packet pipeline.

## Repository Touchpoints

- `server/adapters/mcp/areas/reference_planner.py`
- `server/adapters/mcp/areas/reference.py`
- `tests/unit/adapters/mcp/test_reference_images.py`

## Implementation Notes

- The simple tier should stay on the existing staged compare path with the
  smallest packet plan that still preserves deterministic truth + compare
  provenance.
- Prefer one view packet or one small paired packet first; avoid introducing a
  synthesis pass unless packet conflict or ambiguity makes it necessary.
- Keep the emitted staged response shape identical to larger tiers so callers do
  not need a second contract path for simple runs.

## Acceptance Criteria

- one or two reference images can stay on a lightweight packet plan
- simple models do not require unnecessary synthesis stages
- simple runs may omit rich packet diagnostics on clean paths while still
  surfacing failure/uncertainty additively when needed

## Validation Commands

- `git diff --check`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_reference_images.py -q`
