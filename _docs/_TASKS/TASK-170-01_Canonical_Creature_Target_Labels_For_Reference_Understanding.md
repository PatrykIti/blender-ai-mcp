# TASK-170-01: Canonical Creature Target Labels For Reference Understanding

**Parent:** [TASK-170](./TASK-170_Reference_Target_Canonicalization_And_Support_Latency_Stabilization.md)
**Status:** ✅ Done
**Completed:** 2026-05-20
**Priority:** 🔴 High
**Objective:** Canonicalize common creature RU target labels into the repo-owned creature vocabulary before summary, gate proposal, feedback, and gate-plan seams consume them.
**Repository Touchpoints:** `server/adapters/mcp/vision/parsing.py`, `server/adapters/mcp/areas/reference_understanding.py`, `server/adapters/mcp/areas/reference_feedback.py`, `server/adapters/mcp/contracts/quality_gates.py`, `tests/unit/adapters/mcp/test_vision_parsing.py`, `tests/unit/adapters/mcp/test_reference_images.py`
**Acceptance Criteria:**
- raw RU labels such as `body`, `head`, `ears`, `tail`, and `front legs` normalize to `body_core`, `head_mass`, `ear_pair`, `tail_mass`, and `foreleg_pair` on creature flows
- RU-derived gate ids and gate-plan labels no longer drift to non-canonical `required_part_head` / `required_part_ears` / `required_part_tail` ids on common creature runs
- narrowly specific labels such as `tail_tip` remain distinct and are not over-collapsed into generic creature roles

## Implementation Notes

- normalize at the earliest reliable ingress seam:
  - parsed `required_parts`
  - parsed or explicit RU `gate_proposals`
  - defensive post-parse RU summary canonicalization before gate intake
- keep the mapping creature-only; do not rewrite non-creature labels globally
- preserve gate kind semantics while rewriting labels:
  - `eye_pair` can remain a `reference_part`
  - canonicalization should not silently flip `target_kind`

## Pseudocode

```python
if summary.subject.category == "creature":
    for part in summary.required_parts:
        part.target_label = canonicalize_creature_target_label(part.target_label, part.part_label)
    for gate in summary.gate_proposals:
        gate.target_label = canonicalize_creature_target_label(gate.target_label, gate.label)
```

## Runtime / Security Contract Notes

- canonicalization changes naming only; it must not promote advisory evidence
  into gate authority
- do not remap labels like `tail_tip` or other specific profile/detail targets
  into generic mass labels when the extra specificity matters

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_vision_parsing.py`
- `tests/unit/adapters/mcp/test_reference_images.py`

## Docs To Update

- `_docs/_VISION/README.md`

## Changelog Impact

- covered by the umbrella closeout entry when `TASK-170` lands

## Completion Summary

- creature RU part labels now normalize at parse time and again defensively on
  the RU refresh seam
- gate-plan ingestion and RU gate ids stay aligned with the canonical creature
  vocabulary instead of raw runtime aliases

## Status / Board Update

- closed with parent `TASK-170`

## Validation Commands

- `git diff --check`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_vision_parsing.py tests/unit/adapters/mcp/test_reference_images.py -q`

## Validation Category

- RU parse and gate-ingestion proof
