# AGENTS.md

## Project Purpose

`blender-ai-mcp` is a split Blender control system for LLMs:

- `server/` exposes FastMCP tools and translates them to RPC calls.
- `blender_addon/` runs inside Blender and executes the actual `bpy` operations.
- `server/router/` is a supervisor layer that corrects, expands, and routes LLM tool calls through metadata and workflows.

The project exists to avoid raw-code Blender automation. The intended product surface is a stable, deterministic tool API with strong inspection, recovery, and workflow support.

## Repo Map

- `server/domain/`: abstract tool interfaces and core models. Keep framework-free.
- `server/application/tool_handlers/`: RPC-backed application handlers that implement domain interfaces.
- `server/adapters/mcp/areas/`: FastMCP tool definitions grouped by area.
- `server/adapters/rpc/`: socket RPC client used by handlers.
- `server/infrastructure/`: DI and config.
- `server/router/`: router, metadata, classifiers, workflow engine, vector store, and MCP integration helpers.
- `blender_addon/application/handlers/`: Blender-side handlers using `bpy`.
- `blender_addon/infrastructure/rpc_server.py`: threaded RPC server that schedules work safely on Blender's main thread.
- `tests/unit/`: fast tests with mocked Blender/RPC.
- `tests/e2e/`: Blender-backed end-to-end tests.
- `_docs/`: canonical design/task/history docs. Read the area-specific docs before structural changes.

## Architecture Rules

- Preserve Clean Architecture direction: `adapters -> application -> domain`.
- Do not import FastMCP, socket code, or Blender APIs into `server/domain/`.
- Keep Blender-specific logic inside `blender_addon/`.
- MCP adapters should stay thin. Business logic belongs in handlers or router components, not inside `@mcp.tool` wrappers.
- Dependency wiring belongs in `server/infrastructure/di.py`.
- Router additions must remain metadata-driven where possible.

## Environment Notes

- Python `3.11+` is the practical baseline for full repo functionality.
- Router semantic features rely on `sentence-transformers`, `lancedb`, and `pyarrow`.
- LaBSE is heavy; shared DI instances and lazy initialization are intentional. Do not accidentally reintroduce per-test or per-call model loading.
- Blender `5.0` is the tested target. The addon declares Blender `4.0+`, but 4.x is best effort.

## Commands

- Install deps: `poetry install --no-interaction`
- Run server locally: `poetry run python server/main.py`
- Build addon zip: `python scripts/build_addon.py`
- Unit tests: `PYTHONPATH=. poetry run pytest tests/unit/ -v`
- Unit test collection count: `poetry run pytest tests/unit --collect-only`
- E2E tests: `python3 scripts/run_e2e_tests.py`
- E2E collection count: `poetry run pytest tests/e2e --collect-only`

## Coding Standards

- Fully type Python code.
- Tool docstrings are part of the product. Keep them explicit, accurate, and aligned with actual behavior.
- Prefer meaningful error strings over uncaught exceptions. The server should not crash on normal tool misuse.
- Follow naming patterns already used in the repo: `scene_*`, `modeling_*`, `mesh_*`, `router_*`, etc.
- Match local formatting conventions. There is no enforced formatter in this repo.

## Tool Surface Conventions

- Prefer mega tools for the MCP-facing surface when an area already uses them.
- Keep internal single-action handlers when the router or workflows still need them, even if the public MCP wrapper is consolidated behind a mega tool.
- Current important mega tools include `scene_context`, `scene_create`, `scene_inspect`, `mesh_select`, `mesh_select_targeted`, and `mesh_inspect`.
- Read `_docs/AVAILABLE_TOOLS_SUMMARY.md` and `_docs/_MCP_SERVER/README.md` before changing tool exposure.

## Change Playbook: Adding Or Updating A Tool

When adding a new tool or materially changing an existing one, update all relevant layers:

