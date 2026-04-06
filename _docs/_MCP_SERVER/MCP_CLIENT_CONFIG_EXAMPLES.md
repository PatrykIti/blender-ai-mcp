# MCP Client Config Examples

Copy/paste-ready MCP client configuration examples for local development and
vision-enabled usage.

Use these as a baseline for:

- Claude Code
- Codex CLI / Codex app-style MCP clients
- other clients that read a `mcpServers` JSON object

Practical notes:

- local project `.mcp.json` is ignored by git in this repo
- adapt absolute paths to your machine
- these examples assume the project venv exists at `.venv/`
- prefer `python -m server.main` rather than `python server/main.py`
- docker examples below assume:
  - `ghcr.io/patrykiti/blender-ai-mcp:latest`
- for Docker on macOS / Windows, use `BLENDER_RPC_HOST=host.docker.internal`
- for Docker on Linux, prefer host networking or adapt the RPC host explicitly

## Base Local Guided Profile

Smallest practical local profile on the production-oriented `llm-guided`
surface:

```json
{
  "mcpServers": {
    "blender-ai-mcp-guided-local": {
      "command": "/ABS/PATH/blender-ai-mcp/.venv/bin/python",
      "args": ["-m", "server.main"],
      "env": {
        "ROUTER_ENABLED": "true",
        "MCP_SURFACE_PROFILE": "llm-guided",
        "BLENDER_RPC_HOST": "127.0.0.1",
        "BLENDER_RPC_PORT": "8765",
        "PYTHONUNBUFFERED": "1"
      }
    }
  }
}
```

Guided creature contract reminders for this profile:

- use `call_tool(name=..., arguments=...)` as the canonical discovery wrapper
- use `scene_clean_scene(keep_lights_and_cameras=...)` as the canonical cleanup shape
- attach one reference per call with `reference_images(action="attach", source_path=...)`
- use `collection_manage(action=..., collection_name=...)` as the canonical collection target shape
- use `modeling_create_primitive(...)` only with `primitive_type`,
  `radius`/`size`, `location`, `rotation`, and optional `name`
- if `loop_disposition="inspect_validate"` or degraded compare still returns
  strong truth findings, stop free-form modeling and switch to inspect/measure/assert

## Local Guided + MLX Vision

Recommended for Apple Silicon local vision testing:

```json
{
  "mcpServers": {
    "blender-ai-mcp-guided-local-mlx": {
      "command": "/ABS/PATH/blender-ai-mcp/.venv/bin/python",
      "args": ["-m", "server.main"],
      "env": {
        "ROUTER_ENABLED": "true",
        "MCP_SURFACE_PROFILE": "llm-guided",
        "BLENDER_RPC_HOST": "127.0.0.1",
        "BLENDER_RPC_PORT": "8765",
        "VISION_ENABLED": "true",
        "VISION_PROVIDER": "mlx_local",
        "VISION_MLX_MODEL_ID": "mlx-community/Qwen3-VL-4B-Instruct-4bit",
        "VISION_MAX_IMAGES": "8",
        "VISION_MAX_TOKENS": "600",
        "VISION_TIMEOUT_SECONDS": "120",
        "PYTHONUNBUFFERED": "1"
      }
    }
  }
}
```

## Local Guided + OpenRouter Vision

Uses the external-runtime path with OpenRouter-specific config aliases:

```json
{
  "mcpServers": {
    "blender-ai-mcp-guided-openrouter": {
      "command": "/ABS/PATH/blender-ai-mcp/.venv/bin/python",
      "args": ["-m", "server.main"],
      "env": {
        "ROUTER_ENABLED": "true",
        "MCP_SURFACE_PROFILE": "llm-guided",
        "BLENDER_RPC_HOST": "127.0.0.1",
        "BLENDER_RPC_PORT": "8765",
        "VISION_ENABLED": "true",
        "VISION_PROVIDER": "openai_compatible_external",
        "VISION_EXTERNAL_PROVIDER": "openrouter",
        "VISION_EXTERNAL_CONTRACT_PROFILE": "google_family_compare",
        "VISION_OPENROUTER_MODEL": "google/gemma-3-27b-it:free",
        "VISION_OPENROUTER_API_KEY_ENV": "OPENROUTER_API_KEY",
        "OPENROUTER_API_KEY": "<YOUR_OPENROUTER_KEY>",
        "VISION_OPENROUTER_SITE_URL": "https://example.com",
        "VISION_OPENROUTER_SITE_NAME": "blender-ai-mcp-dev",
        "VISION_MAX_IMAGES": "8",
        "VISION_MAX_TOKENS": "600",
        "VISION_TIMEOUT_SECONDS": "120",
        "PYTHONUNBUFFERED": "1"
      }
    }
  }
}
```

## Local Guided + Google AI Studio / Gemini Vision

Uses the same external-runtime path with the Gemini provider profile:

