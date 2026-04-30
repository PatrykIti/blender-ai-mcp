# TASK-157-04: Cross-Domain E2E Gate Regression Harness

**Status:** ⏳ To Do
**Priority:** 🔴 High
**Parent:** [TASK-157](./TASK-157_Goal_Derived_Quality_Gates_And_Deterministic_Verification.md)
**Category:** Tests / Guided Runtime Regression
**Estimated Effort:** Medium

## Objective

Add E2E and regression coverage proving the gate system works across at least
one creature scenario and one building-style scenario.

## Repository Touchpoints

| Path / Module | Expected Change |
|---------------|-----------------|
| `tests/e2e/vision/` | Creature and building guided gate scenarios |
| `tests/e2e/integration/` | Transport/runtime gate-state preservation scenarios |
| `tests/e2e/tools/macro/` | Macro repair scenarios that satisfy gates |
| `tests/fixtures/vision_eval/` | Reference fixtures or golden gate expectations |
| `_docs/_TESTS/README.md` | Document how to run gate regression lanes |

## Creature Scenario

Use a squirrel-like low-poly reconstruction fixture:

- required parts include body, head, snout, eyes, ears, tail, forelegs,
  hindlegs
- required seams include head/body, tail/body, snout/head, eye/head, limb/body
- primitive-only output without eyes fails
- floating tail/body or limb/body gaps fail
- seated/embedded seams pass according to gate policy
- curved tail profile remains pending/failed until a segment chain or accepted
  profile evidence exists
- optional reference-understanding or perception fixtures may seed the gate
  plan, but the scenario must still fail primitive-only completion until
  server-owned verifiers pass the required gates

## Building Scenario

Use a small building/facade-style fixture:

- required parts include base/walls/roof/openings
- required seams include roof/wall seating and support/base contact where
  relevant
- opening gates fail when windows/doors are missing or not cut/placed into the
  wall surface
- proportion/alignment gates fail on obvious roof/wall or facade rhythm drift

## Perception Adapter Boundary

The first cross-domain harness must not require SAM, CLIP, Grounding DINO, or
any other heavy perception sidecar. Use deterministic fixtures or mocked
reference/perception payloads to prove:

- proposal/evidence provenance is preserved
- perception-derived proposals normalize to `pending`
- unavailable optional perception evidence does not crash the guided loop
- unavailable required perception evidence returns a `blocked` gate with a
  machine-readable reason
- final completion still depends on authoritative scene/spatial/mesh/assertion
  evidence for the gates that require it

## Runtime / Security Contract Notes

- Visibility level: E2E scenarios should exercise existing public/guided MCP
  surfaces and avoid adding test-only tools or alternate discovery paths.
- Read-only vs mutating behavior: the harness may create and repair Blender
  geometry through existing mutating tools, but gate pass/fail assertions must
  come from verifier-supported evidence after those mutations.
- Transport assumptions: include the session/transport lane that changed in the
  implementation slice; Streamable HTTP and stdio should preserve gate ids,
  blockers, and visible repair tools consistently.
- External provider limits: default regression fixtures must not require live
  SAM/CLIP/Grounding DINO/SigLIP, live external VLM calls, or segmentation
  sidecars. Optional live-provider lanes must be separately marked.
- Secret/debug handling: captured fixtures and failure artifacts must not store
  provider keys, sidecar keys, or unredacted external payloads.

## Pseudocode

The field names below are `TASK-157` additions to the existing reference
checkpoint response contract. They should align with `TASK-157-03`
(`active_gate_plan`, `gate_statuses`, `completion_blockers`,
`next_gate_actions`, and `recommended_bounded_tools`) rather than legacy role
mirrors.

```python
def test_creature_gate_completion_blocks_primitive_only_squirrel(blender_scene):
    start_guided_creature_goal()
    create_primitive_only_parts_without_eyes()
    result = reference_iterate_stage_checkpoint(collection_name="Squirrel")

    assert result.completion_blockers
    eye_gate = required_gate(
        result.gate_statuses,
        gate_type="required_part",
        gate_target_kind="reference_part",
        target_label="eye_pair",
    )
    assert eye_gate.status in {"blocked", "failed"}
    assert eye_gate.blocker_reason in {"missing_required_part", "missing_scope"}
    if eye_gate.blocker_reason == "missing_required_part":
        assert eye_gate.evidence_refs
    else:
        assert eye_gate.next_action == "provide_gate_scope"
    symmetry_gate = required_gate(
        result.gate_statuses,
        gate_type="symmetry_pair",
        gate_target_kind="reference_part",
        target_label="eye_pair",
    )
    assert symmetry_gate.status in {"blocked", "failed", "pending"}
    assert any(gate.gate_type == "attachment_seam" and gate.status == "failed" for gate in result.gate_statuses)
    assert result.loop_disposition == "inspect_validate"


def test_building_gate_completion_blocks_floating_roof(blender_scene):
    start_guided_building_goal()
    create_wall_and_floating_roof()
    result = reference_iterate_stage_checkpoint(collection_name="Building")

    assert required_gate(result.gate_statuses, gate_id="roof_wall_seam").status == "failed"
    assert "macro_attach_part_to_surface" in result.recommended_bounded_tools
```

## Tests To Add/Update

- `tests/e2e/vision/test_goal_derived_gate_creature_completion.py`
- `tests/e2e/vision/test_goal_derived_gate_building_completion.py`
- `tests/e2e/integration/test_guided_gate_state_transport.py`
- Macro E2E updates for seam repair satisfying gates.
- Fixture-backed regression for perception-derived gate proposals that does not
  require external model calls or local segmentation/classification sidecars.

## Docs To Update

- `_docs/_TESTS/README.md`
- `_docs/_MCP_SERVER/README.md`
- `_docs/_TASKS/README.md`

## Changelog Impact

- Add a `_docs/_CHANGELOG/*` entry when the first cross-domain gate regression
  harness or transport/runtime gate-state lane ships.

## Validation Commands

- `git diff --check`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_quality_gate_verifier.py tests/unit/adapters/mcp/test_reference_images.py -v`
- `python3 scripts/run_e2e_tests.py` for the Blender-backed creature/building
  gate scenarios introduced by this task.

## Acceptance Criteria

- At least one creature E2E proves primitive-only completion is blocked.
- At least one building-style E2E proves missing/floating structural gates
  block completion.
- E2E evidence exercises real Blender scene state, not only mocked contracts.
- Future perception adapters are optional, default-off, and cannot mark gates
  passed without verifier-supported evidence.
- Docs explain the gate regression lanes and expected runtime requirements.
