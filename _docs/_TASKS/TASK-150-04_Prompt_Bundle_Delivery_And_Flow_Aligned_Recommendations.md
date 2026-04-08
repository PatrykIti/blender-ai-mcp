# TASK-150-04: Prompt Bundle Delivery And Flow-Aligned Recommendations

**Parent:** [TASK-150](./TASK-150_Server_Driven_Guided_Flow_State_Step_Gating_And_Domain_Profiles.md)
**Depends On:** [TASK-150-01](./TASK-150-01_Guided_Flow_State_Contract_And_Session_Model.md), [TASK-150-02](./TASK-150-02_Domain_Profile_Selection_And_Overlay_Policy.md)
**Status:** ⏳ To Do
**Priority:** 🔴 High

## Objective

Turn prompt usage for guided sessions into an explicit server-owned flow
 contract instead of a soft recommendation the model may ignore.

## Repository Touchpoints

- `server/adapters/mcp/prompts/prompt_catalog.py`
- `server/adapters/mcp/prompts/provider.py`
- `_docs/_PROMPTS/README.md`
- `_docs/_PROMPTS/WORKFLOW_ROUTER_FIRST.md`
- `_docs/_PROMPTS/REFERENCE_GUIDED_CREATURE_BUILD.md`

## Acceptance Criteria

- the server can expose required or strongly preferred prompt bundles for the
  current flow/domain/step
- clients that support prompts can retrieve those recommendations in a stable
  machine-readable way
- docs explain prompt usage as part of the guided flow contract, not as an
  optional memory aid

## Docs To Update

- `_docs/_PROMPTS/README.md`
- `_docs/_PROMPTS/WORKFLOW_ROUTER_FIRST.md`
- `_docs/_PROMPTS/REFERENCE_GUIDED_CREATURE_BUILD.md`
- `README.md`

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_public_surface_docs.py`
- prompt/provider tests as needed

## Changelog Impact

- include in the parent umbrella changelog entry when shipped

## Execution Structure

| Order | Leaf | Purpose |
|------|------|---------|
| 1 | [TASK-150-04-01](./TASK-150-04-01_Required_Prompt_Bundle_Contract_And_Provider_Surface.md) | Expose required/preferred prompt bundles as server-owned flow state |
| 2 | [TASK-150-04-02](./TASK-150-04-02_Flow_Domain_Step_To_Prompt_Mapping_And_Guidance.md) | Map flow/domain/step combinations onto concrete prompt bundles and docs guidance |
