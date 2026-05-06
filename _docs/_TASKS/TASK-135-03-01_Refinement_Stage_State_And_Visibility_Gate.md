# TASK-135-03-01: Refinement Stage State And Visibility Gate

**Status:** ⏳ To Do
**Priority:** 🔴 High
**Parent:** [TASK-135-03](./TASK-135-03_Low_Poly_Form_Refinement_Mesh_Window_And_Profile_Macros.md)
**Objective:** Add one explicit low-poly refinement stage to the current creature guided flow so the runtime can open a bounded mesh/modeling window only after required roles and seams are stable enough.
**Repository Touchpoints:** `server/adapters/mcp/session_capabilities.py`, `server/adapters/mcp/session_capabilities_state.py`, `server/adapters/mcp/session_capabilities_flow.py`, `server/adapters/mcp/session_capabilities_runtime_glue.py`, `server/adapters/mcp/transforms/visibility_policy.py`, `server/adapters/mcp/contracts/quality_gates.py`, `tests/unit/adapters/mcp/test_guided_flow_state_contract.py`, `tests/unit/adapters/mcp/test_visibility_policy.py`, `tests/unit/adapters/mcp/test_router_elicitation.py`, `tests/e2e/integration/test_guided_gate_state_transport.py`
**Acceptance Criteria:** the creature domain can advance into one explicit refinement step after prerequisite masses and seams are stable; the refinement step exposes only bounded `macro` / `modeling_mesh` families; stage/gate state survives session persistence and transport.

## Implementation Notes

- keep `server/adapters/mcp/session_capabilities.py` as the stable facade, but
  implement the real state/policy changes in the split session-capability
  modules
- add one explicit creature refinement step such as `refine_low_poly_forms`
  rather than overloading `place_secondary_parts` or `finish_or_stop`
- gate entry on normalized `TASK-157` status, for example:
  - required primary and secondary roles registered
  - required creature seams no longer blocking
  - the session is not currently stale on spatial/gate refresh
- project the new step through current `guided_flow_state`,
  `active_gate_plan`, and visibility/search shaping; do not invent a parallel
  creature-only state envelope
- keep sculpt hidden on this step unless a later `TASK-145` handoff explicitly
  recommends bounded local sculpt

## Pseudocode

```python
if domain_profile == "creature" and current_step == "place_secondary_parts":
    if required_roles_ready and required_creature_seams_stable:
        advance_to("refine_low_poly_forms")

if current_step == "refine_low_poly_forms":
    allowed_families = ["macro", "modeling_mesh", "reference_context"]
    blocked_families = ["sculpt_region"]
```

## Runtime / Security Contract Notes

- reuse the shipped `guided_flow_state` and `active_gate_plan` contracts
- do not expose a new public MCP tool just to enter or inspect the refinement
  stage
- keep verifier authority on the existing `TASK-157` gate path; stage entry is
  a policy decision over normalized gate status, not over perception confidence

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_guided_flow_state_contract.py`
- `tests/unit/adapters/mcp/test_visibility_policy.py`
- `tests/unit/adapters/mcp/test_router_elicitation.py`
- `tests/e2e/integration/test_guided_gate_state_transport.py`

## Docs To Update

- `_docs/_PROMPTS/REFERENCE_GUIDED_CREATURE_BUILD.md`
- `_docs/_MCP_SERVER/README.md`
- `_docs/_TESTS/README.md`

## Changelog Impact

- Add a `_docs/_CHANGELOG/*` entry when the explicit refinement step ships.

## Validation Commands

- `git diff --check`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_guided_flow_state_contract.py tests/unit/adapters/mcp/test_visibility_policy.py tests/unit/adapters/mcp/test_router_elicitation.py -q`
- `poetry run pytest tests/e2e/integration/test_guided_gate_state_transport.py -q`
