# TASK-157-02-01: Attachment, Support, And Contact Gate Verifier

**Status:** ⏳ To Do
**Priority:** 🔴 High
**Parent:** [TASK-157-02](./TASK-157-02_Deterministic_Gate_Verifier_And_Status_Model.md)
**Category:** Guided Runtime / Spatial Gate Verification
**Estimated Effort:** Medium

## Objective

Implement the first deterministic verifier for `attachment_seam` and
`support_contact` gates using existing spatial relation graph evidence.

## Repository Touchpoints

| Path / Module | Expected Change |
|---------------|-----------------|
| `server/application/services/spatial_graph.py` | Map relation graph verdicts into gate evidence |
| `server/adapters/mcp/areas/scene.py` | Reuse `scene_relation_graph` and macro follow-up hints |
| `server/adapters/mcp/contracts/quality_gates.py` | Add seam/contact evidence contract |
| `tests/unit/tools/scene/test_scene_contracts.py` | Gate evidence mapping tests |
| `tests/unit/tools/macro/test_macro_attach_part_to_surface.py` | Verify macro follow-up can satisfy gate evidence |
| `tests/e2e/tools/macro/test_macro_attach_part_to_surface.py` | Blender-backed seam pass/fail cases |

## Technical Requirements

- `floating_gap` fails required attachment/support gates.
- `seated_contact` passes required attachment/support gates.
- `intersecting` may pass only when gate policy marks the seam as embedded or
  organic-rooted.
- `misaligned_attachment` fails unless the gate explicitly allows current
  alignment drift.
- Cleanup of overlap cannot pass a gate unless the final relation verdict also
  satisfies the gate.

## Pseudocode

```python
def verify_attachment_gate(gate, relation_pair):
    verdict = relation_pair.attachment_semantics.attachment_verdict

    if verdict == "seated_contact":
        return passed(evidence=relation_pair)

    if verdict == "intersecting" and gate.allows_embedded_attachment:
        return passed(evidence=relation_pair, note="embedded attachment")

    if verdict == "floating_gap":
        return failed(
            evidence=relation_pair,
            correction_hint="macro_attach_part_to_surface",
        )

    return failed(evidence=relation_pair)
```

## Tests To Add/Update

- `floating_gap` on tail/body fails.
- `seated_contact` on tail/body passes.
- `intersecting` on snout/head passes only when embedded seam is allowed.
- `intersecting` on limb/body fails when gate requires seated contact.
- `macro_cleanup_part_intersections` result does not pass the gate unless
  relation graph re-check reports a passing verdict.

## E2E Tests

- Blender-backed tail/body gap repaired by `macro_attach_part_to_surface` or
  `macro_align_part_with_contact`, then verifier passes.
- Blender-backed cleanup-only scenario remains failed when residual floating
  gap persists.

## Docs To Update

- `_docs/_MCP_SERVER/README.md`
- `_docs/AVAILABLE_TOOLS_SUMMARY.md`
- `_docs/_TESTS/README.md`

## Acceptance Criteria

- Required seam/contact gates use relation graph truth.
- Floating gaps cannot be rationalized as complete.
- Organic embedded seams are handled explicitly through gate policy.
- Macro follow-up hints point to bounded repair tools.
