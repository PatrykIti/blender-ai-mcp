# TASK-140-05-03: Evidence Taxonomy, Promotion Criteria, and Operator Reporting

**Parent:** [TASK-140-05](./TASK-140-05_Regression_Harness_Provider_Notes_And_Operator_Guidance_For_Expanded_Profiles.md)
**Depends On:** [TASK-140-05-01](./TASK-140-05-01_Automated_Coverage_And_Harness_Scenario_Expansion.md)
**Status:** ⏳ To Do
**Priority:** 🟠 High

## Objective

Formalize how the repo records support claims for external multimodal families
so docs-reviewed support, automated evidence, and operator reports remain
separate and reproducible.

This evidence taxonomy is for external model-family support and promotion. It
must not be treated as `TASK-157` gate-verifier evidence. A promoted
`vision_contract_profile` can produce structured compare/iterate payloads that
feed gate proposals or bounded perception evidence, but it cannot make a
quality gate pass without the `TASK-157` verifier layer.

## Repository Touchpoints

- `_docs/_VISION/README.md`
- `_docs/_VISION/HYBRID_LOOP_REAL_CREATURE_EVAL.md`
- `_docs/_VISION/REFERENCE_GUIDED_CREATURE_TEST_PROMPT.md`
- `_docs/_VISION/CROSS_DOMAIN_REFINEMENT_ROUTING_EVAL.md`
- `README.md`

## Acceptance Criteria

- the repo has one explicit evidence taxonomy for external family support
- the taxonomy explicitly distinguishes model/profile support evidence from
  quality-gate verifier evidence
- promotion criteria from "docs-reviewed" to "recommended default" are
  documented
- operator reports include the selected `vision_contract_profile` and enough
  context to be reproduced later
- provider notes no longer blur operator folklore with harness-ranked support

## Docs To Update

- `README.md`
- `_docs/_VISION/README.md`
- `_docs/_VISION/HYBRID_LOOP_REAL_CREATURE_EVAL.md`
- `_docs/_VISION/REFERENCE_GUIDED_CREATURE_TEST_PROMPT.md`
- `_docs/_VISION/CROSS_DOMAIN_REFINEMENT_ROUTING_EVAL.md`

## Tests To Add/Update

- none directly; this leaf mainly governs docs/evidence policy

## Changelog Impact

- include in the parent slice changelog entry when shipped
