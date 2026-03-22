# Development

This folder contains developer-facing docs for working on the MCP server + Blender addon.

## Local Setup

```bash
# Install dependencies
poetry install --no-interaction
```

## Git Hooks

```bash
poetry run pre-commit install --hook-type pre-commit --hook-type pre-push
```

Run the hook sets manually:
```bash
poetry run pre-commit run --all-files
poetry run pre-commit run --hook-stage pre-push --all-files
```

The `pre-commit` stage handles file hygiene, YAML/JSON/TOML checks, GitHub workflow validation, router metadata schema validation, and `ruff` lint/format. The `pre-push` stage additionally runs `poetry check --strict --lock`, unit tests, and the addon build.

## Run the MCP Server (local)

```bash
poetry run python server/main.py
```

Useful environment variables:
- `LOG_LEVEL=DEBUG`
- `ROUTER_ENABLED=true`
- `BLENDER_RPC_HOST=host.docker.internal` (when running the server in Docker on macOS/Windows)

## Build Blender Addon ZIP

```bash
python scripts/build_addon.py
```

Output:
- `outputs/blender_ai_mcp.zip`

## Tests

Unit tests (no Blender required):
```bash
PYTHONPATH=. poetry run pytest tests/unit/ -v
```

E2E tests (requires Blender, automated install/run/cleanup):
```bash
python3 scripts/run_e2e_tests.py
```

## Releasing

See `./RELEASING.md`.
