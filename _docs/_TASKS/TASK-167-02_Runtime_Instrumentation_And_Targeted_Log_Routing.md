# TASK-167-02: Runtime Instrumentation And Targeted Log Routing

**Status:** ⏳ To Do
**Priority:** 🔴 High
**Parent:** [TASK-167](./TASK-167_Cross_Module_Debug_Profile_Registry_And_Runtime_Logging.md)
**Objective:** Wire the shared debug profile registry into the current MCP runtime owners so each selected scope emits useful, bounded diagnostics to the Docker/server terminal for the exact repo-owned seams an operator is trying to debug.
**Repository Touchpoints:** `server/adapters/mcp/areas/reference.py`, `server/adapters/mcp/areas/reference_understanding.py`, `server/adapters/mcp/vision/reference_support.py`, `server/adapters/mcp/discovery/search_surface.py`, `server/adapters/mcp/visibility_runtime.py`, `server/adapters/mcp/session_capabilities*.py`, `server/adapters/mcp/areas/router.py`, `server/application/tool_handlers/router_handler.py`, `server/router/**`, `tests/unit/adapters/mcp/`, `tests/e2e/integration/`
**Acceptance Criteria:**
- `debug=vision` surfaces RU backend timing, optional support timing, and unavailable/blocked reasons without logging secrets or raw payloads
- `debug=reference` surfaces attach/list/remove/clear plus compare/iterate readiness transitions and key reference-id counts
- `debug=tools` surfaces `call_tool(...)` proxy resolution, argument canonicalization, and public-tool contract mismatches
- `debug=visibility`, `debug=guided_flow`, and `debug=router` each emit their own bounded runtime transitions without turning every other subsystem noisy
- the selected profiles write to the normal Docker/server terminal path so operators do not need a second custom log collector for standard debugging

## Execution Structure

| Order | Task | Purpose |
|------|------|---------|
| 1 | [TASK-167-02-01](./TASK-167-02-01_Reference_And_Vision_Debug_Profile_Instrumentation.md) | Cover the reference attach/list/remove/clear, RU refresh, and optional classifier/segmentation seams |
| 2 | [TASK-167-02-02](./TASK-167-02-02_Tool_Proxy_And_Visibility_Debug_Profile_Instrumentation.md) | Cover `call_tool(...)` proxy, argument canonicalization, hidden-tool recovery, and visibility txn/audit seams |
| 3 | [TASK-167-02-03](./TASK-167-02-03_Guided_Flow_And_Router_Debug_Profile_Instrumentation.md) | Cover guided-flow step transitions, spatial-refresh state, router goal/status assembly, and router logger gating |

## Current Owner / Likely Edit Map

| Path | Current owner seam | Likely edit anchors | Why this branch owns it |
|------|--------------------|---------------------|-------------------------|
| `server/adapters/mcp/areas/reference.py` | `reference_images(...)` | lines 1629-1656 | attach/list/remove/clear enters the RU lifecycle here |
| `server/adapters/mcp/areas/reference_understanding.py` | `refresh_reference_understanding_summary(...)` | lines 252-397 | RU backend start/finish, blocked states, and optional-support merge already converge here |
| `server/adapters/mcp/vision/reference_support.py` | `_collect_classifier_support(...)`, `_collect_segmentation_support(...)`, `augment_reference_understanding_optional_support(...)` | lines 347-545 | optional support timing and unavailable summaries live here |
| `server/adapters/mcp/discovery/search_surface.py` | `BlenderDiscoverySearchTransform._make_call_tool()` | lines 329-430 | proxy resolution and compatibility errors already live here |
| `server/adapters/mcp/visibility_runtime.py` | `run_visibility_transaction(...)`, `audit_list_tools_snapshot(...)` | lines 137-229 | visibility txn/audit markers already exist here |
| `server/adapters/mcp/session_capabilities_flow.py` | `_default_next_actions_for_step(...)`, `_apply_spatial_refresh_gate(...)`, `_clear_spatial_refresh_gate(...)` | lines 633-760 | guided-flow state transitions and refresh barriers are computed here |
| `server/adapters/mcp/areas/router.py` | `router_set_goal(...)`, `router_get_status(...)` | lines 424-552 | router goal/status diagnostics are assembled here |
| `server/router/infrastructure/logger.py` | `RouterLogger` | lines 80-220 | router logger gating belongs here rather than in broad `server/router/**` prose |
| `tests/unit/adapters/mcp/test_reference_images.py` | reference/RU proof lane | lines 2940-3005 and current RU transport/attach suites | reference and vision debug instrumentation should prove itself here |
| `tests/unit/adapters/mcp/test_search_surface.py` | proxy proof lane | lines 1368-1465 plus call-tool proxy tests | tool/proxy debug instrumentation should prove itself here |
| `tests/e2e/integration/test_guided_gate_state_transport.py` | transport/runtime proof lane | current attach/list/remove/clear + compare transport surfaces | runtime log profiles must not contradict current transport behavior |

