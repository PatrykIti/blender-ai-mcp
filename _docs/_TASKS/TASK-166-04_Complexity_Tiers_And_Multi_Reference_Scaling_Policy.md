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

## Acceptance Criteria

- simple, complex, and super-complex tiers use different packet/synthesis
  defaults
- 6-12 image runs no longer imply one monolithic compare request
