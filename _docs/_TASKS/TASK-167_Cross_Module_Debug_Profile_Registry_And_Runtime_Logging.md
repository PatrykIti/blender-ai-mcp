# TASK-167: Cross-Module Debug Profile Registry And Runtime Logging

**Status:** ⏳ To Do
**Priority:** 🔴 High
**Category:** Operator Diagnostics / Runtime Debugging / Maintainability
**Estimated Effort:** Large
**Follow-on After:** [TASK-125](./TASK-125_MCP_Transport_Mode_Switching_And_Session_Diagnostics.md), [TASK-160](./TASK-160_Guided_Client_Feedback_And_Streamable_HTTP_Recovery_UX.md), [TASK-163](./TASK-163_Vision_Orchestrator_Feedback_Strategy_Normalization_And_Optional_Perception_Adapters.md), [TASK-164](./TASK-164_Local_SigLIP2_Reference_Classifier_Sidecar_And_Operator_Scripts.md), [TASK-166](./TASK-166_Hierarchical_Reference_Compare_Perceived_Evidence_And_Budget_Control.md)
**Related:** [TASK-148](./TASK-148_No_Auth_HTTP_MCP_Client_Compatibility_And_Auth_Misclassification_Recovery.md), [TASK-165](./TASK-165_Mac_First_Interactive_MCP_Server_Installer_And_Launcher.md)

## Objective

Create one central debug/logging module for the MCP server so operators can
select bounded runtime debug profiles such as:

- `debug=all`
- `debug=vision`
- `debug=reference`
- `debug=tools`
- `debug=transport`
- `debug=visibility`
- `debug=guided_flow`
- `debug=router`

The selected profile must increase logging only for the relevant repo-owned
runtime seams and emit the useful signal directly to the Docker/server terminal
without forcing broad noisy logging from unrelated modules.

This umbrella also needs a future-proof onboarding rule so new modules added
later can register their own debug profile(s) without inventing one-off env
vars, ad hoc `print(...)` debugging, or logger name drift.

## Business Problem

Today the repo exposes useful diagnostics, but they are spread across unrelated
owners and not controlled through one operator contract:

- Docker/Streamable runs already show router, visibility, and HTTP traces
- the classifier sidecar writes to its own file
- some important paths emit `ctx_info(...)`, some use module loggers, and some
  only fail deep inside proxy or vision execution
- there is no single way to say “show me only vision debug” or “show me only
  tool/proxy debug”

That makes debugging real operator failures unnecessarily expensive:

- attach/compare/iterate latency is hard to break down by stage
- `call_tool(...)` proxy regressions can be visible in Docker logs but are not
  grouped under one stable “tools” debug contract
- guided-flow state transitions and visibility churn are diagnosable, but not
  through one predictable selector
- future modules risk adding their own incompatible debug envs or noisy logger
  behavior

## Business Outcome

After this umbrella lands:

- operators can set one debug selector and get targeted logs in the Docker or
  local server terminal
- current repo-owned runtime surfaces use one shared debug registry instead of
  per-module ad hoc logging choices
- future modules have an explicit onboarding rule for adding their own debug
  scope without changing the operator contract shape
- logs remain safe for ordinary operator use: no secrets, raw image bytes, or
  accidental full local path dumps

## Relationship To Existing Board Items

`TASK-167` is a generic runtime/operator substrate, not a new domain consumer.
It should be implemented once and then reused by the current guided/reference,
router, Streamable HTTP, and launcher families already on the board:

- `TASK-160` owns guided client feedback and Streamable HTTP recovery UX
- `TASK-163`, `TASK-164`, and `TASK-166` own RU/orchestrator/classifier/compare
  runtime behavior that needs better operator diagnosis
- `TASK-165` owns launcher/operator wiring that should expose the same central
  debug selector rather than inventing its own logging knobs

This umbrella must extend those existing owners. It must not create a parallel
debug-only runtime surface or a second operator launch model.

## Non-Goals

- do not make `debug=all` the default runtime behavior
- do not turn third-party libraries into unbounded trace spam just because one
  repo-owned profile is enabled
- do not move product/runtime truth into logs; logs remain diagnostic only
- do not create separate incompatible env vars per subsystem when one central
  debug selector can own the contract
- do not treat debug logging as a replacement for typed MCP responses,
  `router_get_status(...)`, or deterministic tests

## Proposed Operator Contract

The implementation under this umbrella should start from one operator-facing
selector, for example:

- `BLENDER_AI_DEBUG=off` (default)
- `BLENDER_AI_DEBUG=all`
- `BLENDER_AI_DEBUG=vision`
- `BLENDER_AI_DEBUG=tools`
- `BLENDER_AI_DEBUG=vision,reference,transport`

The exact env name can still be refined during implementation, but the shipped
contract must satisfy these requirements:

- one central selector instead of many unrelated debug env vars
- `all` means repo-owned debug scopes, not every third-party library at maximum
  verbosity
- one profile can be enabled alone
- multiple profiles may be enabled together if the implementation supports it
- invalid profile names fail clearly and list the accepted values

