# TASK-146-04-02: Main Instructions And Prompt Surface Routing To Prompt Library

**Parent:** [TASK-146-04](./TASK-146-04_Search_First_Prompt_Library_And_Instruction_Surface_Hardening.md)
**Status:** ✅ Done
**Priority:** 🟠 High
**Depends On:** [TASK-146-04-01](./TASK-146-04-01_Generic_Search_First_Guided_Operating_Prompt.md)

**Completion Summary:** Completed on 2026-04-07. Updated the main public
instruction surfaces so they point more explicitly to `_docs/_PROMPTS/` and
reinforce search-first behavior instead of relying on diffuse ad hoc guidance.

## Objective

Update the main operator-facing instruction surfaces so they rely more
explicitly on `_docs/_PROMPTS/` as the canonical library instead of trying to
embed all guided operating logic diffusely across many docs.

## Repository Touchpoints

- `README.md`
- `_docs/_MCP_SERVER/README.md`
- `_docs/_PROMPTS/README.md`
- any other public instruction/doc surface that currently duplicates this logic

## Acceptance Criteria

- main docs explicitly direct operators/models toward `_docs/_PROMPTS/`
- duplicated guidance is reduced or better synchronized
- search-first guidance and prompt-library routing are consistent across the
  main public surfaces

## Docs To Update

- `README.md`
- `_docs/_MCP_SERVER/README.md`
- `_docs/_PROMPTS/README.md`

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_public_surface_docs.py`

## Changelog Impact

- include in the parent TASK-146 changelog entry when shipped

## Status / Board Update

- closed on 2026-04-07 with TASK-146
