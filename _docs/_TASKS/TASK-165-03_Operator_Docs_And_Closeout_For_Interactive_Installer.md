# TASK-165-03: Operator Docs And Closeout For Interactive Installer

**Status:** ⏳ To Do
**Priority:** 🔴 High
**Parent:** [TASK-165](./TASK-165_Mac_First_Interactive_MCP_Server_Installer_And_Launcher.md)
**Objective:** Document the macOS-first interactive installer/launcher, record the supported first-time setup path, and close the umbrella with synchronized docs/board/changelog state.
**Repository Touchpoints:** `README.md`, `scripts/` operator docs, `_docs/_MCP_SERVER/MCP_CLIENT_CONFIG_EXAMPLES.md`, `_docs/_TASKS/README.md`, `_docs/_CHANGELOG/`
**Acceptance Criteria:** a first-time macOS operator can follow the docs that match the launcher exactly; closeout records the supported scope and any explicit non-goals for Linux/Windows parity.

## Implementation Notes

- document the launcher in the same place where operators will look first:
  `scripts/` and `README.md`
- keep macOS-first scope explicit; do not imply full Linux/Windows parity if
  those paths are still future work
- record the exact final launch paths and prerequisite flows that were
  validated during closeout

## Tests To Add/Update

- `tests/unit/scripts/test_script_tooling.py`

## Docs To Update

- `README.md`
- `scripts/` local operator docs
- `_docs/_MCP_SERVER/MCP_CLIENT_CONFIG_EXAMPLES.md`
- `_docs/_TASKS/README.md`

## Changelog Impact

- add one `_docs/_CHANGELOG/*` closeout entry when the umbrella lands

## Validation Commands

- `git diff --check`
- `PYTHONPATH=. poetry run pytest tests/unit/scripts/test_script_tooling.py -q`

## Status / Board Update

- stays nested under `TASK-165`
