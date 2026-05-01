# Tests Documentation

## Quick Start

### Unit Tests (No Blender Required)

```bash
# Run all unit tests
PYTHONPATH=. poetry run pytest tests/unit/ -v

# Run specific area
PYTHONPATH=. poetry run pytest tests/unit/tools/mesh/ -v
```

Important:

- do **not** mix `tests/unit` and `tests/e2e` in one `pytest` invocation
- unit tests install global `bpy` / `bmesh` / `mathutils` mocks from
  [tests/unit/conftest.py](../../tests/unit/conftest.py)
- E2E tests expect real Blender RPC and should run in a separate process

Recommended split runner:

```bash
./scripts/run_unit_then_e2e.sh
```

### E2E Tests (Requires Blender)

**Automated (Recommended):**
```bash
# Full automated flow: build → install addon → start Blender → run tests → cleanup
python3 scripts/run_e2e_tests.py

# Options:
python3 scripts/run_e2e_tests.py --skip-build      # Use existing addon ZIP
python3 scripts/run_e2e_tests.py --keep-blender    # Don't kill Blender after tests
python3 scripts/run_e2e_tests.py --quiet           # Don't stream output to console
```

Current runner diagnostics written automatically on every automated run:

- Blender stdout/stderr runtime log:
  `tests/e2e/blender_runtime_YYYYMMDD_HHMMSS.log`
- pytest session log:
  `tests/e2e/e2e_test_{PASSED|FAILED}_YYYYMMDD_HHMMSS.log`
- addon-side RPC crash trace:
  `/tmp/blender-ai-mcp/rpc_trace_YYYYMMDD_HHMMSS_<pid>.jsonl`
  unless `BLENDER_AI_MCP_TRACE_DIR` overrides the directory

When Blender disappears mid-run, start from those two artifacts:

- the runner-side `blender_runtime_*.log`
- the addon-side `rpc_trace_*.jsonl`

Together they usually reveal whether the last visible event was:

- Blender startup/runtime output
- one specific RPC command entering the addon
- one specific background job starting/failing

**Manual:**
```bash
# 1. Start Blender with addon enabled
# 2. Run E2E tests
PYTHONPATH=. poetry run pytest tests/e2e/ -v

# Or run unit and E2E in two separate pytest processes
./scripts/run_unit_then_e2e.sh
```

### E2E RPC Availability Behavior

`tests/e2e/conftest.py` now does a short retry window before deciding that
Blender RPC is unavailable for the current pytest session.

- the initial E2E availability check now performs a real `ping` RPC instead of
  relying on one fast connect attempt only
- this reduces false `skipped` runs when Blender/addon startup is slightly
  slower than pytest collection
- router/tool E2E suites are still marked `skip` for the current pytest
  session if RPC never becomes reachable during that startup window

Current tuning:

- `E2E_RPC_STARTUP_WAIT_SECONDS`
  default: `8.0`
- `E2E_RPC_RETRY_INTERVAL_SECONDS`
  default: `0.5`

Practical note:

- if Blender RPC was down during collection and then comes back later, rerun
  `pytest tests/e2e ...` in a new process so the session-level availability
  cache is rebuilt

## E2E Env Matrix

Use this table as the single quick-reference for environment variables that
gate or shape the current E2E suites.

