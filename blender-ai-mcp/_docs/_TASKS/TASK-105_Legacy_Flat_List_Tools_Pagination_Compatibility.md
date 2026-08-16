# TASK-105: Legacy-Flat List Tools Pagination Compatibility

**Priority:** 🟡 Medium  
**Category:** FastMCP Platform / Client Compatibility  
**Estimated Effort:** Small  
**Dependencies:** TASK-083, TASK-084  
**Status:** ✅ Done

**Completion Summary:** `legacy-flat` now defaults to a single-page tool catalog large enough to expose the full current MCP surface without returning `nextCursor` on the first `tools/list` call. This preserves broad compatibility for clients that do not correctly follow MCP pagination while leaving `llm-guided` and other shaped surfaces unchanged.

---

## Objective

Prevent partial first-page tool catalogs on the `legacy-flat` surface for clients that ignore `nextCursor`.

---

## Problem

The current `legacy-flat` surface exposes more tools than its configured `list_page_size`.
Standards-compliant clients should keep following `nextCursor`, but some clients stop after page 1.

In practice this means:

- the client sees only the first 100 tools
- later capability families such as `modeling_*` disappear from the user-visible list
- the server is correct, but the effective UX is misleading and incomplete

---

## Solution

Increase the default `legacy-flat` component `list_page_size` so the full current catalog fits in one page.

This is an explicit compatibility workaround, not a change to the MCP pagination contract itself.

Rules:

- apply the workaround only to `legacy-flat`
- leave `llm-guided` and the shaped surfaces unchanged
- keep the real MCP pagination implementation intact

---

## Repository Touchpoints

- `server/adapters/mcp/surfaces.py`
- `tests/unit/adapters/mcp/test_pagination_policy.py`
- `tests/unit/adapters/mcp/test_server_factory.py`
- `README.md`
- `_docs/_MCP_SERVER/README.md`

---

## Acceptance Criteria

- first `tools/list` page on `legacy-flat` contains the full current catalog
- `legacy-flat` no longer emits `nextCursor` for the current tool count
- shaped surfaces keep their existing pagination policy