## Current Runtime Sources To Consolidate

The module created by this umbrella must be able to govern, at minimum, the
repo-owned seams already visible in current debugging sessions:

- vision / RU / optional support
- reference attach/list/remove/clear plus compare/iterate
- guided-flow and spatial-refresh transitions
- visibility transactions and audits
- `call_tool(...)` discovery/proxy behavior
- router interception / firewall / correction summaries
- Docker/operator launcher and sidecar startup diagnostics

## Execution Structure

| Order | Task | Purpose |
|------|------|---------|
| 1 | [TASK-167-01](./TASK-167-01_Debug_Profile_Contract_Registry_And_Future_Module_Onboarding.md) | Define the central debug selector contract, profile registry, validation rules, and future-module onboarding seam |
| 2 | [TASK-167-02](./TASK-167-02_Runtime_Instrumentation_And_Targeted_Log_Routing.md) | Own the runtime instrumentation branch and keep the logger/debug profile behavior split by current owner seam rather than one large implementation pass |
| 3 | [TASK-167-02-01](./TASK-167-02-01_Reference_And_Vision_Debug_Profile_Instrumentation.md) | Instrument `reference_images`, RU refresh, and optional classifier/segmentation support timing and failure summaries |
| 4 | [TASK-167-02-02](./TASK-167-02-02_Tool_Proxy_And_Visibility_Debug_Profile_Instrumentation.md) | Instrument `call_tool(...)` proxy, argument canonicalization, hidden-tool recovery, and visibility transaction/audit paths |
| 5 | [TASK-167-02-03](./TASK-167-02-03_Guided_Flow_And_Router_Debug_Profile_Instrumentation.md) | Instrument guided-flow step transitions, spatial-refresh barriers, and router goal/status/runtime summaries |
| 6 | [TASK-167-03](./TASK-167-03_Docker_Launcher_Docs_Validation_And_Closeout_For_Debug_Profiles.md) | Expose the selector through Docker/operator launch paths, document how to use it, and prove the profiles stay bounded and useful |

## Repository Touchpoints

| Path / Module | Expected Ownership | Why It Is In Scope |
|---------------|--------------------|--------------------|
| `server/infrastructure/config.py` | Runtime config owner | The central debug selector needs a typed config seam |
| `server/infrastructure/` new debug module | New shared owner | This umbrella should create one reusable registry/filter/helper layer instead of duplicating logger logic |
| `server/adapters/mcp/areas/reference.py` | Reference public surface | Attach/compare/iterate debug is one of the main operator pain points |
| `server/adapters/mcp/areas/reference_understanding.py` | RU orchestration seam | RU latency and blocked/available transitions must be attributable in logs |
| `server/adapters/mcp/vision/reference_support.py` | Optional classifier/segmentation support seam | The operator needs to see whether optional support is running, timing out, or unavailable |
| `server/adapters/mcp/discovery/search_surface.py` | `call_tool(...)` proxy seam | Tool/proxy compatibility and hidden-tool recovery need one stable debug channel |
| `server/adapters/mcp/visibility_runtime.py` | Visibility txn/audit owner | Visibility churn is already useful in logs and should move under the shared selector |
| `server/adapters/mcp/session_capabilities*.py` | Guided-flow runtime state | Guided transitions and spatial refresh state need targeted logging rather than scattered messages |
| `server/application/tool_handlers/router_handler.py`, `server/adapters/mcp/areas/router.py`, `server/router/**` | Router/runtime policy seams | Goal routing, no-match transitions, and firewall/correction summaries are part of runtime diagnosis |
| `scripts/run_streamable_openrouter.sh`, `scripts/run_mcp_server.py`, `scripts/run_reference_classifier_sidecar.sh` | Operator launch surface | The selector must be easy to use from the supported Docker/local launch paths |
| `tests/unit/**` and `tests/e2e/integration/**` | Validation lanes | The logging contract should be tested for profile selection, bounded output, and non-regression |
| `README.md`, `_docs/_MCP_SERVER/README.md`, `scripts/_RUN_DOCKER_MCP.md`, `_docs/_DEV/README.md` | Operator/dev docs | The contract must be discoverable and reproducible outside conversation history |

## Current Owner / Likely Edit Map

This umbrella is meant to be implementation-ready. The table below points at
the current owner seams and the live line anchors that are most likely to move
when the family is implemented. Line numbers must be rechecked before coding,
but they are intentionally concrete enough to keep the next agent from starting
with a blind repo-wide search.

