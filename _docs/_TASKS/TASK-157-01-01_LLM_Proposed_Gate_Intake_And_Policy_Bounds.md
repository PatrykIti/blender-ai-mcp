# TASK-157-01-01: LLM-Proposed Gate Intake And Policy Bounds

**Status:** ⏳ To Do
**Priority:** 🔴 High
**Parent:** [TASK-157-01](./TASK-157-01_Gate_Declaration_Schema_Normalization_And_Policy_Bounds.md)
**Category:** Guided Runtime / Gate Intake
**Estimated Effort:** Small

## Objective

Add the first narrow intake path for LLM-proposed gate declarations without
allowing the LLM to mark gates complete or bypass server verification.

The same intake path should be able to accept gate proposals derived from a
reference-understanding summary or bounded perception payload, but those inputs
remain proposal sources only. They must not become verifier status.

## Repository Touchpoints

| Path / Module | Expected Change |
|---------------|-----------------|
| `server/adapters/mcp/areas/router.py` | If goal-time proposal intake is supported, preserve optional gate proposals on `router_set_goal` before checkpoint normalization |
| `server/adapters/mcp/areas/reference.py` | Accept optional gate proposal payload on the existing guided/reference checkpoint path |
| `server/adapters/mcp/contracts/quality_gates.py` | Add intake contract models |
| `server/adapters/mcp/contracts/reference.py` | Reference proposal sources by stable reference/vision payload identifiers |
| `server/adapters/mcp/session_capabilities.py` | Store normalized proposals in session state |
| `server/router/infrastructure/tools_metadata/reference/reference_compare_stage_checkpoint.json` | Add optional proposal fields if the public checkpoint surface accepts gate proposals |
| `server/router/infrastructure/tools_metadata/reference/reference_iterate_stage_checkpoint.json` | Add optional proposal fields if the public iterate surface accepts gate proposals |
| `tests/unit/adapters/mcp/test_quality_gate_intake.py` | Add intake and policy-bound tests |
| `tests/unit/router/infrastructure/test_mcp_tools_metadata_alignment.py` | Keep metadata parameters aligned with public MCP signatures |
| `tests/unit/adapters/mcp/test_public_surface_docs.py` | Keep public docs in sync if checkpoint parameters change |
| `_docs/_PROMPTS/REFERENCE_GUIDED_CREATURE_BUILD.md` | Tell clients how to propose gates without claiming completion |
| `_docs/AVAILABLE_TOOLS_SUMMARY.md` | Document public parameter changes if checkpoint intake is exposed |

## Technical Requirements

- Intake must be optional.
- Intake must be ignored or rejected when there is no active guided goal.
- LLM text such as "all seams are good" must not become `passed`.
- The only statuses accepted from LLM proposal should be declaration-level
  states such as `proposed` or `requested`.
- Server should return policy warnings when it drops or rewrites a proposed
  gate.
- Proposal sources should include structured provenance when available:
  provider, model id, `vision_contract_profile`, reference ids, viewport/capture
  ids, and generated evidence ids.
- `reference_understanding`, `silhouette_analysis`, `part_segmentation`, and
  future `classification_scores` inputs may create or refine proposed gates, but they
  must be normalized to `pending` until a verifier produces evidence.
- The first implementation should not call SAM, CLIP, or another heavy
  perception model. It should only preserve a stable contract for later
  perception outputs to plug into.

## Runtime / Security Contract Notes

- Visibility level: the first slice uses an optional field on the existing
  guided/reference surface. A separate public intake tool is out of scope
  unless a later public-tool review approves it.
- Read-only vs mutating behavior: intake does not mutate Blender scene state;
  it only stores normalized session gate state and policy warnings.
- Session/auth assumptions: intake applies only to the active guided session;
  no gate proposal may be reused across stdio or Streamable HTTP sessions
  without an explicit session-state record.
- Parameter validation: reject or rewrite unsupported statuses, hidden/internal
  tool names, raw code, and unknown fields with machine-readable policy
  warnings.
- Secret/debug handling: provider/model/profile metadata is allowed as
  provenance; provider keys, sidecar keys, and raw unbounded VLM payloads are
  not allowed in persisted gate proposals.

## Pseudocode

```python
def ingest_llm_gate_proposal(ctx, proposal):
    current = get_session_capability_state(ctx)
    if not current.goal or current.guided_flow_state is None:
        return GateIntakeResult(status="ignored", reason="no_active_goal")

    guided_flow = GuidedFlowStateContract.model_validate(current.guided_flow_state)
    normalized = normalize_gate_plan(
        proposal,
        domain_profile=guided_flow.domain_profile,
        templates=templates_for_domain_profile(guided_flow.domain_profile),
    )
    normalized = strip_client_completion_claims(normalized).with_initial_status("pending")

    # TASK-157-01 adds gate_plan to the frozen session state; update through
    # replace(...) or an owning session_capabilities helper, not direct mutation.
    updated = replace(current, gate_plan=normalized)
    set_session_capability_state(ctx, updated)
    return GateIntakeResult(status="accepted", gate_plan=normalized)


def ingest_reference_gate_proposal(ctx, reference_summary):
    proposal = gate_proposal_from_reference_understanding(reference_summary)
    return ingest_llm_gate_proposal(ctx, proposal)
```

## Tests To Add/Update

- LLM proposal with `status="passed"` is rejected or stripped with an
  `unsupported_completion_status` policy warning; any server-created normalized
  gate starts as `pending` only after the client-supplied completion status is
  removed.
- Unsupported tool names are dropped with a policy warning.
- Proposal without active guided goal is ignored or rejected consistently.
- Creature proposal with `eye_pair` and `tail/body seam` becomes typed gates.
- Building proposal with `roof/wall seam` and `window grid` becomes typed
  gates.
- Reference-understanding proposal with `curled tail`, `wedge ears`, and
  `visible eye pair` becomes `shape_profile`, `symmetry_pair`, and
  `required_part` gates with advisory provenance.
- Perception proposal with a segmentation or classification source preserves
  source provenance but cannot set `passed`.

## E2E Tests

- Covered by later TASK-157-04 cross-domain E2E harness.

## Docs To Update

- `_docs/_PROMPTS/REFERENCE_GUIDED_CREATURE_BUILD.md`
- `_docs/_MCP_SERVER/README.md`
- `_docs/AVAILABLE_TOOLS_SUMMARY.md` if the public checkpoint parameter surface
  changes

## Changelog Impact

- Add a `_docs/_CHANGELOG/*` entry only if this intake slice ships as a
  meaningful implementation change; docs-only refinement does not require a new
  entry beyond the current task-family changelog.

## Validation Commands

- `git diff --check`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_quality_gate_intake.py tests/unit/adapters/mcp/test_guided_flow_state_contract.py -v`
- `PYTHONPATH=. poetry run pytest tests/unit/router/infrastructure/test_mcp_tools_metadata_alignment.py tests/unit/adapters/mcp/test_public_surface_docs.py -v` when public checkpoint parameters change
- `rg -n "reference_understanding|part_segmentation|classification_scores|status=\\\"passed\\\"" server/adapters/mcp tests/unit/adapters/mcp _docs/_TASKS/TASK-157*.md`

## Acceptance Criteria

- LLMs can propose gates.
- LLMs cannot mark gates complete.
- Server policy warnings explain dropped or rewritten gates.
