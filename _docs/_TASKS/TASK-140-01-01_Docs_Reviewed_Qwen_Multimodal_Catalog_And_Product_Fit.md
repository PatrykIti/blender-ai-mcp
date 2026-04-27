# TASK-140-01-01: Docs-Reviewed Qwen Multimodal Catalog and Product Fit

**Parent:** [TASK-140-01](./TASK-140-01_Qwen_Family_Contract_Profile_Matrix_And_Routing.md)
**Status:** ⏳ To Do
**Priority:** 🔴 High

## Objective

Produce one explicit, docs-reviewed catalog of the Qwen multimodal families
that matter for this repo and classify each family by product fit before
runtime code starts routing them.

## Technical Direction

This leaf should not start by inventing profiles in code. It should first pin
down the external family space from official docs and then answer:

- which family names/aliases should the repo recognize
- which families are compare-capable
- which families are document/OCR-oriented
- which families should stay out of staged compare entirely

## Repository Touchpoints

- `_docs/_VISION/README.md`
- `_docs/_TASKS/TASK-140-01_Qwen_Family_Contract_Profile_Matrix_And_Routing.md`

## Acceptance Criteria

- the Qwen family matrix is explicit enough that later leaves can implement
  routing without rediscovering product scope
- the task package distinguishes:
  - compare-suitable Qwen families
  - document/OCR-oriented Qwen families
  - out-of-scope families
- the matrix records stable family names and notable aliases/snapshots where
  they affect runtime routing

## Docs To Update

- `_docs/_VISION/README.md`

## Tests To Add/Update

- none at this leaf; later leaves own runtime tests

## Changelog Impact

- include in the parent slice changelog entry when shipped
