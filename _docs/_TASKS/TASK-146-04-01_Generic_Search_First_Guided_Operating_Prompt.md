# TASK-146-04-01: Generic Search-First Guided Operating Prompt

**Parent:** [TASK-146-04](./TASK-146-04_Search_First_Prompt_Library_And_Instruction_Surface_Hardening.md)
**Status:** ✅ Done
**Priority:** 🔴 High
**Depends On:** [TASK-146-04](./TASK-146-04_Search_First_Prompt_Library_And_Instruction_Surface_Hardening.md)

**Completion Summary:** Completed on 2026-04-07. Hardened
`GUIDED_SESSION_START.md` into the generic search-first guided operating
stabilizer for the shaped surface.

## Objective

Create or strengthen one generic `_PROMPTS/` asset that tells the model how to
operate on the guided surface without drifting into speculative hidden-tool
calls.

## Repository Touchpoints

- `_docs/_PROMPTS/`
- `_docs/_PROMPTS/README.md`

## Acceptance Criteria

- one generic guided operating prompt clearly exists in `_PROMPTS/`
- it explicitly teaches:
  - search-first discovery
  - direct-use rules for visible tools
  - reduced speculative `call_tool(...)` usage
  - prompt-library-first behavior
- prompt/doc tests protect that contract

## Docs To Update

- `_docs/_PROMPTS/README.md`
- the new or updated prompt asset itself

## Tests To Add/Update

- prompt/doc regression coverage under `tests/unit/adapters/mcp/`

## Changelog Impact

- include in the parent TASK-146 changelog entry when shipped

## Status / Board Update

- closed on 2026-04-07 with TASK-146
