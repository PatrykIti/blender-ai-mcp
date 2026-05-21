# 358. TASK-171 creature attachment-first build contract closeout

Date: 2026-05-21

## Summary

Closed `TASK-171` by aligning the creature guided-flow stage contract with the
runtime, widening active worksets after live part registration, making required
creature seam planning registry-backed, projecting one compact
`recommended_repair` handoff, and extending reference understanding with typed
attachment-first creature assembly cues.

## What Changed

- made `tail_mass` a required primary-wave exit role and `snout_mass` a
  required secondary-wave exit role on the guided creature flow
- kept buildable gate-only blockers such as `eye_pair` on bounded
  `continue_build` paths until hard seam/support blockers or repeated
  stagnation justify `inspect_validate`
- widened `guided_flow_state.active_target_scope` when
  `guided_register_part(...)` adds an in-workset creature part, so omitted-
  target compare can see the newly added part without a manual session patch
- let registered non-detail secondary focus (`snout_mass`, `foreleg_pair`,
  `hindleg_pair`) override the earlier broad primary-mass compare scope sooner
  than local-detail-only `ear_pair` / `eye_pair`
- made deterministic required creature seam planning prefer
  `guided_part_registry` role mappings and fall back to lexical-name heuristics
  only when registry evidence is unavailable
- added compact `reference_orchestrator_feedback.recommended_repair` with
  `tool_name`, `reason`, and typed `arguments_hint`
- extended the strict RU contract with typed attachment-first creature fields:
  `mass_recipe`, `attachment_plan`, `contact_expectations`,
  `shape_profile_hints`, `silhouette_landmarks`, `part_order`, and
  `must_seat_before_next_stage`
- updated public prompt/runtime docs, board state, and closeout task files to
  match the shipped contract

## Validation

- `git diff --check`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_vision_prompting.py -q`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_vision_parsing.py -q`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_guided_flow_state_contract.py -q`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_reference_images.py -q`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_quality_gate_verifier.py -q`
- `PYTHONPATH=. poetry run pytest tests/unit/tools/scene/test_spatial_graph_service.py -q`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_context_bridge.py -q`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_router_elicitation.py -q`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_contract_payload_parity.py -q`
- `PYTHONPATH=. poetry run pytest tests/e2e/integration/test_guided_surface_contract_parity.py -q`
- `PYTHONPATH=. poetry run pytest tests/e2e/integration/test_guided_gate_state_transport.py -q -k guided_support_gate_state_roundtrip_over_stdio`
