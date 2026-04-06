# TASK-141: Guided Creature Run Contract and Schema Drift Hardening

**Status:** ✅ Done
**Priority:** 🔴 High
**Category:** Product Reliability / Guided Runtime UX
**Follow-on After:** [TASK-128](./TASK-128_Reference_Guided_Creature_Build_Surface_And_Perception_Reliability.md)

**Completion Summary:** The active `llm-guided` creature surface now keeps one
real end-to-end contract for the squirrel-run bootstrap/build seam. Direct
visible guided tools and the discovery `call_tool(...)` proxy now share the
same guided hardening for cleanup, one-reference attach, collection creation,
and primitive creation, while `inspect_validate` and degraded compare now land
on the same explicit inspect/measure/assert handoff. Focused stdio-backed
integration coverage now protects the active client path instead of only
helper-level policy tests.

## Objective

Make the real active `llm-guided` creature build surface behave like the repo
claims it behaves, so a reference-guided low-poly squirrel run can reach the
actual geometry/attachment problems without first bleeding turns on avoidable
surface-contract drift.

## Business Problem

The repo now has many local fixes for guided contract drift, but the latest
real squirrel runs show that those fixes still do not line up cleanly on the
actual active surface used by a live MCP client.

Observed failure shapes now look like this:

- unit/docs-level contract fixes exist, but the real `call_tool(...)` path can
  still surface raw validation failure for creature-blockout calls such as
  `collection_manage(..., name=...)`
- the first real guided run still spends early turns rediscovering:
  - `call_tool(name=..., arguments=...)`
  - `scene_clean_scene(keep_lights_and_cameras=...)`
  - one-reference-per-call `reference_images(action="attach", source_path=...)`
  - `collection_manage(action=..., collection_name=...)`
  - the true public `modeling_create_primitive(...)` shape
- search responses for obvious creature bootstrap queries can still be large,
  noisy, or operationally weak enough that the model falls back to guesswork
- when staged compare is unavailable or returns `loop_disposition="inspect_validate"`,
  the next-step story is still not strong enough to force a clean
  inspect/measure/assert takeover in a real run

This task is therefore no longer just "write better docs and aliases." It is
about proving that the documented guided contract survives the full
surface/visibility/search/proxy/transport path that a real creature session
actually uses.

## Scope

This follow-on covers:

- closing parity gaps between:
  - unit-tested discovery/proxy helpers
  - prompt/docs wording
  - shaped visibility/search behavior
  - the real active `llm-guided` server profile and transport path
- reducing early-run rediscovery cost for the creature bootstrap/build seam:
  - `call_tool(name=..., arguments=...)`
  - `scene_clean_scene(keep_lights_and_cameras=...)`
  - `reference_images(action="attach", source_path=..., ...)`
  - `collection_manage(...)`
  - `modeling_create_primitive(...)`
- making build-surface search materially more useful under real creature-session
  pressure, not only technically available
- making `inspect_validate` and degraded-compare outcomes operationally explicit
  enough that the run cleanly pivots into inspect/measure/assert instead of
  drifting back into free-form modeling
- adding E2E/integration regressions that replay the early squirrel-session
  contract path through the real shaped surface

This follow-on does **not** cover:

- broader bootstrap-default consistency under [TASK-130](./TASK-130_Default_Guided_Surface_Bootstrap_Consistency.md)
- anatomy-aware creature reconstruction under [TASK-135](./TASK-135_Anatomy_Aware_Reference_Guided_Low_Poly_Creature_Reconstruction.md)
- expanding the external `vision_contract_profile` family matrix under
  [TASK-140](./TASK-140_Expand_External_Vision_Contract_Profiles_Across_Qwen_Anthropic_OpenAI_And_NVIDIA.md)

## Acceptance Criteria

- the repo has one explicit first-run guided creature story that is proven on
  the same shaped surface and transport path used by a real client
- the canonical public signatures for cleanup, reference attach, collection
  creation, and primitive creation are easy to reach without repeated search +
  validation churn
- any accepted compatibility alias is verified end to end on the active guided
  surface; unsupported shapes fail with deterministic actionable guidance
  instead of raw schema noise
- early creature runs do not need to rediscover the basic setup/build contract
  from first-failure experience alone before they can even reach geometry work
