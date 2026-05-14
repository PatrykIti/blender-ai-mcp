# TASK-165-01: Mac Prerequisite Detection And Installer Decision Flow

**Status:** 🚧 In Progress
**Priority:** 🔴 High
**Parent:** [TASK-165](./TASK-165_Mac_First_Interactive_MCP_Server_Installer_And_Launcher.md)
**Objective:** Tighten the shipped macOS-first prerequisite checks and interactive install/update/skip decisions on the live `run_mcp_server.py` launcher seam, keeping the documented flow aligned with what the current launcher really does.
**Repository Touchpoints:** `scripts/run_mcp_server.py`, `scripts/run_mcp_server.sh`, `scripts/RUN_MCP_SERVER.md`, `pyproject.toml`, `tests/unit/scripts/test_script_tooling.py`
**Acceptance Criteria:** the launcher detects prerequisite state in the same order the live wizard uses, prints clear operator messages, and offers explicit install/update/skip decisions without silently mutating the system.

## Implementation Notes

- current live baseline:
  - Python / Poetry / Docker are checked before runtime selection
  - optional MLX / vision install prompts happen after the runtime/profile
    choices are collected
- the first release only needs to support macOS checks as first-class paths
- prerequisite checks should include at least:
  - OS / architecture
  - Docker Desktop
  - Python / Poetry state
  - optional MLX and vision dependency state
  - optional classifier-sidecar readiness
- when a prerequisite already exists, check the version and let the user skip
  any proposed update
- the launcher should preserve the user’s current versions if they refuse an
  update

## Pseudocode

```python
detect_os()
assert_macos_first_support()
check_docker_desktop()
check_python_and_poetry()
collect_runtime_profile_choices()
check_optional_mlx_and_vision_after_profile_selection()
check_optional_classifier_sidecar_path()
for each missing_or_outdated_item:
    explain_status()
    ask_install_update_skip()
```

## Runtime / Security Contract Notes

- installation prompts must stay explicit; no background install without consent
- version detection and update prompts must not leak secrets or private files
- if a prerequisite cannot be checked safely, the launcher should say so
  clearly instead of pretending success

## Tests To Add/Update

- `tests/unit/scripts/test_script_tooling.py`

## Docs To Update

- `README.md`
- `_docs/_MCP_SERVER/MCP_CLIENT_CONFIG_EXAMPLES.md`

## Changelog Impact

- fold into one shared `_docs/_CHANGELOG/*` entry when the umbrella lands

## Validation Commands

- `git diff --check`
- `PYTHONPATH=. poetry run pytest tests/unit/scripts/test_script_tooling.py -q`
- `PYTHONPATH=. poetry run pytest ./tests/unit`

## Status / Board Update

- stays nested under `TASK-165`
- no standalone board row unless this prerequisite flow expands beyond the launcher umbrella
- tracks the remaining delta on the shipped launcher rather than a greenfield installer
