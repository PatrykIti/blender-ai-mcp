# TASK-128-03-01: Runtime Boundary, Packaging, and Opt-In Policy

**Parent:** [TASK-128-03](./TASK-128-03_Optional_Part_Segmentation_Sidecar_And_Part_Aware_Perception.md)
**Status:** ⏳ To Do
**Priority:** 🔴 High

## Objective

Define how the segmentation sidecar is packaged, enabled, and isolated so it
never becomes a hidden default dependency of the core MCP server.

## Current Runtime Baseline

`server/infrastructure/config.py` currently exposes bounded vision runtime
configuration only. This leaf should keep segmentation as a separate,
explicitly opt-in concern rather than overloading the existing default vision
path.

## Repository Touchpoints

- `server/infrastructure/config.py`
- `server/adapters/mcp/vision/`
- `_docs/_VISION/README.md`
- `_docs/_ROUTER/RESPONSIBILITY_BOUNDARIES.md`

## Acceptance Criteria

- the sidecar is explicitly opt-in
- runtime/dependency isolation is documented before provider-specific work
- failure or absence of the sidecar does not break normal guided sessions
- any future config/env surface defaults to "off" and preserves the current
  lightweight guided baseline

## Docs To Update

- `_docs/_VISION/README.md`
- `_docs/_ROUTER/RESPONSIBILITY_BOUNDARIES.md`

## Changelog Impact

- include in the parent slice changelog entry when shipped

## Execution Structure

| Order | Subtask | Purpose |
|------|---------|---------|
| 1 | [TASK-128-03-01-01](./TASK-128-03-01-01_Sidecar_Packaging_And_Dependency_Isolation.md) | Define deployment/package isolation for the sidecar runtime |
| 2 | [TASK-128-03-01-02](./TASK-128-03-01-02_Opt_In_Execution_Policy_And_Fallback_Behavior.md) | Define enablement rules, fallback behavior, and disable-safe UX |