| Test family | Required env vars | Optional env vars | Typical command |
|---|---|---|---|
| Standard Blender-backed E2E | none if Blender RPC is already reachable on the default host/port | `BLENDER_RPC_HOST`, `BLENDER_RPC_PORT` | `PYTHONPATH=. poetry run pytest tests/e2e/ -v` |
| Automated addon reinstall + Blender launch flow | none | `--blender-path`, `--skip-build`, `--keep-blender`, `--quiet` CLI flags | `python3 scripts/run_e2e_tests.py` |
| Real view-variant MLX comparison | `RUN_REAL_VISION_MODEL_COMPARISON=1` | use the repo/runtime MLX model defaults unless you intentionally change local config | `RUN_REAL_VISION_MODEL_COMPARISON=1 poetry run pytest tests/e2e/vision/test_real_view_variant_model_comparison.py -q -m slow` |
| Real reference-guided creature comparison | `RUN_REAL_REFERENCE_GUIDED_CREATURE_EVAL=1`, `VISION_REFERENCE_FRONT_PATH`, `VISION_REFERENCE_SIDE_PATH` | `VISION_REFERENCE_CREATURE_MODEL` | `RUN_REAL_REFERENCE_GUIDED_CREATURE_EVAL=1 VISION_REFERENCE_FRONT_PATH=/abs/front.png VISION_REFERENCE_SIDE_PATH=/abs/side.png PYTHONPATH=. poetry run pytest tests/e2e/vision/test_reference_guided_creature_comparison.py -q` |
| Live OpenRouter/Qwen structured-output smoke | `RUN_REAL_OPENROUTER_QWEN_JSON_MODE=1`, `OPENROUTER_API_KEY` | `VISION_OPENROUTER_MODEL` | `RUN_REAL_OPENROUTER_QWEN_JSON_MODE=1 OPENROUTER_API_KEY=... PYTHONPATH=. poetry run pytest tests/e2e/vision/test_openrouter_qwen_json_mode.py -q -s` |
| Docker runtime dependency smoke | `RUN_DOCKER_RUNTIME_VISION_SMOKE=1` | `BLENDER_AI_MCP_DOCKER_IMAGE` (defaults to `blender-ai-mcp:local`) | `RUN_DOCKER_RUNTIME_VISION_SMOKE=1 PYTHONPATH=. poetry run pytest tests/e2e/integration/test_docker_runtime_vision_dependencies.py -q` |
| Streamable guided session-state regression | none | local socket binding required; sandboxed runners may need approval or may skip | `poetry run pytest tests/e2e/integration/test_guided_streamable_spatial_support.py -q -rs` |

OpenRouter/Qwen runtime defaults used by the current repo unless you override
them:

- `VISION_OPENROUTER_REQUIRE_PARAMETERS=false`
- `VISION_OPENROUTER_ENABLE_RESPONSE_HEALING=true`
- `VISION_OPENROUTER_PREFER_JSON_OBJECT_FOR_QWEN=true`

Source-of-truth pointers:

- env names and defaults: [`.env.example`](../../.env.example)
- OpenRouter/Gemini runtime examples: [`_docs/_VISION/README.md`](../_VISION/README.md)
- MCP client/container examples: [`_docs/_MCP_SERVER/MCP_CLIENT_CONFIG_EXAMPLES.md`](../_MCP_SERVER/MCP_CLIENT_CONFIG_EXAMPLES.md)

---

## Test Statistics

| Type | Count | Execution Time |
|------|-------|----------------|
| Unit Tests | 3114 collected | collect-only ~11 seconds; full runtime depends on selected lanes |
| E2E Tests | 428 collected | collect-only ~17 seconds; Blender-backed runtime depends on active RPC/Blender state |

Current repo-wide unit coverage (`server + blender_addon + scripts`):

- `76%`

## Test Coverage by Area

| Area | Unit Tests | E2E Tests |
|------|------------|-----------|
| Scene | ✅ | ✅ |
| Modeling | ✅ | 🔄 |
| Mesh | ✅ | ✅ |
| Collection | ✅ | ✅ |
| Material | ✅ | ✅ |
| UV | ✅ | ✅ |
| Sculpt | ✅ | ✅ |
| Export | ✅ | ✅ |
| Import | ✅ | ✅ |
| Baking | ✅ | ✅ |
| System | ✅ | ✅ |
| Curve | ✅ | 🔄 |
| Router | ✅ | ✅ |

### Router & Workflow Subsystems

| Subsystem | Unit Tests | E2E Tests | Related Tasks |
|-----------|------------|-----------|---------------|
| **Ensemble Matching** | ✅ | ✅ | TASK-053, TASK-054 |
| **Parameter Resolution** | ✅ | ✅ | TASK-055-FIX |
| **Workflow Execution** | ✅ | ✅ | TASK-041, TASK-052 |
| **Expression Evaluator** | ✅ | 📋 Planned | **TASK-056-1**: Extended math functions (13 new) ✅ DONE |
| **Condition Evaluator** | ✅ | 📋 Planned | **TASK-056-2**: Parentheses support, operator precedence ✅ DONE |
| **Parameter Validation** | ✅ | 📋 Planned | **TASK-056-3**: Enum constraints ✅ DONE |
| **Step Dependencies** | ✅ | 📋 Planned | **TASK-056-4**: Topological sort, timeout, retry ✅ DONE |
| **Computed Parameters** | ✅ | 📋 Planned | **TASK-056-5**: Dependency graph, expression eval ✅ DONE |
| **Dynamic Workflow Steps** | 📋 Planned | 📋 Planned | **TASK-055-FIX-7**: Conditional planks, adaptive count |

