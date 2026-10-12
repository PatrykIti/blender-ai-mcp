# Contributing to blender-ai-mcp

> [!WARNING]
> **Project discontinued — this repository is no longer maintained.**
> `blender-ai-mcp` will not be developed further. It is being replaced by an entirely new and significantly better solution: much stronger 3D scene understanding, deeper and more reliable cooperation with Blender, far better workflow control, and more. The new add-on will be released soon.

**New contributions are no longer accepted.** Because the project is discontinued, pull requests, feature requests, and issues will not be reviewed or merged. The guidance below is kept only as a historical reference for the archived codebase.

Thank you for your interest in this project. It was built as a professional, robust bridge between AI and Blender and strictly adhered to specific architectural patterns, documented below for reference.

## 📜 License (Important)

This repository is licensed under the **Apache License 2.0** (see `LICENSE.md`).
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

Also read:
- `_docs/_ROUTER/RESPONSIBILITY_BOUNDARIES.md`

That document defines the runtime responsibility split between:
- FastMCP platform behavior
- LaBSE semantic matching
- Router correction/safety policy
- Inspection/assertion truth

Do not blur those layers when extending the repo.

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
    * If your change touches FastMCP platform design, LaBSE semantics, router correction scope, or verification logic, update `_docs/_ROUTER/RESPONSIBILITY_BOUNDARIES.md` too.

---

## 🛠️ Local Setup

1. Install Python (3.11+ recommended).
2. Install Poetry.
3. Install deps:
```bash
poetry install --no-interaction
```
4. Install repo hooks:
```bash
poetry run pre-commit install --hook-type pre-commit --hook-type pre-push
```

More details:
- `_docs/_DEV/README.md`
- `_docs/_DEV/RELEASING.md`

## 🐍 Coding Standards

- **Type Hints**: Fully typed Python 3.10+.
- **Docstrings**: Tool docstrings are part of the product (LLMs use them) — keep them accurate and explicit.
- **Formatting**: Use the repo `pre-commit` hooks and `ruff` as the canonical formatter/linter baseline.
- **Error Handling**: Never crash the server. Catch exceptions and return meaningful error strings to the AI.

## 🧪 Tests

**Code quality**:
```bash
poetry run pre-commit run --all-files
```

**Unit tests** (no Blender required):
```bash
PYTHONPATH=. poetry run pytest tests/unit/ -v
```

**E2E tests** (requires Blender, automated install/run/cleanup):
```bash
python3 scripts/run_e2e_tests.py
```

CI runs `pre-commit`, unit tests, and also verifies the addon + Docker build (see `.github/workflows/pr_checks.yml`).

## 📦 Pull Requests

> Pull requests are no longer accepted because the project is discontinued. The checklist below is retained for historical reference only.

- Please link the PR to an Issue or Task ID.
- Ensure `poetry run pre-commit run --all-files` passes.
- Ensure unit tests pass (`PYTHONPATH=. poetry run pytest tests/unit/ -v`).
- Update documentation if you added new features.
