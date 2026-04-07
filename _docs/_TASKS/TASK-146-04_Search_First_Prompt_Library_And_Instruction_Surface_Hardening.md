# TASK-146-04: Search-First Prompt Library And Instruction Surface Hardening

**Parent:** [TASK-146](./TASK-146_Guided_Runtime_Guardrails_Vision_Profile_And_Prompting_Hardening.md)
**Status:** ⏳ To Do
**Priority:** 🔴 High
**Depends On:** [TASK-130](./TASK-130_Default_Guided_Surface_Bootstrap_Consistency.md), [TASK-141](./TASK-141_Guided_Creature_Run_Contract_And_Schema_Drift_Hardening.md)

## Objective

Reduce speculative hidden-tool guessing by hardening the prompt/instruction
surfaces around one clearer guided operating model:

- use `_docs/_PROMPTS/` as the canonical operator library
- prefer `search_tools(...)` before speculative `call_tool(...)`
- only call directly visible tools directly
- treat `call_tool(...)` as an informed dispatch wrapper, not a hidden-tool
  guess channel

## Repository Touchpoints

- `_docs/_PROMPTS/`
- `_docs/_PROMPTS/README.md`
- `README.md`
- `_docs/_MCP_SERVER/README.md`
- any prompt assets exposed through the MCP prompt library
- public-surface docs/tests

## Acceptance Criteria

- `_docs/_PROMPTS/` contains stronger generic anti-drift guided operating
  guidance
- main instruction surfaces explicitly push models/operators toward prompt
  assets in `_docs/_PROMPTS/`
- search-first guidance is stronger and more consistent across docs/prompts
- tests lock the updated prompt-library and docs wording in place

## Docs To Update

- `_docs/_PROMPTS/README.md`
- `README.md`
- `_docs/_MCP_SERVER/README.md`
- prompt asset files under `_docs/_PROMPTS/`

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_public_surface_docs.py`
- any prompt/doc regression tests affected by the wording changes

## Changelog Impact

- include in the parent TASK-146 changelog entry when shipped

## Execution Structure

| Order | Leaf | Purpose |
|------|------|---------|
| 1 | [TASK-146-04-01](./TASK-146-04-01_Generic_Search_First_Guided_Operating_Prompt.md) | Strengthen the generic prompt-library operating asset to reduce hidden-tool guessing |
| 2 | [TASK-146-04-02](./TASK-146-04-02_Main_Instructions_And_Prompt_Surface_Routing_To_Prompt_Library.md) | Make the main instruction/doc surfaces point more explicitly to `_PROMPTS/` and the search-first model |

## Status / Board Update

- nested under TASK-146 as the prompt/instruction hardening subtree