---

## TASK-088 Background Task Coverage

Background task mode now has focused unit coverage for:

- candidacy inventory and adopted endpoint classification
- task/runtime compatibility shims for the current FastMCP+Docket baseline
- background job registry and result store bookkeeping
- task-mode registration semantics:
  - `forbidden`
  - `optional`
  - `required`
- addon-side RPC lifecycle:
  - launch
  - poll
  - cancel
  - collect
- adopted tool paths for:
  - `scene_get_viewport`
  - `extraction_render_angles`
  - `workflow_catalog(import_finalize)`
  - `export_glb`
  - `export_fbx`
  - `export_obj`
  - `import_obj`
  - `import_fbx`
  - `import_glb`
  - `import_image_as_plane`

Primary local validation commands for TASK-088:

```bash
poetry run pytest tests/unit/adapters/mcp/test_task_candidacy.py tests/unit/adapters/mcp/test_background_job_registry.py tests/unit/adapters/mcp/test_task_mode_registration.py tests/unit/adapters/mcp/test_task_mode_tools.py tests/unit/adapters/rpc/test_background_job_lifecycle.py tests/unit/router/application/test_router_contracts.py tests/unit/tools/scene/test_mcp_viewport_output.py -q

poetry run pytest tests/unit/adapters/mcp/test_server_factory.py tests/unit/adapters/mcp/test_provider_versions.py tests/unit/adapters/mcp/test_search_surface.py tests/unit/adapters/mcp/test_versioned_surface.py tests/unit/adapters/mcp/test_surface_manifest.py tests/unit/adapters/rpc/test_timeout_coordination.py tests/unit/tools/extraction/test_render_angles.py -q
```

Task-mode regression is intentionally unit/integration focused for now.
No Blender-backed E2E suite has been added yet for background task submission itself.

Primary local validation commands for TASK-098 extension work:

```bash
poetry run pytest tests/unit/adapters/mcp/test_task_candidacy.py tests/unit/adapters/mcp/test_task_mode_registration.py tests/unit/adapters/mcp/test_task_mode_tools.py tests/unit/tools/export/test_export_tools.py tests/unit/tools/import_tool/test_import_handler.py -q

poetry run pytest tests/unit/adapters/mcp/test_server_factory.py tests/unit/adapters/mcp/test_provider_versions.py tests/unit/adapters/mcp/test_search_surface.py tests/unit/adapters/mcp/test_versioned_surface.py tests/unit/adapters/mcp/test_surface_manifest.py tests/unit/adapters/rpc/test_background_job_lifecycle.py tests/unit/adapters/rpc/test_timeout_coordination.py tests/unit/adapters/mcp/test_background_job_registry.py tests/unit/adapters/mcp/test_task_mode_registration.py tests/unit/adapters/mcp/test_task_mode_tools.py -q
```

Primary local validation commands for TASK-099 runtime alignment:

```bash
poetry run pytest tests/unit/adapters/mcp/test_task_runtime_policy.py tests/unit/adapters/mcp/test_background_job_registry.py tests/unit/adapters/mcp/test_server_factory.py tests/unit/adapters/mcp/test_task_mode_registration.py tests/unit/adapters/mcp/test_task_mode_tools.py -q
```

Primary local validation commands for TASK-093 diagnostics/pagination:

```bash
poetry run pytest tests/unit/router/application/test_router_contracts.py tests/unit/adapters/mcp/test_session_phase.py tests/unit/adapters/mcp/test_guided_mode.py tests/unit/adapters/mcp/test_task_runtime_policy.py tests/unit/adapters/mcp/test_background_job_registry.py tests/unit/adapters/mcp/test_timeout_policy.py tests/unit/tools/workflow_catalog/test_workflow_catalog_import.py tests/unit/adapters/mcp/test_pagination_policy.py -q
```

Primary local validation commands for TASK-095 semantic boundary hardening:

```bash
poetry run pytest tests/unit/router/infrastructure/test_semantic_boundary_audit.py tests/unit/router/infrastructure/test_semantic_boundary_telemetry.py tests/unit/router/application/test_correction_audit.py tests/unit/router/application/resolver/test_parameter_resolver.py tests/unit/router/application/matcher/test_semantic_workflow_matcher.py tests/unit/router/application/matcher/test_ensemble_aggregator.py -q
```

