# 220. Guided runtime guardrails and Qwen hardening

Date: 2026-04-07

## Summary

Completed TASK-146 by hardening the current guided runtime around four failure
classes seen in real sessions: spurious workflow triggering, missing Docker
runtime dependencies, weak Qwen/OpenRouter structured-output behavior, and
insufficiently strong search-first / prompt-library guidance.

## What Changed

- repaired `WorkflowTriggerer` so explicit no-match/manual goals suppress
  heuristic workflow activation during ordinary direct tool usage
- added focused unit/E2E coverage for that repaired trigger boundary
- moved `Pillow` onto the main runtime dependency path so Docker images
  installing only `main` still keep deterministic silhouette analysis
- hardened the OpenRouter external vision path:
  - `provider.require_parameters=true`
  - `response-healing` plugin enabled by default
  - `response_format={"type":"json_object"}` preferred for Qwen-family models
- exposed matching OpenRouter/Qwen control env vars in
  `run_streamable_openrouter.sh`
- strengthened `call_tool(...)` failure guidance so hidden-tool guesses now
  point operators/models back toward `search_tools(...)`
- updated README, MCP docs, vision docs, and `_PROMPTS/` assets so:
  - `_docs/_PROMPTS/` is the canonical prompt library
  - `GUIDED_SESSION_START.md` is the generic search-first stabilizer
  - search-first guidance is stronger across the main guided instruction surfaces
- updated task-board state to close TASK-146 in the same branch

## Validation

- `PYTHONPATH=. poetry run pytest tests/unit/router/application/test_workflow_triggerer.py tests/unit/adapters/mcp/test_vision_external_backend.py tests/unit/adapters/mcp/test_search_surface.py tests/unit/adapters/mcp/test_public_surface_docs.py tests/unit/adapters/mcp/test_server_factory.py tests/unit/scripts/test_script_tooling.py tests/e2e/router/test_guided_manual_handoff.py -q`
- result: `84 passed, 4 skipped`
- `poetry run mypy`
- result: `Success: no issues found in 661 source files`

## Why

The repo already had stronger truth, relation, and view-state layers after
TASK-141 through TASK-144, but real guided sessions still paid too much
runtime tax from prompt drift, workflow false positives, dependency drift, and
external JSON-output instability. This hardening wave turns those session logs
into explicit product fixes rather than leaving them as operator folklore.
