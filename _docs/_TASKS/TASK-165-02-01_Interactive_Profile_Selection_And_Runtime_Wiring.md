# TASK-165-02-01: Interactive Profile Selection And Runtime Wiring

**Status:** ⏳ To Do
**Priority:** 🔴 High
**Parent:** [TASK-165-02](./TASK-165-02_Interactive_Run_MCP_Server_Wizard_And_Script_Modularization.md)
**Related:** [TASK-167](./TASK-167_Cross_Module_Debug_Profile_Registry_And_Runtime_Logging.md)
**Objective:** Implement the interactive prompts that decide which runtime/profile paths the current launcher should wire together, starting from the shipped `run_mcp_server.py` seam and its current Docker-guided OpenRouter plus optional classifier-sidecar path.
**Repository Touchpoints:** `scripts/run_mcp_server.sh`, `scripts/run_mcp_server.py`, `scripts/run_streamable_openrouter.sh`, `scripts/RUN_MCP_SERVER.md`, script helper modules under `scripts/`, `tests/unit/scripts/test_script_tooling.py`
**Acceptance Criteria:** the launcher can guide the operator through the current supported macOS-first runtime path, derive a concrete final launch plan from the real `run_mcp_server.py` owner seam, and remain extensible for adjacent selector/runtime follow-ons without inventing a parallel prompt/plan surface.

## Implementation Notes

- current live owner seam is `scripts/run_mcp_server.py`; task wording should
  follow the existing prompt/plan flow there before proposing broader future
  profile matrices
- current shipped path is the Docker-guided OpenRouter launcher with optional
  classifier-sidecar decisions; if broader local/MLX matrices return later,
  they should be explicit follow-on expansion rather than assumed baseline here
- if the user declines a prerequisite install or update, the derived runtime
  plan must adapt rather than pretending the declined feature is available
- print the final plan before launch so the user can see the resolved command,
  endpoints, and enabled options
- keep the runtime/profile wiring extensible enough that the central `TASK-167`
  debug selector can be passed through this same launcher seam instead of
  inventing a parallel launcher-specific debug contract
- if the debug-selector seam is advanced here while `TASK-167-03-01` is still
  open, update both task files in the same branch so the shared launcher seam
  does not drift across families

## Tests To Add/Update

- `tests/unit/scripts/test_script_tooling.py`

## Docs To Update

- `scripts/RUN_MCP_SERVER.md`
- `scripts/_RUN_DOCKER_MCP.md`

## Changelog Impact

- fold into the shared launcher changelog entry

## Validation Commands

- `git diff --check`
- `PYTHONPATH=. poetry run pytest tests/unit/scripts/test_script_tooling.py -q`

## Status / Board Update

- stays nested under `TASK-165-02`