Primary local validation commands for TASK-083 platform closure:

```bash
poetry run pytest tests/unit/adapters/mcp/test_context_bridge.py tests/unit/adapters/mcp/test_platform_migration_docs.py tests/unit/adapters/mcp/test_provider_inventory.py tests/unit/adapters/mcp/test_runtime_inventory.py tests/unit/adapters/mcp/test_server_factory.py tests/unit/adapters/mcp/test_surface_bootstrap.py tests/unit/adapters/mcp/test_surface_inventory.py tests/unit/adapters/mcp/test_surface_compatibility.py tests/unit/adapters/mcp/test_transform_pipeline.py tests/unit/router/infrastructure/test_mcp_tools_metadata_alignment.py tests/unit/router/adapters/test_mcp_integration.py -q
```

Primary local validation commands for TASK-092 sampling assistants:

```bash
poetry run pytest tests/unit/adapters/mcp/test_assistant_runner.py tests/unit/adapters/mcp/test_aliasing_transform.py tests/unit/adapters/mcp/test_sampling_assistant_docs.py tests/unit/router/application/test_router_contracts.py tests/unit/tools/scene/test_scene_inspect_mega.py tests/unit/tools/scene/test_scene_state_assistants.py tests/unit/tools/mesh/test_mesh_inspect_mega.py tests/unit/tools/mesh/test_mesh_contracts.py tests/unit/tools/workflow_catalog/test_workflow_catalog_assistants.py -q
```

Primary local validation commands for TASK-094 guardrails and read-only pilot:

```bash
poetry run pytest tests/unit/adapters/mcp/test_server_factory.py tests/unit/adapters/mcp/test_visibility_policy.py tests/unit/adapters/mcp/test_code_mode_pilot.py -q
```

Primary local validation commands for TASK-094 benchmark and decision memo:

```bash
poetry run pytest tests/unit/adapters/mcp/test_server_factory.py tests/unit/adapters/mcp/test_visibility_policy.py tests/unit/adapters/mcp/test_code_mode_pilot.py tests/unit/adapters/mcp/test_code_mode_benchmarks.py tests/unit/adapters/mcp/test_code_mode_pilot_docs.py tests/unit/adapters/mcp/test_code_mode_decision_docs.py -q
```

Primary local validation commands for TASK-118 scene render/world/configuration wave:

```bash
poetry run pytest tests/unit/tools/scene/test_scene_configure_mega.py tests/unit/tools/scene/test_scene_configure_handler.py tests/unit/tools/scene/test_scene_mcp_tools_batch.py tests/unit/tools/scene/test_scene_contracts.py tests/unit/tools/test_handler_rpc_alignment.py tests/unit/adapters/mcp/test_structured_contract_delivery.py tests/unit/adapters/mcp/test_provider_inventory.py tests/unit/adapters/mcp/test_delivery_strategy.py tests/unit/adapters/mcp/test_legacy_flat_pagination_compat.py tests/unit/adapters/mcp/test_search_surface.py tests/unit/router/infrastructure/test_mcp_tools_metadata_alignment.py tests/unit/router/infrastructure/test_metadata_loader.py tests/unit/adapters/mcp/test_surface_manifest.py tests/unit/adapters/mcp/test_tool_inventory.py tests/unit/adapters/mcp/test_runtime_inventory.py tests/unit/adapters/mcp/test_contract_docs.py -q

poetry run pytest tests/e2e/tools/scene/test_scene_configure_roundtrip.py -q
```

Primary local validation commands for TASK-119 public-surface hardening:

