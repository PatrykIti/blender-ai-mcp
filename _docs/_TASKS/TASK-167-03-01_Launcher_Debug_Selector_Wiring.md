# TASK-167-03-01: Launcher Debug Selector Wiring

**Status:** ⏳ To Do
**Priority:** 🔴 High
**Parent:** [TASK-167-03](./TASK-167-03_Docker_Launcher_Docs_Validation_And_Closeout_For_Debug_Profiles.md)
**Objective:** Wire the central debug selector through the supported Docker/local launcher seams, extending the current open TASK-165 launcher ownership instead of inventing a parallel launch contract.
**Repository Touchpoints:** `scripts/run_streamable_openrouter.sh`, `scripts/run_mcp_server.py`, `scripts/run_mcp_server.sh`, `scripts/RUN_MCP_SERVER.md`, `scripts/run_reference_classifier_sidecar.sh`, `tests/unit/scripts/test_script_tooling.py`
**Acceptance Criteria:**
- the selector is forwarded through the supported launcher paths without manual patching by operators
- the launcher work stays explicitly coordinated with the current open TASK-165 owner seam
- script tests prove the selector reaches the launched server environment

## Current Owner / Likely Edit Map

| Path | Current owner seam | Likely edit anchors | Why this leaf owns it |
|------|--------------------|---------------------|-----------------------|
| `scripts/run_streamable_openrouter.sh` | Docker-guided Streamable launcher | lines 12-186 | current Docker launch env pass-through lives here |
| `scripts/run_mcp_server.py` | interactive launcher plan/env handoff | lines 282-360 | current TASK-165 launcher seam already gathers runtime choices here |
| `scripts/run_mcp_server.sh` | operator shell entrypoint | current wrapper seam | the selector must reach the real shell entrypoint users run |
| `scripts/RUN_MCP_SERVER.md` | colocated launcher runbook | current operator doc seam | launcher-facing guidance must stay aligned with the same selector contract |
| `scripts/run_reference_classifier_sidecar.sh` | sidecar operator wrapper | current startup/env surface | sidecar guidance must stay aligned where launcher examples mention it |
| `tests/unit/scripts/test_script_tooling.py` | launcher/script contract lane | current script env tests | selector pass-through should be proven here |

## Implementation Notes

- extend the current launcher seam under `TASK-165`; do not create a second
  incompatible debug-launch path
- if [TASK-165-02-01](./TASK-165-02-01_Interactive_Profile_Selection_And_Runtime_Wiring.md)
  is still open, patch that launcher/runtime prompt seam in sympathy rather
  than creating a parallel launcher-specific path
- keep the operator contract centered on the shared debug selector from
  `TASK-167-01`

## Runtime / Security Contract Notes

- no secrets should be echoed just because debug selector wiring is added
- launcher pass-through must not alter existing runtime defaults when the
  selector is unset

## Tests To Add/Update

- `tests/unit/scripts/test_script_tooling.py`

## Docs To Update

- implementation-slice launcher docs only:
- `scripts/RUN_MCP_SERVER.md`
- `scripts/_RUN_DOCKER_MCP.md`

## Changelog Impact

- historical closeout entry ownership belongs to
  [TASK-167-03-02](./TASK-167-03-02_Debug_Profile_Docs_Board_Changelog_And_Final_Proof.md)

## Status / Board Update

- remains nested under `TASK-167-03`

## Validation Commands

- `git diff --check`
- `bash -n scripts/run_streamable_openrouter.sh scripts/run_mcp_server.sh scripts/run_reference_classifier_sidecar.sh`
- `PYTHONPATH=. poetry run pytest tests/unit/scripts/test_script_tooling.py -q`

## Validation Category

- script unit tests
- `git diff --check`
