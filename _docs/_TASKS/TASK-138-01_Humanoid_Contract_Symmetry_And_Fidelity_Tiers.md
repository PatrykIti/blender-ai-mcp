# TASK-138-01: Humanoid Contract, Symmetry, And Fidelity Tiers

**Status:** ⏳ To Do
**Priority:** 🔴 High
**Parent:** [TASK-138](./TASK-138_Anatomy_Aware_Reference_Guided_Biped_And_Fantasy_Character_Reconstruction.md)
**Objective:** Define the first humanoid/fantasy target classes, body vocabulary, symmetry rules, and fidelity tiers on the existing RU/gate substrate.
**Repository Touchpoints:** `server/adapters/mcp/vision/prompting.py`, `server/adapters/mcp/vision/parsing.py`, `server/adapters/mcp/areas/reference_understanding.py`, `server/adapters/mcp/contracts/quality_gates.py`, `server/adapters/mcp/contracts/reference.py`, `server/adapters/mcp/areas/reference.py`, `server/adapters/mcp/areas/reference_truth.py`, likely new `_docs/_PROMPTS/REFERENCE_GUIDED_CHARACTER_BUILD.md`, `_docs/_VISION/README.md`, `tests/unit/adapters/mcp/test_vision_prompting.py`, `tests/unit/adapters/mcp/test_vision_parsing.py`, `tests/unit/adapters/mcp/test_quality_gate_contracts.py`
**Acceptance Criteria:** the repo can describe bounded humanoid/fantasy body structure, symmetry, and fidelity tiers without collapsing the domain into generic creature guidance or into unbounded hero-character work.

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
- tie symmetry and segment-ratio expectations into normalized gate templates,
  not into prose-only guidance

## Pseudocode

```python
character_class = select_character_target_class(goal, references)
fidelity_tier = resolve_body_fidelity_tier(character_class, goal)
body_vocab = build_humanoid_vocabulary(character_class, fidelity_tier)

gate_templates = derive_character_gate_templates(
    body_vocab=body_vocab,
    symmetry_rules=bounded_humanoid_symmetry_rules(),
)
```

## Runtime / Security Contract Notes

- no actor likeness, portrait fidelity, or hero-character sculpting claims
- humanoid/fantasy RU remains advisory-only and bounded by the existing verifier
  authority split
- do not add a new public character-only gate tool in this slice

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_vision_prompting.py`
- `tests/unit/adapters/mcp/test_vision_parsing.py`
- `tests/unit/adapters/mcp/test_quality_gate_contracts.py`

## Docs To Update

- likely new `_docs/_PROMPTS/REFERENCE_GUIDED_CHARACTER_BUILD.md`
- `_docs/_VISION/README.md`
- `_docs/_MCP_SERVER/README.md`
- `_docs/_TESTS/README.md`

## Changelog Impact

- Add a `_docs/_CHANGELOG/*` entry when the first character domain-contract
  slice ships.

## Validation Commands

- `git diff --check`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_vision_prompting.py tests/unit/adapters/mcp/test_vision_parsing.py tests/unit/adapters/mcp/test_quality_gate_contracts.py -q`
