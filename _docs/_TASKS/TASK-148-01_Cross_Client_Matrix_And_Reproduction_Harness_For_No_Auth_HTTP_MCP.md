# TASK-148-01: Cross-Client Matrix And Reproduction Harness For No-Auth HTTP MCP

**Parent:** [TASK-148](./TASK-148_No_Auth_HTTP_MCP_Client_Compatibility_And_Auth_Misclassification_Recovery.md)
**Status:** ⏳ To Do
**Priority:** 🔴 High
**Objective:** Produce one explicit reproduction and evidence matrix for how major MCP clients behave against the repo's session-aware no-auth Streamable HTTP server, using the guided local harness rather than the OpenRouter helper as the primary repro surface.
**Repository Touchpoints:** `tests/e2e/integration/_guided_surface_harness.py`, `tests/e2e/integration/test_guided_gate_state_transport.py`, `tests/e2e/integration/test_guided_surface_contract_parity.py`, `tests/e2e/integration/test_mcp_transport_modes.py`, `server/infrastructure/config.py`, `server/adapters/mcp/factory.py`, `scripts/run_mcp_server.py`, `scripts/RUN_MCP_SERVER.md`, `_docs/_MCP_SERVER/README.md`, `_docs/_MCP_SERVER/MCP_CLIENT_CONFIG_EXAMPLES.md`
**Acceptance Criteria:**
- the repo documents which clients are in scope for this wave:
  - Claude Code / Claude Desktop
  - Codex CLI / desktop-style Codex consumers
  - Gemini CLI / Gemini-compatible MCP consumers
- the current `needs-auth` incident is reproduced with enough evidence to
  distinguish:
  - server process failure
  - guided-surface/session reset
  - auth-state poisoning
  - client auth-discovery misclassification
- the reproduction notes include exact request/response evidence or client logs
  for any auth-discovery probes
- the matrix records whether `MCP_PROMPTS_AS_TOOLS_ENABLED=true|false` changes
  client behavior on the same no-auth Streamable surface

## Implementation Notes

- use the repo's current session-aware local Streamable harness as the primary
  reproduction path:
  - `_guided_surface_harness.py`
  - `test_guided_gate_state_transport.py`
  - `test_guided_surface_contract_parity.py`
- treat `test_mcp_transport_modes.py` as a supplemental transport continuity
  control only; it uses `legacy-flat` and `ROUTER_ENABLED=false`, so it cannot
  be the only owner lane for a guided no-auth incident
- treat `scripts/run_streamable_openrouter.sh` as a contrast surface only when
  documenting why it is *not* the canonical no-auth repro path
- capture the matrix across at least:
  - tool-only prompt bridge enabled
  - tool-only prompt bridge disabled
  - same-session reconnect / stale local auth cache
  - fresh profile versus previously poisoned profile
- ground the repro notes in the current FastMCP compatibility lever:
  `MCP_PROMPTS_AS_TOOLS_ENABLED` on `config.py` and `factory.py`

## Pseudocode

```python
for prompt_bridge_enabled in (True, False):
    server = run_guided_streamable_server(
        extra_env={
            "ROUTER_ENABLED": "true",
            "MCP_SURFACE_PROFILE": "llm-guided",
            "MCP_PROMPTS_AS_TOOLS_ENABLED": str(prompt_bridge_enabled).lower(),
        }
    )
    for client in matrix_clients:
        record_startup_probe(client, server.url)
        record_reconnect_behavior(client, server.url)
        record_auth_probe_behavior(client, server.url)
```

## Runtime / Security Contract Notes

- do not add fake OAuth endpoints or compatibility lies just to make the repro
  pass
- keep client logs sanitized; do not paste live API keys or local secrets into
  the matrix notes
- keep the reproduction path on the repo-supported no-auth surface, not on an
  OpenRouter-dependent helper that changes the problem being measured

## Tests To Add/Update

- `tests/e2e/integration/test_guided_gate_state_transport.py`
- `tests/e2e/integration/test_guided_surface_contract_parity.py`
- `tests/e2e/integration/test_mcp_transport_modes.py` as a supplemental control

## Docs To Update

- `_docs/_MCP_SERVER/README.md`
- `_docs/_MCP_SERVER/MCP_CLIENT_CONFIG_EXAMPLES.md`
- `scripts/RUN_MCP_SERVER.md`
- `_docs/_TASKS/README.md` if promoted scope changes

## Changelog Impact

- include in the parent umbrella changelog entry when shipped

## Status / Board Update

- remains nested under `TASK-148`
- should close before the policy/fix slices claim a chosen repo-side remedy

## Validation Commands

- `git diff --check`
- `PYTHONPATH=. poetry run pytest tests/e2e/integration/test_guided_gate_state_transport.py -q`
- `PYTHONPATH=. poetry run pytest tests/e2e/integration/test_guided_surface_contract_parity.py -q`
- `PYTHONPATH=. poetry run pytest tests/e2e/integration/test_mcp_transport_modes.py -q`

## Validation Category

- guided Streamable transport and compatibility harness proof
- `git diff --check`
