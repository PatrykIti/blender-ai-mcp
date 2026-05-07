# TASK-165-01-01: Docker Desktop Mac Install And Update Path

**Status:** ⏳ To Do
**Priority:** 🔴 High
**Parent:** [TASK-165-01](./TASK-165-01_Mac_Prerequisite_Detection_And_Installer_Decision_Flow.md)
**Objective:** Add the macOS Docker Desktop detection/install/update slice used by the interactive MCP launcher.
**Repository Touchpoints:** `scripts/run_mcp_server.sh`, macOS-specific helper modules/scripts under `scripts/`, `tests/unit/scripts/test_script_tooling.py`
**Acceptance Criteria:** the launcher can detect whether Docker Desktop is installed, report its version, and guide the operator through install/update/skip using the official macOS path.

## Implementation Notes

- use the current official Docker Desktop for Mac operator path as the source
  of truth
- current Docker docs expose:
  - interactive install via `Docker.dmg` -> Applications
  - command-line install after download via
    `hdiutil attach Docker.dmg`, `/Volumes/Docker/Docker.app/Contents/MacOS/install`, `hdiutil detach`
- do not assume Docker publishes one stable `curl | sh` style installer for macOS
- prefer a launcher flow that can:
  - detect `/Applications/Docker.app`
  - detect whether `docker` CLI exists and whether the daemon is reachable
  - open or explain the official install path
  - optionally automate the documented CLI install steps after the user confirms
- record in docs that Docker Desktop licensing/subscription constraints are operator-owned

## Tests To Add/Update

- `tests/unit/scripts/test_script_tooling.py`

## Docs To Update

- `README.md`
- `scripts/` local operator docs

## Changelog Impact

- fold into the shared launcher changelog entry

## Validation Commands

- `git diff --check`
- `PYTHONPATH=. poetry run pytest tests/unit/scripts/test_script_tooling.py -q`

## Status / Board Update

- stays nested under `TASK-165-01`
