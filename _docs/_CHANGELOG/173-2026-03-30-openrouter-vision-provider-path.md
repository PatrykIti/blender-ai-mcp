# 173. OpenRouter vision provider path

Date: 2026-03-30

## Summary

Added the first named remote-provider path for the bounded vision layer:
OpenRouter.

## What Changed

- external vision config now supports `VISION_EXTERNAL_PROVIDER=openrouter`
- dedicated OpenRouter env aliases now exist for:
  - model
  - API key / API key env var
  - optional site URL / site name headers
- OpenRouter defaults to:
  - `https://openrouter.ai/api/v1`
- the OpenAI-compatible external backend now sends OpenRouter-specific headers
  when configured
- `scripts/vision_harness.py` now supports OpenRouter-oriented flags

## Why

The generic external provider path already existed, but it still required
manual generic wiring. This change makes OpenRouter a first-class remote option
for vision experiments and model selection without changing the MCP-facing
contract.
