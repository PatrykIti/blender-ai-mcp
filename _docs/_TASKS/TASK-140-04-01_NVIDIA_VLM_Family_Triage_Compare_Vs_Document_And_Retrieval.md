# TASK-140-04-01: NVIDIA VLM Family Triage, Compare vs Document and Retrieval

**Parent:** [TASK-140-04](./TASK-140-04_NVIDIA_VLM_Support_And_Exclusion_Policy.md)
**Status:** ⏳ To Do
**Priority:** 🟠 High

## Objective

Create one explicit NVIDIA family matrix that separates:

- compare-capable generative VLMs
- document parsing models
- retrieval/embedding/reranking-style visual models

## Repository Touchpoints

- `_docs/_VISION/README.md`
- `_docs/_TASKS/TASK-140-04_NVIDIA_VLM_Support_And_Exclusion_Policy.md`

## Acceptance Criteria

- the task package records which NVIDIA models are even eligible for compare
  integration
- document/retrieval NVIDIA models are called out explicitly as non-compare
  classes when that is the right product boundary
- later implementation leaves can work from a stable shortlist

## Implementation Notes

- use official NVIDIA family docs and current operator evidence to separate:
  - compare-capable generative VLMs
  - document parsers
  - retrieval/embedding/reranking families
- keep this leaf docs-first so later runtime-routing leaves can implement from
  a stable shortlist instead of rediscovering family scope

## Docs To Update

- `_docs/_VISION/README.md`

## Tests To Add/Update

- none at this leaf

## Changelog Impact

- include in the parent slice changelog entry when shipped

## Validation Commands

- `git diff --check`
- targeted consistency audit between this leaf and `_docs/_VISION/README.md`

## Status / Board Update

- remains nested under `TASK-140-04`
- should close before routing or exclusion leaves claim a stable NVIDIA matrix
