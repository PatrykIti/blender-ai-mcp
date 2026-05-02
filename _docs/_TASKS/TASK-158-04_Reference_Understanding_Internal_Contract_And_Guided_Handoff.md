# TASK-158-04: Reference Understanding Internal Contract And Guided Handoff

**Status:** ⏳ To Do
**Priority:** 🔴 High
**Parent:** [TASK-158](./TASK-158_Vision_And_Creature_Gate_Boundary_Doc_Alignment.md)
**Category:** Guided Runtime / Reference Understanding
**Estimated Effort:** Medium

## Objective

Implement the bounded reference-understanding follow-up that was intentionally
kept out of `TASK-157`: a typed summary contract, parser/prompt path, alias
normalization, and handoff into existing reference/guided surfaces on top of
the closed `TASK-157` generic quality-gate substrate.

This slice must let reference understanding propose gate inputs or support refs
for `TASK-157` gates, but it must not own gate pass/fail truth.

This file is the technical subtask for Scope B. Execute it through the narrower
child leaves below rather than as one broad implementation pass.

## Execution Structure

| Order | Task | Purpose |
|-------|------|---------|
| 1 | [TASK-158-04-01](./TASK-158-04-01_Reference_Understanding_Contract_And_Parser_Normalization.md) | Add the typed reference-understanding contract, alias normalization, and shared prompt/parser/backend path without inventing a second runtime flow |
| 2 | [TASK-158-04-02](./TASK-158-04-02_Reference_Understanding_Session_Linkage_And_Checkpoint_Contracts.md) | Persist accepted reference-understanding linkage in session state and thread declared fields through compare/iterate checkpoint contracts |
| 3 | [TASK-158-04-03](./TASK-158-04-03_Reference_Understanding_Visibility_Diagnostics_And_Transport_Parity.md) | Expose bounded hints only through existing guided visibility, router diagnostics, and transport parity lanes |

## Repository Touchpoints

| Path / Module | Expected Change |
|---------------|-----------------|
| `server/adapters/mcp/contracts/reference.py` | Add or compose reference-understanding summary/result contracts without duplicating gate status contracts |
| `server/adapters/mcp/contracts/quality_gates.py` | Reuse the closed `TASK-157` proposal/evidence contracts; do not re-create the substrate here |
| `server/adapters/mcp/contracts/guided_flow.py` | Keep any new guided family, step, or session-exposed hint vocabulary inside `GuidedFlowStateContract` / `GuidedFlowFamilyLiteral` instead of ad hoc strings |
| `server/adapters/mcp/contracts/router.py` | Declare any public `router_get_status(...)` summary or hint fields before exposing them through the router surface |
| `server/adapters/mcp/vision/prompting.py` | Extend the shared vision prompt contract first; add a reference-understanding wrapper only if the shared owner becomes too large |
| `server/adapters/mcp/vision/parsing.py` | Extend the shared parsing/repair contract first; add a focused parser helper only if the shared owner becomes too large |
| `server/adapters/mcp/vision/backends.py` | Keep any new payload normalization on the existing shared backend path rather than forking a second prompt/parser flow |
| `server/adapters/mcp/areas/reference.py` | Surface summaries/proposal refs through existing reference/checkpoint flow unless a separate public-tool review promotes a new tool |
| `server/adapters/mcp/session_capabilities.py` | Store summary ids, provenance, proposal refs, and guided handoff hints scoped to the current session |
| `server/adapters/mcp/transforms/visibility_policy.py` | React only to existing declared contracts (`gate_plan`, `guided_handoff`, or declared router/reference fields) when visibility really changes; do not add a summary-only side channel |
| `server/adapters/mcp/discovery/search_surface.py` | Own public search exposure, visibility refresh, and discovery serialization when new reference-understanding hints affect `search_tools` / `call_tool` behavior |
| `server/adapters/mcp/guided_mode.py` | Thread any new visibility/search diagnostics through the current guided visibility assembly path rather than a second handoff channel |
| `server/adapters/mcp/areas/router.py` | Keep `router_get_status(...)` and guided diagnostics aligned with `RouterStatusContract` if new summary or hint fields become public there |
| `tests/unit/adapters/mcp/` | Add or extend contract, parser, prompt-shape, reference-surface, guided-session, router, and search-owner tests |
| `tests/e2e/integration/` | Add a focused transport/surface parity lane if new client-facing summary fields or hint-driven visibility become public on stdio or Streamable HTTP |

