# TASK-166-02: Truth-First Two-Pass Compare Execution

**Parent:** [TASK-166](./TASK-166_Hierarchical_Reference_Compare_Perceived_Evidence_And_Budget_Control.md)  
**Status:** 🚧 In Progress
**Priority:** 🔴 High
**Objective:** Split compare into deterministic preflight + narrow visual extraction first, then bounded correction ranking only when needed.

## Repository Touchpoints

- `server/adapters/mcp/areas/reference.py`
- `server/adapters/mcp/areas/reference_planner.py`
- `server/adapters/mcp/areas/reference_feedback.py`
- `server/adapters/mcp/contracts/reference.py`
- `server/adapters/mcp/sampling/result_types.py`
- `server/adapters/mcp/vision/prompting.py`
- `server/adapters/mcp/vision/parsing.py`
- `server/adapters/mcp/vision/runner.py`
- `server/application/services/`
- `tests/unit/adapters/mcp/test_reference_images.py`

## Implementation Notes

- Pass 1:
  - deterministic truth preflight
  - narrow packet question
  - 3-5 visual mismatches max
- Pass 2:
  - correction ranking
  - support-tool hints
  - packet synthesis where needed
- Keep `server/adapters/mcp/vision/runner.py` as the bounded
  transport/budget executor; the narrow extraction-vs-ranking contract belongs
  in typed result, prompting, and parsing seams, while packet execution
  ordering should move into dedicated helper/service code rather than
  accreting inside the `@mcp.tool` wrapper.

## Current Flow Integration

- `reference_compare_stage_checkpoint(...)` should remain the public staged
  orchestration entrypoint for packet extraction, conditional ranking, and
  packet synthesis for the current stage; durable execution ordering and
  ranking/synthesis policy should live in dedicated helper/service code rather
  than in the `@mcp.tool` body itself.
- `reference_iterate_stage_checkpoint(...)` should consume packet results and
  the already synthesized staged compare result when deciding loop disposition;
  it must not become a second ranking/synthesis owner flow.
- Existing deterministic gates, `truth_followup`, and `planner_summary` stay in
  the same staged response family; the internal sequencing changes, not the
  public contract ownership.
- `reference_orchestrator_feedback` remains the compact consumer-facing read
  model built from the staged compare result, not a new direct projection from
  raw packet internals.

## Pseudocode

```text
for packet in compare_plan.packet_order:
  preflight = build_packet_preflight(packet, truth_inputs, view_inputs)
  extraction = run_packet_extraction(packet, preflight)
  ranking = maybe_run_packet_ranking(packet, extraction)
  collect_packet_result(packet, preflight, extraction, ranking)

staged_compare = assemble_staged_compare(packet_results, budget_state)
iterate = consume_staged_compare(staged_compare)
```

## Runtime / Security Contract Notes

- Ranking/extraction remain server-owned staged compare work; iterate must not
  become a second public or hidden execution path for packet ranking.
- Packet status and diagnostics remain additive to the existing staged compare /
  iterate contracts; they do not replace `truth_followup`,
  `correction_candidates`, or `planner_summary`.
- Public client-visible failure/uncertainty semantics must stay explicit across
  stdio and Streamable HTTP.

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_reference_images.py`
- `tests/unit/adapters/mcp/test_vision_prompting.py`
- `tests/unit/adapters/mcp/test_vision_parsing.py`
- `tests/unit/adapters/mcp/test_vision_result_types.py`
- `tests/unit/adapters/mcp/test_vision_runner.py`
- `tests/unit/adapters/mcp/test_contract_payload_parity.py`
- `tests/unit/adapters/mcp/test_public_surface_docs.py`
- `tests/unit/router/application/test_router_contracts.py`
- `tests/e2e/vision/test_reference_stage_truth_handoff.py`
- `tests/e2e/integration/test_guided_gate_state_transport.py`

## Docs To Update

- `_docs/_VISION/README.md`
- `_docs/_MCP_SERVER/README.md`
- `README.md`
- `_docs/AVAILABLE_TOOLS_SUMMARY.md`
- `_docs/_TESTS/README.md`

## Changelog Impact

- include in the umbrella `_docs/_CHANGELOG/` entry when two-pass staged compare
  ships

## Status / Board Update

- keep parent `TASK-166` and this subtask aligned in `_docs/_TASKS/README.md`
- when this subtask closes, update child-leaf state and note whether transport
  proof shipped or remains explicit follow-on work

## Validation Commands

- `git diff --check`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_vision_prompting.py -q`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_vision_parsing.py -q`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_vision_result_types.py -q`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_vision_runner.py -q`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_reference_images.py -q`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_contract_payload_parity.py -q`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_public_surface_docs.py -q`
- `PYTHONPATH=. poetry run pytest tests/unit/router/application/test_router_contracts.py -q`
- `PYTHONPATH=. poetry run pytest tests/e2e/vision/test_reference_stage_truth_handoff.py -q`
- `PYTHONPATH=. poetry run pytest tests/e2e/integration/test_guided_gate_state_transport.py -q`
- `poetry run pytest ./tests/unit`
- `poetry run python scripts/run_e2e_tests.py`

## Acceptance Criteria

- compare no longer mixes extraction and ranking in one always-large payload
- the LLM receives narrower packet questions instead of one whole-model prompt
- extraction and ranking outcomes are independently representable so skipped or
  failed ranking does not erase usable packet evidence
- iterate consumes staged packet synthesis and loop guidance instead of owning a
  second ranking/synthesis pass