```bash
poetry run pytest tests/unit/router/infrastructure/test_mcp_tools_metadata_alignment.py tests/unit/router/infrastructure/test_metadata_loader.py tests/unit/adapters/mcp/test_visibility_policy.py tests/unit/adapters/mcp/test_guided_mode.py tests/unit/adapters/mcp/test_search_surface.py tests/unit/adapters/mcp/test_name_resolution.py tests/unit/adapters/mcp/test_surface_manifest.py tests/unit/adapters/mcp/test_aliasing_transform.py tests/unit/adapters/mcp/test_tool_inventory.py tests/unit/adapters/mcp/test_public_surface_docs.py tests/unit/adapters/mcp/test_contract_docs.py tests/unit/adapters/mcp/test_delivery_strategy.py tests/unit/adapters/mcp/test_structured_contract_delivery.py tests/unit/tools/scene/test_scene_create_mega.py tests/unit/tools/scene/test_scene_contracts.py tests/unit/tools/mesh/test_mesh_select_mega.py tests/unit/tools/mesh/test_mesh_select_targeted_mega.py tests/unit/tools/mesh/test_mesh_contracts.py tests/unit/adapters/mcp/test_guided_surface_benchmarks.py -q
```

Primary local validation commands for TASK-120 macro regression/benchmark pack:

```bash
poetry run pytest tests/unit/tools/macro/test_macro_cutout_recess.py tests/unit/tools/macro/test_macro_finish_form.py tests/unit/tools/macro/test_macro_relative_layout.py tests/unit/tools/modeling/test_macro_cutout_recess_mcp.py tests/unit/tools/modeling/test_macro_finish_form_mcp.py tests/unit/tools/scene/test_macro_relative_layout_mcp.py tests/unit/adapters/mcp/test_macro_contracts.py tests/unit/adapters/mcp/test_provider_inventory.py tests/unit/adapters/mcp/test_delivery_strategy.py tests/unit/adapters/mcp/test_structured_contract_delivery.py tests/unit/adapters/mcp/test_contract_docs.py tests/unit/adapters/mcp/test_search_surface.py tests/unit/adapters/mcp/test_legacy_flat_pagination_compat.py tests/unit/adapters/mcp/test_guided_surface_benchmarks.py tests/unit/router/infrastructure/test_mcp_tools_metadata_alignment.py tests/unit/router/infrastructure/test_metadata_loader.py tests/unit/router/application/test_intent_classifier.py -q

poetry run pytest tests/e2e/tools/macro/test_macro_cutout_recess.py tests/e2e/tools/macro/test_macro_finish_form.py tests/e2e/tools/macro/test_macro_relative_layout.py -q
```

Primary local validation commands for TASK-121 vision runtime/capture/evaluation scaffolding:

```bash
poetry run pytest tests/unit/adapters/mcp/test_reference_images.py tests/unit/tools/macro/test_macro_capture_bundle.py tests/unit/adapters/mcp/test_macro_contracts.py tests/unit/adapters/mcp/test_vision_runtime_config.py tests/unit/adapters/mcp/test_vision_result_types.py tests/unit/adapters/mcp/test_vision_external_backend.py tests/unit/adapters/mcp/test_vision_local_backend.py tests/unit/adapters/mcp/test_vision_capture_bundle.py tests/unit/adapters/mcp/test_vision_capture_runtime.py tests/unit/adapters/mcp/test_vision_runner.py tests/unit/adapters/mcp/test_vision_macro_reporting.py tests/unit/adapters/mcp/test_vision_macro_mcp_integration.py tests/unit/adapters/mcp/test_vision_macro_reference_integration.py tests/unit/adapters/mcp/test_vision_evaluation.py tests/unit/infrastructure/test_vision_di.py tests/unit/adapters/mcp/test_assistant_runner.py tests/unit/adapters/mcp/test_sampling_assistant_docs.py -q
```

Primary local validation commands for TASK-144 camera-aware view diagnostics:

```bash
PYTHONPATH=. poetry run pytest tests/unit/tools/scene/test_scene_contracts.py tests/unit/tools/scene/test_scene_mcp_tools_batch.py tests/unit/tools/scene/test_viewport_control.py tests/unit/tools/test_handler_rpc_alignment.py tests/unit/adapters/mcp/test_structured_contract_delivery.py tests/unit/adapters/mcp/test_provider_inventory.py tests/unit/adapters/mcp/test_tool_inventory.py tests/unit/adapters/mcp/test_search_surface.py tests/unit/adapters/mcp/test_visibility_policy.py tests/unit/adapters/mcp/test_guided_mode.py tests/unit/adapters/mcp/test_guided_surface_benchmarks.py tests/unit/adapters/mcp/test_reference_images.py -q

PYTHONPATH=. poetry run pytest tests/e2e/tools/scene/test_scene_view_diagnostics.py tests/e2e/tools/scene/test_scene_get_viewport.py tests/e2e/tools/scene/test_scene_get_viewport_camera.py -q
```

