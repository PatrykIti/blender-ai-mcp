# TASK-171-05: Attachment-First Creature Reference Understanding Contract Expansion

**Parent:** [TASK-171](./TASK-171_Creature_Attachment_First_Build_Contract_And_Structured_Vision_Handoff.md)
**Status:** ⏳ To Do
**Priority:** 🔴 High
**Objective:** Expand the strict RU contract with typed creature assembly fields such as `mass_recipe`, `attachment_plan`, `contact_expectations`, `shape_profile_hints`, `silhouette_landmarks`, `support_surface_candidates`, `anchor_object_candidates`, `part_order`, and `must_seat_before_next_stage`, while keeping the output advisory-only and on the existing RU surfaces.
**Repository Touchpoints:** `server/adapters/mcp/contracts/reference.py`, `server/adapters/mcp/areas/reference_understanding.py`, `server/adapters/mcp/areas/reference_feedback.py`, `server/adapters/mcp/vision/prompting.py`, `server/adapters/mcp/vision/parsing.py`, `tests/unit/adapters/mcp/test_vision_prompting.py`, `tests/unit/adapters/mcp/test_vision_parsing.py`, `tests/e2e/vision/test_reference_understanding_runtime_surface.py`, `_docs/_VISION/REFERENCE_UNDERSTANDING_ROADMAP.md`
**Acceptance Criteria:**
- the RU contract can express creature assembly structure beyond `required_parts` without weakening strict schema validation
- the new fields are clearly documented as semantic/advisory RU outputs rather than live Blender-scene truth
- RU runtime surfaces, prompt templates, parser validation, and tests all stay in sync

## Implementation Notes

- the current RU path is not “required_parts only”; it already carries:
  - `subject`
  - `style`
  - `views`
  - `construction_strategy`
  - `router_handoff_hints`
  - `gate_proposals`
  - `visual_evidence_refs`
  - `visual_metrics`
  - optional support evidence
- the actual missing piece is deeper attachment-first creature assembly
  structure
- the contract must make one explicit meaning decision for object-sounding
  fields such as `anchor_object_candidates` and
  `support_surface_candidates`:
  - either they are semantic role/part anchors at RU time
  - or they are later-resolved placeholders that the runtime binds after scene
    objects exist
- prefer canonical creature role labels such as `body_core`, `head_mass`,
  `tail_mass`, `snout_mass`, and pair roles inside these new RU structures
- keep unknown-field rejection intact; this slice must update contract,
  prompt/schema, parser normalization, parser validation, and runtime-surface
  tests together

## Pseudocode

```python
class ReferenceUnderstandingAssemblyPartContract(...):
    target_label: str
    geometry_family: str
    anchor_candidates: list[str]
    required_relation: str | None
    forbid: list[str]

summary = ReferenceUnderstandingSummaryContract(
    ...,
    mass_recipe=[...],
    attachment_plan=[...],
    part_order=[...],
    must_seat_before_next_stage=[...],
)
```

## Runtime / Security Contract Notes

- RU remains advisory-only; the new fields must not unlock tools, pass gates, or
  override scene truth
- the slice must stay on the existing `reference_images(...)`, `router_*`, and
  staged compare/iterate seams; do not add a new public RU tool
- typed RU fields should prefer canonical creature roles over raw prose labels
  so later runtime normalization stays deterministic

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_vision_prompting.py`
- `tests/unit/adapters/mcp/test_vision_parsing.py`
- `tests/e2e/vision/test_reference_understanding_runtime_surface.py`

## Docs To Update

- `_docs/_VISION/REFERENCE_UNDERSTANDING_ROADMAP.md`
- `_docs/_VISION/README.md`
- `_docs/_MCP_SERVER/README.md`
- `_docs/_PROMPTS/REFERENCE_GUIDED_CREATURE_BUILD.md`

## Changelog Impact

- add/update the historical `_docs/_CHANGELOG/*` entry when this slice lands

## Validation Commands

- `git diff --check`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_vision_prompting.py -q`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_vision_parsing.py -q`
- `PYTHONPATH=. poetry run pytest tests/e2e/vision/test_reference_understanding_runtime_surface.py -q`

## Validation Category

- RU contract, prompt/schema, and runtime-surface proof
