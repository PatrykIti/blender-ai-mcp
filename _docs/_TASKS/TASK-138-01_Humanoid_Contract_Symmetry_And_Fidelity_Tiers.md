# TASK-138-01: Humanoid Contract, Symmetry, And Fidelity Tiers

**Status:** ⏳ To Do
**Priority:** 🔴 High
**Parent:** [TASK-138](./TASK-138_Anatomy_Aware_Reference_Guided_Biped_And_Fantasy_Character_Reconstruction.md)
**Objective:** Define the first humanoid/fantasy target classes, body vocabulary, symmetry rules, and fidelity tiers on the existing RU/gate substrate.
**Repository Touchpoints:** `server/adapters/mcp/contracts/guided_flow.py`, `server/adapters/mcp/vision/prompting.py`, `server/adapters/mcp/vision/parsing.py`, `server/adapters/mcp/areas/reference_understanding.py`, `server/adapters/mcp/areas/reference_images_runtime.py`, `server/adapters/mcp/contracts/quality_gates.py`, `server/adapters/mcp/transforms/quality_gate_verifier.py`, `server/adapters/mcp/contracts/reference.py`, `server/adapters/mcp/session_capabilities_flow.py`, `server/adapters/mcp/session_capabilities_bootstrap.py`, `server/adapters/mcp/session_capabilities_runtime_glue.py`, `_docs/_VISION/README.md`, `_docs/_MCP_SERVER/README.md`, `tests/unit/adapters/mcp/test_vision_prompting.py`, `tests/unit/adapters/mcp/test_vision_parsing.py`, `tests/unit/adapters/mcp/test_quality_gate_contracts.py`, `tests/unit/adapters/mcp/test_quality_gate_intake.py`, `tests/unit/adapters/mcp/test_reference_images.py`, `tests/unit/adapters/mcp/test_guided_flow_domain_profiles.py`, `tests/e2e/vision/test_reference_understanding_runtime_surface.py`
**Acceptance Criteria:** character-domain RU, gate-ingestion, and reference-envelope contracts serialize bounded torso/pelvis/head/limb vocabulary, symmetry/proportion/final-completion templates, and explicit low/mid-fidelity limits without treating creature fallback or hero-sculpt claims as acceptable substitutes.

## Implementation Notes

- define reusable body nouns and relations:
  - torso
  - pelvis
  - head
  - upper/lower arm
  - hand
  - upper/lower leg
  - foot
  - seated on
  - attached to
  - articulated from
  - mirrored pair
- keep garments, armor, appendages, and props explicitly as later-stage or
  separately bounded follow-ons
- define the first explicit `character` domain profile on the shared
  guided/gate contract, but keep prompt-bundle exposure and guided-handoff
  recipe ownership in `TASK-138-02`
- keep downstream owner boundaries explicit for later leaves:
  - `vision/prompting.py`, `vision/parsing.py`, and
    `reference_understanding.py` for advisory vocabulary and gate seeds
  - `reference_feedback.py` for later server-owned support metrics and bounded
    checkpoint hints once the staged runtime envelopes are in scope
  - `quality_gate_verifier.py` plus the current inspection/assertion seams for
    authoritative pass/fail and evidence authority
- tie symmetry and segment-ratio expectations into normalized gate templates,
  not into prose-only guidance

## Pseudocode

```python
domain_profile = "character"
character_class = select_character_target_class(goal, references)
fidelity_tier = resolve_body_fidelity_tier(character_class, goal)
body_vocab = build_humanoid_vocabulary(character_class, fidelity_tier)

gate_templates = derive_character_gate_templates(
    domain_profile=domain_profile,
    body_vocab=body_vocab,
    symmetry_rules=bounded_humanoid_symmetry_rules(),
)
```

## Runtime / Security Contract Notes

- no actor likeness, portrait fidelity, or hero-character sculpting claims
- humanoid/fantasy RU remains advisory-only and bounded by the existing verifier
  authority split
- do not move deterministic support metrics or pass/fail truth onto the RU or
  prompt-rendering path
- do not add a new public character-only gate tool in this slice

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_guided_flow_domain_profiles.py`
- `tests/unit/adapters/mcp/test_vision_prompting.py`
- `tests/unit/adapters/mcp/test_vision_parsing.py`
- `tests/unit/adapters/mcp/test_quality_gate_contracts.py`
- `tests/unit/adapters/mcp/test_quality_gate_intake.py`
- `tests/unit/adapters/mcp/test_reference_images.py`
- `tests/e2e/vision/test_reference_understanding_runtime_surface.py`

## Docs To Update

- `_docs/_VISION/README.md`
- `_docs/_MCP_SERVER/README.md`
- `_docs/_TESTS/README.md`

## Changelog Impact

- Add a `_docs/_CHANGELOG/*` entry when the first character domain-contract
  slice ships.

## Validation Commands

- `git diff --check`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_guided_flow_domain_profiles.py tests/unit/adapters/mcp/test_vision_prompting.py tests/unit/adapters/mcp/test_vision_parsing.py tests/unit/adapters/mcp/test_quality_gate_contracts.py tests/unit/adapters/mcp/test_quality_gate_intake.py tests/unit/adapters/mcp/test_reference_images.py -q`
- `poetry run pytest ./tests/unit`
- `poetry run python scripts/run_e2e_tests.py`
  Covers the runtime-surface lane including `tests/e2e/vision/test_reference_understanding_runtime_surface.py`.

## Status / Board Update

- keep `TASK-138-02` and `TASK-138-03` open after this leaf lands; `TASK-138-01`
  only closes the character contract substrate and does not close the umbrella
- if downstream runtime envelopes or public prompt surfaces still need work
  after this slice, record that on the remaining open children instead of
  folding it back into this contract leaf