```json
{
  "mcpServers": {
    "blender-ai-mcp-guided-gemini": {
      "command": "/ABS/PATH/blender-ai-mcp/.venv/bin/python",
      "args": ["-m", "server.main"],
      "env": {
        "ROUTER_ENABLED": "true",
        "MCP_SURFACE_PROFILE": "llm-guided",
        "BLENDER_RPC_HOST": "127.0.0.1",
        "BLENDER_RPC_PORT": "8765",
        "VISION_ENABLED": "true",
        "VISION_PROVIDER": "openai_compatible_external",
        "VISION_EXTERNAL_PROVIDER": "google_ai_studio",
        "VISION_EXTERNAL_CONTRACT_PROFILE": "google_family_compare",
        "VISION_GEMINI_MODEL": "gemini-2.5-flash",
        "VISION_GEMINI_API_KEY_ENV": "GEMINI_API_KEY",
        "GEMINI_API_KEY": "<YOUR_GEMINI_KEY>",
        "VISION_MAX_IMAGES": "8",
        "VISION_MAX_TOKENS": "600",
        "VISION_TIMEOUT_SECONDS": "120",
        "PYTHONUNBUFFERED": "1"
      }
    }
  }
}
```

## Optional Segmentation Sidecar Add-On

This sidecar stays disabled by default and is separate from the normal
`VISION_EXTERNAL_CONTRACT_PROFILE` routing surface.

Add these env vars only when you explicitly want the advisory part-segmentation path:

```json
{
  "VISION_SEGMENTATION_ENABLED": "true",
  "VISION_SEGMENTATION_PROVIDER": "generic_sidecar",
  "VISION_SEGMENTATION_ENDPOINT": "http://127.0.0.1:9100/segment",
  "VISION_SEGMENTATION_MODEL": "sam-sidecar-v1",
  "VISION_SEGMENTATION_API_KEY_ENV": "SEGMENTATION_API_KEY",
  "VISION_SEGMENTATION_TIMEOUT_SECONDS": "15",
  "VISION_SEGMENTATION_MAX_PARTS": "16"
}
```

## Docker Guided Profile

Smallest practical docker-backed guided profile:

```json
{
  "mcpServers": {
    "blender-ai-mcp-guided-docker": {
      "command": "docker",
      "args": [
        "run",
        "-i",
        "--rm",
        "-v", "/tmp:/tmp",
        "-e", "BLENDER_AI_TMP_INTERNAL_DIR=/tmp",
        "-e", "BLENDER_AI_TMP_EXTERNAL_DIR=/tmp",
        "-e", "ROUTER_ENABLED=true",
        "-e", "MCP_SURFACE_PROFILE=llm-guided",
        "-e", "BLENDER_RPC_HOST=host.docker.internal",
        "-e", "PYTHONUNBUFFERED=1",
        "ghcr.io/patrykiti/blender-ai-mcp:latest"
      ]
    }
  }
}
```

## Docker Guided Profile Over Streamable HTTP

For Streamable HTTP, treat the Docker container and the MCP client as two
separate pieces:

1. start the MCP server container yourself
2. point the MCP client at the exposed HTTP endpoint

### Server Side

```bash
docker run --rm \
  -p 8000:8000 \
  -v /tmp:/tmp \
  -e BLENDER_AI_TMP_INTERNAL_DIR=/tmp \
  -e BLENDER_AI_TMP_EXTERNAL_DIR=/tmp \
  -e ROUTER_ENABLED=true \
  -e MCP_SURFACE_PROFILE=llm-guided \
  -e MCP_TRANSPORT_MODE=streamable \
  -e MCP_HTTP_HOST=0.0.0.0 \
  -e MCP_HTTP_PORT=8000 \
  -e MCP_STREAMABLE_HTTP_PATH=/mcp \
  -e BLENDER_RPC_HOST=host.docker.internal \
  -e PYTHONUNBUFFERED=1 \
  ghcr.io/patrykiti/blender-ai-mcp:latest
```

### Client Side

```json
{
  "mcpServers": {
    "blender-ai-mcp-guided-streamable-docker": {
      "type": "http",
      "url": "http://127.0.0.1:8000/mcp"
    }
  }
}
```

Do **not** combine `command: "docker"` and `type: "http"` in the same MCP
entry. That mixes local stdio process startup with remote HTTP connection
semantics and will not work reliably.

## Docker Guided + OpenRouter Vision

