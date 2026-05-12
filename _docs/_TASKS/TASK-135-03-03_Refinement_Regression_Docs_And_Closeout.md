# TASK-135-03-03: Refinement Regression Docs And Closeout

**Status:** ✅ Done
**Priority:** 🔴 High
**Parent:** [TASK-135-03](./TASK-135-03_Low_Poly_Form_Refinement_Mesh_Window_And_Profile_Macros.md)
**Depends On:** [TASK-135-03-01](./TASK-135-03-01_Refinement_Stage_State_And_Visibility_Gate.md), [TASK-135-03-02](./TASK-135-03-02_Bounded_Profile_Tools_And_Optional_Macro_Wave.md)
**Objective:** Lock the new refinement stage with owner-lane regression, Blender-backed proof, and docs that describe the shipped bounded creature refinement path accurately.
**Acceptance Criteria:** primitive-only creature runs cannot complete past the new refinement gate without the required profile work; transport and checkpoint surfaces describe the same stage/blocker semantics; docs and changelog record the shipped behavior and validation lanes accurately.

## Repository Touchpoints

| Path / Module | Owner Seam / Current Lines | Closeout Responsibility |
|---------------|----------------------------|-------------------------|
| `server/adapters/mcp/areas/reference.py` | checkpoint route/handoff projection around `reference.py:1490` | Verify staged compare/iterate envelopes report shipped refinement blockers and handoff state |
| `server/adapters/mcp/areas/reference_planner.py` | `select_refinement_route(...)` at `reference_planner.py:542`; `build_refinement_handoff(...)` at `reference_planner.py:672` | Verify planner route/handoff semantics match docs and tests |
| `server/adapters/mcp/areas/reference_feedback.py` | orchestrator feedback projection | Verify selected family, next actions, and loop disposition mirror checkpoint state |
| `server/adapters/mcp/contracts/guided_flow.py` | `GuidedFlowStepLiteral` / `GuidedFlowStateContract` | Verify public contract includes only shipped step/family semantics |
| `server/adapters/mcp/transforms/visibility_policy.py` | `build_visibility_rules(...)`; `visible_tools_for_gate_plan(...)` | Verify public visible-tool behavior matches the final task docs |
| `tests/unit/adapters/mcp/test_reference_images.py` | checkpoint fixtures | Owner lane for checkpoint, route, handoff, and feedback semantics |
| `tests/unit/adapters/mcp/test_contract_payload_parity.py` | public payload parity | Verify response schemas remain stable across direct and transported surfaces |
| `tests/unit/adapters/mcp/test_context_bridge.py` | guided execution enforcement | Verify mapped mutators are accepted and unmapped mutators remain blocked |
| `tests/unit/adapters/mcp/test_guided_mode.py`, `test_guided_surface_benchmarks.py`, `test_public_surface_docs.py` | guided/public documentation parity | Verify docs and visible surface describe the same shipped behavior |
| `tests/e2e/integration/test_guided_gate_state_transport.py`, `test_guided_surface_contract_parity.py`, `test_guided_streamable_spatial_support.py` | stdio/Streamable proof | Verify transport-visible state, visibility, and gate payloads align |
| `tests/e2e/vision/test_goal_derived_gate_creature_completion.py`, `test_reference_stage_assembled_creature_attachment_truth.py`, `test_reference_stage_truth_handoff.py` | Blender/vision regression proof | Verify primitive-only creature, assembled seams, and refinement handoff behavior in runtime scenarios |
| `_docs/_PROMPTS/REFERENCE_GUIDED_CREATURE_BUILD.md`, `_docs/_MCP_SERVER/README.md`, `_docs/_TESTS/README.md`, `_docs/_CHANGELOG/` | docs/changelog closeout | Record exact shipped behavior, validation commands, and remaining follow-ons |

## Implementation Notes

- prove the refinement stage on the existing staged checkpoint and gate-transport
  surfaces; do not create a docs-only notion of refinement that the runtime
  never emits
