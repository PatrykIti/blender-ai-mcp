# TASK-167-01: Debug Profile Contract, Registry, And Future Module Onboarding

**Status:** ⏳ To Do
**Priority:** 🔴 High
**Parent:** [TASK-167](./TASK-167_Cross_Module_Debug_Profile_Registry_And_Runtime_Logging.md)
**Objective:** Define one central debug selector contract plus a shared registry module so current and future repo-owned modules can opt into bounded debug scopes without inventing their own env vars or logger naming rules.
**Repository Touchpoints:** `server/infrastructure/config.py`, new shared debug module under `server/infrastructure/`, `server/adapters/mcp/discovery/search_surface.py`, `server/adapters/mcp/visibility_runtime.py`, `server/adapters/mcp/areas/reference_understanding.py`, `server/adapters/mcp/vision/reference_support.py`, `server/router/**`, `tests/unit/infrastructure/`, `tests/unit/adapters/mcp/`
**Acceptance Criteria:**
- one typed config surface parses `off`, `all`, and named debug scopes such as `vision`, `reference`, `tools`, `transport`, `visibility`, `guided_flow`, and `router`
- invalid names fail with a clear operator-facing message that lists supported scopes
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
- decide whether the selector is one enum or a comma-separated set, but keep the
  public operator shape simple and documented

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

## Tests To Add/Update

- config parsing tests for valid and invalid selector values
- registry tests proving scope names and namespace ownership stay deterministic
- onboarding tests showing a new scope can be registered without changing the
  public selector contract shape

## Docs To Update

- `_docs/_MCP_SERVER/README.md`
- `_docs/_DEV/README.md`

## Changelog Impact

- covered by the first `_docs/_CHANGELOG/*` entry that ships the `TASK-167`
  implementation family

## Validation Category

- unit tests for config/registry behavior
- `git diff --check`
