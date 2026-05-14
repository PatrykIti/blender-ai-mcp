# TASK-165-01-01: Docker Desktop Mac Install And Update Path

**Status:** 🚧 In Progress
**Priority:** 🔴 High
**Parent:** [TASK-165-01](./TASK-165-01_Mac_Prerequisite_Detection_And_Installer_Decision_Flow.md)
**Objective:** Audit and tighten the shipped Docker Desktop detection/install/update slice on `scripts/run_mcp_server.py`, keeping the live macOS-first launcher honest about what it can check and automate today.
**Repository Touchpoints:** `scripts/run_mcp_server.py`, `scripts/run_mcp_server.sh`, `scripts/RUN_MCP_SERVER.md`, `scripts/_RUN_DOCKER_MCP.md`, `tests/unit/scripts/test_script_tooling.py`
**Acceptance Criteria:** the launcher can detect whether Docker Desktop is installed, report its version, and guide the operator through install/update/skip using the official macOS path without diverging from the live launcher flow.

## Implementation Notes

- use the current official Docker Desktop for Mac operator path as the source
  of truth
- current owner seam already exists in `scripts/run_mcp_server.py`; the
  remaining work is to tighten and document that implementation, not invent a
  second Docker prerequisite flow
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
- `PYTHONPATH=. poetry run pytest ./tests/unit`

## Status / Board Update

- stays nested under `TASK-165-01`
- represents a shipped-but-not-closed launcher slice
