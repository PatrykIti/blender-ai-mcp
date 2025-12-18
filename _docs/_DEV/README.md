# Development

This folder contains developer-facing docs for working on the MCP server + Blender addon.

## Local Setup

```bash
# Install dependencies
poetry install --no-interaction
```

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

