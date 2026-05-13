# TASK-167-01: Debug Profile Contract, Registry, And Future Module Onboarding

**Status:** ⏳ To Do
**Priority:** 🔴 High
**Parent:** [TASK-167](./TASK-167_Cross_Module_Debug_Profile_Registry_And_Runtime_Logging.md)
**Objective:** Define one central debug selector contract plus a shared registry module so current and future repo-owned modules can opt into bounded debug scopes without inventing their own env vars or logger naming rules.
**Repository Touchpoints:** `server/infrastructure/config.py`, `server/main.py`, `server/infrastructure/di.py`, `server/router/infrastructure/config.py`, `server/router/application/router.py`, `server/router/application/matcher/ensemble_matcher.py`, `server/router/infrastructure/logger.py`, new shared debug module under `server/infrastructure/`, `server/adapters/mcp/discovery/search_surface.py`, `server/adapters/mcp/visibility_runtime.py`, `server/adapters/mcp/areas/reference_understanding.py`, `server/adapters/mcp/vision/reference_support.py`, `tests/unit/infrastructure/`, `tests/unit/adapters/mcp/`
**Acceptance Criteria:**
- one typed config surface parses `off`, `all`, and one or more
  comma-separated named debug scopes such as `vision`, `reference`, `tools`,
  `transport`, `visibility`, `guided_flow`, and `router`
- invalid names fail with a clear operator-facing message that lists supported scopes
- when `BLENDER_AI_DEBUG` is set it is authoritative for repo-owned debug
  scopes, `ROUTER_LOG_DECISIONS` remains compatibility-only when the selector
  is unset, and `BLENDER_AI_DEBUG=off` suppresses repo-owned debug scopes
- the registry maps one stable scope name to the repo-owned logger namespaces and helper hooks it owns
- the onboarding rules for future modules are documented in code comments and task/docs so new owners can register a scope without creating a separate env contract

## Implementation Notes

- prefer one shared registry module, for example `server/infrastructure/debug_profiles.py`
  or `server/infrastructure/debug_logging.py`, rather than spreading selector
  parsing across multiple owners
- keep the central selector independent from specific transport/runtime code so
  scripts and server bootstraps can consume the same contract
- distinguish repo-owned scopes from third-party logger names; the registry may
  include selected third-party logger adjustments only where they are explicitly
  tied to one repo-owned scope
- define a stable profile vocabulary early and reuse it everywhere:
  `all`, `vision`, `reference`, `tools`, `transport`, `visibility`,
  `guided_flow`, `router`, plus future additions
- keep the public selector as one comma-separated set contract from the start;
  single-scope values like `vision` remain valid degenerate cases of the same
  grammar
- define explicit compatibility/precedence for existing knobs such as
  `ROUTER_LOG_DECISIONS`: when `BLENDER_AI_DEBUG` is explicitly set, it must be
  authoritative for repo-owned debug scopes; `ROUTER_LOG_DECISIONS` should
  remain only as a compatibility shim when the new selector is unset; current
  router-decision behavior stays legacy-default only in that unset case, while
  `BLENDER_AI_DEBUG=off` suppresses repo-owned debug scopes

## Current Owner / Likely Edit Map

