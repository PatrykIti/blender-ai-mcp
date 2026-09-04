# TASK-157 deterministic quality-gate verifier

Date: 2026-05-01

## Summary

- Added evidence-backed quality-gate status contracts, completion blockers,
  status summaries, and verifier result payloads.
- Added the first deterministic verifier path for `required_part`,
  `attachment_seam`, and `support_contact` gates using existing
  `scene_relation_graph(...)` payloads.
- Persisted relation-graph verifier results into session `active_gate_plan`
  and marked evidence-backed gates stale after guided scene mutations.
- Documented the server-owned verification boundary and prompt expectations for
  completion blockers, status reasons, and bounded repair-tool hints.

## Validation

- `git diff --check`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_quality_gate_contracts.py tests/unit/adapters/mcp/test_quality_gate_verifier.py tests/unit/adapters/mcp/test_quality_gate_intake.py -v`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_quality_gate_contracts.py tests/unit/adapters/mcp/test_quality_gate_verifier.py tests/unit/adapters/mcp/test_quality_gate_intake.py tests/unit/adapters/mcp/test_guided_flow_state_contract.py tests/unit/adapters/mcp/test_contract_payload_parity.py tests/unit/tools/scene/test_scene_contracts.py -v`
- `PYTHONPATH=. poetry run pytest tests/unit/tools/scene/test_spatial_graph_service.py tests/unit/tools/scene/test_scene_contracts.py tests/unit/adapters/mcp/test_quality_gate_verifier.py -v`
- `PRE_COMMIT_HOME=/tmp/pre-commit-cache poetry run pre-commit run --files README.md _docs/AVAILABLE_TOOLS_SUMMARY.md _docs/_CHANGELOG/README.md _docs/_CHANGELOG/280-2026-05-01-task-157-deterministic-gate-verifier.md _docs/_MCP_SERVER/README.md _docs/_PROMPTS/README.md _docs/_PROMPTS/REFERENCE_GUIDED_CREATURE_BUILD.md _docs/_ROUTER/RESPONSIBILITY_BOUNDARIES.md _docs/_TASKS/README.md _docs/_TASKS/TASK-157-02-01_Attachment_Support_And_Contact_Gate_Verifier.md _docs/_TASKS/TASK-157-02_Deterministic_Gate_Verifier_And_Status_Model.md _docs/_TASKS/TASK-157_Goal_Derived_Quality_Gates_And_Deterministic_Verification.md _docs/_TESTS/README.md server/adapters/mcp/areas/scene.py server/adapters/mcp/contracts/__init__.py server/adapters/mcp/contracts/quality_gates.py server/adapters/mcp/session_capabilities.py server/adapters/mcp/transforms/quality_gate_verifier.py tests/unit/adapters/mcp/test_quality_gate_intake.py tests/unit/adapters/mcp/test_quality_gate_verifier.py`
