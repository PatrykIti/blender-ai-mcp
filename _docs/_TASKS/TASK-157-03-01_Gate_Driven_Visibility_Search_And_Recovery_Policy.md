# TASK-157-03-01: Gate-Driven Visibility, Search, And Recovery Policy

**Status:** ⏳ To Do
**Priority:** 🔴 High
**Parent:** [TASK-157-03](./TASK-157-03_Guided_Flow_Gate_Runtime_Integration.md)
**Category:** Guided Runtime / Visibility Policy
**Estimated Effort:** Medium

## Objective

Make unresolved gates open the narrow bounded tool surface needed for the next
repair, without encouraging the LLM to reset goals, guess hidden tools, or use
the broad catalog.

## Repository Touchpoints

| Path / Module | Expected Change |
|---------------|-----------------|
| `server/adapters/mcp/transforms/visibility_policy.py` | Gate-to-tool-family visibility rules |
| `server/adapters/mcp/discovery/search_surface.py` | Gate-aware search and call-path diagnostics |
| `server/adapters/mcp/discovery/search_documents.py` | Gate-oriented search documents |
| `server/router/infrastructure/tools_metadata/` | Gate family metadata and examples |
| `tests/unit/adapters/mcp/test_search_surface.py` | Search/tool exposure tests |
| `tests/unit/adapters/mcp/test_visibility_policy.py` | Gate-driven visibility tests |

## Technical Requirements

- `attachment_seam` gates expose:
  - `scene_relation_graph`
  - `macro_attach_part_to_surface`
  - `macro_align_part_with_contact`
- `support_contact` gates expose support/contact repair tools.
- `shape_profile` gates expose mesh/modeling refinement tools only after
  required seam/contact gates are not failed.
- Recovery guidance should say "verify or repair active gate" instead of
  "reset router goal".
- `router_set_goal` must not be recommended as a deadlock escape when active
  unresolved gates exist.

## Pseudocode

```python
def visibility_for_gate(gate):
    match gate.gate_type:
        case "attachment_seam":
            return {"spatial_context", "macro_attachment"}
        case "shape_profile" if prerequisites_passed(gate):
            return {"modeling_mesh", "macro_profile"}
        case "opening_or_cut":
            return {"macro_cutout", "scene_measure"}
        case _:
            return {"reference_context", "inspect_assert"}
```

## Tests To Add/Update

- Active seam gate makes attachment macros visible.
- Active shape-profile gate does not expose mesh tools while seam gates fail.
- Search for "fix floating tail gap" returns seam repair tools.
- Search for "reset goal" does not become the recommended recovery for active
  gate blockers.

## E2E Tests

- Add a guided Streamable/stdio scenario where a failed seam gate opens repair
  tools and the client can proceed without `router_set_goal` reset.

## Docs To Update

- `_docs/_MCP_SERVER/README.md`
- `_docs/_PROMPTS/README.md`
- `_docs/_ROUTER/RESPONSIBILITY_BOUNDARIES.md`

## Acceptance Criteria

- Gate blockers drive small, relevant visibility changes.
- Clients receive recovery guidance tied to gate verification/repair.
- Broad catalog exposure is not required to resolve common gate failures.
