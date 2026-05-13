# TASK-167-03-02: Debug Profile Docs, Board, Changelog, And Final Proof

**Status:** ⏳ To Do
**Priority:** 🔴 High
**Parent:** [TASK-167-03](./TASK-167-03_Docker_Launcher_Docs_Validation_And_Closeout_For_Debug_Profiles.md)
**Objective:** Close the `TASK-167` family only after docs, board/changelog sync, and the final repo-standard proof bundle confirm that the shipped debug profiles are visible on the promised runtime surfaces.
**Repository Touchpoints:** `README.md`, `_docs/_MCP_SERVER/README.md`, `_docs/_MCP_SERVER/MCP_CLIENT_CONFIG_EXAMPLES.md`, `scripts/_RUN_DOCKER_MCP.md`, `scripts/RUN_MCP_SERVER.md`, `_docs/_DEV/README.md`, `_docs/_VISION/README.md`, `_docs/_ROUTER/README.md`, `_docs/_TASKS/README.md`, `_docs/_TASKS/TASK-167*.md`, `_docs/_TASKS/TASK-165-02-01_Interactive_Profile_Selection_And_Runtime_Wiring.md`, `_docs/_CHANGELOG/README.md`, new `_docs/_CHANGELOG/*`
**Acceptance Criteria:**
- operator docs explain `all` vs targeted scopes and match the shipped selector vocabulary
- board and changelog state are synchronized with the final implementation status
- final proof records the exact focused lanes plus the repo-standard validation bundle needed for a runtime-contract family

## Current Owner / Likely Edit Map

| Path | Current owner seam | Likely edit anchors | Why this leaf owns it |
|------|--------------------|---------------------|-----------------------|
| `README.md` | top-level operator docs | current Docker/OpenRouter sections | top-level operator guidance must expose the selector clearly |
| `_docs/_MCP_SERVER/README.md` | detailed MCP/operator docs | current Streamable/Docker sections | detailed selector/profile guidance belongs here |
| `_docs/_MCP_SERVER/MCP_CLIENT_CONFIG_EXAMPLES.md` | copy-paste env examples | current client/operator config examples | shipped selector/env examples must stay aligned here too |
| `scripts/_RUN_DOCKER_MCP.md` | launcher snippets/runbook | current Docker helper snippets | examples must match the shipped selector names and launcher contract |
| `scripts/RUN_MCP_SERVER.md` | local launcher runbook | current interactive launcher docs | local launcher guidance must match the same shipped selector vocabulary |
| `_docs/_DEV/README.md` | developer workflow docs | runtime/dev debugging guidance | future implementers need one canonical debug-profile explanation here |
| `_docs/_VISION/README.md` | sidecar/operator guidance | current classifier-sidecar docs | sidecar/operator guidance must stay aligned with the shipped selector and launcher story |
| `_docs/_ROUTER/README.md` | router behavior docs | current router-facing runtime docs | router-facing debug behavior must be documented where router runtime changes are explained |
| `_docs/_TASKS/README.md` | board state | current promoted rows | board state must match the family closeout |
| `_docs/_TASKS/TASK-167*.md`, `_docs/_TASKS/TASK-165-02-01_Interactive_Profile_Selection_And_Runtime_Wiring.md` | task-family governance | current task files for the family and the overlapping launcher seam | final closeout must update the affected task files, not only the board row |
| `_docs/_CHANGELOG/README.md` and new `_docs/_CHANGELOG/*` | historical tracking | new final family entry | runtime-contract work needs proper historical closeout |

## Implementation Notes

- do not close this family on docs-only proof; the final validation record must
  include the runtime lanes required to trust the shipped selector behavior
- use this leaf as the single closeout owner so board/changelog/docs do not
  drift across multiple branches

## Runtime / Security Contract Notes

- docs must say clearly that debug logs are diagnostic and can be noisy under
  `all`
- examples must not encourage logging or copying secrets

## Tests To Add/Update

