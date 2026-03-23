# TASK-110: Legacy Manual Surface Boundary

**Priority:** 🟡 Medium  
**Category:** MCP / Surface UX  
**Estimated Effort:** Small  
**Dependencies:** None  
**Status:** ✅ Done

**Completion Summary:** Introduced a dedicated `legacy-manual` surface that exposes the broad manual tool catalog without router or workflow tools, so manual clients no longer see disabled router endpoints or read-only workflow helpers that are not actionable in that mode.

---

## Objective

Remove router/workflow abstraction leakage from the manual legacy client experience.

---

## Problem

The previous `blender-ai-mcp-legacy-manual` config still booted the `legacy-flat` surface and only disabled router behavior at runtime with `ROUTER_ENABLED=false`.

That caused two UX failures:

- router tools were still visible in the MCP namespace, but returned `status="disabled"`
- `workflow_catalog` stayed visible even though the manual surface had no router-driven execution path

For MCP clients, a listed tool is assumed to be usable. Exposing tools that are present-but-not-meaningful creates a surface-level abstraction leak.

---

## Solution

Add a separate bootstrap-time surface, `legacy-manual`, that:

- mounts the core tool provider
- mounts prompt assets
- does **not** mount router tools
- does **not** mount workflow catalog tools

Then point the local manual client config at `legacy-manual` instead of `legacy-flat`, and update local allow-lists/docs/tests accordingly.

---

## Repository Touchpoints

- `server/adapters/mcp/surfaces.py`
- `server/adapters/mcp/version_policy.py`
- `server/adapters/mcp/client_profiles.py`
- `server/adapters/mcp/transforms/visibility_policy.py`
- `.mcp.json`
- `.claude/settings.local.json`
- `README.md`
- `_docs/_MCP_SERVER/README.md`
- `_docs/AVAILABLE_TOOLS_SUMMARY.md`
- `tests/unit/adapters/mcp/`

---

## Acceptance Criteria

- `legacy-manual` exists as a first-class surface profile
- `legacy-manual` does not expose `router_*` or `workflow_catalog` in `tools/list`
- local manual client config uses `MCP_SURFACE_PROFILE=legacy-manual`
- local allow-lists for the manual client no longer include router/workflow tools
- regression coverage verifies the manual surface namespace boundary