| Path | Current owner seam | Likely edit anchors | Why this leaf owns it |
|------|--------------------|---------------------|-----------------------|
| `server/infrastructure/config.py` | `Config` env/runtime contract plus `get_config()` env ingestion | lines 23-43 and 242-325 | the central debug selector belongs with current MCP transport/surface runtime config, env ingestion, and validation |
| `server/main.py` | logging bootstrap | lines 15-20 | terminal logging is bootstrapped here, so the selector contract must fit the live logging entrypoint |
| `server/infrastructure/di.py` | router config injection | lines 214-220 | one existing router config seam enters through DI here, so the shared selector contract must reconcile with it |
| `server/router/infrastructure/config.py` | `RouterConfig.log_decisions` seam | lines 78-82 | an existing router logging/config flag already exists here and should be reconciled with the central selector |
| `server/router/application/router.py` | live `RouterLogger` instantiation | current router construction seam | real router logger instances are created here, so selector wiring must acknowledge this owner |
| `server/router/application/matcher/ensemble_matcher.py` | live `RouterLogger` instantiation inside ensemble classification | current ensemble seam | the central selector must also govern router summaries emitted from ensemble classification |
| `server/router/infrastructure/logger.py` | router logger singleton/helper seam | current router logger owner | the central selector contract must fit both direct router instances and the shared helper logger path |
| `server/infrastructure/debug_logging.py` or `server/infrastructure/debug_profiles.py` | new shared registry module | new file | this is the correct place for selector parsing, registry state, and future-module onboarding helpers |
| `server/adapters/mcp/discovery/search_surface.py` | `BlenderDiscoverySearchTransform._canonicalize_call_arguments()` call chain | lines 329-371 | the registry contract must be consumable from current guided proxy owners rather than designed in isolation |
| `server/adapters/mcp/visibility_runtime.py` | logger-driven visibility audit owner | lines 137-229 | existing logging seams here should consume the same registry contract, which constrains the shared interface shape |
| `tests/unit/infrastructure/` | config/registry proof lane | new tests | selector parsing and invalid-name failures should be proven at the infrastructure owner layer first |

## Pseudocode

```python
profiles = parse_debug_selector(env_value)
registry = build_debug_profile_registry()
validate_requested_profiles(profiles, registry)
debug_state = materialize_enabled_debug_scopes(profiles, registry)

def debug_scope_enabled(scope_name: str) -> bool:
    return "all" in debug_state or scope_name in debug_state
```

## Runtime / Security Contract Notes

- default behavior must remain effectively `off`
- debug selection must not expose provider secrets, API keys, raw image bytes,
  or unrestricted local paths
- `all` means all repo-owned debug scopes, not unconstrained global trace
- future-module onboarding must remain additive and explicit; unknown names must
  fail closed

## Error Cases To Cover

- invalid profile names such as `vison` or `router_debug`
- duplicate profile names in a comma-separated selector
- empty items such as `vision,,tools`
- mixed `all` plus specific scopes
- conflicting old-vs-new logging knobs such as `ROUTER_LOG_DECISIONS` together
  with the central debug selector, proving the documented precedence rule
- future-module registration collisions on one scope name

## Tests To Add/Update

- focused selector-registry proof plus the direct config/runtime consumer lanes,
  including:
  - `tests/unit/infrastructure/test_debug_profile_config.py`
  - `tests/unit/infrastructure/test_debug_profile_registry.py`
  - `tests/unit/adapters/mcp/test_vision_runtime_config.py`
  - `tests/unit/infrastructure/test_vision_di.py`
  - `tests/unit/router/infrastructure/test_config.py`
  - `tests/unit/router/infrastructure/test_logger.py`
  - `tests/unit/router/application/matcher/test_ensemble_matcher.py`

## Docs To Update

- `_docs/_MCP_SERVER/README.md`
- `_docs/_DEV/README.md`

## Changelog Impact

- historical closeout entry ownership belongs to
  [TASK-167-03-02](./TASK-167-03-02_Debug_Profile_Docs_Board_Changelog_And_Final_Proof.md)

## Status / Board Update

- remains nested under `TASK-167`
- should close before runtime instrumentation leaves start broad logger wiring

## Validation Commands

- `git diff --check`
- after implementation adds the new focused config/registry tests above, run a
  lane such as:
  - `PYTHONPATH=. poetry run pytest tests/unit/infrastructure/test_debug_profile_config.py -q`
  - `PYTHONPATH=. poetry run pytest tests/unit/infrastructure/test_debug_profile_registry.py -q`
- run the direct config/runtime consumer lanes too:
  - `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_vision_runtime_config.py -q`
  - `PYTHONPATH=. poetry run pytest tests/unit/infrastructure/test_vision_di.py -q`
  - `PYTHONPATH=. poetry run pytest tests/unit/router/infrastructure/test_config.py -q`
  - `PYTHONPATH=. poetry run pytest tests/unit/router/infrastructure/test_logger.py -q`
  - `PYTHONPATH=. poetry run pytest tests/unit/router/application/matcher/test_ensemble_matcher.py -q`

## Validation Category

- unit tests for config/registry behavior
- `git diff --check`