Primary local validation commands for TASK-146 guided runtime hardening:

```bash
PYTHONPATH=. poetry run pytest tests/unit/router/application/test_workflow_triggerer.py tests/unit/adapters/mcp/test_vision_external_backend.py tests/unit/adapters/mcp/test_search_surface.py tests/unit/adapters/mcp/test_public_surface_docs.py tests/unit/adapters/mcp/test_server_factory.py tests/unit/scripts/test_script_tooling.py tests/e2e/router/test_guided_manual_handoff.py -q

poetry run mypy
```

Primary local validation commands for TASK-147 guided build cleanup recovery hatch:

```bash
PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_visibility_policy.py tests/unit/adapters/mcp/test_search_surface.py tests/unit/adapters/mcp/test_guided_surface_benchmarks.py tests/unit/adapters/mcp/test_public_surface_docs.py tests/e2e/integration/test_guided_surface_contract_parity.py -q
```

Additional coverage added after the first TASK-146 hardening slice:

- transport-backed guided search/call boundary:
  - `tests/e2e/integration/test_guided_search_first_call_tool_boundary.py`
- Streamable HTTP guided session-state/visibility regression:
  - `tests/e2e/integration/test_guided_streamable_spatial_support.py`
  - validates same-session guided visibility, cleanup recovery, dirty mesh
    re-arm, reconnect continuity, and Streamable HTTP return behavior for
    routed mutating calls
- broader guided direct-call trigger regressions:
  - `tests/e2e/router/test_guided_direct_calls_do_not_trigger_workflows.py`
- OpenRouter/Qwen live structured-output smoke (opt-in):
  - `tests/e2e/vision/test_openrouter_qwen_json_mode.py`
- Docker runtime dependency smoke (opt-in):
  - `tests/e2e/integration/test_docker_runtime_vision_dependencies.py`

Targeted validation command for those additions:

```bash
PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_vision_runtime_config.py tests/e2e/integration/test_guided_search_first_call_tool_boundary.py tests/e2e/router/test_guided_direct_calls_do_not_trigger_workflows.py tests/e2e/vision/test_openrouter_qwen_json_mode.py tests/e2e/integration/test_docker_runtime_vision_dependencies.py -q
```

Opt-in environment gates for the new real-runtime smokes:

- `RUN_REAL_OPENROUTER_QWEN_JSON_MODE=1`
  - requires `OPENROUTER_API_KEY`
- `RUN_DOCKER_RUNTIME_VISION_SMOKE=1`
  - optional `BLENDER_AI_MCP_DOCKER_IMAGE=<image>` override, defaults to
    `blender-ai-mcp:local`

Repo-tracked synthetic vision evaluation scenarios now live under:

- `tests/fixtures/vision_eval/synthetic_round_cutout/`
- `tests/fixtures/vision_eval/synthetic_no_change/`
- `tests/fixtures/vision_eval/synthetic_reference_mismatch/`
- `tests/fixtures/vision_eval/default_cube_to_picnic_table/`
- `tests/fixtures/vision_eval/squirrel_head_to_face/`
- `tests/fixtures/vision_eval/squirrel_face_to_body/`
- `tests/fixtures/vision_eval/squirrel_head_to_body/`
- `tests/fixtures/vision_eval/squirrel_head_to_face_user_top/`
- `tests/fixtures/vision_eval/squirrel_face_to_body_user_top/`
- `tests/fixtures/vision_eval/squirrel_head_to_body_user_top/`
- `tests/fixtures/vision_eval/squirrel_head_to_face_camera_perspective/`
- `tests/fixtures/vision_eval/squirrel_face_to_body_camera_perspective/`
- `tests/fixtures/vision_eval/squirrel_head_to_body_camera_perspective/`

Opt-in real-model comparison coverage for the new view-family variants:

- `tests/e2e/vision/test_real_view_variant_model_comparison.py`
- requires `RUN_REAL_VISION_MODEL_COMPARISON=1`
- currently intended for local/macOS Metal validation, not default CI

Opt-in real reference-guided creature comparison coverage:

- `tests/e2e/vision/test_reference_guided_creature_comparison.py`
- requires:
  - `RUN_REAL_REFERENCE_GUIDED_CREATURE_EVAL=1`
  - `VISION_REFERENCE_FRONT_PATH`
  - `VISION_REFERENCE_SIDE_PATH`
