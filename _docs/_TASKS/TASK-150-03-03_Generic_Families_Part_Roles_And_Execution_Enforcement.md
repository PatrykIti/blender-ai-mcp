# TASK-150-03-03: Generic Families, Part Roles, And Execution Enforcement

**Parent:** [TASK-150-03](./TASK-150-03_Step_Gated_Visibility_And_Execution_Policy.md)
**Depends On:** [TASK-150-02](./TASK-150-02_Domain_Profile_Selection_And_Overlay_Policy.md), [TASK-150-03-02](./TASK-150-03-02_Step_Completion_Checks_And_Execution_Blocks.md)
**Status:** 🚧 In Progress
**Priority:** 🔴 High

## Objective

Extend TASK-150 from visibility/search gating into real execution-time guided
policy without exploding the MCP surface into one macro/mega tool per domain
part.

The intended shape is:

- shared generic build families
- one shared `guided_flow_state`
- domain overlays define allowed part roles, required checkpoints, prompt
  bundles, and family ordering
- existing atomics/macros continue doing the actual work
- router/firewall policy decides whether one action is allowed for the current
  family/role/step

## Business Problem

The current TASK-150 delivery successfully gates the early guided session:

- no-goal bootstrap is bounded
- `establish_spatial_context` is real
- search/list/call behavior can unlock after required checks

But after that unlock, broad build families still become too permissive.
The server does not yet know whether a new primitive is:

- body/core mass
- head mass
- tail mass
- ear pair
- facade opening
- roof mass

Without that semantic layer, the model can still improvise the in-family build
order even when the outer `guided_flow_state.current_step` says
`create_primary_masses`.

## Repository Touchpoints

- `server/adapters/mcp/contracts/guided_flow.py`
- `server/adapters/mcp/session_capabilities.py`
- `server/adapters/mcp/router_helper.py`
- `server/adapters/mcp/transforms/visibility_policy.py`
- `server/adapters/mcp/discovery/search_surface.py`
- `server/adapters/mcp/areas/router.py`
- `tests/unit/adapters/mcp/`
- `tests/e2e/integration/`
- `tests/e2e/router/`
- `_docs/_MCP_SERVER/README.md`
- `_docs/_PROMPTS/README.md`

## Acceptance Criteria

- the guided runtime has one shared vocabulary for build families such as:
  - `primary_masses`
  - `secondary_parts`
  - `attachment_alignment`
  - `checkpoint_iterate`
  - `inspect_validate`
  - `finish`
- the server can track bounded part roles in session state without adding a
  large family of domain-specific build tools
- router/firewall execution policy can block actions that belong to the wrong
  family or wrong role group for the current step
- blocked actions return typed guidance instead of relying only on visibility
  shaping
- domain overlays remain metadata/policy driven instead of forking into
  unrelated state machines

## Planned Unit Test Scenarios

- verify shared family vocabulary serializes through `guided_flow_state`
- verify overlay family order differs between `generic`, `creature`, and
  `building`
- verify part-role summaries persist in session state without exposing the full
  internal registry
- verify family/role enforcement blocks the wrong family even when the tool is
  otherwise valid
- verify required role-group completion advances the flow step

## Planned E2E / Transport Scenarios

- stdio guided creature session:
  - spatial checks unlock `create_primary_masses`
  - secondary-part creation is still blocked before primary role groups complete
- streamable guided creature session:
  - same-session role registration or guided role hints unlock the next family
  - `search_tools(...)` / `call_tool(...)` stay aligned with the new step
- no-match/manual creature path:
  - direct build calls can still be blocked by family/role policy even after
    broad build unlock

## Detailed Design Direction

- do **not** solve this by creating a separate macro/mega tool for every
  creature/building part
- add one small semantic layer so existing tools can be interpreted by the
  server:
  - shared tool families
  - session-scoped part-role registry
  - bounded role registration / optional role hints
- keep `guided_flow_state` as the machine-readable surface contract, and extend
  it with family/role summaries instead of replacing it
- keep `guided_handoff` and prompt bundles as support structures; execution
  policy must live in server/runtime code

## Execution Structure

| Order | Leaf | Purpose |
|------|------|---------|
| 1 | [TASK-150-03-03-01](./TASK-150-03-03-01_Shared_Tool_Family_Vocabulary_And_Overlay_Mapping.md) | Define shared generic tool families and map domain overlays onto those families instead of domain-specific mega-tool proliferation |
| 2 | [TASK-150-03-03-02](./TASK-150-03-03-02_Guided_Part_Role_Registry_And_Session_Contracts.md) | Add session-scoped part-role tracking so the server knows what kind of object/part the model is currently creating or editing |
| 3 | [TASK-150-03-03-03](./TASK-150-03-03-03_Guided_Register_Part_And_Role_Hint_Input_Path.md) | Add the minimal public/server input path for assigning part roles without creating a large new family of build tools |
| 4 | [TASK-150-03-03-04](./TASK-150-03-03-04_Router_Execution_Guards_And_Blocked_Response_Policy.md) | Enforce family/role policy in router/firewall execution rather than only in visibility/search |
| 5 | [TASK-150-03-03-05](./TASK-150-03-03-05_Flow_Transitions_From_Role_Groups_And_Checkpoints.md) | Advance guided flow steps from completed role groups and checkpoint outcomes instead of only from spatial checks |
| 6 | [TASK-150-03-03-06](./TASK-150-03-03-06_Regression_And_Docs_For_Execution_Enforcement.md) | Add regression coverage and operator docs for family/role execution enforcement |

## Docs To Update

- `_docs/_MCP_SERVER/README.md`
- `_docs/_PROMPTS/README.md`
- `_docs/_TASKS/README.md`

## Tests To Add/Update

- `tests/unit/adapters/mcp/`
- `tests/e2e/integration/`
- `tests/e2e/router/`

## Changelog Impact

- include in the parent TASK-150 changelog wave when this continuation ships
