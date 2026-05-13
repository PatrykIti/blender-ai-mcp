# TASK-167-03: Docker Launcher, Docs, Validation, And Closeout For Debug Profiles

**Status:** ⏳ To Do
**Priority:** 🔴 High
**Parent:** [TASK-167](./TASK-167_Cross_Module_Debug_Profile_Registry_And_Runtime_Logging.md)
**Objective:** Own the launcher/docs/closeout branch for the debug-profile family and keep the implementation split into focused leaves rather than one oversized final-pass task.
**Repository Touchpoints:** `scripts/run_streamable_openrouter.sh`, `scripts/run_mcp_server.py`, `scripts/run_mcp_server.sh`, `scripts/RUN_MCP_SERVER.md`, `scripts/run_reference_classifier_sidecar.sh`, `README.md`, `_docs/_MCP_SERVER/README.md`, `_docs/_MCP_SERVER/MCP_CLIENT_CONFIG_EXAMPLES.md`, `scripts/_RUN_DOCKER_MCP.md`, `_docs/_DEV/README.md`, `_docs/_VISION/README.md`, `_docs/_ROUTER/README.md`, `_docs/_TASKS/README.md`, `_docs/_CHANGELOG/`
**Acceptance Criteria:**
- launcher/runtime wiring is isolated in its own implementation leaf
- docs plus board/changelog/final proof are isolated in their own closeout leaf
- the parent closeout branch cannot be marked complete before both children are implemented and validated

## Execution Structure

| Order | Task | Purpose |
|------|------|---------|
| 1 | [TASK-167-03-01](./TASK-167-03-01_Launcher_Debug_Selector_Wiring.md) | Wire the central selector through the supported Docker/local launchers, including the current TASK-165 launcher seam |
| 2 | [TASK-167-03-02](./TASK-167-03-02_Debug_Profile_Docs_Board_Changelog_And_Final_Proof.md) | Finalize docs, board/changelog sync, and the repo-standard proof bundle for the whole family |

## Implementation Notes

- keep the launcher contract simple: one selector env passed through the current
  supported scripts
- do not create one-off launch-script flags that bypass the central server
  config contract
- document the primary operator workflows explicitly:
  - attach/compare/iterate latency -> `vision,reference`
  - proxy arg mismatch / hidden-tool drift -> `tools,visibility`
  - guided step churn -> `guided_flow,router`
  - broad incident trace -> `all`
- preserve the current sidecar log guidance where it remains useful, but make
  clear which diagnostics should now appear directly in the Docker/server
  terminal

## Current Owner / Likely Edit Map

| Path | Current owner seam | Likely edit anchors | Why this leaf owns it |
|------|--------------------|---------------------|-----------------------|
| `scripts/run_streamable_openrouter.sh` | Docker-guided Streamable launcher | lines 12-186 | the central debug selector must be forwarded through the current Docker runtime path here |
| `scripts/run_mcp_server.py` | interactive launcher plan/env handoff | lines 282-360 | the macOS-first launcher should expose the same selector instead of inventing a second debug path |
| `scripts/run_mcp_server.sh` | operator shell entrypoint | current wrapper seam | the shared launcher branch still terminates at the real shell entrypoint operators run |
| `scripts/RUN_MCP_SERVER.md` | local launcher runbook | current operator doc seam | the colocated launcher runbook is part of the live shared launcher surface |
| `scripts/run_reference_classifier_sidecar.sh` | sidecar operator wrapper | current startup/env surface | sidecar-local guidance should stay aligned with the central selector story where applicable |
| `tests/unit/scripts/test_script_tooling.py` | launcher/script contract lane | existing script env tests | forwarding and help/usage examples should be proven here |
| `README.md` | top-level operator entry docs | current Docker/OpenRouter instructions | the primary operator docs must show the selector clearly |
| `_docs/_MCP_SERVER/README.md` | MCP server operator docs | current Streamable/Docker sections | the detailed operator/debug contract belongs here |
| `_docs/_MCP_SERVER/MCP_CLIENT_CONFIG_EXAMPLES.md` | copy-paste env examples | current client/operator config examples | shipped selector/env examples must stay aligned here too |
| `scripts/_RUN_DOCKER_MCP.md` | launcher snippets/runbook | current Docker helper snippets | examples must stay aligned with the shipped env name and scope list |
| `_docs/_DEV/README.md` | developer workflow docs | runtime/dev debugging guidance | future implementers need one canonical debug-profile explanation here |
| `_docs/_VISION/README.md` | sidecar/operator guidance | current classifier-sidecar docs | the shared launcher branch also owns the user-facing sidecar/debug guidance surface |
| `_docs/_ROUTER/README.md` | router behavior docs | current router-facing runtime docs | router-facing debug behavior must be documented where router runtime changes are explained |

## Pseudocode

```bash
export BLENDER_AI_DEBUG=vision,reference
./scripts/run_streamable_openrouter.sh

export BLENDER_AI_DEBUG=tools
./scripts/run_streamable_openrouter.sh
```

## Runtime / Security Contract Notes

- docs must state clearly that debug logs are diagnostic only and may be noisy
  when `all` is enabled
- examples must not encourage logging secrets or copying raw sensitive payloads
- Docker/local launch examples must preserve the current supported runtime paths
  instead of inventing a new unsupported operator entrypoint

## Error Cases To Cover

- selector passed through the Docker launcher but missing in the container env
- selector shown in docs with names that do not exist in the central registry
- sidecar-specific guidance that contradicts the central Docker/server terminal
  story

## Tests To Add/Update

- script tests proving the debug selector is forwarded into the launched server
- docs/grep checks ensuring the accepted profile names stay aligned with the
  shared registry

## Docs To Update

- `README.md`
- `_docs/_MCP_SERVER/README.md`
- `_docs/_MCP_SERVER/MCP_CLIENT_CONFIG_EXAMPLES.md`
- `scripts/_RUN_DOCKER_MCP.md`
- `scripts/RUN_MCP_SERVER.md`
- `_docs/_DEV/README.md`
- `_docs/_VISION/README.md`
- `_docs/_ROUTER/README.md`
- `_docs/_TASKS/README.md`

## Changelog Impact

- final historical entry ownership belongs to
  [TASK-167-03-02](./TASK-167-03-02_Debug_Profile_Docs_Board_Changelog_And_Final_Proof.md)

## Status / Board Update

- remains nested under `TASK-167`
- owns the final board/changelog/docs closeout once the implementation leaves
  are green

## Validation Commands

- `git diff --check`
- the parent should close only after `TASK-167-03-01` and `TASK-167-03-02`
  are implemented and validated

## Validation Category

- `git diff --check`
- targeted grep/audit for profile names and launcher examples