- keep the main creature proof focused on:
  - primitive-only squirrel blocked before final completion
  - required creature seams still visible in truth/follow-up payloads
  - refinement-stage blockers visible on transport-friendly envelopes
- keep the existing `refinement_route` / `refinement_handoff` checkpoint surfaces
  in the proof pack so the explicit creature refinement step does not drift
  from the shipped planner baseline
- update `_docs/_TESTS/README.md` only after the owner lanes are stable enough to
  document as the current rerun baseline
- record whether the relevant `pre-commit` lane ran or was intentionally skipped,
  and record the parent/child status sync plus `_docs/_TASKS/README.md` board
  update proof when this closeout leaf actually ships

## Pseudocode

```python
owner_lanes = [
    "checkpoint_route_handoff",
    "guided_visibility_and_context_bridge",
    "payload_contract_parity",
    "stdio_streamable_transport",
    "blender_geometry_runtime",
    "public_docs_and_changelog",
]

for lane in owner_lanes:
    result = run_or_record_skip(lane.validation_command)
    if result.failed:
        keep_task_open(result.failure_summary)

assert task_statuses_are_consistent(
    parent="TASK-135-03",
    children=[
        "TASK-135-03-01",
        "TASK-135-03-02",
        "TASK-135-03-02-01",
        "TASK-135-03-02-02",
        "TASK-135-03-02-03",
        "TASK-135-03-03",
    ],
)
assert every_direct_or_nested_child_is_closed_done_superseded_or_cancelled(
    before_closing_parent="TASK-135-03",
)
assert docs_match_runtime_surface()
close_leaf_and_parent_only_if_no_follow_on_remains()
```

## Runtime / Security Contract Notes

- Visibility level: transport/runtime proof must use the existing public
  reference/gate surfaces, including `guided_flow_state`, `active_gate_plan`,
  `refinement_route`, and `refinement_handoff`; do not close this task from a
  docs-only notion of refinement.
- Read-only vs mutating behavior: closeout proof may read session/checkpoint
  envelopes, but any repair or refinement behavior still relies on the existing
  mutating modeling, mesh, scene, and macro surfaces.
- Mode and selection impact: Blender-backed proof must confirm that refinement
  steps and follow-on repairs do not leave sessions stranded in the wrong mode
  or selection state.
- Session and auth assumptions: validation must cover the repo-supported stdio /
  Streamable HTTP session path plus the local Blender RPC-backed runtime
  surface; session state must remain isolated per request flow.
- Parameter validation and compatibility: closeout should confirm strict
  response-contract parity for new step names, blockers, and route/handoff
  fields, with explicit compatibility behavior where relevant.
- Side effects, recovery, and logging: do not claim refinement closeout without
  a matching regression lane. Keep logs and proof artifacts free of provider
  keys, raw local paths, or unredacted vision payloads.
- Resource and timeout limits: keep the closeout proof pack on owner-lane
  reruns plus the repo-supported full unit/E2E commands; do not rely on ad hoc
  long-running provider loops or unbounded manual reruns to declare this leaf
  complete.

## Tests To Add/Update

| Test File | Cases / Assertions |
|-----------|--------------------|
| `tests/unit/adapters/mcp/test_reference_images.py` | primitive-only creature reports refinement blocker; route/handoff/feedback selected family remain aligned after checkpoint and iterate |
| `tests/unit/adapters/mcp/test_contract_payload_parity.py` | public checkpoint/status payload shape includes shipped refinement fields without unknown extras |
| `tests/unit/adapters/mcp/test_context_bridge.py` | refinement-visible mutators pass guided enforcement; unrelated hidden mutators remain blocked |
| `tests/unit/adapters/mcp/test_guided_mode.py` and `test_guided_surface_benchmarks.py` | guided visible capability list and benchmark expectations include only shipped refinement tools |
| `tests/unit/adapters/mcp/test_public_surface_docs.py` | prompt/MCP/test docs mention only shipped refinement behavior and explicit limitations |
| `tests/e2e/integration/test_guided_gate_state_transport.py` | active gate/refinement state serializes through transport envelopes |
| `tests/e2e/integration/test_guided_surface_contract_parity.py` | stdio live tool surface matches contract expectations |
| `tests/e2e/integration/test_guided_streamable_spatial_support.py` | Streamable HTTP visible tools and guided state match stdio for the same scenario |
| `tests/e2e/vision/test_goal_derived_gate_creature_completion.py` | primitive-only creature cannot pass final completion before profile/refinement blockers clear |
| `tests/e2e/vision/test_reference_stage_assembled_creature_attachment_truth.py` | required seams and refinement blockers remain visible in truth/follow-up payloads |
| `tests/e2e/vision/test_reference_stage_truth_handoff.py` | refinement route/handoff survives real staged truth handoff |

