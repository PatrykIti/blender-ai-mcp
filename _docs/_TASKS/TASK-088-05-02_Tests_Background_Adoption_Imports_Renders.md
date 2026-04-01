# TASK-088-05-02: Tests and Docs Background Adoption for Imports, Renders, Extraction, and Workflow Import

**Parent:** [TASK-088-05](./TASK-088-05_Background_Adoption_for_Imports_Renders_Extraction_and_Workflow_Import.md)  
**Status:** ✅ Done  
**Priority:** 🔴 High  
**Depends On:** [TASK-088-05-01](./TASK-088-05-01_Core_Background_Adoption_Imports_Renders.md)

---

## Objective

Add tests and documentation updates for **Background Adoption for Imports, Renders, Extraction, and Workflow Import**.

---

## Repository Touchpoints

- `tests/unit/`
- `_docs/`

---

## Planned Work

### Regression Scenarios (Required)

1. background happy path: launch -> progress -> completion -> result retrieval works end-to-end.
2. cancellation path: cancel request stops execution and reports terminal cancelled state.
3. timeout boundary path: tool/task/RPC timeouts trigger correct boundary-specific error handling.
4. foreground compatibility path: non-task calls retain expected synchronous behavior.

### Metrics To Capture

- job launch-to-first-progress latency
- cancellation acknowledgement latency
- timeout classification accuracy across MCP/task/RPC boundaries

### Documentation Deliverables

- update task-linked docs with a before/after summary tied to the captured metrics
- document exact test commands, fixtures, and profile/config used during validation
- record compatibility or migration notes when behavior differs between surfaces

---

## Acceptance Criteria

- all required regression scenarios are implemented and passing in CI/local test runs
- metrics are captured with baseline vs post-change values and attached to the task update
- docs include the regression matrix and explain expected behavior boundaries
- no untracked regressions are observed on related router/dispatcher/platform paths

---

## Atomic Work Items

1. Implement the required regression scenarios in focused unit/integration tests.
2. Run the target suites, collect metric outputs, and compare to baseline values.
3. Update docs with regression matrix, metric table, and migration/compatibility notes.
4. Verify adjacent surfaces for spillover regressions and document the result.

## Completion Summary

- adopted-path regressions now cover `scene_get_viewport`, `extraction_render_angles`, and `workflow_catalog(import_finalize)`
- local validation command:
  - `poetry run pytest tests/unit/adapters/mcp/test_task_candidacy.py tests/unit/adapters/mcp/test_background_job_registry.py tests/unit/adapters/mcp/test_task_mode_registration.py tests/unit/adapters/mcp/test_task_mode_tools.py tests/unit/adapters/rpc/test_background_job_lifecycle.py tests/unit/router/application/test_router_contracts.py tests/unit/tools/scene/test_mcp_viewport_output.py tests/unit/adapters/mcp/test_server_factory.py tests/unit/adapters/mcp/test_provider_versions.py tests/unit/adapters/mcp/test_search_surface.py tests/unit/adapters/mcp/test_versioned_surface.py tests/unit/adapters/mcp/test_surface_manifest.py tests/unit/adapters/rpc/test_timeout_coordination.py tests/unit/tools/extraction/test_render_angles.py -q`
- observed result during completion pass: `55 passed in 8.13s`
