# TASK-165-02: Interactive Run MCP Server Wizard And Script Modularization

**Status:** ⏳ To Do
**Priority:** 🔴 High
**Parent:** [TASK-165](./TASK-165_Mac_First_Interactive_MCP_Server_Installer_And_Launcher.md)
**Objective:** Replace the current narrow Streamable helper with a guided `run_mcp_server.sh` wizard and a clearer `scripts/` module layout.
**Repository Touchpoints:** `scripts/run_mcp_server.sh`, `scripts/run_streamable_openrouter.sh`, `scripts/run_reference_classifier_sidecar.sh`, `scripts/` helper subdirectories/modules, `tests/unit/scripts/test_script_tooling.py`
**Acceptance Criteria:** a first-time macOS user can follow one guided terminal flow from environment checks to final MCP launch, while legacy helpers remain callable as lower-level building blocks.

## Implementation Notes

- `run_mcp_server.sh` should become the top-level operator entrypoint
- keep existing focused helpers as reusable building blocks rather than deleting
  them immediately
- allow `scripts/` reorganization into subdirectories/modules if that is needed
  for maintainability
- the interactive flow should print clear step headers and current status before
  asking the next question
- the launcher should support at least:
  - Docker-guided MCP
  - local classifier sidecar
  - OpenRouter-backed vision path

## Pseudocode

```python
print_welcome()
run_prerequisite_flow()
ask_runtime_profile()
ask_classifier_options()
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
- `bash -n scripts/run_mcp_server.sh`

## Status / Board Update

- stays nested under `TASK-165`