- `inspect_validate` and vision-unavailable/degraded compare outcomes are
  documented and regression-tested as true inspect/measure/assert handoffs
- E2E/integration coverage protects the concrete squirrel-run failure shapes
  that still appear on the real guided surface

## Repository Touchpoints

- `_docs/_PROMPTS/REFERENCE_GUIDED_CREATURE_BUILD.md`
- `_docs/_PROMPTS/README.md`
- `_docs/_MCP_SERVER/README.md`
- `_docs/_MCP_SERVER/MCP_CLIENT_CONFIG_EXAMPLES.md`
- `README.md`
- `server/adapters/mcp/transforms/visibility_policy.py`
- `server/adapters/mcp/discovery/search_documents.py`
- `server/adapters/mcp/discovery/search_surface.py`
- `server/adapters/mcp/factory.py`
- `server/adapters/mcp/surfaces.py`
- `server/adapters/mcp/areas/reference.py`
- `server/adapters/mcp/areas/router.py`
- `server/adapters/mcp/areas/collection.py`
- `server/adapters/mcp/areas/modeling.py`
- `tests/unit/adapters/mcp/test_public_surface_docs.py`
- `tests/unit/adapters/mcp/test_reference_images.py`
- `tests/unit/adapters/mcp/test_search_surface.py`
- `tests/unit/adapters/mcp/test_router_elicitation.py`
- `tests/e2e/router/test_guided_manual_handoff.py`
- `tests/e2e/integration/test_guided_surface_contract_parity.py`
- `tests/e2e/integration/test_guided_inspect_validate_handoff.py`

## Docs To Update

- `README.md`
- `_docs/_PROMPTS/REFERENCE_GUIDED_CREATURE_BUILD.md`
- `_docs/_PROMPTS/README.md`
- `_docs/_MCP_SERVER/README.md`
- `_docs/_MCP_SERVER/MCP_CLIENT_CONFIG_EXAMPLES.md`
- `_docs/_TASKS/README.md`

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_public_surface_docs.py`
- `tests/unit/adapters/mcp/test_reference_images.py`
- `tests/unit/adapters/mcp/test_search_surface.py`
- `tests/unit/adapters/mcp/test_router_elicitation.py`
- `tests/e2e/router/test_guided_manual_handoff.py`
- `tests/e2e/integration/test_guided_surface_contract_parity.py`
- `tests/e2e/integration/test_guided_inspect_validate_handoff.py`

## Changelog Impact

- add a dedicated `_docs/_CHANGELOG/*` entry when this follow-on ships

## Execution Structure

| Order | Subtask | Purpose |
|------|---------|---------|
| 1 | [TASK-141-01](./TASK-141-01_Guided_Call_Path_Compatibility_And_Public_Contract_Ergonomics.md) | Prove that the early guided utility/intake contract really works on the active shaped surface instead of only in local helper tests and docs |
| 2 | [TASK-141-02](./TASK-141-02_Creature_Build_Signature_Cues_And_Discovery_Surface_Alignment.md) | Make the creature blockout tool signatures discoverable and operational under real session pressure, including search payload quality and actual `call_tool(...)` parity |
| 3 | [TASK-141-03](./TASK-141-03_Inspect_Validate_Handoff_And_Regression_Pack.md) | Turn `inspect_validate` and degraded compare outcomes into an explicit truth-first handoff and lock that behavior with real-session regression coverage |

## Status / Board Update

- promote this as a board-level follow-on after the first real `TASK-128`
  squirrel run
- keep it separate from `TASK-130` because this is guided creature
  operator-path/schema drift, not the broader default-bootstrap story
- keep board tracking on this parent unless one execution slice needs to be
  promoted independently
- treat `TASK-141-01` through `TASK-141-03` as the canonical technical
  execution tree for this follow-on

## Validation

- `poetry run pytest tests/unit/adapters/mcp/test_search_surface.py tests/unit/adapters/mcp/test_reference_images.py tests/unit/adapters/mcp/test_public_surface_docs.py tests/unit/adapters/mcp/test_router_elicitation.py -q`
- `poetry run pytest tests/e2e/integration/test_guided_surface_contract_parity.py tests/e2e/integration/test_guided_inspect_validate_handoff.py -q`
- `poetry run pytest tests/e2e/router/test_guided_manual_handoff.py -q` (`3 skipped`)
