# 235. OpenAI/Azure vision schema strictness

Date: 2026-04-12

## Summary

Hardened the external vision JSON Schema contract for OpenAI/Azure-style strict
structured outputs after OpenRouter routed `openai/gpt-5.4-nano` to Azure and
the provider rejected the generic vision schema.

## What Changed

- updated the generic full vision response schema so every top-level property
  is listed in `required`
- updated nested object schemas so every key under `properties` is also listed
  in `required`, including:
  - `likely_issues.items.severity`
  - `recommended_checks.items.priority`
- kept optional/low-confidence fields represented as nullable values or empty
  arrays instead of omitting keys from strict structured output
- documented the OpenAI/Azure strict structured-output requirement in
  `_docs/_VISION/README.md`
- added recursive unit coverage to keep strict schema `required` keys aligned
  with `properties`

## Validation

- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_vision_prompting.py tests/unit/adapters/mcp/test_vision_external_backend.py -q`
  - result on this machine: `17 passed`
- `poetry run ruff check server/adapters/mcp/vision/prompting.py tests/unit/adapters/mcp/test_vision_prompting.py tests/unit/adapters/mcp/test_vision_external_backend.py`
  - result on this machine: passed
