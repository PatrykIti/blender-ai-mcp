# TASK-134: Stage Compare Error Response Hardening

**Status:** ✅ Done
**Priority:** 🟠 High
**Category:** Guided Reference Reliability
**Estimated Effort:** Small
**Dependencies:** TASK-121-07, TASK-124
**Follow-on After:** [TASK-121-07](./TASK-121-07_Vision_Guided_Iterative_Correction_Loop.md), [TASK-124](./TASK-124_Guided_Session_Goal_And_Reference_Orchestration.md)

**Completion Summary:** The staged reference-compare path now preserves its
structured error contract when target-scope resolution fails. Invalid
`collection_name` input no longer risks an uncaught second failure while
building the response; the adapter now returns the intended structured
`error=str(exc)` payload with `assembled_target_scope=None`.

## Objective

Close the review regression where `reference_compare_stage_checkpoint(...)`
could fail again while constructing its error response after an invalid
collection-scope resolution error.

## Business Problem

The stage-compare path already had the right top-level behavior:

- resolve capture scope
- catch `RuntimeError`
- return a structured MCP error payload

But `_stage_compare_response(...)` still rebuilt assembled target scope on all
paths, including the error path. That meant a bad `collection_name` could
trigger the same failure twice:

1. once during the intended scope-resolution step
2. again inside the error-response builder

That undermines the product contract for guided staged compare, where invalid
scope input should still return one structured failure payload instead of an
uncaught tool failure.

## Business Outcome

If this follow-on is closed correctly, the repo regains:

- stable structured failure semantics for invalid stage-compare collection
  scope
- safer staged compare behavior on the guided reference surface
- regression coverage for the exact invalid-collection failure mode

## Scope

This follow-on covers:

- stage-compare error-response construction when target-scope resolution fails
- focused regression coverage for invalid `collection_name`
- concise MCP docs/changelog updates for the hardened structured-error path

This follow-on does **not** cover:

- redesigning assembled-target-scope modeling
- changing success-path target-scope semantics
- changing staged readiness policy

## Repository Touchpoints

- `server/adapters/mcp/areas/reference.py`
- `tests/unit/adapters/mcp/test_reference_images.py`
- `_docs/_MCP_SERVER/README.md`
- `_docs/_CHANGELOG/README.md`
- `_docs/_TASKS/README.md`

## Acceptance Criteria

- invalid `collection_name` input on `reference_compare_stage_checkpoint(...)`
  returns the intended structured `error=str(exc)` payload
- the error path does not re-trigger capture-scope resolution inside the
  response builder
- focused regression coverage proves the invalid-collection path directly

## Docs To Update

- `_docs/_MCP_SERVER/README.md`
- `_docs/_CHANGELOG/README.md`
- `_docs/_TASKS/README.md`

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_reference_images.py`

## Changelog Impact

- add one `_docs/_CHANGELOG/*` entry for the stage-compare error-path hardening

## Status / Board Update

- track this as a standalone completed follow-on on `_docs/_TASKS/README.md`

## Validation

- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_reference_images.py -q`