- docs/grep audits only as a supplement to the final runtime proof bundle
- final closeout must inherit the focused owner-lane commands from:
  - `TASK-167-01`
  - `TASK-167-02-01`
  - `TASK-167-02-02`
  - `TASK-167-02-03-01`
  - `TASK-167-02-03-02`
  - `TASK-167-02-04`
  - `TASK-167-03-01`

## Docs To Update

- final closeout/harmonization docs:
- `README.md`
- `_docs/_MCP_SERVER/README.md`
- `_docs/_MCP_SERVER/MCP_CLIENT_CONFIG_EXAMPLES.md`
- `scripts/_RUN_DOCKER_MCP.md`
- `scripts/RUN_MCP_SERVER.md`
- `_docs/_DEV/README.md`
- `_docs/_VISION/README.md`
- `_docs/_ROUTER/README.md`
- `_docs/_TASKS/README.md`
- `_docs/_CHANGELOG/README.md`
- new `_docs/_CHANGELOG/*`

## Changelog Impact

- add the historical `_docs/_CHANGELOG/*` entry when the family is ready to
  close and index it in `_docs/_CHANGELOG/README.md`

## Status / Board Update

- remains nested under `TASK-167-03`
- owns final promotion/closure bookkeeping for the family

## Validation Commands

- `git diff --check`
- run the focused owner-lane commands from the child leaves before the broad
  repo bundle, including at minimum:
  - `PYTHONPATH=. poetry run pytest tests/unit/infrastructure/test_debug_profile_config.py -q`
  - `PYTHONPATH=. poetry run pytest tests/unit/infrastructure/test_debug_profile_registry.py -q`
  - `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_vision_runtime_config.py -q`
  - `PYTHONPATH=. poetry run pytest tests/unit/infrastructure/test_vision_di.py -q`
  - `PYTHONPATH=. poetry run pytest tests/unit/router/infrastructure/test_config.py -q`
  - `PYTHONPATH=. poetry run pytest tests/unit/router/infrastructure/test_logger.py -q`
  - `PYTHONPATH=. poetry run pytest tests/unit/router/application/matcher/test_ensemble_matcher.py -q`
  - `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_reference_images.py -q`
  - `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_reference_compare_packets.py -q`
  - `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_search_surface.py -q`
  - `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_visibility_runtime.py -q`
  - `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_guided_flow_state_contract.py -q`
  - `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_session_phase.py -q`
  - `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_router_elicitation.py -q`
  - `PYTHONPATH=. poetry run pytest tests/unit/router/application/test_router_handler_parameters.py -q`
  - `PYTHONPATH=. poetry run pytest tests/unit/router/application/test_router_contracts.py -q`
- `PYTHONPATH=. poetry run pytest tests/unit/router/application/test_supervisor_router.py -q`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_context_bridge.py -q`
- `PYTHONPATH=. poetry run pytest tests/unit/router/application/test_correction_audit.py -q`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_server_transport_mode.py -q`
- `PYTHONPATH=. poetry run pytest tests/unit/scripts/test_script_tooling.py -q`
- `bash -n scripts/run_streamable_openrouter.sh scripts/run_mcp_server.sh scripts/run_reference_classifier_sidecar.sh`
- `PRE_COMMIT_HOME=/tmp/pre-commit-cache poetry run pre-commit run --all-files --show-diff-on-failure` (outside sandbox)
- `PYTHONPATH=. poetry run pytest ./tests/unit` (outside sandbox)
- `poetry run python scripts/run_e2e_tests.py` (outside sandbox)
- targeted grep/audit for accepted profile names across:
  - `README.md`
  - `_docs/_MCP_SERVER/README.md`
  - `_docs/_MCP_SERVER/MCP_CLIENT_CONFIG_EXAMPLES.md`
  - `scripts/_RUN_DOCKER_MCP.md`
  - `scripts/RUN_MCP_SERVER.md`
  - `_docs/_DEV/README.md`
  - `_docs/_ROUTER/README.md`
  - `_docs/_TASKS/README.md`
  - `_docs/_CHANGELOG/README.md`
  - the new `_docs/_CHANGELOG/*.md` entry added by this family

## Validation Category

- final repo-standard proof bundle for a runtime-contract family
- `git diff --check`
