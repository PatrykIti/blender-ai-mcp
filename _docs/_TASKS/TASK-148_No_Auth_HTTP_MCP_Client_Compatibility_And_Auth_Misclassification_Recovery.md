# TASK-148: No-Auth HTTP MCP Client Compatibility And Auth Misclassification Recovery

**Status:** ⏳ To Do
**Priority:** 🔴 High
**Category:** Product Reliability / Client Compatibility
**Estimated Effort:** Large
**Dependencies:** TASK-125, TASK-130
**Related:** [TASK-160](./TASK-160_Guided_Client_Feedback_And_Streamable_HTTP_Recovery_UX.md)

## Objective

Stabilize the repo's no-auth Streamable HTTP MCP path across real client
families so a session-aware local server is not misclassified as
OAuth-required during reconnect, discovery, or stale-client-state recovery.

This umbrella is intentionally broader than one Claude Code bug report. The
target surface is the repo's no-auth HTTP MCP product path as seen by:

- Claude Code / Claude Desktop
- Codex CLI / desktop-style Codex MCP consumers
- Gemini CLI / Gemini-compatible MCP consumers
- other clients that probe auth/discovery metadata during HTTP startup

## Business Problem

The repo intentionally supports a stateful no-auth HTTP MCP runtime. That
surface must remain truthful:

- if the server does not require OAuth, it should not be documented or shaped
  as though it does
- if a client loses its transport/session state, that must not silently mutate
  into a fake authentication problem

Current evidence shows one important failure mode:

- a no-auth HTTP MCP server can be reclassified client-side as
  `needs authentication`
- a later `authenticate` attempt then fails on `/register` or related OAuth
  routes because the server never claimed to implement them
- once a client stores partial auth state for that profile, later reconnects
  may stay poisoned even though the server itself still runs normally

This is a product compatibility problem, not just a session bug:

- a Claude-only workaround could misrepresent the repo to Codex, Gemini, or
  future clients
- a fake OAuth surface may repair one client while teaching other clients the
  wrong auth semantics
- a pure docs workaround would leave real operator sessions fragile

## Business Outcome

After this umbrella lands:

- the repo has one explicit no-auth Streamable HTTP compatibility contract for
  serious MCP clients
- reproduction evidence distinguishes guided-surface/session issues from true
  auth-discovery misclassification
- the chosen fix stays on FastMCP platform/discovery seams first, instead of
  smuggling repo-specific behavior into an OpenRouter-only launcher
- operators have one bounded recovery path for poisoned local client auth state
  without the repo pretending to support OAuth where it does not

## Non-Goals

- do not turn the local no-auth MCP runtime into a real OAuth product surface
  unless the matrix and policy work explicitly justify that move
- do not treat `scripts/run_streamable_openrouter.sh` as the canonical no-auth
  reproduction harness; it is an OpenRouter-specific helper, not the generic
  session-aware local server path
- do not solve generic Streamable HTTP visibility churn that belongs to the
  in-progress `TASK-160` family
- do not rely on client-specific prompt hacks as the primary fix
- do not broaden the transport story beyond the supported `stdio` and
  `streamable` modes

## Relationship To Existing Board Items

- `TASK-125` remains the substrate that introduced explicit `stdio` versus
  `streamable` transport support.
- `TASK-160` and `TASK-160-01` remain the adjacent guided-runtime recovery
  track for visibility churn, guided-flow deltas, and “tool disappeared”
  diagnostics on the `llm-guided` surface.
- `TASK-148` must stay narrower than `TASK-160`: it owns truthful no-auth
  discovery/auth-state semantics and client poisoning recovery, not the full
  guided feedback contract.

## Repository Touchpoints

