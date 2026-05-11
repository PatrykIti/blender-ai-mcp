# 342. TASK-166 ranking downgrade actionability

Date: 2026-05-11
Task: `TASK-166`

## Summary

- Prevented packet ranking downgrades to `low_information` or `blocked` from
  inheriting actionable correction focus from the earlier extraction pass.
- Kept downgraded packets visible as uncertainty through `compare_diagnostics`
  while avoiding correction candidates that are no longer justified by the
  ranking result.
- Removed stale packet-planning helper duplicates from
  `server/adapters/mcp/areas/reference_planner.py`; the durable packet policy
  remains owned by `server/adapters/mcp/areas/reference_compare_packets.py`.
- Switched the local Transformers backend to the same effective output-token
  cap used by the other vision backends, and let backend-refined OpenRouter
  capabilities update runner/staged `budget_control` diagnostics before final
  projection.
- Allowed compact orchestrator feedback to project standalone
  `compare_diagnostics` uncertainty even when RU summary/strategy state is not
  present.
- Added unit regressions for merge-time downgrade behavior and compact staged
  compare actionability, fail-safe staged image budgets, backend budget
  projection, local backend output caps, standalone diagnostics feedback, and
  sidecar config docs.

## Runtime / Contract Notes

- No public MCP tool names or payload fields changed.
- Ranking failures still preserve extraction evidence as uncertainty.
- Ranking downgrades are treated differently from failures: they retain packet
  diagnostics but do not promote extraction-only focus into actionable
  correction candidates.
- `budget_control` continues to report configured and effective limits; lazy
  backend capability refreshes now feed the effective values back to the runner
  and staged compare projection.

## Validation

- Passed in this pass:
  - `poetry run pytest tests/unit/adapters/mcp/test_reference_compare_packets.py tests/unit/adapters/mcp/test_vision_runner.py tests/unit/adapters/mcp/test_reference_images.py::test_reference_compare_stage_checkpoint_emits_compare_diagnostics_on_compact_ranking_downgrade tests/unit/adapters/mcp/test_reference_images.py::test_reference_compare_stage_checkpoint_uses_effective_fail_safe_image_budget tests/unit/adapters/mcp/test_reference_images.py::test_reference_orchestrator_feedback_projects_compare_diagnostics_without_ru_summary tests/unit/adapters/mcp/test_vision_local_backend.py::test_local_backend_uses_effective_output_token_cap tests/unit/adapters/mcp/test_public_surface_docs.py::test_mcp_client_config_examples_document_guided_creature_contract -q`
    (`29 passed`)
  - `poetry run pytest tests/unit/adapters/mcp/test_reference_images.py tests/unit/adapters/mcp/test_reference_compare_packets.py tests/unit/adapters/mcp/test_contract_payload_parity.py tests/unit/adapters/mcp/test_public_surface_docs.py tests/unit/adapters/mcp/test_vision_prompting.py tests/unit/adapters/mcp/test_vision_parsing.py tests/unit/adapters/mcp/test_vision_result_types.py tests/unit/adapters/mcp/test_vision_silhouette.py tests/unit/adapters/mcp/test_vision_runtime_config.py tests/unit/adapters/mcp/test_vision_runner.py tests/unit/adapters/mcp/test_vision_local_backend.py tests/unit/scripts/test_script_tooling.py -q`
    (`302 passed`)
  - `PRE_COMMIT_HOME=/tmp/pre-commit-cache poetry run pre-commit run --all-files --show-diff-on-failure`
    (passed)
  - `poetry run pytest ./tests/unit` (`3334 passed`)
  - `poetry run python scripts/run_e2e_tests.py` (`470 passed, 3 skipped`)
