---
type: task
id: TASK-001
title: Project Initialization and Structure
status: done
priority: high
assignee: unassigned
---

# 🎯 Objective
Prepare the work environment, repository, and basic file structure compliant with "Clean Architecture" described in the main README, using **Poetry** for dependency management.

# 📋 Scope of Work

1. **Directory Structure**
   - Create directories:
     - `server/domain/models`
     - `server/domain/tools`
     - `server/application/tool_handlers`
     - `server/adapters/rpc`
     - `server/adapters/mcp`
     - `server/infrastructure`
     - `blender_addon/api`
     - `blender_addon/utils`

2. **Dependencies (Poetry)**
   - Initialize project `poetry init`.
   - Add dependencies:
     - `mcp`
     - `pydantic`
     - `uvicorn`

3. **Git Configuration**
   - `.gitignore` (ignoring `__pycache__`, `.venv`, `*.zip`, `.DS_Store`).

4. **Developer Documentation**
   - Add installation and running instructions (`poetry install`) in `README.md`.

# ✅ Acceptance Criteria
- Directory structure exists.
- `pyproject.toml` and `poetry.lock` are present.
- Dependencies install correctly (`poetry install`).
- Repository is clean.
