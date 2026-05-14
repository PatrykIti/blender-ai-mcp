# TASK-165-01-02: Mac MLX And Vision Dependency Install Path

**Status:** 🚧 In Progress
**Priority:** 🔴 High
**Parent:** [TASK-165-01](./TASK-165-01_Mac_Prerequisite_Detection_And_Installer_Decision_Flow.md)
**Objective:** Tighten the shipped optional MLX / vision dependency prompts on the live launcher seam, keeping them aligned with the repo's actual Python baseline, dependency groups, and current prompt order.
**Repository Touchpoints:** `scripts/run_mcp_server.py`, `scripts/run_mcp_server.sh`, `scripts/RUN_MCP_SERVER.md`, `pyproject.toml`, `tests/unit/scripts/test_script_tooling.py`
**Acceptance Criteria:** the launcher can explain whether the current Mac can run MLX, whether the repo’s optional vision dependencies are installed, and can guide the user through install/update/skip decisions that match the current launcher flow and repo baseline.

## Implementation Notes

- use the current official MLX requirements as the operator baseline:
  - Apple silicon
  - native Python >= 3.11
  - macOS >= 14
- current official install path is `pip install mlx`; repo-specific operator
  flow should likely prefer `poetry install --with mlx` and
  `poetry install --with vision` where that matches the repo’s dependency groups
- current live launcher flow asks for runtime/profile choices first and then
  offers optional MLX / vision installs; task wording and validation should
  follow that order unless the family explicitly changes it
- the launcher should distinguish:
  - base repo prerequisites
  - optional MLX runtime for local models
  - optional `vision` dependencies for the SigLIP2 sidecar
- if the shell is under Rosetta or Python is non-native, explain that clearly
  before attempting MLX install

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