- uses repo-tracked squirrel checkpoint images plus local front/side reference
  images to validate correction-oriented output on a real creature flow

Hybrid-loop assembled-creature regression pack:

- `_docs/_VISION/HYBRID_LOOP_REAL_CREATURE_EVAL.md`
- `_docs/_VISION/REFERENCE_GUIDED_CREATURE_TEST_PROMPT.md`
- `_docs/_VISION/CROSS_DOMAIN_REFINEMENT_ROUTING_EVAL.md`
- combines:
  - `tests/e2e/vision/test_reference_stage_truth_handoff.py`
  - `tests/e2e/vision/test_reference_guided_creature_comparison.py`
- review staged hybrid-loop output in this order:
  - `loop_disposition`
  - `correction_candidates`
  - `refinement_route`
  - `refinement_handoff`
  - `truth_followup`
  - `action_hints`
  - `correction_focus`

Focused unit coverage now also protects:

- deterministic silhouette metric/action-hint contracts on
  `tests/unit/adapters/mcp/test_reference_images.py`
- optional segmentation-sidecar config defaults and opt-in validation on
  `tests/unit/adapters/mcp/test_vision_runtime_config.py`
- goal-derived quality-gate contract and intake coverage on:
  - `tests/unit/adapters/mcp/test_quality_gate_contracts.py`
  - `tests/unit/adapters/mcp/test_quality_gate_verifier.py`
  - `tests/unit/adapters/mcp/test_quality_gate_intake.py`
  - `tests/unit/adapters/mcp/test_guided_flow_state_contract.py`
- gate-driven guided visibility/search coverage on:
  - `tests/unit/adapters/mcp/test_visibility_policy.py`
  - `tests/unit/adapters/mcp/test_search_surface.py`
- reference checkpoint gate summary projection coverage on:
  - `tests/unit/adapters/mcp/test_reference_images.py`
- compact view-space contracts, search/discovery shaping, and reference-loop
  adoption hints on:
  - `tests/unit/tools/scene/test_scene_contracts.py`
  - `tests/unit/tools/scene/test_scene_mcp_tools_batch.py`
  - `tests/unit/tools/scene/test_viewport_control.py`
  - `tests/unit/adapters/mcp/test_search_surface.py`
  - `tests/unit/adapters/mcp/test_visibility_policy.py`
  - `tests/unit/adapters/mcp/test_reference_images.py`

First Blender-backed E2E coverage for the guided utility prep path now includes:

- `tests/e2e/tools/scene/test_scene_clean_scene.py`
- `tests/e2e/tools/scene/test_scene_get_viewport.py`
- `tests/e2e/tools/scene/test_scene_view_diagnostics.py`
- `tests/e2e/router/test_utility_goal_boundary.py`

Camera-faithful viewport capture regression coverage now also includes:

- `tests/e2e/tools/scene/test_scene_get_viewport_camera.py`

---

## E2E Test Runner Workflow

```
┌─────────────────────────────────────────────────────────────┐
│ 1. BUILD ADDON                                              │
│    python scripts/build_addon.py → outputs/blender_ai_mcp.zip│
├─────────────────────────────────────────────────────────────┤
│ 2. CHECK & UNINSTALL OLD ADDON                              │
│    Blender --background → addon_utils.disable + rmtree      │
├─────────────────────────────────────────────────────────────┤
│ 3. INSTALL NEW ADDON                                        │
│    Blender --background → extract ZIP + addon_utils.enable  │
├─────────────────────────────────────────────────────────────┤
│ 4. START BLENDER WITH RPC                                   │
│    Blender (GUI mode) - RPC server requires main event loop │
│    Wait for port 8765...                                    │
├─────────────────────────────────────────────────────────────┤
│ 5. RUN E2E TESTS                                            │
│    poetry run pytest tests/e2e/ -v --tb=short               │
├─────────────────────────────────────────────────────────────┤
│ 6. SAVE LOG & CLEANUP                                       │
│    tests/e2e/e2e_test_{PASSED|FAILED}_{timestamp}.log       │
│    Kill Blender process                                     │
└─────────────────────────────────────────────────────────────┘
```

---

## Latest E2E Test Run

See [EXAMPLE_E2E_TESTS_RESULT.md](./EXAMPLE_E2E_TESTS_RESULT.md) for full output.