## Docs To Update

- `README.md`
- `_docs/_MCP_SERVER/MCP_CLIENT_CONFIG_EXAMPLES.md`
- `_docs/_PROMPTS/REFERENCE_GUIDED_CREATURE_BUILD.md`
- `_docs/_PROMPTS/README.md`
- `_docs/_PROMPTS/GUIDED_SESSION_START.md`
- `_docs/_PROMPTS/WORKFLOW_ROUTER_FIRST.md`
- `_docs/_PROMPTS/MANUAL_TOOLS_NO_ROUTER.md`
- `_docs/_MCP_SERVER/README.md`
- `_docs/_TESTS/README.md`
- `_docs/_TASKS/README.md`
- `_docs/_VISION/README.md`
- relevant `_docs/_VISION/*` creature and refinement docs enforced by
  `test_public_surface_docs.py`
- `_docs/_CHANGELOG/README.md`

## Changelog Impact

- Add a `_docs/_CHANGELOG/*` entry when the refinement stage and its proof pack
  are shipped.

## Validation Commands

- `git diff --check`
- `PRE_COMMIT_HOME=/tmp/pre-commit-cache poetry run pre-commit run --all-files --show-diff-on-failure`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_reference_images.py tests/unit/adapters/mcp/test_contract_payload_parity.py tests/unit/adapters/mcp/test_guided_mode.py tests/unit/adapters/mcp/test_guided_surface_benchmarks.py tests/unit/adapters/mcp/test_public_surface_docs.py -q`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_context_bridge.py -q`
- `poetry run pytest tests/e2e/integration/test_guided_gate_state_transport.py tests/e2e/integration/test_guided_surface_contract_parity.py tests/e2e/integration/test_guided_streamable_spatial_support.py -q`
- `PYTHONPATH=. poetry run pytest tests/e2e/vision/test_goal_derived_gate_creature_completion.py tests/e2e/vision/test_reference_stage_assembled_creature_attachment_truth.py tests/e2e/vision/test_reference_stage_truth_handoff.py -q`
- `Outside sandbox before closeout: PYTHONPATH=. poetry run pytest ./tests/unit`
- `Outside sandbox for Blender-backed runtime proof: poetry run python scripts/run_e2e_tests.py`

## Status / Board Update

- `TASK-135-03-03` is closed.
- The parent `TASK-135-03`, the umbrella `TASK-135`, and `_docs/_TASKS/README.md`
  all changed in the same branch so nested task state and board state do not
  drift.

## Completion Summary

- 2026-05-11: The refinement-stage closeout now includes owner-lane unit
  coverage, Blender-backed proof for the first body/ear/snout profile cases,
  and task/changelog/test-doc sync.
- The generic creature path is no longer squirrel-only at the goal-classifier /
  prompt-recommendation / gate-template layer: common quadruped mammals such as
  beaver, dog, and cat now resolve to the same creature handoff and required
  gate template path as squirrel runs.
- The bounded refinement wave is implemented on the existing mesh/macro
  surface, with `TASK-135-03-02-03` superseded and no remaining implementation
  follow-on leaf under `TASK-135-03`.
- The repo-supported full runner now also passed after the validation tooling
  fix path moved addon reinstall off the crash-prone background lane and
  allowed per-run RPC port fallback when `8765` is already occupied.
