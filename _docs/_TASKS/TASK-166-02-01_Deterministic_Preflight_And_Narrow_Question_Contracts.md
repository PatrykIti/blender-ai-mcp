# TASK-166-02-01: Deterministic Preflight And Narrow Question Contracts

**Parent:** [TASK-166-02](./TASK-166-02_Truth_First_Two_Pass_Compare_Execution.md)  
**Status:** ⏳ To Do  
**Priority:** 🔴 High
**Objective:** Define the deterministic preflight and narrow packet question contract that sits in front of any LLM compare call.

## Repository Touchpoints

- `server/adapters/mcp/areas/reference.py`
- `server/adapters/mcp/contracts/reference.py`
- `server/adapters/mcp/sampling/result_types.py`
- `server/adapters/mcp/vision/prompting.py`
- `server/adapters/mcp/vision/parsing.py`
- `server/adapters/mcp/vision/runner.py`

## Implementation Notes

- Likely implementation shape:
  - one packet-preflight helper that resolves deterministic inputs first
  - one packet-question builder that receives the resolved truth slice plus
    selected captures/reference ids
- Keep `server/adapters/mcp/vision/runner.py` limited to bounded execution and
  budget enforcement; packet question schema ownership belongs in
  `server/adapters/mcp/sampling/result_types.py`,
  `server/adapters/mcp/vision/prompting.py`, and
  `server/adapters/mcp/vision/parsing.py`.
- Preflight must always be grounded in:
  - `scene_scope_graph`
  - `scene_relation_graph`
  - `scene_view_diagnostics`
- Packet questions should be narrow, for example:
  - "Is tail silhouette too short from side?"
  - "Are ears visible and readable from front?"
- Error cases to make explicit:
  - missing reference slice
  - missing target view coverage
  - preflight ambiguity that should yield a typed blocked or low-information
    packet instead of a broad fallback prompt

## Acceptance Criteria

- the compare family can express packet-specific questions
- deterministic preflight stays first authority
- packet question contracts can name the packet id, selected reference ids,
  selected capture labels, and required deterministic inputs for that packet

## Validation Commands

- `git diff --check`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_reference_images.py -q`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_vision_prompting.py -q`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_vision_parsing.py -q`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_vision_result_types.py -q`

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_reference_images.py`
- `tests/unit/adapters/mcp/test_vision_prompting.py`
- `tests/unit/adapters/mcp/test_vision_parsing.py`
- `tests/unit/adapters/mcp/test_vision_result_types.py`
- packet-preflight contract tests for blocked, low-information, and narrow
  question shaping outcomes

## Docs To Update

- `_docs/_VISION/README.md`
- `_docs/_MCP_SERVER/README.md`
- `README.md`
- `_docs/AVAILABLE_TOOLS_SUMMARY.md`
- `_docs/_TESTS/README.md`

## Changelog Impact

- include in the umbrella `_docs/_CHANGELOG/` entry when packet preflight and
  narrow question contracts ship

## Status / Board Update

- keep parent `TASK-166` and this leaf aligned when deterministic packet
  preflight closes or splits into follow-on work
