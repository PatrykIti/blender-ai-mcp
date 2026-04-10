# TASK-155: Guided Post-Run Reliability Follow-Ups

**Status:** ⏳ To Do
**Priority:** 🔴 High
**Category:** Guided Runtime / Production Reliability / Post-Run Hardening
**Follow-on After:** [TASK-130](./TASK-130_Default_Guided_Surface_Bootstrap_Consistency.md)

## Objective

Turn the latest long-running guided creature session findings into one
actionable follow-on umbrella, without reopening closed TASK-130 / TASK-151 /
TASK-152 / TASK-154 children.

This umbrella covers the remaining runtime/product failures observed after the
generic guided-governor hardening wave:

- `misaligned_attachment` contract drift and seam-truth semantics
- over-eager spatial refresh after small build mutations
- create-then-transform visibility contradictions
- scope/workset mismatch guidance
- checkpoint target-scope and role-summary drift
- macro/assert argument UX noise
- oversized checkpoint payloads
- empty-scene bootstrap before a meaningful spatial target exists

## Repository Touchpoints

- `server/adapters/mcp/contracts/scene.py`
- `server/application/services/spatial_graph.py`
- `server/adapters/mcp/areas/reference.py`
- `server/adapters/mcp/areas/scene.py`
- `server/adapters/mcp/session_capabilities.py`
- `server/adapters/mcp/transforms/visibility_policy.py`
- `server/adapters/mcp/router_helper.py`
- `server/adapters/mcp/discovery/search_surface.py`
- `_docs/_MCP_SERVER/README.md`
- `_docs/_PROMPTS/REFERENCE_GUIDED_CREATURE_BUILD.md`
- `_docs/_PROMPTS/GUIDED_SESSION_START.md`
- `_docs/_TASKS/README.md`

## Acceptance Criteria

- guided relation/checkpoint payloads no longer crash when attachment semantics
  emit `misaligned_attachment`
- seated organic seams such as `Head -> Body` are not falsely escalated solely
  because center-Z alignment differs from the support object
- guided blockout can perform a bounded create-and-initial-shape move without
  immediately hiding the documented transform path
- spatial refresh remains safety-preserving but reports mismatched scope and
  stale-workset state with actionable guidance
- checkpoint and role summaries match the actual roles/families that execution
  will allow
- common macro/assert argument slips are normalized or returned as guided,
  actionable errors instead of raw schema noise
- guided checkpoint responses have a compact mode suitable for long-running LLM
  sessions
- empty-scene guided sessions enter a primary-workset bootstrap path before
  requiring target-bound spatial checks

## Tests To Add/Update

- Unit:
  - `tests/unit/tools/scene/test_scene_contracts.py`
  - `tests/unit/tools/test_handler_rpc_alignment.py`
  - `tests/unit/adapters/mcp/test_reference_images.py`
  - `tests/unit/adapters/mcp/test_guided_flow_state_contract.py`
  - `tests/unit/adapters/mcp/test_visibility_policy.py`
  - `tests/unit/adapters/mcp/test_search_surface.py`
  - `tests/unit/adapters/mcp/test_scene_guided_scope_requirements.py`
  - `tests/unit/adapters/mcp/test_public_surface_docs.py`
  - `tests/unit/adapters/mcp/test_structured_contract_delivery.py`
  - `tests/unit/tools/scene/test_macro_attach_part_to_surface_mcp.py`
  - `tests/unit/tools/scene/test_scene_mcp_tools_batch.py`
- E2E:
  - `tests/e2e/integration/test_guided_surface_contract_parity.py`
  - `tests/e2e/integration/test_guided_streamable_spatial_support.py`
  - `tests/e2e/integration/test_guided_inspect_validate_handoff.py`
  - `tests/e2e/vision/test_reference_stage_assembled_creature_attachment_truth.py`
  - `tests/e2e/vision/test_reference_stage_silhouette_contract.py`
  - `tests/e2e/tools/macro/test_macro_attach_part_to_surface.py`
  - `tests/e2e/tools/macro/test_macro_align_part_with_contact.py`

## Changelog Impact

- add a dedicated `_docs/_CHANGELOG/*` entry when this umbrella ships
- update `_docs/_CHANGELOG/README.md` with that entry during closeout

## Execution Structure

| Order | Subtask | Purpose |
|------|---------|---------|
| 1 | [TASK-155-01](./TASK-155-01_Attachment_Verdict_Contract_And_Truth_Semantics.md) | Fix attachment verdict schema drift and make seated organic seam semantics reliable |
| 2 | [TASK-155-02](./TASK-155-02_Governor_Workset_Refresh_And_Bootstrap_Discipline.md) | Tighten guided governor behavior around spatial refresh, workset scope, checkpoint targets, roles, and empty-scene bootstrap |
| 3 | [TASK-155-03](./TASK-155-03_Guided_Tool_UX_And_Response_Budget.md) | Reduce avoidable schema/tool UX loops and checkpoint token pressure |
| 4 | [TASK-155-04](./TASK-155-04_Regression_And_Docs_Closeout_For_Post_Run_Reliability.md) | Lock the fixes with targeted unit/E2E coverage, docs, and changelog closeout |

## Status / Board Update

- promote as a board-level follow-on after TASK-130 because the real post-run
  failures cross several closed guided-runtime waves
- keep descendant work under this new open umbrella so closed historical
  parents do not accumulate open direct children