1. Domain interface in `server/domain/tools/`.
2. Application handler in `server/application/tool_handlers/`.
3. Blender handler in `blender_addon/application/handlers/`.
4. Addon registration in `blender_addon/__init__.py`.
5. MCP adapter in `server/adapters/mcp/areas/`.
6. DI wiring in `server/infrastructure/di.py` if a new handler/provider is needed.
7. Dispatcher mapping in `server/adapters/mcp/dispatcher.py` if the router or internal execution path depends on it.
8. Router metadata in `server/router/infrastructure/tools_metadata/**/<tool>.json` if the tool should be router-aware.
9. Unit tests in `tests/unit/`.
10. E2E tests in `tests/e2e/` when Blender behavior changes.
11. Documentation in `README.md`, `CHANGELOG.md`, and the relevant `_docs/` files.

Use `_docs/_ROUTER/TOOLS/README.md` as the checklist for router-facing tools.

## Change Playbook: Router Or Workflow Work

- Read `_docs/_ROUTER/README.md` and the relevant implementation/workflow docs before changing router behavior.
- Router logic is not just intent matching. It includes correction, override, workflow expansion, parameter resolution, adaptation, and firewall behavior.
- Preserve edit-mode selection state where possible. This is a documented project goal and already has explicit fixes/tasks around it.
- Keep metadata, workflow YAML, router engines, and tests in sync.
- Prefer deterministic rules plus metadata over prompt-only heuristics.
- For workflow execution semantics, use `_docs/_ROUTER/WORKFLOWS/workflow-execution-pipeline.md`.

## Change Playbook: Blender Addon Or RPC Work

- Keep networking and threading concerns in infrastructure, not in business handlers.
- Blender work must remain main-thread safe. The addon architecture relies on timer/main-loop scheduling for that.
- If you change RPC method names or payloads, update both sides together:
  - server application handler call
  - addon handler implementation
  - addon RPC registration
  - tests
  - docs

## Testing Expectations

- For server-side logic, default to unit tests first.
- For Blender behavior, add or update E2E coverage if the change affects real geometry, mode handling, selection handling, viewport output, router correction, or workflow execution.
- Router tests should avoid repeated heavy model initialization. Follow the shared/session-scoped patterns already used in tests.

## Documentation Expectations

For meaningful product changes, update docs in the same branch:

- `README.md` for user-facing capabilities or commands.
- `CHANGELOG.md` for shipped behavior changes.
- `_docs/AVAILABLE_TOOLS_SUMMARY.md` for tool inventory changes.
- `_docs/_MCP_SERVER/README.md` for MCP surface changes.
- `_docs/_ADDON/README.md` for addon-side API changes.
- `_docs/_ROUTER/*` for router/workflow behavior changes.
- `_docs/_TESTS/README.md` when test architecture or counts materially change.
- `_docs/_TASKS/README.md` and the relevant task file if the work completes or advances a tracked task.

## Current Strategic Direction

The active direction in `_docs/_TASKS/README.md` is shifting from basic tool coverage to higher-level LLM reliability and reconstruction:

- workflow extraction and router improvements
- `mesh_build` for write-side reconstruction
- `node_graph` for material and geometry-node rebuilds
- image asset management
- scene render/world configuration
- animation and drivers support

If your change touches these areas, read the corresponding task docs first. They already contain design constraints and expected file touch points.

## High-Value Docs

- Root overview: `README.md`
- Architecture: `ARCHITECTURE.md`
- Contribution rules: `CONTRIBUTING.md`
- Development commands: `_docs/_DEV/README.md`
- Test strategy: `_docs/_TESTS/README.md`
- Tool inventory: `_docs/AVAILABLE_TOOLS_SUMMARY.md`
- MCP surface: `_docs/_MCP_SERVER/README.md`
- Addon surface: `_docs/_ADDON/README.md`
- Router system: `_docs/_ROUTER/README.md`
- Prompting patterns for LLM clients: `_docs/_PROMPTS/README.md`

## Practical Guidance For Agents

- Before changing a tool, inspect both the MCP adapter and the Blender handler. Many apparent server changes are really cross-boundary contracts.
- Before changing router behavior, inspect metadata and tests, not just Python code.
- Before adding a new public tool, check whether it should instead be an action on an existing mega tool.
- Before adding a new workflow feature, check the existing task docs. Several future features are already predesigned there and should not be reinvented ad hoc.
