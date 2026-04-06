# TASK-128-03-01-02: Opt-In Execution Policy and Fallback Behavior

**Parent:** [TASK-128-03-01](./TASK-128-03-01_Runtime_Boundary_Packaging_And_Opt_In_Policy.md)
**Status:** ✅ Done
**Priority:** 🔴 High

## Objective

Define the execution policy for when the segmentation sidecar may run and what
happens when it is disabled, unavailable, or rejected by policy.

## Repository Touchpoints

- `server/infrastructure/config.py`
- `server/adapters/mcp/vision/config.py`
- `server/adapters/mcp/vision/runtime.py`
- `_docs/_VISION/README.md`
- `_docs/_MCP_SERVER/MCP_CLIENT_CONFIG_EXAMPLES.md`

## Acceptance Criteria

- the sidecar has an explicit opt-in enablement model
- failure/unavailability falls back cleanly to the existing vision path
- sidecar enablement/fallback does not overload `VISION_EXTERNAL_CONTRACT_PROFILE`
  or the current external compare-provider selection path
- policy docs explain when the heavier path should and should not be used

## Docs To Update

- `_docs/_VISION/README.md`
- `_docs/_MCP_SERVER/MCP_CLIENT_CONFIG_EXAMPLES.md`

## Changelog Impact

- include in the parent slice changelog entry when shipped
