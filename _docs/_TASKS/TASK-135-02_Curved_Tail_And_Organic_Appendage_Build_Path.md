# TASK-135-02: Curved Tail And Organic Appendage Build Path

**Status:** ⏳ To Do
**Priority:** 🔴 High
**Parent:** [TASK-135](./TASK-135_Anatomy_Aware_Reference_Guided_Low_Poly_Creature_Reconstruction.md)
**Category:** Reconstruction / Guided Creature Tooling
**Estimated Effort:** Medium
**Depends On:** [TASK-157](./TASK-157_Goal_Derived_Quality_Gates_And_Deterministic_Verification.md)

## Objective

Make reference-guided creature sessions able to build a recognizable curved or
arched tail instead of defaulting to one vertical oval primitive.

The repo already has `macro_adjust_segment_chain_arc(...)`, but that macro only
repositions an existing ordered segment chain. The guided creature flow still
needs a policy and build path that creates an appropriate tail chain in the
first place, seats the root into the body, and then arcs the ordered segments.

## Business Problem

For animals such as squirrels, a tail is one of the main silhouette anchors.
The latest blockout produced a tail that is recognizable as "large rear oval",
but not as a shaped bushy squirrel tail:

- the tail was one detached-looking primitive
- it did not bend or wrap along the reference silhouette
- it lacked a root/mid/tip structure that a low-poly model can still express
- the flow did not naturally choose the existing segment-chain arc macro

This keeps the result below the expected low-poly bar even when the broad
front/side reference proportions are partially followed.

## Repository Touchpoints

| Path / Module | Expected Change |
|---------------|-----------------|
| `server/adapters/mcp/areas/scene.py` | Keep `macro_adjust_segment_chain_arc(...)` visible/recommended for appendage-chain gates |
| `server/application/tool_handlers/macro_handler.py` | Extend only if a new `macro_build_curved_tail_chain` becomes necessary |
| `server/adapters/mcp/session_capabilities.py` | Represent tail chain/profile gates in guided state |
| `server/adapters/mcp/discovery/search_documents.py` | Add search cues for curved/bushy/arched appendage chains |
| `server/router/infrastructure/tools_metadata/` | Add metadata linking tail profile gates to arc and attachment macros |
| `server/adapters/mcp/prompts/` | Teach multi-segment tail creation before arc adjustment |
| `tests/unit/tools/macro/test_macro_adjust_segment_chain_arc.py` | Add appendage-chain arc cases |
| `tests/unit/tools/scene/test_macro_adjust_segment_chain_arc_mcp.py` | Add MCP structured contract cases |
| `tests/e2e/tools/macro/test_macro_adjust_segment_chain_arc.py` | Add Blender-backed tail-chain arc case |
| `tests/e2e/vision/` | Add squirrel-tail profile gate scenario |
| `_docs/_PROMPTS/REFERENCE_GUIDED_CREATURE_BUILD.md` | Document tail chain and arc gate flow |
| `_docs/_MCP_SERVER/README.md` | Document appendage-chain use of existing macro |

## Implementation Notes

- Keep `macro_adjust_segment_chain_arc(...)` as the first reusable primitive for
  ordered appendage arcs.
- Add a guided creature build policy that prefers a multi-segment tail for
  reference cues such as:
  - bushy tail
  - curved tail
  - arched tail
  - tail wrapping up behind the body
- Define the expected segment vocabulary, for example:
  - `TailRoot`
  - `TailMid`
  - `TailTip`
  - or `Tail_01`, `Tail_02`, `Tail_03`, `Tail_04`
- Seat the tail root to the body with a creature seam macro before or after the
  arc operation.
- Consider adding a new bounded macro only if prompt/search policy is not
  enough:
  - `macro_build_curved_tail_chain`
  - input: root object/body, segment count, arc plane, total angle, taper
  - output: created segment names, root seam verdict, arc verification hints
- Keep the first version low-poly and object-based; do not require rigging,
  sculpt, or a heavy curve system for the baseline.
- Model this as a generic `shape_profile` gate:
  - `profile_kind="curved_appendage_chain"`
  - `required_segments >= 3` for squirrel-like bushy tails unless waived
  - `root_attachment_gate` points to `TailRoot -> Body`
  - `repair_family=["macro_attach_part_to_surface", "macro_adjust_segment_chain_arc"]`

## Pseudocode

```python
if creature_profile.tail_shape in {"curved", "bushy", "arched"}:
    if not tail_segments_exist:
        create_tail_segments(names=["TailRoot", "TailMid", "TailTip"])
        register_roles(role="tail_mass", role_group="tail_chain")

    macro_attach_part_to_surface(
        part_object="TailRoot",
        surface_object="Body",
        surface_axis="X",
        surface_side="negative",
    )

    macro_adjust_segment_chain_arc(
        segment_objects=["TailRoot", "TailMid", "TailTip"],
        rotation_axis="Y",
        total_angle=80,
    )
```

## Tests To Add/Update

| Layer | Tests |
|-------|-------|
| Unit gate template | Curved squirrel tail emits `shape_profile=curved_appendage_chain` |
| Unit search | Curved/bushy/arched tail queries rank `macro_adjust_segment_chain_arc` |
| Unit macro | Existing arc macro handles three or more tail-like segments |
| Unit MCP contract | Arc macro returns structured verification recommendations |
| E2E macro | TailRoot/TailMid/TailTip arc while TailRoot remains attached to Body |
| E2E vision | One detached vertical oval tail fails the curved-tail profile gate |

## Docs To Update

- `_docs/_PROMPTS/REFERENCE_GUIDED_CREATURE_BUILD.md`
- `_docs/_MCP_SERVER/README.md`
- `_docs/AVAILABLE_TOOLS_SUMMARY.md`
- `_docs/_TESTS/README.md`

## Changelog Impact

- Add a `_docs/_CHANGELOG/*` entry when the tail-chain path ships.

## Acceptance Criteria

- The guided creature flow can represent a curved tail as an ordered chain of
  low-poly parts.
- `macro_adjust_segment_chain_arc(...)` is discoverable and recommended for
  ordered appendage arc repair.
- A squirrel-like tail can be seated to the body and arced without broad
  free-form transform guessing.
- The result keeps separate low-poly parts while still visually reading as one
  attached organic appendage.
