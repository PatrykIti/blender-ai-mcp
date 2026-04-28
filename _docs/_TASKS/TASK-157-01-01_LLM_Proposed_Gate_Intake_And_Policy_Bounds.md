# TASK-157-01-01: LLM-Proposed Gate Intake And Policy Bounds

**Status:** ⏳ To Do
**Priority:** 🔴 High
**Parent:** [TASK-157-01](./TASK-157-01_Gate_Declaration_Schema_Normalization_And_Policy_Bounds.md)
**Category:** Guided Runtime / Gate Intake
**Estimated Effort:** Small

## Objective

Add the first narrow intake path for LLM-proposed gate declarations without
allowing the LLM to mark gates complete or bypass server verification.

## Repository Touchpoints

| Path / Module | Expected Change |
|---------------|-----------------|
| `server/adapters/mcp/areas/reference.py` | Accept optional gate proposal payload on goal/checkpoint path if this is the chosen public surface |
| `server/adapters/mcp/contracts/quality_gates.py` | Add intake contract models |
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
```

## Tests To Add/Update

- LLM proposal with `status="passed"` is normalized to `pending`.
- Unsupported tool names are dropped with a policy warning.
- Proposal without active guided goal is ignored or rejected consistently.
- Creature proposal with `eye_pair` and `tail/body seam` becomes typed gates.
- Building proposal with `roof/wall seam` and `window grid` becomes typed
  gates.

## E2E Tests

- Covered by later TASK-157-04 cross-domain E2E harness.

## Docs To Update

- `_docs/_PROMPTS/REFERENCE_GUIDED_CREATURE_BUILD.md`
- `_docs/_MCP_SERVER/README.md`

## Acceptance Criteria

- LLMs can propose gates.
- LLMs cannot mark gates complete.
- Server policy warnings explain dropped or rewritten gates.
