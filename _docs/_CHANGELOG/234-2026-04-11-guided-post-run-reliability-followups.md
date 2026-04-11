# 234. Guided post-run reliability follow-ups

Date: 2026-04-11

## Summary

Completed TASK-155 by closing the runtime gaps found in the latest real guided
creature session after the generic guided-governor hardening wave.

## What Changed

- fixed attachment verdict contract drift by allowing `misaligned_attachment`
  anywhere relation/checkpoint verdict lists can carry attachment semantics
- made attachment truth prefer `seated_contact` when the contact assertion
  passes, so valid support-axis offsets such as `Head -> Body` no longer turn
  into false `misaligned_attachment` loops solely from bbox center alignment
- added active-scope mismatch guidance for spatial refresh reads, so
  `scene_relation_graph(...)` / `scene_view_diagnostics(...)` can explain that
  a read-only payload did not satisfy the active guided scope
- added an empty-scene guided bootstrap branch that moves the flow to
  `bootstrap_primary_workset` before requiring spatial checks when no
  meaningful target/workset objects exist
- kept checkpoint-iterate create/initial-transform work more usable by not
  immediately re-arming spatial refresh for every small create/transform batch
  in that bounded step
- tightened checkpoint target-scope enforcement so assembled worksets cannot be
  advanced by narrowing to one safe object while required seams remain outside
  the requested scope
- made checkpoint role summaries keep missing primary/secondary roles visible
  when execution policy would still allow those role-sensitive build calls
- normalized common guided `call_tool(...)` argument slips for
  `macro_attach_part_to_surface(...)` and `scene_assert_proportion(...)`
- made compact stage checkpoint responses omit full capture records while
  preserving capture counts, truth/correction summaries, and budget metadata

## Validation

- `PYTHONPATH=. poetry run pytest tests/unit/tools/scene/test_scene_contracts.py tests/unit/tools/test_handler_rpc_alignment.py tests/unit/adapters/mcp/test_guided_flow_state_contract.py tests/unit/adapters/mcp/test_scene_guided_scope_requirements.py tests/unit/adapters/mcp/test_search_surface.py tests/unit/adapters/mcp/test_reference_images.py -q`
  - result on this machine: `157 passed`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_public_surface_docs.py tests/unit/adapters/mcp/test_visibility_policy.py tests/unit/adapters/mcp/test_guided_mode.py tests/unit/adapters/mcp/test_contract_payload_parity.py -q`
  - result on this machine: `37 passed`
- `poetry run ruff check server/adapters/mcp/contracts/scene.py server/adapters/mcp/contracts/guided_flow.py server/application/services/spatial_graph.py server/adapters/mcp/areas/reference.py server/adapters/mcp/areas/router.py server/adapters/mcp/areas/scene.py server/adapters/mcp/guided_contract.py server/adapters/mcp/session_capabilities.py tests/unit/tools/scene/test_scene_contracts.py tests/unit/tools/test_handler_rpc_alignment.py tests/unit/adapters/mcp/test_guided_flow_state_contract.py tests/unit/adapters/mcp/test_scene_guided_scope_requirements.py tests/unit/adapters/mcp/test_search_surface.py tests/unit/adapters/mcp/test_reference_images.py`
  - result on this machine: passed
- `poetry run mypy server/adapters/mcp/contracts/scene.py server/adapters/mcp/contracts/guided_flow.py server/application/services/spatial_graph.py server/adapters/mcp/areas/reference.py server/adapters/mcp/areas/router.py server/adapters/mcp/areas/scene.py server/adapters/mcp/guided_contract.py server/adapters/mcp/session_capabilities.py`
  - result on this machine: passed
- `PYTHONPATH=. poetry run pytest tests/e2e/integration/test_guided_surface_contract_parity.py tests/e2e/integration/test_guided_streamable_spatial_support.py tests/e2e/integration/test_guided_inspect_validate_handoff.py -q`
  - result on this machine: `4 passed, 2 skipped`
- `PYTHONPATH=. poetry run pytest tests/e2e/vision/test_reference_stage_assembled_creature_attachment_truth.py tests/e2e/tools/macro/test_macro_attach_part_to_surface.py tests/e2e/tools/macro/test_macro_align_part_with_contact.py -q`
  - result on this machine: `8 skipped` because the Blender-backed cases were
    gated by the local Blender RPC test environment
