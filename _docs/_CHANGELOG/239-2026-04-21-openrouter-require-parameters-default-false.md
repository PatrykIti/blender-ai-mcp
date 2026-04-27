# 239. OpenRouter require_parameters default false

Date: 2026-04-21

## Summary

Changed the repo-wide OpenRouter vision default so `require_parameters` is now
off unless an operator explicitly opts into stricter provider filtering.

## What Changed

- changed the typed runtime config default for
  `VISION_OPENROUTER_REQUIRE_PARAMETERS` from `true` to `false`
- changed the environment fallback for
  `VISION_OPENROUTER_REQUIRE_PARAMETERS` from `true` to `false`
- aligned `.env.example` and operator docs with the new default
- updated MCP client config examples to show the relaxed default
- documented the main failure mode:
  - an OpenRouter model can exist and work in a simpler project, while a richer
    vision request returns `404` / `not found` because strict
    `require_parameters=true` routing filtered out every compatible provider
- kept explicit opt-in coverage so stricter provider filtering can still be
  enabled intentionally for repro or compatibility checks

## Validation

- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_vision_runtime_config.py tests/unit/adapters/mcp/test_vision_external_backend.py -q`
  - result on this machine: `46 passed`
- `poetry run ruff check server/infrastructure/config.py server/adapters/mcp/vision/config.py tests/unit/adapters/mcp/test_vision_runtime_config.py tests/unit/adapters/mcp/test_vision_external_backend.py`
  - result on this machine: passed