**Historical sample (2025-11-30):**
- **142 tests passed** in 12.25s
- Platform: macOS (Darwin), Python 3.13.9, Blender 5.0
- Kept as a sample output reference; current collection counts are listed above.

---

## Directory Structure

```
tests/
├── unit/                    # Fast tests with mocked bpy (CI/CD)
│   └── tools/
│       ├── mesh/
│       ├── modeling/
│       ├── scene/
│       ├── sculpt/
│       └── ...
├── e2e/                     # Integration tests with real Blender
│   ├── conftest.py          # RPC fixtures
│   └── tools/
│       ├── baking/
│       ├── collection/
│       ├── export/
│       ├── import_tool/
│       ├── knife_cut/
│       ├── material/
│       ├── mesh/
│       ├── scene/
│       ├── sculpt/
│       ├── system/
│       └── uv/
└── fixtures/                # Shared test fixtures
```

---

## CI/CD

GitHub Actions run **only unit tests** (no Blender available in CI):

- `pr_checks.yml` - Runs on pull requests
- `release.yml` - Runs on push to main

---

## Upcoming Test Requirements

### TASK-056: Workflow System Enhancements

**New Unit Tests Required:**

```
tests/unit/router/application/evaluator/
├── test_expression_evaluator_extended.py   # TASK-056-1: 13 new math functions
├── test_condition_evaluator_parentheses.py # TASK-056-2: Parentheses & precedence
└── test_parameter_validation_enum.py       # TASK-056-3: Enum constraints

tests/unit/router/infrastructure/
├── test_dependency_resolver.py             # TASK-056-4: Step dependencies
└── test_computed_parameters.py             # TASK-056-5: Computed param resolution
```

**Test Coverage Goals:**
- Expression evaluator: Each new function (tan, atan2, log, exp, etc.)
- Condition evaluator: Operator precedence `not` > `and` > `or`, nested parentheses
- Parameter validation: Enum constraints, rejection of invalid values
- Dependency resolver: Graph construction, circular dependency detection
- Computed parameters: Evaluation order, dependency tracking

**E2E Integration Tests:**
- Workflow loading with new features
- End-to-end execution with dependencies
- Error handling and retry logic
- Complex boolean conditions in real workflows

### TASK-055-FIX-7: Dynamic Plank System

**Manual Verification Required:**

```bash
# Test simple_table.yaml with different widths
ROUTER_ENABLED=true poetry run python -c "
from server.router.application.router import SupervisorRouter
router = SupervisorRouter()

# Test cases:
# 1. Default (0.8m) → 8 planks × 0.10m each
result = router.set_goal('simple table 0.8m wide')

# 2. Narrow (0.45m) → 5 planks × 0.09m each (fractional)
result = router.set_goal('table 0.45m wide')

# 3. Wide (1.2m) → 12 planks × 0.10m each
result = router.set_goal('table 1.2m wide')

# 4. Fractional (0.83m) → 9 planks × 0.0922m each
result = router.set_goal('table 0.83m wide')
"
```

**Visual Verification:**
- Use `scene_get_viewport` to verify plank count and spacing
- Check plank width adapts correctly (`table_width / ceil(table_width / 0.10)`)
- Verify no gaps or overlaps in table top
- Confirm fractional widths work correctly

**Acceptance Criteria:**
- Parameter names: `leg_offset_x`, `leg_offset_y` (not old verbose names)
- New parameter: `plank_max_width` (default 0.10)
- 15 conditional planks with `condition: "ceil(table_width / plank_max_width) >= N"`
- Plank count adapts to table width dynamically
- No visual artifacts in generated tables

---

## Documentation

- **[ARCHITECTURE.md](./ARCHITECTURE.md)** - Detailed test architecture, patterns, and guidelines
- **[EXAMPLE_E2E_TESTS_RESULT.md](./EXAMPLE_E2E_TESTS_RESULT.md)** - Example E2E test output

## See Also

- [TASK-028: E2E Testing Infrastructure](../_TASKS/TASK-028_E2E_Testing_Infrastructure.md)
- [TASK-056: Workflow System Enhancements](../_TASKS/TASK-056_Workflow_System_Enhancements.md)
- [TASK-055-FIX-7: Dynamic Plank System](../_TASKS/TASK-055-FIX-7_Dynamic_Plank_System_Simple_Table.md)
