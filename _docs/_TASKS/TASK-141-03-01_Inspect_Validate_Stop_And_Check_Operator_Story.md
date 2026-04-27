# TASK-141-03-01: `inspect_validate` Stop-and-Check Operator Story

**Parent:** [TASK-141-03](./TASK-141-03_Inspect_Validate_Handoff_And_Regression_Pack.md)
**Status:** ✅ Done
**Priority:** 🔴 High

**Completion Summary:** Runtime messaging and prompt/docs wording now agree
that `loop_disposition="inspect_validate"` means stop free-form modeling and
switch to inspect/measure/assert now. Degraded compare with strong truth
signals follows the same operator story.

## Objective

Align runtime messaging and operator-facing docs so
`loop_disposition="inspect_validate"` always means "pause free-form modeling
and validate with truth tools now," and make degraded compare responses follow
the same operator story.

## Business Problem

Without one explicit operator story, `inspect_validate` stays easy to ignore or
reinterpret as just another suggestion. The same weakness appears when compare
degrades and the runtime still has strong deterministic truth data.

That weakens the whole guided creature contract because a high-priority truth
handoff is only useful if the next step is clear and repeated consistently
across runtime and docs.

## Repository Touchpoints

- `server/adapters/mcp/areas/reference.py`
- `tests/unit/adapters/mcp/test_reference_images.py`
- `tests/unit/adapters/mcp/test_public_surface_docs.py`
- `tests/e2e/integration/test_guided_inspect_validate_handoff.py`
- `_docs/_PROMPTS/README.md`
- `_docs/_PROMPTS/REFERENCE_GUIDED_CREATURE_BUILD.md`
- `_docs/_MCP_SERVER/README.md`

## Acceptance Criteria

- runtime messages for `inspect_validate` explicitly tell the operator to stop
  free-form modeling and switch to inspect/measure/assert
- prompt/docs guidance names the same next-step pattern and field priority
- examples use concrete truth-layer tools instead of vague "check it" prose
- compare-unavailable or truth-only handoff messages still direct the operator
  into the same inspect/measure/assert branch instead of leaving the next step
  ambiguous

## Leaf Work Items

- tighten runtime `inspect_validate` messaging
- align prompt/docs wording and field-order guidance
- align degraded-compare wording to the same handoff contract
- add docs plus E2E regressions so the handoff wording does not drift back into
  soft prose

## Docs To Update

- `_docs/_PROMPTS/README.md`
- `_docs/_PROMPTS/REFERENCE_GUIDED_CREATURE_BUILD.md`
- `_docs/_MCP_SERVER/README.md`

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_reference_images.py`
- `tests/unit/adapters/mcp/test_public_surface_docs.py`
- `tests/e2e/integration/test_guided_inspect_validate_handoff.py`

## Changelog Impact

- include in the parent follow-on changelog entry when shipped

## Status / Board Update

- keep board tracking on `TASK-141`
- record the final inspect/validate/degraded-compare operator story in the
  parent summary when this leaf closes

## Validation

- `poetry run pytest tests/unit/adapters/mcp/test_reference_images.py tests/unit/adapters/mcp/test_public_surface_docs.py -q`
- `poetry run pytest tests/e2e/integration/test_guided_inspect_validate_handoff.py -q`
