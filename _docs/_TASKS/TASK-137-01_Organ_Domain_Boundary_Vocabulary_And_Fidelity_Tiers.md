# TASK-137-01: Organ Domain Boundary, Vocabulary, And Fidelity Tiers

**Status:** ⏳ To Do
**Priority:** 🔴 High
**Parent:** [TASK-137](./TASK-137_Anatomy_Aware_Reference_Guided_Organ_Reconstruction.md)
**Depends On:** [TASK-157](./TASK-157_Goal_Derived_Quality_Gates_And_Deterministic_Verification.md), [TASK-158](./TASK-158_Vision_And_Creature_Gate_Boundary_Doc_Alignment.md), [TASK-163](./TASK-163_Vision_Orchestrator_Feedback_Strategy_Normalization_And_Optional_Perception_Adapters.md)
**Objective:** Define the first safe organ target classes, anatomy vocabulary, fidelity tiers, and medical-scope guardrails on the existing RU/gate substrate.
**Repository Touchpoints:** `server/adapters/mcp/vision/prompting.py`, `server/adapters/mcp/vision/parsing.py`, `server/adapters/mcp/vision/reference_support.py`, `server/adapters/mcp/areas/reference_understanding.py`, `server/adapters/mcp/areas/reference_feedback.py`, `server/adapters/mcp/areas/reference.py`, `server/adapters/mcp/areas/reference_images_runtime.py`, `server/adapters/mcp/areas/reference_planner.py`, `server/adapters/mcp/areas/router.py`, `server/adapters/mcp/contracts/quality_gates.py`, `server/adapters/mcp/contracts/reference.py`, `server/adapters/mcp/contracts/router.py`, `server/adapters/mcp/prompts/prompt_catalog.py`, `server/adapters/mcp/prompts/provider.py`, `server/adapters/mcp/prompts/rendering.py`, `server/adapters/mcp/session_capabilities_flow.py`, likely new `_docs/_PROMPTS/REFERENCE_GUIDED_ORGAN_BUILD.md`, `_docs/_PROMPTS/README.md`, `_docs/_VISION/README.md`, `_docs/_MCP_SERVER/README.md`, `tests/unit/adapters/mcp/test_vision_prompting.py`, `tests/unit/adapters/mcp/test_vision_parsing.py`, `tests/unit/adapters/mcp/test_quality_gate_contracts.py`, `tests/unit/adapters/mcp/test_quality_gate_intake.py`, `tests/unit/adapters/mcp/test_reference_images.py`, `tests/unit/adapters/mcp/test_contract_payload_parity.py`, `tests/unit/adapters/mcp/test_prompt_catalog.py`, `tests/unit/adapters/mcp/test_prompt_catalog_flow_mapping.py`, `tests/unit/adapters/mcp/test_prompt_provider.py`, `tests/unit/adapters/mcp/test_prompt_provider_flow_bundles.py`, `tests/unit/adapters/mcp/test_public_surface_docs.py`, `tests/unit/router/application/test_router_contracts.py`, `tests/e2e/vision/test_reference_understanding_runtime_surface.py`
**Acceptance Criteria:** the repo names explicit non-clinical organ target classes and fidelity tiers; RU/reference/gate contracts can express organ-specific masses, chambers, lobes, cavities, and ports without implying medical diagnosis or patient-specific use.

## Implementation Notes

- start with safe visualization/teaching targets, not patient-specific or
  diagnostic flows
- define reusable organ nouns and relations:
  - lobe
  - chamber
  - cavity
  - inlet/outlet/port
  - fused into mass
  - embedded cavity
  - attached landmark
  - paired but separate
- keep the medical boundary explicit in every contract and prompt surface
- register any organ prompt asset through the existing `prompt_catalog.py` /
  prompt-provider flow, and thread required/recommended prompt bundles through
  the owning `session_capabilities_flow.py` path; do not add a second prompt
  exposure path
