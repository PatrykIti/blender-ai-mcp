# TASK-167-02-02: Tool Proxy And Visibility Debug Profile Instrumentation

**Status:** ⏳ To Do
**Priority:** 🔴 High
**Parent:** [TASK-167-02](./TASK-167-02_Runtime_Instrumentation_And_Targeted_Log_Routing.md)
**Objective:** Add bounded `tools` and `visibility` debug instrumentation to the existing `call_tool(...)` proxy and visibility transaction/audit seams so operators can diagnose contract mismatches, hidden-tool recovery, and visibility churn directly from the Docker/server terminal.
**Repository Touchpoints:** `server/adapters/mcp/discovery/search_surface.py`, `server/adapters/mcp/visibility_runtime.py`, `server/adapters/mcp/guided_contract.py`, `tests/unit/adapters/mcp/test_search_surface.py`, `tests/unit/adapters/mcp/test_visibility_runtime.py`, `tests/e2e/integration/test_guided_streamable_spatial_support.py`, `tests/e2e/integration/test_guided_surface_contract_parity.py`
**Acceptance Criteria:**
- `debug=tools` surfaces proxy name resolution, canonical argument keys, compatibility normalization, and hidden-tool recovery classification without logging raw sensitive payloads
- `debug=visibility` surfaces visibility txn start/finish, expected vs observed tool-set summaries, and audit drift in one consistent scope
- operators can distinguish “proxy arg mismatch”, “tool hidden due to spatial refresh”, and “visibility churn after step change” from the normal Docker/server terminal
- logs stay bounded and do not dump full tool catalogs or raw content blocks by default

## Current Owner / Likely Edit Map

| Path | Current owner seam | Likely edit anchors | Why this leaf owns it |
|------|--------------------|---------------------|-----------------------|
| `server/adapters/mcp/discovery/search_surface.py` | `BlenderDiscoverySearchTransform._make_call_tool()` | lines 329-430 | call-tool proxy behavior and current log markers already live here |
| `server/adapters/mcp/visibility_runtime.py` | `run_visibility_transaction(...)`, `audit_list_tools_snapshot(...)` | lines 137-229 | visibility txn/audit summaries are already owned here |
| `server/adapters/mcp/guided_contract.py` | `canonicalize_guided_tool_arguments(...)` and tool-specific compatibility shims | lines around the public dispatcher and per-tool canonicalizers | tool-profile diagnostics need to classify compatibility normalization against the real canonicalization owner |
| `tests/unit/adapters/mcp/test_search_surface.py` | proxy proof lane | current proxy log assertion around line 1153 and hidden-tool recovery around lines 1903-2032 | unit proof for proxy/visibility debug belongs here |
| `tests/unit/adapters/mcp/test_visibility_runtime.py` | visibility owner lane | current transaction/audit tests | direct visibility-profile proof belongs here too |
| `tests/e2e/integration/test_guided_streamable_spatial_support.py` | Streamable guided proof lane | current hidden-tool / refresh-barrier transport surface | integration proof for visibility churn and hidden-tool diagnosis lives here |
| `tests/e2e/integration/test_guided_surface_contract_parity.py` | surface parity proof lane | current visible-vs-usable drift surface | ensures debug output does not contradict the shaped guided contract |

## Implementation Notes

- distinguish clearly between:
  - compatibility alias normalized
  - proxy call accepted
  - hidden due to spatial refresh
  - hidden due to phase/surface visibility
  - visibility audit mismatch
- prefer concise stable markers over dumping full resolved payloads
- keep `call_tool(...)` public behavior unchanged; this leaf is about diagnosis,
  not changing proxy semantics

## Pseudocode

```python
if debug_scope_enabled("tools"):
    logger.info("[TOOLS_DEBUG] proxy_call name=%s canonical_keys=%s aliases=%s", name, keys, used_aliases)

if debug_scope_enabled("visibility"):
    logger.info("[VISIBILITY_DEBUG] txn phase=%s step=%s expected=%d", phase, step, expected_count)
```

## Runtime / Security Contract Notes

- no raw content blocks, no secret-bearing arguments, and no unbounded tool list
  dumps in normal logs
- visibility/tool debug must not bypass existing fail-closed behavior

## Error Cases To Cover

- legacy proxy arguments normalized into canonical public form
- hidden tool because of `spatial_refresh_required`
- hidden tool because of phase/surface visibility rather than refresh
- visibility audit mismatch between expected and observed tool sets
- `Unknown tool` vs visible-but-hidden recovery classification

## Tests To Add/Update

- unit tests for profile-gated proxy and visibility log emission
- `tests/unit/adapters/mcp/test_visibility_runtime.py`
- `tests/e2e/integration/test_guided_streamable_spatial_support.py`
- `tests/e2e/integration/test_guided_surface_contract_parity.py`

## Docs To Update

- `_docs/_MCP_SERVER/README.md`

## Changelog Impact

- historical closeout entry ownership belongs to
  [TASK-167-03-02](./TASK-167-03-02_Debug_Profile_Docs_Board_Changelog_And_Final_Proof.md)

## Status / Board Update

- remains nested under `TASK-167-02`

## Validation Commands

- `git diff --check`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_search_surface.py -q`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_visibility_runtime.py -q`
- final E2E/runtime proof for this leaf should be exercised through the
  repo-supported runner and the relevant updated integration coverage:
  - `poetry run python scripts/run_e2e_tests.py`

## Validation Category

- focused unit and transport integration tests
- `git diff --check`
