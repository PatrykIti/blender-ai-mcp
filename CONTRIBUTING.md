# Contributing to blender-ai-mcp

> **💡 Support the Project**
>
> This project is currently developed after hours as a passion project.
> If you find this tool useful or want to accelerate the development of advanced features, please consider supporting the project.
>
> [**💖 Sponsor on GitHub**](https://github.com/sponsors/PatrykIti) | [**☕ Buy me a coffee**](https://buymeacoffee.com/PatrykIti)

Thank you for your interest in contributing! We are building a professional, robust bridge between AI and Blender. To maintain high quality, we strictly adhere to specific architectural patterns.

## 📜 License (Important)

This repository is licensed under the **Business Source License 1.1 (BUSL-1.1)** (see `LICENSE.md`).
By submitting a contribution (code, docs, workflows, etc.), you agree that your contribution will be licensed under the same terms.

## 🏗️ Architecture Compliance (Mandatory)

This project follows **Clean Architecture**. Before writing code, understand the layers:

1.  **Domain (`server/domain/`)**:
    *   Pure Python. No external frameworks.
    *   Define **Interfaces** here (e.g., `IModelingTool`).
2.  **Application (`server/application/`)**:
    *   Logic implementing Domain Interfaces.
    *   Classes like `ModelingToolHandler`.
3.  **Adapters (`server/adapters/`)**:
    *   Connects the world to the app.
    *   `FastMCP` definitions (`server.py`) and `RpcClient`.
4.  **Infrastructure (`server/infrastructure/`)**:
    *   Dependency Injection (`di.py`), Config, Drivers.

**Rule:** Dependencies only point **INWARD**. `Adapters` -> `Application` -> `Domain`.

---

## 🚀 Development Workflow

1.  **Create a Task (recommended)**: Add a markdown file in `_docs/_TASKS/` describing your objective.
2.  **Domain First**: Define the interface in `server/domain/tools/`.
3.  **Implement Application**: Create the handler in `server/application/tool_handlers/`.
4.  **Implement Addon**: Add the `bpy` logic in `blender_addon/application/handlers/`.
5.  **Wire it up**:
    *   Register Addon handler in `blender_addon/__init__.py`.
    *   Update `server/infrastructure/di.py`.
    *   Expose MCP tool in `server/adapters/mcp/areas/<area>.py` (and import the module in `server/adapters/mcp/areas/__init__.py` if it's a new area).
    *   If the tool should be understood by the Router, add/update metadata in `server/router/infrastructure/tools_metadata/**/<tool>.json`.
6.  **Test**: Add/update unit tests in `tests/unit/` (mock Blender RPC; no Blender needed).
7.  **Document**: Update `CHANGELOG.md`, `README.md`, and relevant docs in `_docs/` (especially `_docs/_ROUTER/` for router/workflow changes).

---

## 🛠️ Local Setup

1. Install Python (3.11+ recommended).
2. Install Poetry.
3. Install deps:
```bash
poetry install --no-interaction
```

## 🐍 Coding Standards

- **Type Hints**: Fully typed Python 3.10+.
- **Docstrings**: Tool docstrings are part of the product (LLMs use them) — keep them accurate and explicit.
- **Formatting**: Keep formatting consistent with nearby code (no project-wide formatter is enforced).
- **Error Handling**: Never crash the server. Catch exceptions and return meaningful error strings to the AI.

## 🧪 Tests

**Unit tests** (no Blender required):
```bash
PYTHONPATH=. poetry run pytest tests/unit/ -v
```

**E2E tests** (requires Blender, automated install/run/cleanup):
```bash
python3 scripts/run_e2e_tests.py
```

CI runs unit tests and also verifies the addon + Docker build (see `.github/workflows/pr_checks.yml`).

## 📦 Pull Requests

- Please link the PR to an Issue or Task ID.
- Ensure unit tests pass (`PYTHONPATH=. poetry run pytest tests/unit/ -v`).
- Update documentation if you added new features.
