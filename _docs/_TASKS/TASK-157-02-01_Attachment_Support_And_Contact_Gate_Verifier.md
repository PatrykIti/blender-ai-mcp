# TASK-157-02-01: Attachment, Support, And Contact Gate Verifier

**Status:** ✅ Done
**Priority:** 🔴 High
**Parent:** [TASK-157-02](./TASK-157-02_Deterministic_Gate_Verifier_And_Status_Model.md)
**Category:** Guided Runtime / Spatial Gate Verification
**Estimated Effort:** Medium

## Objective

Implement the first deterministic verifier for `attachment_seam` and
`support_contact` gates using existing spatial relation graph evidence.

## Completion Summary

Completed on 2026-05-01.

- Implemented `attachment_seam` and `support_contact` evaluation from
  `SceneRelationGraphPayloadContract` pairs.
- `floating_gap`, non-embedded `intersecting`, unsupported support, and
  relation errors now produce machine-readable `failed` or `blocked` states.
- `seated_contact` and `supported` relation verdicts pass only with
  authoritative spatial relation evidence refs.
- Embedded/organic intersections pass only when the normalized gate policy sets
  `allow_embedded_intersection=true`.
- Repair hints reuse existing bounded tools such as
  `scene_relation_graph`, `scene_measure_gap`, `scene_assert_contact`,
  `macro_attach_part_to_surface`, `macro_align_part_with_contact`, and
  `macro_place_supported_pair`.

Blender-backed creature/building regression coverage remains under
[TASK-157-04](./TASK-157-04_Cross_Domain_E2E_Gate_Regression_Harness.md) so the
first verifier slice does not create an isolated E2E flow.

## Validation

- `git diff --check`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_quality_gate_contracts.py tests/unit/adapters/mcp/test_quality_gate_verifier.py tests/unit/adapters/mcp/test_quality_gate_intake.py -v`
- `PYTHONPATH=. poetry run pytest tests/unit/tools/scene/test_spatial_graph_service.py tests/unit/tools/scene/test_scene_contracts.py tests/unit/adapters/mcp/test_quality_gate_verifier.py -v`
- `PRE_COMMIT_HOME=/tmp/pre-commit-cache poetry run pre-commit run --files README.md _docs/AVAILABLE_TOOLS_SUMMARY.md _docs/_CHANGELOG/README.md _docs/_CHANGELOG/280-2026-05-01-task-157-deterministic-gate-verifier.md _docs/_MCP_SERVER/README.md _docs/_PROMPTS/README.md _docs/_PROMPTS/REFERENCE_GUIDED_CREATURE_BUILD.md _docs/_ROUTER/RESPONSIBILITY_BOUNDARIES.md _docs/_TASKS/README.md _docs/_TASKS/TASK-157-02-01_Attachment_Support_And_Contact_Gate_Verifier.md _docs/_TASKS/TASK-157-02_Deterministic_Gate_Verifier_And_Status_Model.md _docs/_TASKS/TASK-157_Goal_Derived_Quality_Gates_And_Deterministic_Verification.md _docs/_TESTS/README.md server/adapters/mcp/areas/scene.py server/adapters/mcp/contracts/__init__.py server/adapters/mcp/contracts/quality_gates.py server/adapters/mcp/session_capabilities.py server/adapters/mcp/transforms/quality_gate_verifier.py tests/unit/adapters/mcp/test_quality_gate_intake.py tests/unit/adapters/mcp/test_quality_gate_verifier.py`

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
- Embedded/organic-rooted gates must read pair-level relation semantics
  directly instead of relying on aggregated `failing_pairs` or truth-followup
  repair candidates. Current spatial summaries can classify `intersecting`
  pairs as failing by default; the gate verifier must apply the normalized gate
  policy before deciding whether an intersecting relation passes or fails.

## Runtime / Security Contract Notes

- Visibility level: the first seam/contact verifier should report through
  existing guided/reference checkpoint outputs and may recommend existing
  repair tools; it should not expose a new mutating MCP surface.
- Read-only vs mutating behavior: relation-graph evidence collection is
  read-only. Macro hints such as `macro_attach_part_to_surface` are
  recommendations only until the client explicitly calls the mutating tool.
- Verification boundary: cleanup or repair macros never mark a gate passed by
  themselves; the verifier must re-read relation graph truth after the mutation.
- Transport assumptions: Streamable HTTP and stdio behavior must preserve the
  same session-scoped gate ids, evidence refs, and stale markers.
- Side-effect limits: E2E repair flows may mutate Blender through existing macro
  tools only, and must keep mode/selection recovery behavior aligned with those
  tools' current contracts.

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
- Embedded/organic `intersecting` passes when the normalized gate policy allows
  it, even if the broader spatial summary lists the pair as failing.
- Non-embedded `intersecting` fails and produces a bounded repair hint.
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

## Changelog Impact

- Add a `_docs/_CHANGELOG/*` entry when the first seam/contact verifier or its
  macro repair evidence integration ships.

## Validation Commands

- `git diff --check`
- `PYTHONPATH=. poetry run pytest tests/unit/tools/scene/test_scene_contracts.py tests/unit/tools/macro/test_macro_attach_part_to_surface.py -v`
- `python3 scripts/run_e2e_tests.py` for the Blender-backed seam/contact repair
  scenarios introduced by this slice.

## Acceptance Criteria

- Required seam/contact gates use relation graph truth.
- Floating gaps cannot be rationalized as complete.
- Organic embedded seams are handled explicitly through gate policy.
- Macro follow-up hints point to bounded repair tools.
