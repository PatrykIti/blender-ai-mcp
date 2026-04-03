# TASK-124-05: Natural Request Regression Pack and Prompting

**Parent:** [TASK-124](./TASK-124_Guided_Session_Goal_And_Reference_Orchestration.md)  
**Status:** ⏳ To Do  
**Priority:** 🟡 Medium

## Objective

Validate the guided goal/reference orchestration flow against natural user
requests instead of only idealized operator scripts.

## Business Problem

Real users do not say:

- set the goal first
- then attach references
- then verify status

They say:

- "make me a low-poly squirrel"
- "here are two reference images"

If the guided surface only works when the operator already knows the correct
order, the product is not robust enough.

## Technical Direction

Add explicit regression coverage and docs for natural request flows such as:

- user gives a build goal plus references in one turn
- references arrive before a goal is active
- `guided_manual_build` no-match path with references still leads to a ready
  staged compare session

Prompt guidance should be updated to reflect the final session-safe flow, but
the runtime should still remain authoritative when prompts are imperfect.

## Repository Touchpoints

- `_docs/_PROMPTS/README.md`
- `_docs/_VISION/REFERENCE_GUIDED_CREATURE_TEST_PROMPT.md`
- `_docs/_MCP_SERVER/README.md`
- `tests/unit/adapters/mcp/test_public_surface_docs.py`
- `tests/e2e/vision/`

## Acceptance Criteria

- regression guidance includes natural-language reference-driven request flows
- prompt docs no longer encode an operator order that contradicts runtime
  preconditions
- later regressions can be measured against realistic user behavior

## Docs To Update

- `_docs/_PROMPTS/README.md`
- `_docs/_VISION/REFERENCE_GUIDED_CREATURE_TEST_PROMPT.md`
- `_docs/_MCP_SERVER/README.md`

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_public_surface_docs.py`
- `tests/e2e/vision/` when natural-flow scenarios are formalized

## Changelog Impact

- include in the parent task changelog entry when shipped