```json
{
  "mcpServers": {
    "blender-ai-mcp-guided-openrouter-docker": {
      "command": "docker",
      "args": [
        "run",
        "-i",
        "--rm",
        "-v", "/tmp:/tmp",
        "-e", "BLENDER_AI_TMP_INTERNAL_DIR=/tmp",
        "-e", "BLENDER_AI_TMP_EXTERNAL_DIR=/tmp",
        "-e", "ROUTER_ENABLED=true",
        "-e", "MCP_SURFACE_PROFILE=llm-guided",
        "-e", "BLENDER_RPC_HOST=host.docker.internal",
        "-e", "VISION_ENABLED=true",
        "-e", "VISION_PROVIDER=openai_compatible_external",
        "-e", "VISION_EXTERNAL_PROVIDER=openrouter",
        "-e", "VISION_EXTERNAL_CONTRACT_PROFILE=google_family_compare",
        "-e", "VISION_OPENROUTER_MODEL=google/gemma-3-27b-it:free",
        "-e", "VISION_OPENROUTER_API_KEY_ENV=OPENROUTER_API_KEY",
        "-e", "OPENROUTER_API_KEY=<YOUR_OPENROUTER_KEY>",
        "-e", "VISION_OPENROUTER_SITE_URL=https://example.com",
        "-e", "VISION_OPENROUTER_SITE_NAME=blender-ai-mcp-dev",
        "-e", "VISION_MAX_IMAGES=8",
        "-e", "VISION_MAX_TOKENS=600",
        "-e", "VISION_TIMEOUT_SECONDS=120",
        "-e", "PYTHONUNBUFFERED=1",
        "ghcr.io/patrykiti/blender-ai-mcp:latest"
      ]
    }
  }
}
```

## Docker Guided + Google AI Studio / Gemini Vision

```json
{
  "mcpServers": {
    "blender-ai-mcp-guided-gemini-docker": {
      "command": "docker",
      "args": [
        "run",
        "-i",
        "--rm",
        "-v", "/tmp:/tmp",
        "-e", "BLENDER_AI_TMP_INTERNAL_DIR=/tmp",
        "-e", "BLENDER_AI_TMP_EXTERNAL_DIR=/tmp",
        "-e", "ROUTER_ENABLED=true",
        "-e", "MCP_SURFACE_PROFILE=llm-guided",
        "-e", "BLENDER_RPC_HOST=host.docker.internal",
        "-e", "VISION_ENABLED=true",
        "-e", "VISION_PROVIDER=openai_compatible_external",
        "-e", "VISION_EXTERNAL_PROVIDER=google_ai_studio",
        "-e", "VISION_EXTERNAL_CONTRACT_PROFILE=google_family_compare",
        "-e", "VISION_GEMINI_MODEL=gemini-2.5-flash",
        "-e", "VISION_GEMINI_API_KEY_ENV=GEMINI_API_KEY",
        "-e", "GEMINI_API_KEY=<YOUR_GEMINI_KEY>",
        "-e", "VISION_MAX_IMAGES=8",
        "-e", "VISION_MAX_TOKENS=600",
        "-e", "VISION_TIMEOUT_SECONDS=120",
        "-e", "PYTHONUNBUFFERED=1",
        "ghcr.io/patrykiti/blender-ai-mcp:latest"
      ]
    }
  }
}
```

## Legacy Manual Surface

Use this only when you intentionally want the broader non-goal-first manual
surface:

```json
{
  "mcpServers": {
    "blender-ai-mcp-legacy-manual": {
      "command": "/ABS/PATH/blender-ai-mcp/.venv/bin/python",
      "args": ["-m", "server.main"],
      "env": {
        "ROUTER_ENABLED": "true",
        "MCP_SURFACE_PROFILE": "legacy-manual",
        "BLENDER_RPC_HOST": "127.0.0.1",
        "BLENDER_RPC_PORT": "8765",
        "PYTHONUNBUFFERED": "1"
      }
    }
  }
}
```

## Legacy Flat Surface

Compatibility-oriented broad surface:

```json
{
  "mcpServers": {
    "blender-ai-mcp-legacy-flat": {
      "command": "/ABS/PATH/blender-ai-mcp/.venv/bin/python",
      "args": ["-m", "server.main"],
      "env": {
        "ROUTER_ENABLED": "true",
        "MCP_SURFACE_PROFILE": "legacy-flat",
        "BLENDER_RPC_HOST": "127.0.0.1",
        "BLENDER_RPC_PORT": "8765",
        "PYTHONUNBUFFERED": "1"
      }
    }
  }
}
```

## Notes

- `llm-guided` should remain the default for normal production-like model use
- `legacy-manual` is the explicit escape hatch for broad manual tool control
- OpenRouter and Gemini both ride on the same bounded
  `openai_compatible_external` path; the difference is the provider profile and
  provider-specific env vars
- `VISION_EXTERNAL_PROVIDER` chooses transport/provider wiring, while
  `VISION_EXTERNAL_CONTRACT_PROFILE` optionally forces the external
  prompt/schema/parser contract for compare flows
- when `VISION_EXTERNAL_CONTRACT_PROFILE` is omitted, the runtime can
  auto-match Google-family model ids such as `gemma` / `gemini`; the explicit
  examples above keep the compare-path assumption visible in client config
- the same env model works for both local venv launch and Docker launch; only
  `command` / `args` differ
- for local image/file outputs, keep `/tmp` host-visible if your client expects
  file paths that can be opened outside the container/runtime
