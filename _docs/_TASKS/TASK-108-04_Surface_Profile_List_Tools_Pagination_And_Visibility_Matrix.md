# TASK-108-04: Surface Profile, List Tools, Pagination, and Visibility Matrix

**Parent:** [TASK-108](./TASK-108_Coverage_Expansion_For_Contracts_MCP_Areas_RPC_And_Surface_Runtime.md)  
**Status:** ⬜ To Do  
**Priority:** 🟡 Medium  
**Depends On:** TASK-083, TASK-093, TASK-105

---

## Objective

Expand runtime-facing FastMCP tests so profile shaping, `list_tools`, component pagination, and session visibility are validated together as one regression matrix.

---

## Repository Touchpoints

- `server/adapters/mcp/factory.py`
- `server/adapters/mcp/surfaces.py`
- `server/adapters/mcp/guided_mode.py`
- `server/adapters/mcp/session_capabilities.py`
- `server/adapters/mcp/transforms/visibility.py`
- `server/adapters/mcp/transforms/visibility_policy.py`
- `tests/unit/adapters/mcp/test_server_factory.py`
- `tests/unit/adapters/mcp/test_search_surface.py`
- `tests/unit/adapters/mcp/test_pagination_policy.py`
- `tests/unit/adapters/mcp/test_visibility_policy.py`
- `tests/unit/adapters/mcp/test_guided_mode.py`
- `tests/unit/adapters/mcp/test_legacy_flat_pagination_compat.py`

---

## Planned Work

- add cross-profile `list_tools` assertions for `legacy-flat`, `llm-guided`, `internal-debug`, and `code-mode-pilot`
- cover first-page and cursor behavior for component pagination separately from tool payload pagination
- verify that session phase updates and visibility application remain aligned with the actual listed tool set
- add hidden-tool and shaped-surface regression checks so discovery exposure matches visibility policy

---

## Acceptance Criteria

- surface-profile tests cover representative presence/absence sets across the supported profiles
- `legacy-flat` keeps its compatibility-first listing behavior while shaped surfaces keep constrained exposure
- visibility diagnostics, applied session visibility, and actual `list_tools` output stay consistent
- pagination regressions on the first page or cursor emission are caught by targeted unit tests
