# 350. TASK-167 debug profiles and runtime logging

Date: 2026-05-13

## Summary

Implemented the `TASK-167` family end to end:

- added one central `BLENDER_AI_DEBUG` selector with strict parsing, shared
  registry metadata, authoritative precedence over repo-owned debug scopes, and
  compatibility-only fallback to `ROUTER_LOG_DECISIONS` when the selector is
  unset
- routed bounded repo-owned diagnostics through `vision`, `reference`, `tools`,
  `transport`, `visibility`, `guided_flow`, and `router` scopes without
  reintroducing ad hoc `print(...)` debugging or third-party trace spam
- wired the selector through the supported Docker/macOS launcher seams and
  updated operator docs, MCP examples, and task/changelog governance

## Runtime Surface

- `server/infrastructure/debug_profiles.py` now owns the shipped vocabulary,
  registry/onboarding seam, effective-scope resolution, and shared
  `emit_debug_log(...)` helper
- `Config` parses `BLENDER_AI_DEBUG` directly and fails closed on invalid,
  duplicated, or malformed values
- repo-owned runtime seams now emit targeted summaries only when their scope is
  enabled:
  - RU backend and optional classifier/segmentation support
  - reference attach/list/remove/clear and staged compare / iterate
  - `call_tool(...)` proxy and guided visibility txn/audit
  - guided-flow bootstrap, spatial-refresh, and stale-state transitions
  - router handler / goal-status / logger / audit paths
  - transport bootstrap plus surfaced session/transport context

## Operator Surface

- `scripts/run_mcp_server.py` now asks for an optional `BLENDER_AI_DEBUG`
  selector and prints it in the final launch plan
- `scripts/run_streamable_openrouter.sh` forwards `BLENDER_AI_DEBUG` into the
  Docker runtime and echoes the active selector at startup
- `README.md`, `_docs/_MCP_SERVER/README.md`,
  `_docs/_MCP_SERVER/MCP_CLIENT_CONFIG_EXAMPLES.md`, `scripts/RUN_MCP_SERVER.md`,
  `scripts/_RUN_DOCKER_MCP.md`, `_docs/_DEV/README.md`, `_docs/_VISION/README.md`,
  and `_docs/_ROUTER/README.md` now document the shared selector and the common
  troubleshooting combinations

## Validation

- focused unit coverage added/updated for config/registry parsing, launcher
  pass-through, transport bootstrap logs, `call_tool(...)` proxy logs,
  visibility audits, reference lifecycle logs, guided stale-state logs, router
  handler logs, and router transport/logging emission
- broad repo validation and E2E proof are tracked as the required closeout lane
  for this family
