# 137 - 2026-03-23: Legacy manual surface boundary

**Status**: ✅ Completed  
**Type**: Surface UX / Compatibility  
**Task**: TASK-110

---

## Summary

Split the old “legacy manual” bootstrap path away from `legacy-flat` and made it a
real `legacy-manual` surface profile.

This removes router/workflow namespace leakage from manual clients:

- no visible `router_*` tools that only answer with `status="disabled"`
- no visible `workflow_catalog` on the manual surface

---

## Changes

- Added `legacy-manual` as a first-class surface profile with only core tools and prompt assets.
- Kept `legacy-flat` as the broader legacy compatibility surface that still includes router/workflow tools.
- Updated local MCP and Claude allow-list config so the manual profile points at `legacy-manual`.
- Added regression coverage for the manual surface runtime namespace boundary.

---

## Files Modified (high level)

- `server/adapters/mcp/surfaces.py`
- `server/adapters/mcp/version_policy.py`
- `server/adapters/mcp/client_profiles.py`
- `server/adapters/mcp/transforms/visibility_policy.py`
- `.mcp.json`
- `.claude/settings.local.json`
- `README.md`
- `_docs/_MCP_SERVER/README.md`
- `_docs/AVAILABLE_TOOLS_SUMMARY.md`
- `tests/unit/adapters/mcp/*`

---

## Validation

- `poetry run pytest tests/unit/adapters/mcp/test_server_factory.py tests/unit/adapters/mcp/test_version_policy.py tests/unit/adapters/mcp/test_client_profiles.py tests/unit/adapters/mcp/test_pagination_policy.py tests/unit/adapters/mcp/test_visibility_policy.py tests/unit/adapters/mcp/test_surface_bootstrap.py tests/unit/adapters/mcp/test_delivery_strategy.py tests/unit/adapters/mcp/test_legacy_flat_pagination_compat.py -q`