| Path / Module | Expected Ownership | Why It Is In Scope |
|---------------|--------------------|--------------------|
| `server/infrastructure/config.py` | transport/platform settings owner | owns `MCP_TRANSPORT_MODE`, `MCP_HTTP_*`, and `MCP_PROMPTS_AS_TOOLS_ENABLED`, which are the current repo-side compatibility knobs for Streamable HTTP clients |
| `server/adapters/mcp/factory.py` | FastMCP platform composition owner | the prompt bridge and delivery-mode shaping live here, so client-facing compatibility fixes must examine this seam before launcher-only work |
| `server/adapters/mcp/server.py` | Streamable server bootstrap owner | if auth/discovery behavior needs repo-side transport or initialization changes, this is the current runtime seam |
| `tests/e2e/integration/_guided_surface_harness.py` | guided Streamable harness owner | the repo already has a session-aware local Streamable harness for `llm-guided`; this should be the primary repro surface instead of the OpenRouter helper |
| `tests/e2e/integration/test_guided_gate_state_transport.py` | guided Streamable transport owner lane | covers session-aware guided state over Streamable HTTP and is the closest existing regression seam for no-auth client recovery |
| `tests/e2e/integration/test_guided_surface_contract_parity.py` | prompt bridge / guided surface parity owner lane | covers tool-only versus prompt-capable client shaping, including `list_prompts` and `get_prompt` exposure |
| `tests/e2e/integration/test_mcp_transport_modes.py` | transport smoke owner lane | remains useful as a supplemental transport/session continuity control, but not as the primary guided no-auth auth-misclassification proof |
| `scripts/run_mcp_server.py`, `scripts/RUN_MCP_SERVER.md` | operator launcher and operator docs | the supported macOS-first launcher documents the real local Streamable operator path; recovery guidance must stay aligned here |
| `README.md`, `_docs/_MCP_SERVER/README.md`, `_docs/_MCP_SERVER/MCP_CLIENT_CONFIG_EXAMPLES.md` | public compatibility docs | no-auth support, prompt-bridge guidance, and recovery steps must stay truthful across operator docs |

## Test Matrix

| Slice | Primary Validation Lane | Why |
|------|--------------------------|-----|
| guided Streamable no-auth repro | `tests/e2e/integration/_guided_surface_harness.py` plus `test_guided_gate_state_transport.py` | this is the repo's current session-aware local Streamable surface |
| prompt-capable versus tool-only compatibility shaping | `tests/e2e/integration/test_guided_surface_contract_parity.py` | prompt bridge exposure is an existing FastMCP/platform compatibility lever |
| baseline transport/session continuity | `tests/e2e/integration/test_mcp_transport_modes.py` | useful control lane to separate generic transport continuity from guided-surface/auth-state issues |
| operator recovery docs | README plus MCP server docs and launcher docs | poisoned auth-state recovery is only useful if the supported local operator path is documented consistently |

## Acceptance Criteria

- the repo has one explicit matrix for how major MCP clients behave against the
  no-auth Streamable HTTP path
- the current `needs-auth` / failed-`authenticate` incident is reproduced and
  categorized clearly as:
  - guided-surface/session reset
  - stale auth-state poisoning
  - client auth-discovery misclassification
  - or genuine server auth behavior
- any adopted fix keeps the repo honest about auth support to clients that do
  not need OAuth
- operators have one bounded recovery path for poisoned local client auth state
- regression coverage proves the chosen behavior on the repo side across the
  current guided Streamable and prompt-bridge seams

## Docs To Update

- `README.md`
- `_docs/_MCP_SERVER/README.md`
- `_docs/_MCP_SERVER/MCP_CLIENT_CONFIG_EXAMPLES.md`
- `scripts/RUN_MCP_SERVER.md`
- `_docs/_TASKS/README.md`

## Tests To Add/Update

- `tests/e2e/integration/test_guided_gate_state_transport.py`
- `tests/e2e/integration/test_guided_surface_contract_parity.py`
- `tests/e2e/integration/test_mcp_transport_modes.py`
- any focused unit or integration coverage needed for `factory.py`,
  `config.py`, or `server.py` once the matrix selects a repo-side fix

## Changelog Impact

- add a dedicated `_docs/_CHANGELOG/*` entry when the umbrella ships

## Execution Structure

| Order | Subtask | Purpose |
|------|---------|---------|
| 1 | [TASK-148-01](./TASK-148-01_Cross_Client_Matrix_And_Reproduction_Harness_For_No_Auth_HTTP_MCP.md) | Build the client matrix and grounded reproduction harness on the repo's current guided Streamable surface |
| 2 | [TASK-148-02](./TASK-148-02_Auth_State_Poisoning_And_Recovery_Policy_For_No_Auth_HTTP_Servers.md) | Define how stale client-side auth state is detected, cleared, or safely bypassed without lying about server auth semantics |
| 3 | [TASK-148-03](./TASK-148-03_Runtime_Compatibility_Fix_Regression_Pack_And_Docs.md) | Implement the chosen repo-side compatibility fix, then lock it in with tests and docs |

## Status / Board Update

- promoted as a board-level follow-on after `TASK-125`
- explicitly coordinated with in-progress `TASK-160` so guided visibility-churn
  diagnosis stays separate from no-auth discovery/auth-state semantics

## Validation Commands

- `git diff --check`
- targeted consistency grep for:
  - `MCP_PROMPTS_AS_TOOLS_ENABLED`
  - `streamable`
  - `/register`
  - `authenticate`
  - `guided`

## Validation Category

- docs-only umbrella drift repair
- `git diff --check`
