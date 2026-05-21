# TASK-171-06: Squirrel Regression Proof, Docs, And Closeout

**Parent:** [TASK-171](./TASK-171_Creature_Attachment_First_Build_Contract_And_Structured_Vision_Handoff.md)
**Status:** ⏳ To Do
**Priority:** 🔴 High
**Objective:** Close the family with live registration-backed squirrel regression proof, canonical docs updates, and board/changelog synchronization.
**Repository Touchpoints:** `tests/e2e/integration/test_guided_gate_state_transport.py`, `tests/e2e/integration/test_guided_streamable_spatial_support.py`, `tests/e2e/integration/test_guided_surface_contract_parity.py`, `tests/e2e/vision/test_reference_guided_squirrel_quality_regression.py`, `tests/e2e/vision/test_reference_stage_truth_handoff.py`, `tests/e2e/vision/test_reference_understanding_runtime_surface.py`, `_docs/_PROMPTS/REFERENCE_GUIDED_CREATURE_BUILD.md`, `_docs/_PROMPTS/GUIDED_SESSION_START.md`, `_docs/_MCP_SERVER/README.md`, `_docs/_VISION/REFERENCE_UNDERSTANDING_ROADMAP.md`, `_docs/_VISION/README.md`, `_docs/_TASKS/README.md`, `_docs/_TASKS/TASK-171_Creature_Attachment_First_Build_Contract_And_Structured_Vision_Handoff.md`, `_docs/_TASKS/TASK-171-0*.md`, `_docs/_CHANGELOG/README.md`, `_docs/_CHANGELOG/*`
**Acceptance Criteria:**
- the squirrel regression lane exercises the live `guided_register_part(...)` and active-workset path instead of manual session seeding shortcuts where that matters to the repaired contract
- the public registration/transport owner lanes also prove the repaired compact feedback and active-workset behavior without relying only on seeded vision fixtures
- prompt/docs wording matches the shipped runtime contract for stage advancement, buildable gate blockers, compact repair plans, and RU assembly structure
- board and changelog state close cleanly with no dangling open children under the parent

## Implementation Notes

- the current squirrel regression e2e manually seeds `guided_part_registry` and
  `active_target_scope`, which is useful for today’s scope assertions but not
  enough for the `TASK-171` live registration repair
- the closeout proof must therefore cover both:
  - public registration/transport owner lanes
  - creature-specific squirrel regression lanes
- refresh the regression family to cover:
  - live part registration
  - widened active scope on the next compare/iterate pass
  - earlier local secondary compare precedence where appropriate
  - compact repair-plan projection
  - opaque-name creature seam fallback or registry-first coverage
- do not let docs drift back into “prompt-only” framing; this family exists
  precisely because the current remaining bug class is runtime-contract work

## Pseudocode

```python
register_guided_part("OpaqueBodyA", "body_core")
register_guided_part("OpaqueHeadA", "head_mass")
register_guided_part("OpaqueTailA", "tail_mass")
register_guided_part("OpaqueEarL", "ear_pair")

iterate = reference_iterate_stage_checkpoint(...)
assert "OpaqueEarL" in iterate.target_objects
assert iterate.reference_orchestrator_feedback.recommended_repair is not None
```

## Runtime / Security Contract Notes

- keep the closeout proof on repo-supported guided/reference paths; do not rely
  on private harness-only shortcuts as the only evidence
- when docs describe new compact repair-plan fields or RU assembly fields, keep
  their advisory/authority limits explicit

## Tests To Add/Update

- `tests/e2e/integration/test_guided_gate_state_transport.py`
- `tests/e2e/integration/test_guided_streamable_spatial_support.py`
- `tests/e2e/integration/test_guided_surface_contract_parity.py`
- `tests/e2e/vision/test_reference_guided_squirrel_quality_regression.py`
- `tests/e2e/vision/test_reference_stage_truth_handoff.py`
- `tests/e2e/vision/test_reference_understanding_runtime_surface.py`

## Docs To Update

- `_docs/_PROMPTS/REFERENCE_GUIDED_CREATURE_BUILD.md`
- `_docs/_PROMPTS/GUIDED_SESSION_START.md`
- `_docs/_MCP_SERVER/README.md`
- `_docs/_VISION/REFERENCE_UNDERSTANDING_ROADMAP.md`
- `_docs/_VISION/README.md`
- `_docs/_TASKS/README.md`
- `_docs/_TASKS/TASK-171_Creature_Attachment_First_Build_Contract_And_Structured_Vision_Handoff.md`
- the `TASK-171-0*.md` child files whose statuses, acceptance proof, or closeout summaries change
- `_docs/_CHANGELOG/README.md`
- one new `_docs/_CHANGELOG/*` entry

## Changelog Impact

- add one `_docs/_CHANGELOG/*` entry when the first `TASK-171` runtime slice
  lands and extend/update it through closeout as appropriate

## Validation Commands

- `git diff --check`
- `PYTHONPATH=. poetry run pytest tests/e2e/integration/test_guided_gate_state_transport.py -q`
- `PYTHONPATH=. poetry run pytest tests/e2e/integration/test_guided_streamable_spatial_support.py -q`
- `PYTHONPATH=. poetry run pytest tests/e2e/integration/test_guided_surface_contract_parity.py -q`
- `PYTHONPATH=. poetry run pytest tests/e2e/vision/test_reference_guided_squirrel_quality_regression.py -q`
- `PYTHONPATH=. poetry run pytest tests/e2e/vision/test_reference_stage_truth_handoff.py -q`
- `PYTHONPATH=. poetry run pytest tests/e2e/vision/test_reference_understanding_runtime_surface.py -q`
- `PYTHONPATH=. poetry run pytest ./tests/unit`
- `poetry run python scripts/run_e2e_tests.py`

## Validation Category

- regression, docs, and governance closeout proof
