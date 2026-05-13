# TASK-165-02-01: Interactive Profile Selection And Runtime Wiring

**Status:** ⏳ To Do
**Priority:** 🔴 High
**Parent:** [TASK-165-02](./TASK-165-02_Interactive_Run_MCP_Server_Wizard_And_Script_Modularization.md)
**Related:** [TASK-167](./TASK-167_Cross_Module_Debug_Profile_Registry_And_Runtime_Logging.md)
**Objective:** Implement the interactive prompts that decide which runtime/profile paths the launcher should wire together.
**Repository Touchpoints:** `scripts/run_mcp_server.sh`, `scripts/run_mcp_server.py`, script helper modules under `scripts/`, `tests/unit/scripts/test_script_tooling.py`
**Acceptance Criteria:** the launcher can guide the operator through profile selection and derive a concrete final launch plan for the supported macOS-first runtime combinations.

## Implementation Notes

- initial question set should likely cover:
  - local vs Docker-guided MCP
  - OpenRouter vision yes/no
  - classifier enabled yes/no
  - local classifier sidecar auto-start vs remote endpoint
  - local MLX path yes/no
- if the user declines a prerequisite install or update, the derived runtime
  plan must adapt rather than pretending the declined feature is available
- print the final plan before launch so the user can see the resolved command,
  endpoints, and enabled options
- keep the runtime/profile wiring extensible enough that the central `TASK-167`
  debug selector can be passed through this same launcher seam instead of
  inventing a parallel launcher-specific debug contract

## Tests To Add/Update

- `tests/unit/scripts/test_script_tooling.py`

## Docs To Update

- `scripts/` local operator docs

## Changelog Impact

- fold into the shared launcher changelog entry

## Validation Commands

- `git diff --check`
- `PYTHONPATH=. poetry run pytest tests/unit/scripts/test_script_tooling.py -q`

## Status / Board Update

- stays nested under `TASK-165-02`
