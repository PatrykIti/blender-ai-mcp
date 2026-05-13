# TASK-167-02: Runtime Instrumentation And Targeted Log Routing

**Status:** ✅ Done
**Priority:** 🔴 High
**Parent:** [TASK-167](./TASK-167_Cross_Module_Debug_Profile_Registry_And_Runtime_Logging.md)
**Objective:** Wire the shared debug profile registry into the current MCP runtime owners so each selected scope emits useful, bounded diagnostics to the Docker/server terminal for the exact repo-owned seams an operator is trying to debug.
**Repository Touchpoints:** `server/adapters/mcp/areas/reference.py`, `server/adapters/mcp/areas/reference_images_runtime.py`, `server/adapters/mcp/areas/reference_understanding.py`, `server/adapters/mcp/vision/reference_support.py`, `server/adapters/mcp/discovery/search_surface.py`, `server/adapters/mcp/visibility_runtime.py`, `server/adapters/mcp/session_capabilities_flow.py`, `server/adapters/mcp/session_capabilities_registry.py`, `server/adapters/mcp/session_capabilities_bootstrap.py`, `server/adapters/mcp/session_capabilities_runtime_glue.py`, `server/adapters/mcp/areas/router.py`, `server/adapters/mcp/router_helper.py`, `server/application/tool_handlers/router_handler.py`, `server/router/application/router.py`, `server/router/application/matcher/ensemble_matcher.py`, `server/router/infrastructure/logger.py`, `server/adapters/mcp/server.py`, `server/adapters/mcp/context_utils.py`, `tests/unit/adapters/mcp/`, `tests/unit/router/infrastructure/`, `tests/e2e/integration/`
**Acceptance Criteria:**
- `debug=vision` surfaces RU backend timing, optional support timing, and unavailable/blocked reasons without logging secrets or raw payloads
- `debug=reference` surfaces attach/list/remove/clear plus compare/iterate readiness transitions and key reference-id counts
- `debug=tools` surfaces `call_tool(...)` proxy resolution, argument canonicalization, and public-tool contract mismatches
- `debug=visibility`, `debug=guided_flow`, and `debug=router` each emit their own bounded runtime transitions without turning every other subsystem noisy
- `debug=transport` surfaces bounded bootstrap, reconnect, and surfaced
  session/transport identity diagnostics on the repo-owned `stdio` and
  Streamable seams
- the selected profiles write to the normal Docker/server terminal path so operators do not need a second custom log collector for standard debugging

## Execution Structure

| Order | Task | Purpose |
|------|------|---------|
| 1 | [TASK-167-02-01](./TASK-167-02-01_Reference_And_Vision_Debug_Profile_Instrumentation.md) | Cover the reference attach/list/remove/clear, RU refresh, and optional classifier/segmentation seams |
| 2 | [TASK-167-02-02](./TASK-167-02-02_Tool_Proxy_And_Visibility_Debug_Profile_Instrumentation.md) | Cover `call_tool(...)` proxy, argument canonicalization, hidden-tool recovery, and visibility txn/audit seams |
| 3 | [TASK-167-02-03](./TASK-167-02-03_Guided_Flow_And_Router_Debug_Profile_Instrumentation.md) | Own the guided-flow/router branch and keep it split by current owner seam |
| 4 | [TASK-167-02-03-01](./TASK-167-02-03-01_Guided_Flow_Debug_Profile_Instrumentation.md) | Cover guided-flow step transitions, spatial-refresh state, and state-shaping seams |
| 5 | [TASK-167-02-03-02](./TASK-167-02-03-02_Router_Debug_Profile_Instrumentation.md) | Cover router goal/status assembly, logger usage, and execution-audit seams |
| 6 | [TASK-167-02-04](./TASK-167-02-04_Transport_And_Session_Debug_Profile_Instrumentation.md) | Cover `stdio` / Streamable bootstrap, reconnect/session diagnostics, and the repo-owned `debug=transport` contract |

## Current Owner / Likely Edit Map