## Implementation Notes

- Default public path: existing reference/guided surfaces. Do not add a public
  `reference_understand` MCP tool unless a separate public-tool review promotes
  it.
- Do not add `router_apply_reference_strategy`. Strategy application belongs to
  server-owned guided state, visibility, and `TASK-157` gate policy.
- Normalize draft family names:
  - `mesh_edit` -> current `modeling_mesh`
  - `material_finish` -> stage/action hint or future family, not canonical here
  - `macro_create_part` -> `modeling_create_primitive(...)` with guided
    role/group auto-registration for new objects, or `guided_register_part(...)`
    for existing objects
  - `mesh_shade_flat` and `macro_low_poly_*` -> future optional candidates
- Parser output may include proposed gate seeds, likely parts, construction
  path, style hints, relation candidates, and support provenance.
- Parser output must not include `status=passed`, `final_completion=true`, raw
  tool names outside the allowlist, hidden/internal tools, raw Blender code, or
  provider secrets.
- Shared prompt/parser owners are the existing `vision/prompting.py`,
  `vision/parsing.py`, and `vision/backends.py` path first. Introduce
  `reference_understanding*.py` helpers only if the shared modules become too
  large and the split preserves one backend contract.
- `GuidedFlowFamilyLiteral`, `GuidedFlowStateContract`, and
  `RouterStatusContract` are the declared vocabulary/transport owners for any
  new family hints or router-visible diagnostics. Do not add free-form session
  keys or router-only payload fields outside those contracts.
- Gate proposals must enter through the live
  `ingest_quality_gate_proposal[_async](...)` seam in `session_capabilities.py`
  and then obey the current goal-time bounds path. Do not introduce a second
  reference-specific gate normalizer.
- If the client needs explicit linkage between one reference-understanding
  summary and the accepted gates, add declared session/reference payload fields
  in this slice. Do not assume `GatePlanContract` already exposes a built-in
  gate-to-summary linkage field.
- If public search or call-tool discovery behavior changes, route it through
  `apply_visibility_for_session_state(...)`,
  `visible_tools_for_gate_plan(...)`, and
  `server/adapters/mcp/discovery/search_surface.py`. Do not create a
  router-only or reference-only parallel visibility/search channel.

## Pseudocode

```python
parsed_payload = parse_vision_output_text(
    provider_text,
    request,
    vision_contract_profile=runtime.active_vision_contract_profile,
    provider_name=provider_name,
)
summary_contract = ReferenceUnderstandingSummaryContract.model_validate(
    _coerce_reference_understanding_payload(parsed_payload)
)  # new contract/helper introduced by this task, backed by reference.py

gate_proposal = GateProposalContract.model_validate(
    {
        "proposal_id": summary_contract.understanding_id,
        "source": "reference_understanding",
        "goal": request.goal,
        "gates": summary_contract.gate_proposals,
        "source_provenance": summary_contract.source_provenance,
    }
)
intake_result = ingest_quality_gate_proposal(
    ctx,
    gate_proposal.model_dump(mode="json", exclude_none=True),
)
accepted_gate_plan = intake_result.gate_plan if intake_result.status == "accepted" else None
accepted_gate_ids = [
    gate.gate_id for gate in (accepted_gate_plan.gates if accepted_gate_plan is not None else [])
]

session_state = get_session_capability_state(ctx)
session_state = replace(
    session_state,
    reference_understanding_summary={
        "understanding_id": summary_contract.understanding_id,
        "summary": summary_contract.model_dump(mode="json", exclude_none=True),
        "accepted_gate_ids": accepted_gate_ids,
    },  # new explicit session field/helper owned by this task
)
set_session_capability_state(ctx, session_state)

return _stage_compare_response(
    ...,
    active_gate_plan=(
        accepted_gate_plan.model_dump(mode="json", exclude_none=True)
        if accepted_gate_plan is not None
        else session_state.gate_plan
    ),
    reference_understanding_summary=summary_contract.model_dump(mode="json", exclude_none=True),
    reference_understanding_gate_ids=accepted_gate_ids,  # new declared response field only if linkage is needed
)
```

