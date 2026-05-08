# TASK-166-02-02: Visual Extraction And Correction Ranking Split

**Parent:** [TASK-166-02](./TASK-166-02_Truth_First_Two_Pass_Compare_Execution.md)  
**Status:** ✅ Done
**Priority:** 🔴 High
**Objective:** Separate packet-level visual extraction from later correction ranking so one failed ranking step does not invalidate usable extraction evidence.

## Completion Summary

- staged compare packet execution now runs:
  - one bounded extraction pass first
  - one bounded ranking pass only when extraction returns
    `ranking_recommendation="rank"`
- packet-local prompt/schema/parser seams now distinguish extraction and
  ranking request phases through the packet compare contract
- ranking failure no longer discards usable extraction evidence; staged compare
  keeps the extraction result and marks the packet `ranking_status="error"`
- packet clean / low-information / blocked outcomes now skip the ranking pass
  explicitly instead of inferring that state from missing fields

## Repository Touchpoints

- `server/adapters/mcp/areas/reference.py`
- `server/adapters/mcp/contracts/reference.py`
- `server/adapters/mcp/areas/reference_planner.py`
- `server/adapters/mcp/sampling/result_types.py`
- `server/adapters/mcp/vision/prompting.py`
- `server/adapters/mcp/vision/parsing.py`
- `tests/unit/adapters/mcp/test_reference_images.py`
- `tests/unit/adapters/mcp/test_contract_payload_parity.py`
- `tests/unit/adapters/mcp/test_public_surface_docs.py`
- `tests/unit/router/application/test_router_contracts.py`
- `tests/e2e/integration/test_guided_gate_state_transport.py`

## Implementation Notes

- Extraction pass should be small and retryable.
- Ranking pass should be skipped when extraction shows a clean packet or too
  little information.
- Both phases still project back through the staged compare assembler; this leaf
  does not create a second iterate-owned ranking path.
- Prompt/schema/parser ownership for extraction and ranking status stays in
  `server/adapters/mcp/sampling/result_types.py`,
  `server/adapters/mcp/vision/prompting.py`, and
  `server/adapters/mcp/vision/parsing.py`; do not push that contract work down
  into `server/adapters/mcp/vision/runner.py` alone.
- Packet status, skip reasons, and ranking failure details should stay explicit
  enough for additive compare diagnostics and compact orchestrator projection.

## Acceptance Criteria

- extraction-only success is representable in the compare contract
- ranking is a second bounded phase, not an always-on payload burden
- extraction and ranking can expose independent packet status so a clean,
  low-information, skipped, or failed ranking phase is explicit instead of
  being inferred from omission
- ranking skipped after a clean or low-information extraction is represented as
  an intentional outcome with a reason, not as a hidden failure

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_reference_images.py`
- `tests/unit/adapters/mcp/test_vision_prompting.py`
- `tests/unit/adapters/mcp/test_vision_parsing.py`
- `tests/unit/adapters/mcp/test_vision_result_types.py`
- `tests/unit/adapters/mcp/test_contract_payload_parity.py`
- `tests/unit/adapters/mcp/test_public_surface_docs.py`
- `tests/unit/router/application/test_router_contracts.py`
- staged compare/iterate contract tests covering extraction-only success,
  ranking skip, and ranking failure projection
- `tests/e2e/integration/test_guided_gate_state_transport.py` when packet
  status or diagnostics become client-visible

## Docs To Update

- `_docs/_VISION/README.md`
- `_docs/_MCP_SERVER/README.md`
- `README.md`
- `_docs/AVAILABLE_TOOLS_SUMMARY.md`
- `_docs/_TESTS/README.md`

## Changelog Impact

- include in the umbrella `_docs/_CHANGELOG/` entry when extraction/ranking
  split semantics ship

## Status / Board Update

- keep parent `TASK-166` and this leaf aligned when extraction/ranking split
  semantics close or are split into follow-on work

## Validation Commands

- `git diff --check`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_reference_images.py -q`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_vision_prompting.py -q`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_vision_parsing.py -q`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_vision_result_types.py -q`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_contract_payload_parity.py -q`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_public_surface_docs.py -q`
- `PYTHONPATH=. poetry run pytest tests/unit/router/application/test_router_contracts.py -q`
- `PYTHONPATH=. poetry run pytest tests/e2e/integration/test_guided_gate_state_transport.py -q`
- `poetry run pytest ./tests/unit`
- `poetry run python scripts/run_e2e_tests.py`
