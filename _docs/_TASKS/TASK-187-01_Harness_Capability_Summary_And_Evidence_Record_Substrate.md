# TASK-187-01: Harness Capability Summary And Evidence Record Substrate

**Parent:** [TASK-187](./TASK-187_External_Vision_Model_Evidence_And_Profile_Promotion_Governance.md)
**Status:** ✅ Done
**Priority:** 🔴 High
**Category:** Vision Runtime / External Model Governance

## Objective

Make `scripts/vision_harness.py` evidence trustworthy for future external-model
promotion decisions by recording the backend-resolved runtime state after a
request has had a chance to perform lazy OpenRouter `/models` metadata lookup.

This slice is governance substrate only. It does not promote a model, add a new
fallback profile, add a new `VisionContractProfile`, or widen
`VISION_EXTERNAL_PROVIDER`.

## Repository Touchpoints

| Path | Ownership |
|---|---|
| `scripts/vision_harness.py` | read `backend.runtime_config` after `backend.analyze(...)` when available before emitting `model_name`, `vision_contract_profile`, and `capability_summary` |
| `tests/unit/scripts/test_script_tooling.py` | add regression coverage for a fake OpenRouter backend that updates runtime capabilities during analysis |
| `_docs/_VISION/README.md` | document that promotion evidence must use resolved post-request capabilities |
| `_docs/_MCP_SERVER/README.md` | document the operator-facing evidence requirement where TASK-187 promotion rules are summarized |
| `_docs/_CHANGELOG/` | record the governance substrate and changelog index entry |

## Implementation Notes

The harness now keeps the original runtime config as a fallback but prefers a
typed post-request runtime from the backend:

```text
runtime = build_vision_runtime_config(...)
backend = create_vision_backend(runtime)
result = await backend.analyze(request)
runtime = backend.runtime_config if available else runtime
emit model/profile/capability diagnostics from runtime
```

That preserves existing local/fake backend behavior while allowing
OpenRouter-backed evidence records to reflect lazy catalog capability metadata,
request mode, requested token cap, and response-healing policy.

## Tests To Add/Update

- Added a focused `vision_harness` unit test that simulates an OpenRouter
  backend replacing preflight config with live catalog capability metadata
  during `analyze(...)`.
- The test proves harness output uses live `capability_source`, model caps,
  request mode, requested max tokens, response-healing status, `model_name`,
  and `vision_contract_profile`.

## Docs To Update

- `_docs/_VISION/README.md`
- `_docs/_MCP_SERVER/README.md`
- `_docs/_TASKS/README.md`
- `_docs/_CHANGELOG/README.md`

## Changelog Impact

- Added `_docs/_CHANGELOG/397-2026-06-24-task-187-harness-evidence-substrate.md`.

## Acceptance Criteria

- Harness evidence records use post-request backend runtime capabilities when a
  backend resolves them lazily.
- Future model/profile promotion evidence can distinguish live OpenRouter API
  metadata from fallback registry metadata.
- No model/provider/profile vocabulary changes ship in this first slice.
- Live OpenRouter validation remains optional and credential-gated.

## Validation

All validation passed on 2026-06-24:

- `PYTHONPATH=. poetry run pytest tests/unit/scripts/test_script_tooling.py -q -k 'vision_harness and (openrouter_backend_config or backend_path or capability_summary)'`
  - `6 passed, 44 deselected`
- `git diff --check`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_vision_runner.py tests/unit/adapters/mcp/test_vision_result_types.py -q`
  - `14 passed`
- `PYTHONPATH=. poetry run pytest ./tests/unit`
  - `3644 passed`
- `PRE_COMMIT_HOME=/tmp/pre-commit-cache poetry run pre-commit run --all-files --show-diff-on-failure`
- `PRE_COMMIT_HOME=/tmp/pre-commit-cache poetry run pre-commit run --files _docs/_CHANGELOG/397-2026-06-24-task-187-harness-evidence-substrate.md _docs/_TASKS/TASK-187-01_Harness_Capability_Summary_And_Evidence_Record_Substrate.md --show-diff-on-failure`

## Completion Summary

Closed the first `TASK-187` implementation slice as evidence substrate. The
harness now emits capability summaries from backend-refined runtime config, so
future OpenRouter model promotion decisions can rely on resolved post-request
capabilities instead of stale pre-request config. No concrete external model,
fallback profile, provider, or contract-profile promotion was made.