`session_capabilities.py` owns `ingest_quality_gate_proposal[_async](ctx, ...)`
and the current `_apply_goal_time_gate_input_bounds(...)` path. This task
should feed that seam and consume the accepted result; it should not add a
second reference-specific gate normalizer. Use the live
`parse_vision_output_text(...)` shared backend parser first, then add only the
minimum new coercion/summary contract helper needed in this task instead of
inventing a second standalone parser path. `SessionCapabilityState` is
currently frozen and its helpers accept the FastMCP `Context`, so new
summary/linkage persistence should use an owning helper or `replace(...)`
pattern instead of mutating fields in place or using a bare `session_id`.

Implementation must add any new response fields explicitly to
`ReferenceCompareStageCheckpointResponseContract` and
`ReferenceIterateStageCheckpointResponseContract`; `MCPContract` payloads reject
undeclared extras. Thread those fields through `_stage_compare_response(...)`,
`_iterate_stage_response(...)`, and `_compact_compare_result_for_iterate(...)`.
If hint-driven visibility or guided diagnostics change, declare any router
fields in `server/adapters/mcp/contracts/router.py`, then thread the same data
through `guided_mode.py`, `server/adapters/mcp/areas/router.py`,
`server/adapters/mcp/discovery/search_surface.py`, and the existing public
surface diagnostics/tests rather than patching `visibility_policy.py` in
isolation or creating a second discovery path.

## Runtime / Security Contract Notes

- Visibility level: internal/guided-reference by default; public tool exposure
  requires a separate public MCP review.
- Read-only vs mutating behavior: this slice is read-only and session-state
  oriented. It must not mutate Blender scene state.
- Session/auth assumptions: summaries and proposal refs stay scoped to the
  active stdio or Streamable HTTP MCP session.
- Validation: reject unknown fields and unsupported aliases; preserve explicit
  compatibility adapters only where documented.
- Side effects: no implicit provider call, sidecar activation, model download,
  or hidden router execution.
- Logging: carry redacted provider/model/profile metadata and stable ids, not
  raw image bytes, provider keys, local private paths, or full debug payloads.

## Tests To Add / Update

- Extend `tests/unit/adapters/mcp/test_vision_prompting.py` and
  `tests/unit/adapters/mcp/test_vision_parsing.py` first, or split focused
  `test_reference_understanding_*` files only if the shared owners become too
  large.
- Extend `tests/unit/adapters/mcp/test_reference_images.py` and
  `tests/unit/adapters/mcp/test_contract_payload_parity.py` for declared
  reference/checkpoint response fields and compact iterate payloads.
- Extend `tests/unit/adapters/mcp/test_quality_gate_intake.py`,
  `tests/unit/adapters/mcp/test_guided_flow_state_contract.py`,
  `tests/unit/adapters/mcp/test_visibility_policy.py`,
  `tests/unit/adapters/mcp/test_guided_mode.py`,
  `tests/unit/adapters/mcp/test_router_elicitation.py`, and
  `tests/unit/adapters/mcp/test_search_surface.py` for bounded hint-driven
  exposure from unresolved gates, declared session linkage, and public guided
  diagnostics.
- Add focused guided-session tests around `session_capabilities.py` persistence
  helpers for summary ids and accepted gate ids.
