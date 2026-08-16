# 216. Creature attachment seam coverage for guided assembled models

Date: 2026-04-07

## Summary

Closed TASK-142 by extending the guided assembled-creature truth/correction
path from narrow anchor-only checks to one deterministic required seam set with
structured attachment semantics, bounded macro-family selection, and
Blender-backed multi-pair E2E proof.

## What Changed

- added explicit `attachment_semantics` / `attachment_verdict` contract fields
  on scene truth pairs, including required seam metadata and preferred bounded
  macro family
- extended assembled creature scope expansion from `primary_to_others` into
  deterministic `required_creature_seams` for supported face/head,
  nose/snout, head/body, tail/body, limb/body, and limb-segment relations
- updated truth-followup and ranked correction-candidate generation so
  multiple failing required creature seams stay visible together instead of
  disappearing once one local pair improves
- aligned bounded macro guidance with seam semantics:
  `macro_attach_part_to_surface` for embedded seams such as snout/head or
  nose/snout, `macro_align_part_with_contact` for head/body, tail/body, and
  limb seating, and generic cleanup only for non-attachment overlap cases
- expanded macro, MCP-delivery, scene-contract, and reference-stage unit
  regressions around attachment verdicts and multi-pair seam planning
- added a Blender-backed assembled-creature E2E pack that proves simultaneous
  face/head, torso/body, and limb seam coverage on the guided truth path
- updated operator-facing vision/MCP/prompt docs plus TASK-142 admin docs to
  use the same required-seam and attachment-verdict vocabulary

## Why

The real guided squirrel run was still passing locally repaired pairs while the
assembled creature remained globally detached. The product needed one bounded,
deterministic way to surface and prioritize the whole required seam set, not
another ad hoc pair-specific attachment patch.

## Validation

- `poetry run pytest tests/unit/adapters/mcp/test_reference_images.py tests/unit/adapters/mcp/test_structured_contract_delivery.py tests/unit/tools/scene/test_scene_contracts.py tests/unit/tools/macro/test_macro_attach_part_to_surface.py tests/unit/tools/macro/test_macro_align_part_with_contact.py tests/unit/tools/macro/test_macro_cleanup_part_intersections.py tests/unit/tools/scene/test_macro_attach_part_to_surface_mcp.py tests/unit/tools/scene/test_macro_align_part_with_contact_mcp.py tests/unit/tools/scene/test_macro_cleanup_part_intersections_mcp.py -q`
- `poetry run pytest tests/unit/adapters/mcp/test_public_surface_docs.py -q`
- `poetry run mypy server/adapters/mcp/areas/reference.py server/adapters/mcp/contracts/scene.py`
- `poetry run pytest tests/e2e/vision/test_reference_stage_assembled_creature_attachment_truth.py tests/e2e/vision/test_reference_stage_truth_handoff.py`
