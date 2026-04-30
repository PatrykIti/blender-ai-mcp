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
| `server/adapters/mcp/areas/reference.py` | Accept optional gate proposal payload on goal/checkpoint path if this is the chosen public surface |
| `server/adapters/mcp/contracts/quality_gates.py` | Add intake contract models |
| `server/adapters/mcp/contracts/reference.py` | Reference proposal sources by stable reference/vision payload identifiers |
| `server/adapters/mcp/session_capabilities.py` | Store normalized proposals in session state |
| `tests/unit/adapters/mcp/test_quality_gate_intake.py` | Add intake and policy-bound tests |
| `_docs/_PROMPTS/REFERENCE_GUIDED_CREATURE_BUILD.md` | Tell clients how to propose gates without claiming completion |

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
  `classification_score` inputs may create or refine proposed gates, but they
  must be normalized to `pending` until a verifier produces evidence.
- The first implementation should not call SAM, CLIP, or another heavy
  perception model. It should only preserve a stable contract for later
  perception outputs to plug into.

## Runtime / Security Contract Notes

- Visibility level: prefer adding intake as an optional field on the existing
  guided/reference surface unless a public-tool review justifies a separate MCP
  tool.
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
    state = get_session_capability_state(ctx)
    if not state.current_goal:
        return GateIntakeResult(status="ignored", reason="no_active_goal")

    normalized = normalize_gate_plan(
        proposal,
        domain_profile=state.guided_flow_state.domain_profile,
        templates=load_domain_templates(state.guided_flow_state.domain_profile),
    )

    for gate in normalized.gates:
        gate.status = "pending"
        gate.evidence = None

    state.gate_plan = normalized
    set_session_capability_state(ctx, state)
    return GateIntakeResult(status="accepted", gate_plan=normalized)


def ingest_reference_gate_proposal(ctx, reference_summary):
    proposal = gate_proposal_from_reference_understanding(reference_summary)
    return ingest_llm_gate_proposal(ctx, proposal)
```

## Tests To Add/Update

- LLM proposal with `status="passed"` is normalized to `pending`.
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

## Changelog Impact

- Add a `_docs/_CHANGELOG/*` entry only if this intake slice ships as a
  meaningful implementation change; docs-only refinement does not require a new
  entry beyond the current task-family changelog.

## Validation Commands

- `git diff --check`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_quality_gate_intake.py tests/unit/adapters/mcp/test_guided_flow_state_contract.py -v`
- `rg -n "reference_understanding|part_segmentation|classification_score|status=\\\"passed\\\"" server/adapters/mcp tests/unit/adapters/mcp _docs/_TASKS/TASK-157*.md`

## Acceptance Criteria

- LLMs can propose gates.
- LLMs cannot mark gates complete.
- Server policy warnings explain dropped or rewritten gates.