- Add or update one integration/transport lane under
  `tests/e2e/integration/test_guided_surface_contract_parity.py` or
  `tests/e2e/integration/test_guided_gate_state_transport.py` when new summary
  fields or hint-driven visibility become visible on stdio or Streamable HTTP
  public surfaces.
- Add `tests/e2e/integration/test_guided_search_first_call_tool_boundary.py`
  when new search hints change `search_tools` / `call_tool` discovery output.
- Metadata/search tests only if this slice adds new search hints or schema
  fields.

## Docs To Update

- `_docs/_MCP_SERVER/README.md` if reference/checkpoint payloads change.
- `_docs/_PROMPTS/README.md` if prompting guidance changes.
- `_docs/_VISION/REFERENCE_UNDERSTANDING_ROADMAP.md` with the final implemented
  surface and any deferred public-tool decision.
- `_docs/_TASKS/TASK-158_Vision_And_Creature_Gate_Boundary_Doc_Alignment.md`
  completion summary.

## Changelog Impact

- If this subtask closes independently, add a scoped `_docs/_CHANGELOG/*`
  entry in the same branch and update `_docs/_CHANGELOG/README.md`.
- If multiple `TASK-158` slices land together in one wave, one shared
  completion entry may cover them, but it must name this subtask explicitly and
  record its validation in the summary.

## Status / Board Update

- Keep `_docs/_TASKS/README.md` on the umbrella `TASK-158` row; this subtask
  does not become its own promoted board item.
- Close or supersede `TASK-158-04-01`, `TASK-158-04-02`, and `TASK-158-04-03`
  in the same branch before closing this subtask, and summarize which response
  fields, session helpers, and transport lanes changed in the parent closeout.
- Do not leave this subtask or any direct child open under a closed
  `TASK-158-04` or `TASK-158`. If work is deferred, spin it into an explicit
  `Follow-on After` task and close or supersede the stale child docs with a
  reason in the same branch.

## Validation Commands

- `git diff --check`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_vision_prompting.py tests/unit/adapters/mcp/test_vision_parsing.py tests/unit/adapters/mcp/test_reference_images.py tests/unit/adapters/mcp/test_contract_payload_parity.py tests/unit/adapters/mcp/test_quality_gate_intake.py tests/unit/adapters/mcp/test_guided_flow_state_contract.py tests/unit/adapters/mcp/test_visibility_policy.py tests/unit/adapters/mcp/test_guided_mode.py tests/unit/adapters/mcp/test_router_elicitation.py tests/unit/adapters/mcp/test_search_surface.py -v`
- `poetry run pytest tests/e2e/integration/test_guided_surface_contract_parity.py -q`
  when new summary fields or hint-driven visibility become transport-visible.
- `poetry run pytest tests/e2e/integration/test_guided_gate_state_transport.py -q`
  when reference-understanding linkage changes transport-visible gate payloads.
- `poetry run pytest tests/e2e/integration/test_guided_search_first_call_tool_boundary.py -q`
  when new search hints change `search_tools` / `call_tool` discovery output.
- `rg -n "reference_understand|router_apply_reference_strategy|status=\\\"passed\\\"|final_completion" server/adapters/mcp tests/unit/adapters/mcp server/router/infrastructure/tools_metadata`

## Acceptance Criteria

- Reference-understanding output is typed, strict, and bounded.
- Reference-understanding can seed `TASK-157` gate proposals/support refs but
  cannot pass gates.
- Existing reference/guided surfaces are the default exposure path.
- Any transport-visible summary or hint field is declared in
  `ReferenceCompareStageCheckpointResponseContract`,
  `ReferenceIterateStageCheckpointResponseContract`, or
  `RouterStatusContract` before exposure.
- Search and visibility changes stay on the existing
  `apply_visibility_for_session_state(...)` plus
  `server/adapters/mcp/discovery/search_surface.py` lane; no parallel
  discovery/visibility channel is introduced.
- No public `reference_understand` or `router_apply_reference_strategy` tool is
  introduced by this slice.
- Alias normalization maps draft names to current seams or future candidates.
