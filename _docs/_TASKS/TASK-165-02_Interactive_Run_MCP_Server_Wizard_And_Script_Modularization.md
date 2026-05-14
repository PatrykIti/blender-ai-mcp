# TASK-165-02: Interactive Run MCP Server Wizard And Script Modularization

**Status:** 🚧 In Progress
**Priority:** 🔴 High
**Parent:** [TASK-165](./TASK-165_Mac_First_Interactive_MCP_Server_Installer_And_Launcher.md)
**Objective:** Tighten the shipped `run_mcp_server.sh` / `run_mcp_server.py` wizard and its supporting `scripts/` layout so the task tracks the real remaining delta instead of restating already-landed launcher work as greenfield implementation.
**Repository Touchpoints:** `scripts/run_mcp_server.py`, `scripts/run_mcp_server.sh`, `scripts/run_streamable_openrouter.sh`, `scripts/run_reference_classifier_sidecar.sh`, `scripts/RUN_MCP_SERVER.md`, `scripts/_RUN_DOCKER_MCP.md`, script helper modules under `scripts/`, `tests/unit/scripts/test_script_tooling.py`
**Acceptance Criteria:** a first-time macOS user can follow the shipped guided terminal flow from environment checks to final MCP launch, while lower-level helpers remain callable as narrower building blocks and the docs describe the same flow.

## Implementation Notes

- `run_mcp_server.sh` is already the top-level operator entrypoint and
  `run_mcp_server.py` is the current owner seam; remaining work should refine
  that flow rather than redefining it from scratch
- keep existing focused helpers as reusable building blocks rather than deleting
  them immediately
- allow `scripts/` reorganization into subdirectories/modules if that is needed
  for maintainability
- the interactive flow should print clear step headers and current status before
  asking the next question
- current shipped flow order is:
  - Python / Poetry / Docker checks
  - runtime/profile, classifier, model, and debug prompts
  - optional MLX / vision dependency prompts
  - final launch plan and launch confirmation
- the launcher should currently document and preserve the supported path:
  - Docker-guided MCP
  - optional local or remote classifier sidecar
  - OpenRouter-backed vision path

## Pseudocode

```python
print_welcome()
run_python_poetry_docker_checks()
ask_runtime_profile_and_classifier_options()
ask_model_and_debug_options()
offer_optional_mlx_and_vision_installs()
show_final_plan()
confirm_launch()
start_sidecars_if_needed()
start_mcp_server()
```

## Runtime / Security Contract Notes

- prompt wording should be explicit about what is being installed or launched
- the final launcher should show the commands/endpoints it derived so the user
  can understand the outcome
- if a required background process fails to start, stop and explain instead of
  continuing into a half-configured MCP launch

## Tests To Add/Update

- `tests/unit/scripts/test_script_tooling.py`

## Docs To Update

- `README.md`
- `scripts/` local operator docs
- `_docs/_MCP_SERVER/MCP_CLIENT_CONFIG_EXAMPLES.md`

## Changelog Impact

- fold into the shared launcher changelog entry

## Validation Commands

- `git diff --check`
- `PYTHONPATH=. poetry run pytest tests/unit/scripts/test_script_tooling.py -q`
- `PYTHONPATH=. poetry run pytest ./tests/unit`
- `bash -n scripts/run_mcp_server.sh`

## Status / Board Update

- stays nested under `TASK-165`
- documents the remaining delta on the shipped wizard instead of a not-yet-landed launcher
