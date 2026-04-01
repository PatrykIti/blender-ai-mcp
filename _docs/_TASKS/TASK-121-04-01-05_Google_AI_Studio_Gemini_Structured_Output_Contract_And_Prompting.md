# TASK-121-04-01-05: Google AI Studio Gemini Structured Output Contract and Prompting

**Follow-on After:** [TASK-121-04-01](./TASK-121-04-01_Small_Vision_Runtime_Selection_And_Execution_Policy.md)  
**Board Tracking:** Standalone provider-hardening carveout kept open after the
parent closed. `_docs/_TASKS/README.md` tracks it as its own open item while
the older numbering is preserved for continuity.  
**Status:** ⏳ To Do  
**Priority:** 🔴 High

Google AI Studio / Gemini now has a working provider path for bounded vision,
but the current generic external contract is still too heavy for reliable
iterative checkpoint/reference compare flows.

## Objective

Add a Gemini-specific structured-output contract and prompt path so Gemini can
reliably support:

- `reference_compare_*`
- `reference_iterate_stage_checkpoint(...)`
- harder staged creature/reference flows

without drifting into malformed or partial JSON.

## Business Problem

Current status on this branch:

- simple macro smoke paths can succeed on Gemini
- harder staged/reference compare flows still often return malformed or
  incomplete JSON
- the current generic external contract appears too broad for Gemini on these
  compare-heavy requests

That means the provider transport works, but the product contract is still not
stable enough for real iterative compare loops.

## Implementation Direction

- add one provider-specific Gemini contract for iterative compare flows
- keep the contract narrower than the generic external contract
- add one Gemini-specific prompt builder for:
  - checkpoint vs reference
  - staged iterative compare
- add provider-specific parse-repair for near-JSON / truncated-JSON Gemini
  responses
- keep OpenRouter/local paths on their current contract unless they also
  benefit from the narrower compare contract

Suggested first-pass Gemini compare contract:

- `goal_summary`
- `reference_match_summary`
- `shape_mismatches`
- `proportion_mismatches`
- `correction_focus`
- `next_corrections`

Likely omit from the Gemini compare-specific path:

- `likely_issues`
- `recommended_checks`
- `confidence`
- `captures_used`
- possibly `visible_changes`

## Repository Touchpoints

- `server/adapters/mcp/vision/prompting.py`
- `server/adapters/mcp/vision/backends.py`
- `server/adapters/mcp/vision/parsing.py`
- `tests/unit/adapters/mcp/test_vision_external_backend.py`
- `tests/e2e/vision/`
- `_docs/_VISION/README.md`

## Docs To Update

- `_docs/_VISION/README.md`
- `_docs/_MCP_SERVER/README.md`
- `_docs/_TASKS/README.md` if the board state changes

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_vision_external_backend.py`
- `tests/unit/adapters/mcp/test_vision_prompting.py`
- `tests/unit/adapters/mcp/test_vision_parsing.py`
- `tests/e2e/vision/` for staged compare flows when provider behavior changes

## Changelog Impact

- add a `_docs/_CHANGELOG/*.md` entry if this task changes provider behavior,
  prompt/parse guarantees, or provider-facing documentation

## Status / Board Update

- keep this leaf `⏳ To Do` until the Gemini-specific contract, prompting path,
  docs, and tests are complete
- when it closes, update this file, the closed parent follow-on note, and
  `_docs/_TASKS/README.md`

## Acceptance Criteria

- Gemini iterative/reference compare returns valid structured output reliably
- provider-specific prompt/contract behavior is explicit in code and docs
- Gemini no longer needs to be treated as unstable for staged compare flows
