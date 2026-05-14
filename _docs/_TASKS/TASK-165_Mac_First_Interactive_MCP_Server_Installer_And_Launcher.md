# TASK-165: macOS-First Interactive MCP Server Installer And Launcher

**Status:** 🚧 In Progress
**Priority:** 🔴 High
**Category:** Operator UX / Installation / Streamable Runtime
**Estimated Effort:** Large
**Follow-on After:** [TASK-164](./TASK-164_Local_SigLIP2_Reference_Classifier_Sidecar_And_Operator_Scripts.md)
**Related:** [TASK-148](./TASK-148_No_Auth_HTTP_MCP_Client_Compatibility_And_Auth_Misclassification_Recovery.md), [TASK-160](./TASK-160_Guided_Client_Feedback_And_Streamable_HTTP_Recovery_UX.md)

## Objective

Advance the shipped `run_mcp_server.sh` / `run_mcp_server.py` launcher from its
current Docker-guided OpenRouter path into a well-scoped macOS-first operator
flow that keeps prerequisite checks, runtime wiring, docs, and closeout aligned
with the live repo.

Version 1 is explicitly macOS-first. Linux and Windows should be anticipated in
structure and script layout, but not treated as required implementation scope
for the first ship.

## Business Problem

Today the repo assumes a lot of operator context:

- Docker Desktop may or may not be installed
- Apple Silicon / Rosetta / native Python / MLX support may or may not be ready
- optional classifier sidecar, OpenRouter envs, and MCP transport choices all
  require manual wiring across several documents and scripts

That is workable for maintainers, but not for a new macOS user who has never
configured Docker, MLX, or a Streamable MCP runtime before.

## Business Outcome

After this umbrella lands:

- a macOS user can start from one launcher entrypoint and be guided step by step
- the launcher can detect missing prerequisites, explain what it is checking,
  and offer clear install/update/skip decisions
- the repo’s existing MCP + classifier + Streamable runtime helpers are exposed
  through one operator-facing setup flow instead of scattered shell snippets

## Non-Goals

- do not make Linux or Windows parity a blocker for the first ship
- do not silently install system packages without explicit user confirmation
- do not replace the existing low-level scripts; wrap and orchestrate them
- do not invent a GUI app; this remains a terminal-first installer/launcher
- do not claim full fleet-management or MDM automation in the first wave

## Execution Structure

| Order | Task | Purpose |
|------|------|---------|
| 1 | [TASK-165-01](./TASK-165-01_Mac_Prerequisite_Detection_And_Installer_Decision_Flow.md) | Detect Docker/macOS/Python/optional vision prerequisites and define the interactive install/update decisions |
| 2 | [TASK-165-01-01](./TASK-165-01-01_Docker_Desktop_Mac_Install_And_Update_Path.md) | Implement the macOS Docker Desktop detection/install/update slice using the official operator path |
| 3 | [TASK-165-01-02](./TASK-165-01-02_Mac_MLX_And_Vision_Dependency_Install_Path.md) | Implement MLX / native Python / optional vision dependency checks and guided install/update flow |
| 4 | [TASK-165-02](./TASK-165-02_Interactive_Run_MCP_Server_Wizard_And_Script_Modularization.md) | Replace the current single-purpose launcher with a guided terminal wizard and a modular `scripts/` layout |
| 5 | [TASK-165-02-01](./TASK-165-02-01_Interactive_Profile_Selection_And_Runtime_Wiring.md) | Implement the profile/config prompts that wire MCP, OpenRouter, classifier, and local vs Docker flows together |
| 6 | [TASK-165-03](./TASK-165-03_Operator_Docs_And_Closeout_For_Interactive_Installer.md) | Document the launcher, operator expectations, and final proof lanes |

## Repository Touchpoints

| Path / Module | Expected Ownership | Why It Is In Scope |
|---------------|--------------------|--------------------|
| `scripts/run_mcp_server.py` | Interactive launcher owner | This is the live prompt/plan orchestration seam the remaining task family must refine |
| `scripts/run_mcp_server.sh` | Shell entrypoint wrapper | Operators launch through this wrapper, so final docs and validation must keep it honest |
| `scripts/RUN_MCP_SERVER.md`, `scripts/_RUN_DOCKER_MCP.md` | Colocated operator docs | The shipped launcher flow and lower-level Docker helper are documented here now, not only in generic `_docs/` pages |
| `scripts/run_streamable_openrouter.sh` | Lower-level Docker/OpenRouter helper | The launcher still terminates at this narrower helper for the current supported profile, so its contract remains in scope |
| `scripts/run_reference_classifier_sidecar.sh` | Existing sidecar runner | The new launcher should orchestrate, not replace, this helper |
| `scripts/reference_classifier_sidecar.py` | Existing optional classifier runtime | The launcher must be able to detect and wire this path when enabled |
| `pyproject.toml` | Python/dependency baseline | The launcher must stay aligned with the repo's `3.11+` baseline and optional dependency groups |
| `tests/unit/scripts/test_script_tooling.py` | Script owner lane | All launcher/operator script contract changes must be covered here first |
| `README.md`, `_docs/_MCP_SERVER/MCP_CLIENT_CONFIG_EXAMPLES.md` | Operator docs | Current operator guidance must match the shipped launcher flow |
| `scripts/` subdirectories introduced by this umbrella | New script layout owner | The macOS-first installer can split helpers into clearer modules/files if needed |

## Test Matrix

| Slice | Primary Validation Lane | Why |
|------|--------------------------|-----|
| prerequisite detection and prompt flow | `tests/unit/scripts/test_script_tooling.py` plus `pytest ./tests/unit` | install/update decisions are script-owned logic, but repo guidance now requires the full unit pass for implementation work |
| launcher modularization and profile wiring | `tests/unit/scripts/test_script_tooling.py`, `bash -n scripts/run_mcp_server.sh`, and `pytest ./tests/unit` | command construction and prompt routing live in `scripts/`, but the family is client-facing enough that the broader unit lane must stay green |
| docs/operator examples | diff checks plus targeted grep/audit | the installer only helps if docs and prompts stay aligned |
| live operator smoke | optional manual macOS runbook lane | this wave is macOS-first and user-facing |

## Acceptance Criteria

- a macOS user can start the repo from one launcher entrypoint and understand
  what the launcher is checking at each step
- missing Docker Desktop and MLX/vision prerequisites are detected explicitly
  and handled through yes/no install or update prompts
- refusing an install/update leaves the current state intact and clearly
  explains the consequence
- the launcher can still start the MCP server with the repo’s current runtime
  combinations after the setup questions are answered
- the first shipped version is honest about being macOS-first and does not
  pretend Linux/Windows parity that does not yet exist
