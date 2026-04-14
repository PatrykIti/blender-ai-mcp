# TASK-156: Guided Pair Role Cardinality And Sibling Part Registration

**Status:** ✅ Done
**Priority:** 🔴 High
**Category:** Guided Runtime / Role Semantics / Creature Blockout
**Follow-on After:** [TASK-155](./TASK-155_Guided_Post_Run_Reliability_Followups.md)

## Objective

Fix role semantics for pair/group creature parts such as `ear_pair`,
`foreleg_pair`, and `hindleg_pair`.

Recent guided runs show that once the LLM creates `Ear_L` with
`guided_role="ear_pair"`, the role is considered complete and a subsequent
`Ear_R` with the same role is blocked. The LLM then tries to create the sibling
without a role, register it manually, or skip it entirely. This is a runtime
contract problem: pair roles should not be treated as singletons.

## Repository Touchpoints

- `server/adapters/mcp/contracts/guided_flow.py`
- `server/adapters/mcp/session_capabilities.py`
- `server/adapters/mcp/router_helper.py`
- `server/adapters/mcp/guided_naming_policy.py`
- `server/adapters/mcp/areas/router.py`
- `server/adapters/mcp/areas/modeling.py`
- `tests/unit/adapters/mcp/test_guided_flow_state_contract.py`
- `tests/unit/adapters/mcp/test_context_bridge.py`
- `tests/unit/adapters/mcp/test_guided_naming_policy.py`
- `tests/e2e/integration/test_guided_surface_contract_parity.py`
- `_docs/_MCP_SERVER/README.md`
- `_docs/_PROMPTS/REFERENCE_GUIDED_CREATURE_BUILD.md`
- `_docs/_TASKS/README.md`

## Acceptance Criteria

- role groups can declare cardinality:
  - singleton roles such as `body_core`, `head_mass`, `tail_mass`
  - pair roles such as `ear_pair`, `foreleg_pair`, `hindleg_pair`
  - future counted/group roles if needed
- `allowed_roles` and `missing_roles` reflect remaining cardinality, not only
  whether a role string exists at least once
- creating `Ear_L` with `guided_role="ear_pair"` should still allow `Ear_R`
  under the same role until the pair cardinality is satisfied
- completed role summaries distinguish:
  - role name completion
  - registered object count
  - object names already registered for the role
- naming policy can suggest side-specific names for the next missing sibling
- execution policy blocks the third ear/leg by cardinality once the pair is
  complete

## Tests To Add/Update

- Unit:
  - `ear_pair` allows two distinct objects and blocks the third
  - `foreleg_pair` / `hindleg_pair` cardinality works the same
  - `allowed_roles` remains visible until cardinality is satisfied
  - `completed_roles` / public summaries remain compact and deterministic
  - role-sensitive transform still works for registered siblings
- E2E:
  - guided creature flow creates `Ear_L` + `Ear_R`
  - guided creature flow creates `ForeLeg_L` + `ForeLeg_R` and
    `HindLeg_L` + `HindLeg_R`

## Docs To Update

- `_docs/_MCP_SERVER/README.md`
- `_docs/_PROMPTS/REFERENCE_GUIDED_CREATURE_BUILD.md`
- `_docs/_PROMPTS/GUIDED_SESSION_START.md`
- `_docs/_TASKS/README.md`
- `_docs/_CHANGELOG/README.md`

## Changelog Impact

- add a dedicated `_docs/_CHANGELOG/*` entry when this task ships

## Execution Structure

| Order | Subtask | Purpose |
|------|---------|---------|
| 1 | [TASK-156-01](./TASK-156-01_Guided_Role_Cardinality_Contract_And_State_Model.md) | Add cardinality metadata and state summary for guided roles |
| 2 | [TASK-156-02](./TASK-156-02_Pair_Role_Execution_And_Naming_Policy.md) | Enforce pair role counts and side-aware naming suggestions |
| 3 | [TASK-156-03](./TASK-156-03_Regression_Docs_And_Closeout_For_Pair_Roles.md) | Lock pair-role behavior with unit/E2E coverage and docs closeout |

## Status / Board Update

- promote as a board-level follow-on because TASK-155 is closed and this work
  changes guided role semantics rather than only planner behavior

## Status / Closeout Note

- when this umbrella closes, update every descendant status, record validation
  commands, add the changelog entry, and keep the board row synchronized with
  the parent task status

## Completion Summary

- completed on 2026-04-14 by adding role cardinality metadata and public compact role diagnostics
- pair roles `ear_pair`, `foreleg_pair`, and `hindleg_pair` now remain allowed until two side-specific siblings or one aggregate pair object is registered
- execution policy blocks over-cardinality calls once the pair role is complete
- updated MCP/prompt docs and added `_docs/_CHANGELOG/237-2026-04-14-guided-pair-role-cardinality.md`
- validated with focused guided flow and context bridge unit tests