| Path | Current owner seam | Likely edit anchors | Why this owner is the real edit surface |
|------|--------------------|---------------------|-----------------------------------------|
| `server/infrastructure/config.py` | `Config` runtime env contract | lines 23-43 | current MCP/factory env vocabulary already lives here; the central debug selector belongs beside transport/surface/runtime config |
| `server/infrastructure/debug_logging.py` or `server/infrastructure/debug_profiles.py` | new shared registry module | new file | central profile parsing, validation, and per-scope registry should not be scattered across existing owners |
| `server/adapters/mcp/discovery/search_surface.py` | `BlenderDiscoverySearchTransform._make_call_tool()` | lines 329-430 | current `call_tool(...)` proxy canonicalization and compatibility/error semantics already live here |
| `server/adapters/mcp/visibility_runtime.py` | `run_visibility_transaction(...)` and `audit_list_tools_snapshot(...)` | lines 137-229 | current visibility txn/audit markers already exist here and should move under the shared debug selector |
| `server/adapters/mcp/areas/reference.py` | `reference_images(...)` wrapper | lines 1629-1656 | reference attach/list/remove/clear enters RU refresh through this public MCP seam |
| `server/adapters/mcp/areas/reference_understanding.py` | `refresh_reference_understanding_summary(...)` | lines 252-397 | RU refresh, cache-hit reuse, blocked/unavailable status, and backend invocation already converge here |
| `server/adapters/mcp/vision/reference_support.py` | `_collect_classifier_support(...)`, `_collect_segmentation_support(...)`, `augment_reference_understanding_optional_support(...)` | lines 347-545 | optional classifier/segmentation support timing, availability, and summary generation already live here |
| `server/adapters/mcp/session_capabilities_flow.py` | `_default_next_actions_for_step(...)`, `_apply_spatial_refresh_gate(...)`, `_clear_spatial_refresh_gate(...)` | lines 633-760 | guided-flow step changes and refresh barrier semantics are currently computed here |
| `server/adapters/mcp/areas/router.py` | `router_set_goal(...)`, `router_get_status(...)` | lines 424-552 | router goal/status MCP responses and `ctx_info(...)` summaries already assemble guided/reference runtime status here |
| `server/router/infrastructure/logger.py` | `RouterLogger` | lines 80-220 | router logging already has a dedicated owner instead of generic module-level logging |
| `scripts/run_streamable_openrouter.sh` | Docker-guided operator launcher | lines 12-186 | current Streamable Docker launch envs and sidecar wiring are passed through here |
| `scripts/run_mcp_server.py` | interactive launcher plan | lines 282-360 | the macOS-first launcher already gathers runtime choices here and will need the same debug selector passthrough |
| `tests/unit/adapters/mcp/test_search_surface.py` | `call_tool(...)` proxy regression lane | existing compatibility tests around lines 1368-1465 | tools/proxy debug profile proof should stay anchored to the current proxy owner lane |
| `tests/unit/adapters/mcp/test_reference_images.py` | RU/reference lifecycle proof lane | existing attach/RU tests around lines 2940-3005 and 8440+ | reference/RU debug scopes need proof on the current reference lifecycle owner lane |
| `tests/unit/scripts/test_script_tooling.py` | launcher/script contract lane | existing script env/launcher tests | Docker/local launcher forwarding belongs on the script owner lane first |

## Test Matrix

| Slice | Primary Validation Lane | Why |
|------|--------------------------|-----|
| config parsing and profile validation | unit tests | selector grammar and invalid-name failures are pure config logic |
| profile registry and module onboarding | unit tests | the shared registry must stay deterministic and future-proof |
| targeted runtime instrumentation | unit tests plus focused integration tests | log emission should prove owner seams without needing full Blender runs for every case |
| Docker/operator wiring | unit script tests and shell syntax checks | launch paths must pass the debug selector through correctly |
| real runtime smoke when needed | focused integration or existing Streamable/transport proof lanes | this work is not Blender-geometry-first, but selected scopes still need proof on the live runtime path when unit coverage alone would miss wiring drift |
| bounded output / redaction | unit tests | secrets, raw image bytes, and private paths must stay out of normal debug output |
| docs/operator guidance | `git diff --check` plus targeted grep/audit | examples and accepted profiles must match the live contract |

## Acceptance Criteria

- one central debug selector can enable either `all` repo-owned debug scopes or
  one or more named scopes such as `vision`, `tools`, or `reference`
- enabling a profile only increases logging for the intended repo-owned seams
  and does not silently make unrelated modules noisy
- current Docker/server terminal output becomes sufficient to trace common
  runtime problems such as RU latency, proxy contract mismatches, visibility
  churn, and guided-flow step transitions
- a future module can register its own debug scope by following one documented
  registry/onboarding pattern instead of creating a new ad hoc env contract
- debug output is bounded and redacted: no provider secrets, raw image bytes,
  or accidental full local private paths in normal operator logs

## Documentation Scope

- `README.md`
- `_docs/_MCP_SERVER/README.md`
- `scripts/_RUN_DOCKER_MCP.md`
- `_docs/_DEV/README.md`
- `_docs/_TASKS/README.md`

## Changelog Impact

- add a `_docs/_CHANGELOG/*` entry when the first implementation slice under
  this umbrella ships
- update `_docs/_CHANGELOG/README.md` when that entry is added

## Status / Board Update

- promote `TASK-167` as a new board-level `⏳ To Do` follow-on
- keep the detailed execution split in the child task files rather than
  overloading this umbrella with line-by-line implementation steps

## Validation Category

Docs/planning-only in this branch:

- `git diff --check`
- targeted consistency grep for `TASK-167` links and board references