## Implementation Notes

- reuse existing logger seams where they already exist, especially:
  - `visibility_runtime`
  - `search_surface` / `call_tool` proxy
  - router interception/firewall summaries
  - RU refresh and optional classifier/segmentation support
- avoid scattering raw `print(...)` statements; instrument through shared helpers
  and normal loggers so profile filtering stays consistent
- prefer explicit high-signal events over firehose dumps:
  - attach start/finish, RU refresh start/finish, elapsed time, reference count
  - optional classifier/segmentation invoked/skipped/timeout/unavailable
  - proxy compatibility normalization and hidden-tool recovery
  - guided-flow step change, refresh barrier set/cleared, required checks
- treat `ctx_info(...)` and logger output as complementary:
  client-facing guidance stays on MCP responses, operator debugging stays in logs

## Pseudocode

```python
if debug_scope_enabled("reference"):
    logger.info("[REFERENCE_DEBUG] attach_start goal=%s refs=%s", goal, count)

if debug_scope_enabled("vision"):
    logger.info("[VISION_DEBUG] ru_backend_start provider=%s ref_count=%s", provider, count)

if debug_scope_enabled("tools"):
    logger.info("[TOOLS_DEBUG] call_tool name=%s canonical_args=%s", name, canonical_keys)
```

## Runtime / Security Contract Notes

- debug messages must stay bounded and summary-level by default
- no provider secrets, auth headers, raw image bytes, or unconstrained local
  private paths in normal logs
- debug scopes must not change runtime behavior or authority; they are
  observational only
- third-party library noise should be opt-in and tied to one repo-owned scope
  only when it materially helps diagnosis

## Error Cases To Cover

- proxy compatibility errors that should be visible under `tools` without
  dumping full payloads
- visibility audit mismatches that should be visible under `visibility`
  without flooding the terminal
- RU attach latency where backend and optional support need separate timing
  attribution
- guided-flow step transitions that should be visible under `guided_flow`
  without printing full session state blobs
- router goal/status transitions that should be visible under `router`
  without duplicating every lower-level event

## Tests To Add/Update

- unit tests for profile-gated emission on current owner seams
- focused integration tests that enable one profile and assert the expected
  repo-owned log markers appear while unrelated markers stay absent
- regression tests for known operator failures such as proxy arg drift and RU
  attach/refresh timing attribution

## Docs To Update

- `_docs/_MCP_SERVER/README.md`
- `README.md`

## Changelog Impact

- covered by the first `_docs/_CHANGELOG/*` entry that ships the `TASK-167`
  implementation family

## Status / Board Update

- remains nested under `TASK-167`
- should close only after `TASK-167-02-01`, `TASK-167-02-02`, and
  `TASK-167-02-03` all have concrete implementation-ready contracts

## Validation Commands

- `git diff --check`
- after implementation, run the focused owner lanes from the child tasks before
  any broader unit or integration sweep

## Validation Category

- focused unit/integration tests for gated logging behavior
- `git diff --check`
