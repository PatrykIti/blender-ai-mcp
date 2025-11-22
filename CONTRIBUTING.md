# Contributing to blender-ai-mcp

Thank you for your interest in contributing! We are building a professional, robust bridge between AI and Blender. To maintain high quality, we strictly adhere to specific architectural patterns.

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

1.  **Create a Task**: Add a markdown file in `_docs/_TASKS/` describing your objective.
2.  **Domain First**: Define the interface in `server/domain/tools/`.
3.  **Implement Application**: Create the handler in `server/application/tool_handlers/`.
4.  **Implement Addon**: Add the `bpy` logic in `blender_addon/application/handlers/`.
5.  **Wire it up**:
    *   Register Addon handler in `blender_addon/__init__.py`.
    *   Update `server/infrastructure/di.py`.
    *   Expose tool in `server/adapters/mcp/server.py`.
6.  **Test**: Write a unit test in `tests/` using mocks.
7.  **Document**: Update `CHANGELOG`, `README`, and Semantic Docs in `_docs/`.

---

## 🐍 Coding Standards

- **Type Hints**: Fully typed Python 3.10+.
- **Docstrings**: Google Style docstrings for all tools (AI uses them!).
- **Formatting**: We use standard Python formatting (black/ruff compatible).
- **Error Handling**: Never crash the server. Catch exceptions and return meaningful error strings to the AI.

## 📦 Pull Requests

- Please link the PR to an Issue or Task ID.
- Ensure all tests pass (`poetry run python -m unittest discover tests`).
- Update documentation if you added new features.