- this leaf owns the first runtime registration of the organ prompt asset on
  `prompt_catalog.py` / `provider.py` / `rendering.py`; do not leave a
  docs-only prompt markdown without the live prompt-provider path
- if organ-safe vocabulary becomes visible on `reference_images(...)`,
  `router_get_status(...)`, or staged checkpoint payloads, thread it through the
  existing reference/router contracts instead of ad hoc response fields
- audit `reference_planner.py` in the same slice so pathology-adjacent wording
  or `anatomy` refinement routing does not silently bypass the new
  medical-scope boundary

## Pseudocode

```python
organ_class = select_safe_organ_target_class(goal, references)
fidelity_tier = resolve_non_clinical_fidelity_tier(organ_class, goal)
organ_vocab = build_organ_vocabulary(organ_class, fidelity_tier)

ru_contract = extend_reference_understanding_contract(
    domain_vocabulary=organ_vocab,
    boundary_policy=medical_safe_boundary_policy(),
)
```

## Runtime / Security Contract Notes

- no diagnosis, pathology inference, regulatory claims, or patient-specific
  planning
- organ-aware RU remains advisory-only and bounded by the existing verifier
  authority split
- do not add a new public organ-only MCP tool in this slice

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_vision_prompting.py`
- `tests/unit/adapters/mcp/test_vision_parsing.py`
- `tests/unit/adapters/mcp/test_quality_gate_contracts.py`
- `tests/unit/adapters/mcp/test_quality_gate_intake.py`
- `tests/unit/adapters/mcp/test_reference_images.py`
- `tests/unit/adapters/mcp/test_contract_payload_parity.py`
- `tests/unit/adapters/mcp/test_prompt_catalog.py`
- `tests/unit/adapters/mcp/test_prompt_catalog_flow_mapping.py`
- `tests/unit/adapters/mcp/test_prompt_provider.py`
- `tests/unit/adapters/mcp/test_prompt_provider_flow_bundles.py`
- `tests/unit/adapters/mcp/test_public_surface_docs.py`
- `tests/unit/router/application/test_router_contracts.py`
- `tests/e2e/vision/test_reference_understanding_runtime_surface.py`

## Docs To Update

- `_docs/_PROMPTS/README.md`
- likely new `_docs/_PROMPTS/REFERENCE_GUIDED_ORGAN_BUILD.md`
- `_docs/_VISION/README.md`
- `_docs/_MCP_SERVER/README.md`
- `_docs/AVAILABLE_TOOLS_SUMMARY.md`
- `_docs/_TESTS/README.md`

## Changelog Impact

- Add a `_docs/_CHANGELOG/*` entry when the first organ domain-contract slice
  ships.

## Validation Commands

- `git diff --check`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_vision_prompting.py tests/unit/adapters/mcp/test_vision_parsing.py tests/unit/adapters/mcp/test_quality_gate_contracts.py tests/unit/adapters/mcp/test_quality_gate_intake.py tests/unit/adapters/mcp/test_reference_images.py tests/unit/adapters/mcp/test_contract_payload_parity.py tests/unit/adapters/mcp/test_prompt_catalog.py tests/unit/adapters/mcp/test_prompt_catalog_flow_mapping.py tests/unit/adapters/mcp/test_prompt_provider.py tests/unit/adapters/mcp/test_prompt_provider_flow_bundles.py tests/unit/adapters/mcp/test_public_surface_docs.py -q`
- `PYTHONPATH=. poetry run pytest tests/unit/router/application/test_router_contracts.py -q`
- `poetry run pytest tests/e2e/vision/test_reference_understanding_runtime_surface.py -q`
- `Outside sandbox before closeout: PYTHONPATH=. poetry run pytest ./tests/unit`
- `Outside sandbox before closeout: poetry run python scripts/run_e2e_tests.py`

## Status / Board Update

- keep `_docs/_TASKS/README.md` on the umbrella `TASK-137` row; this leaf does
  not become its own promoted board item
- if the first organ domain-boundary slice lands independently, update this leaf
  and the parent umbrella in the same branch before any later closeout leaf
