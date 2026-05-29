# TASK-180-02: Stable Mark Identifiers Across Views And Iterations

**Parent:** [TASK-180](./TASK-180_Set_Of_Mark_Object_Bound_Visual_Marks.md)
**Status:** ⏳ To Do
**Priority:** 🔴 High
**Follow-on After:** [TASK-180-01](./TASK-180-01_Object_ID_Driven_Numbered_Mark_Overlay_Render.md)
**Objective:** Assign each mark ID from the part registry so that the same registered part keeps the same number across every captured view in a bundle and across every iterate cycle for the same session target, enabling cross-view and cross-iteration correspondence without re-deriving IDs from per-image geometry.

**Repository Touchpoints:** `server/adapters/mcp/vision/capture_runtime.py`, `server/adapters/mcp/areas/reference_compare_packets.py`, `server/adapters/mcp/session_capabilities_registry.py`, `server/adapters/mcp/contracts/vision.py`, `tests/unit/adapters/mcp/test_reference_compare_packets.py`, `tests/e2e/vision/test_reference_guided_creature_comparison.py`

**Acceptance Criteria:**
- mark IDs are derived from the part registry / assembled-target-scope object set, not from per-image detection order, so the assignment is stable for a given registered object set.
- the same `object_name` resolves to the same mark number in `target_front`, `target_side`, `target_top`, and oblique overlay captures within one bundle.
- the same `object_name` keeps its mark number across consecutive iterate cycles for one session target; adding a new part appends a new ID without renumbering existing parts; renaming a part preserves its ID via the registry rename path.
- the mark-id map is carried on the compare packet so the parser (TASK-180-04) can validate cited marks against the exact map that produced the captured overlay.

## Implementation Notes

- The stable-ID requirement is the GPT4Scene (arXiv:2501.01428) cross-view ID
  property: the same object must carry the same visual ID across viewpoints so a
  model can reason about it consistently across frames. SAM2 (arXiv:2408.00714)
  is the upstream analogue for stable object identity across a sequence; here the
  "sequence" is the multi-view bundle plus the iterate-cycle history, and the
  identity source is the deterministic part registry rather than a tracker.
- The part registry is the authority. `session_capabilities_registry.py` already
  carries per-object entries keyed by `object_name` (e.g.
  `item.get("object_name")` ~:241/303/359, with a rename path that preserves the
  entry when `updated_item.get("object_name") == normalized_old_name`). Mark IDs
  must be assigned from a stable ordering over this registry (and/or
  `assembled_target_scope.object_names` from `SceneAssembledTargetScopeContract`)
  so that a given object always maps to the same integer.
- `reference_compare_packets.py` already builds stable packet ids
  (`_stable_packet_id` via a sha1 of normalized parts ~:181-184) and resolves
  query labels per packet; extend the same module to attach a per-packet
  `mark_id_map` (object_name -> mark_id, plus role when known from
  `assembled_target_scope.object_roles`). Reuse the existing normalization
  helpers so IDs are computed once and threaded, not recomputed per view.
- `capture_runtime.py` must accept the resolved mark-id map and apply it when
  emitting overlay captures (TASK-180-01), instead of numbering parts in
  isolation order. This is the seam that makes the same part keep its number
  across `target_front`/`target_side`/`target_top` in one
  `capture_stage_images(...)` run.
- Iteration stability: persist the mark-id assignment alongside the session
  target so the next iterate cycle reuses it. Append-on-new, preserve-on-rename;
  never renumber existing parts, because a renumber would silently invalidate the
  orchestrator's memory of "mark 3".
- Keep the assignment deterministic and bounded: cap the mark set to the
  registered object count for the active scope so a huge scene cannot explode the
  overlay or the packet payload.

## Pseudocode

```python
def resolve_mark_id_map(part_registry, assembled_scope, prior_map):
    # prior_map: persisted {object_name: mark_id} from earlier iterate cycles
    ordered_names = stable_object_order(part_registry, assembled_scope)
    mark_map = dict(prior_map)  # preserve existing assignments
    next_id = (max(mark_map.values(), default=0) + 1)
    for object_name in ordered_names:
        if object_name in mark_map:
            continue  # stable across iterations and views
        mark_map[object_name] = next_id
        next_id += 1
    # renames already preserved by registry rename path -> same entry, same id
    return mark_map  # object_name -> stable int
```

## Runtime / Security Contract Notes

- mark IDs are deterministic registry-derived identifiers, not vision output;
  the VLM never assigns or reorders them.
- the assignment carries no scene-truth authority: it only labels which object a
  later finding refers to, and that finding still needs deterministic
  verification before any edit.
- the per-packet `mark_id_map` is the single source the validity-retry guard
  (TASK-180-04) checks against, so it must be the exact map used to render the
  overlay; do not let the parser re-derive IDs independently.
- no coordinates are emitted by this slice; IDs are symbolic and stable.

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_reference_compare_packets.py` (same object -> same mark id across multi-view packets; append-on-new; preserve-on-rename; bounded to registered object count)
- `tests/e2e/vision/test_reference_guided_creature_comparison.py` (same part keeps its mark number across iterate cycles for one creature target)

## Docs To Update

- `_docs/_VISION/README.md`
- `_docs/_VISION/REFERENCE_UNDERSTANDING_ROADMAP.md`

## Changelog Impact

- add/update the historical `_docs/_CHANGELOG/*` entry when this slice lands

## Status / Board Update

- board tracking remains on umbrella `TASK-180`
- no separate promoted board-row change is expected for this subtask

## Validation Commands

- `git diff --check`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_reference_compare_packets.py -q`
- `PYTHONPATH=. poetry run pytest ./tests/unit`
- `poetry run python scripts/run_e2e_tests.py`  # when overlay/iterate Blender behavior changes

## Validation Category

- stable-identifier and cross-view/cross-iteration correspondence proof
