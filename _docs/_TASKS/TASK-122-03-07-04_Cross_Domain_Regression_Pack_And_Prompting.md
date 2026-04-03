# TASK-122-03-07-04: Cross-Domain Regression Pack and Prompting

**Parent:** [TASK-122-03-07](./TASK-122-03-07_Deterministic_Cross_Domain_Refinement_Routing_And_Sculpt_Exposure.md)  
**Status:** ✅ Done  
**Priority:** 🟡 Medium

**Completion Summary:** Added an explicit cross-domain regression pack and
updated prompt guidance so refinement-family routing is no longer documented
only through the squirrel flow. The docs now spell out expected routing across
hard-surface, architecture, garments, anatomy, local-form creature/character
 cases, and low-poly assembled models, and prompt guidance now tells operators
to read `refinement_route` / `refinement_handoff` before choosing the next tool
family.

## Objective

Validate refinement-family routing across multiple Blender domains and make the
prompt guidance explicit enough to keep the policy stable.

## Business Problem

If refinement-family routing is only tested on one squirrel flow, it will
likely regress on other content classes:

- buildings
- electronics
- garments
- organs
- characters
- animals

The product needs one explicit cross-domain regression story.

## Technical Direction

Add or formalize representative scenario slices such as:

- hard-surface / electronics:
  - should stay on modeling/mesh/macro
- building massing / architecture:
  - should stay on modeling/mesh/macro
- garment or soft accessory:
  - may justify deterministic sculpt-region refinement
- organ / anatomy blob:
  - may justify deterministic sculpt-region refinement
- creature / character local form:
  - may justify deterministic sculpt-region refinement

Prompt docs should explain:

- when sculpt should be considered
- when it should explicitly not be considered
- that viewport/camera review and truth checks still remain the authority over
  correctness

## Repository Touchpoints

- `_docs/_VISION/README.md`
- `_docs/_VISION/HYBRID_LOOP_REAL_CREATURE_EVAL.md`
- `_docs/_PROMPTS/README.md`
- `_docs/_VISION/REFERENCE_GUIDED_CREATURE_TEST_PROMPT.md`
- `tests/e2e/vision/`
- `tests/unit/adapters/mcp/test_public_surface_docs.py`

## Acceptance Criteria

- regression guidance covers more than one content class
- prompt guidance explains how refinement-family routing should be interpreted
- later regressions can be measured against an explicit cross-domain pack

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_public_surface_docs.py`
- `tests/e2e/vision/` when new regression scenarios are added

## Changelog Impact

- include in the parent follow-on changelog entry when shipped

## Status / Board Update

- this leaf is closed
- the parent follow-on is now complete
