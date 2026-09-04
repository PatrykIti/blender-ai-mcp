# 215. Guided creature contract parity on the active client surface

Date: 2026-04-06

## Summary

Closed the remaining TASK-141 gap between the documented guided squirrel-run
contract and the real `llm-guided` client path by hardening direct visible
tools, the discovery proxy, and the truth-first `inspect_validate` handoff
under stdio-backed integration coverage.

## What Changed

- added one shared adapter-level guided contract hardening helper so
  `call_tool(...)` and directly visible guided tools now use the same
  canonicalization/guidance policy
- direct `scene_clean_scene(...)` now accepts the legacy split cleanup flags
  only in the same narrow compatible form already used by the proxy path
- direct `reference_images(...)` attach now catches batch-like `images=[...]`
  / `source_paths=[...]` drift with structured recovery guidance instead of raw
  FastMCP validation noise
- direct `collection_manage(...)` now accepts the narrow legacy `name` alias
  while keeping `collection_name` canonical on the guided surface
- direct `modeling_create_primitive(...)` now rejects `scale`, `segments`,
  `rings`, `subdivisions`, and primitive-time `collection_name` shortcuts with
  actionable guided guidance instead of schema churn
- tightened `reference_iterate_stage_checkpoint(...)` messaging so
  `loop_disposition="inspect_validate"` and degraded compare with strong truth
  findings both explicitly stop free-form modeling and hand off into
  inspect/measure/assert
- added stdio-backed integration regressions for the active guided contract and
  inspect-validate/degraded-compare handoff seams
- updated README, prompt docs, MCP docs, client-config examples, and TASK-141
  admin docs to describe the shipped contract line

## Why

Helper-level fixes already existed, but real guided creature sessions could
still hit raw validation noise on directly visible tools and a too-soft
truth-first handoff story. That left the squirrel run rediscovering surface
rules instead of reaching the actual geometry problems.

## Validation

- `poetry run pytest tests/unit/adapters/mcp/test_search_surface.py tests/unit/adapters/mcp/test_reference_images.py tests/unit/adapters/mcp/test_public_surface_docs.py tests/unit/adapters/mcp/test_router_elicitation.py -q`
- `poetry run pytest tests/e2e/integration/test_guided_surface_contract_parity.py tests/e2e/integration/test_guided_inspect_validate_handoff.py -q`
- `poetry run pytest tests/e2e/router/test_guided_manual_handoff.py -q` (`3 skipped`)
