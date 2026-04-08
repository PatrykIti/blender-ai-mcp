# TASK-150-04-01: Required Prompt Bundle Contract And Provider Surface

**Parent:** [TASK-150-04](./TASK-150-04_Prompt_Bundle_Delivery_And_Flow_Aligned_Recommendations.md)
**Status:** ⏳ To Do
**Priority:** 🔴 High

## Objective

Expose required/preferred prompt bundles as part of the server-owned guided
flow contract rather than as optional docs-only recommendations.

## Repository Touchpoints

- `server/adapters/mcp/prompts/prompt_catalog.py`
- `server/adapters/mcp/prompts/provider.py`
- `server/adapters/mcp/contracts/router.py`
- `tests/unit/adapters/mcp/test_public_surface_docs.py`

## Planned File Work

- Modify:
  - `server/adapters/mcp/prompts/prompt_catalog.py`
  - `server/adapters/mcp/prompts/provider.py`
  - `server/adapters/mcp/contracts/router.py`
  - `tests/unit/adapters/mcp/test_public_surface_docs.py`

## Detailed Implementation Notes

- distinguish:
  - `required_prompts`
  - `preferred_prompts`
  - `recommended_prompts`
- keep prompt bundle state server-owned and step-aware
- do not collapse prompt bundles into one giant concatenated prompt string in
  the contract; the contract should name assets, not duplicate their contents

## Planned Test Files And Scenarios

- Modify `tests/unit/adapters/mcp/test_public_surface_docs.py`
  - docs mention required/preferred prompt bundles as part of the flow
- Create `tests/unit/adapters/mcp/test_prompt_provider_flow_bundles.py`
  - provider reads `guided_flow_state`
  - recommended bundle changes by domain/step
  - required prompts remain stable even when optional recommendations differ

## Example Test Sketch

```python
def test_recommended_prompts_use_flow_state_domain_and_step():
    session.guided_flow_state = {
        "domain_profile": "creature",
        "current_step": "establish_spatial_context",
        "required_prompts": ["guided_session_start", "reference_guided_creature_build"],
    }
    result = render_recommended_prompts(...)
    assert "reference_guided_creature_build" in result
```

## Acceptance Criteria

- the flow state can name required and strongly preferred prompts
- the prompt provider can render those bundles from session state
- prompt bundles are machine-readable and stable

## Pseudocode Sketch

```python
guided_flow_state.required_prompts = ("guided_session_start", "reference_guided_creature_build")
guided_flow_state.preferred_prompts = ("workflow_router_first",)

def recommended_prompts(ctx, ...):
    session = get_session_capability_state_async(ctx)
    return render_recommended_prompts(..., guided_flow_state=session.guided_flow_state)
```

## Docs To Update

- `_docs/_PROMPTS/README.md`

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_public_surface_docs.py`

## Changelog Impact

- include in the parent TASK-150 changelog entry when shipped