| Path | Current owner seam | Likely edit anchors | Why this branch owns it |
|------|--------------------|---------------------|-------------------------|
| `server/adapters/mcp/areas/reference.py` | `reference_images(...)`, `reference_compare_stage_checkpoint(...)`, `reference_iterate_stage_checkpoint(...)` public facade | lines 1629-1656 and 1745-1780 | compare/iterate public seams stay here even though attach lifecycle moved into the runtime helper |
| `server/adapters/mcp/areas/reference_images_runtime.py` | `handle_reference_images(...)`, `_attach_reference_image(...)`, `_remove_reference_image(...)`, `_clear_reference_images(...)` | lines 228-427 | active vs pending reference adoption and RU refresh triggering are owned here, not in the thin facade |
| `server/adapters/mcp/areas/reference_understanding.py` | `refresh_reference_understanding_summary(...)` | lines 252-487 | RU refresh, blocked/unavailable states, backend invocation, and final persistence converge here |
| `server/adapters/mcp/vision/reference_support.py` | `_collect_classifier_support(...)`, `_collect_segmentation_support(...)`, `augment_reference_understanding_optional_support(...)` | lines 347-545 | optional support timing and unavailable summaries live here |
| `server/adapters/mcp/discovery/search_surface.py` | `BlenderDiscoverySearchTransform._make_call_tool()` | lines 329-430 | proxy resolution and compatibility errors already live here |
| `server/adapters/mcp/visibility_runtime.py` | `run_visibility_transaction(...)`, `audit_list_tools_snapshot(...)` | lines 137-229 | visibility txn/audit markers already exist here |
| `server/adapters/mcp/session_capabilities_flow.py` | `_default_next_actions_for_step(...)`, `_apply_spatial_refresh_gate(...)`, `_clear_spatial_refresh_gate(...)` | lines 633-760 | guided-flow default step and refresh semantics are computed here |
| `server/adapters/mcp/session_capabilities_registry.py` | `record_guided_flow_spatial_check_completion(...)`, `advance_guided_flow_from_iteration_async(...)` | lines 504-645 | live guided-flow completion and iteration transitions are applied here |
| `server/adapters/mcp/session_capabilities_bootstrap.py` | router-goal bootstrap and ready-session reference adoption | current router-goal/update seams | initial guided-flow state and pending-reference adoption are bootstrapped here |
| `server/adapters/mcp/session_capabilities_runtime_glue.py` | stale-state rearm and runtime persistence glue | current runtime-glue seams | guided-flow rearm and persistence are applied here |
| `server/adapters/mcp/areas/router.py` | `router_set_goal(...)`, `router_get_status(...)` | lines 364-648 | router goal/status diagnostics are assembled here |
| `server/router/application/matcher/ensemble_matcher.py` | router logger usage inside ensemble classification | current ensemble seam | router debug must also cover the existing `RouterLogger` usage from ensemble classification |
| `server/router/infrastructure/logger.py` | `RouterLogger`, especially `log_info(...)` and `log_execution_audit(...)` | lines 80-220 and 368-426 | router logger gating belongs here rather than in broad `server/router/**` prose |
| `server/adapters/mcp/server.py` | `run(...)` | lines 34-75 | transport bootstrap/reconnect diagnostics are owned here |
| `server/adapters/mcp/context_utils.py` | `ctx_session_id(...)`, `ctx_transport_type(...)` | current response identity helpers | transport/session diagnostics also flow through these response-side helpers |
| `tests/unit/adapters/mcp/test_server_transport_mode.py` | transport bootstrap proof lane | lines 19-75 | direct unit lane for transport bootstrap ownership |
| `tests/e2e/integration/test_mcp_transport_modes.py` | transport runtime proof lane | lines 24-180 | direct runtime lane for transport/session behavior |
| `tests/unit/adapters/mcp/test_reference_images.py` | reference/RU proof lane | lines 2940-3005 and current RU transport/attach suites | reference and vision debug instrumentation should prove itself here |
| `tests/unit/adapters/mcp/test_search_surface.py` | proxy proof lane | current proxy log assertion around line 1153 and hidden-tool recovery around lines 1903-2032 | tool/proxy debug instrumentation should prove itself here |
| `tests/unit/adapters/mcp/test_visibility_runtime.py` | visibility owner lane | current transaction/audit tests | direct visibility-profile proof belongs here too |
| `tests/unit/router/infrastructure/test_logger.py` | router logger owner lane | current RouterLogger tests | direct router logger proof belongs here too |
| `tests/unit/router/application/test_router_handler_parameters.py` | router handler owner lane | current goal-shape/handler tests | direct router handler proof belongs here too |
| `tests/e2e/integration/test_guided_gate_state_transport.py` | reference/guided transport proof lane | current attach/list/remove/clear + compare transport surfaces | reference/guided debug profiles must not contradict current transport behavior |

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
- transport bootstrap/reconnect/session-id transitions that should be visible
  under `transport`

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

- historical closeout entry ownership belongs to
  [TASK-167-03-02](./TASK-167-03-02_Debug_Profile_Docs_Board_Changelog_And_Final_Proof.md)

## Status / Board Update

- remains nested under `TASK-167`
- should close only after `TASK-167-02-01`, `TASK-167-02-02`,
  `TASK-167-02-03-01`, `TASK-167-02-03-02`, and `TASK-167-02-04` are
  implemented and validated on their owned seams

## Validation Commands

- `git diff --check`
- after implementation, run the focused owner lanes from the child tasks before
  any broader unit or integration sweep

## Validation Category

- focused unit/integration tests for gated logging behavior
- `git diff --check`
