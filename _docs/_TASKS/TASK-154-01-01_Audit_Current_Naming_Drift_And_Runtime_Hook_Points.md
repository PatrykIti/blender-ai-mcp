# TASK-154-01-01: Audit Current Naming Drift And Runtime Hook Points

**Parent:** [TASK-154-01](./TASK-154-01_Naming_Policy_Contract_And_Role_Based_Suggestion_Vocabulary.md)
**Status:** ⏳ To Do
**Priority:** 🔴 High

## Objective

Map where the repo currently relies on prompt guidance, role enforcement, and
heuristic fallback for object naming, and identify the narrow runtime hook
points for a deterministic guided naming policy.

## Repository Touchpoints

- `server/adapters/mcp/surfaces.py`
- `_docs/_PROMPTS/GUIDED_SESSION_START.md`
- `_docs/_PROMPTS/REFERENCE_GUIDED_CREATURE_BUILD.md`
- `_docs/_PROMPTS/WORKFLOW_ROUTER_FIRST.md`
- `server/adapters/mcp/router_helper.py`
- `server/adapters/mcp/areas/router.py`
- `server/adapters/mcp/areas/modeling.py`
- `server/adapters/mcp/session_capabilities.py`
- `server/application/services/spatial_graph.py`
- `server/adapters/mcp/areas/reference.py`

## Current Code Anchors

- prompt/runtime guidance:
  - `surfaces.py`
  - prompt docs under `_docs/_PROMPTS/`
- semantic role enforcement:
  - `router_helper.py`
  - `areas/router.py`
  - `areas/modeling.py`
- heuristic recovery:
  - `spatial_graph.py`
  - `areas/reference.py`

## Planned Audit Output

- classify current behavior as:
  - prompt-only guidance
  - deterministic role/family enforcement
  - heuristic naming recovery
- identify one canonical naming-policy hook set:
  - `guided_register_part(...)`
  - role-sensitive build calls with `guided_role=...`
- explicitly reject false hook points such as:
  - public tool naming transforms
  - scene-wide global renaming rules unrelated to guided flow context

## Pseudocode Sketch

```python
hook_points = [
    "guided_register_part",
    "modeling_create_primitive(guided_role=...)",
    "modeling_transform_object(guided_role=...)",
]

for hook in hook_points:
    audit_rows.append(
        {
            "hook": hook,
            "has_role_context": True,
            "can_warn": True,
            "can_block": True,
            "needs_policy_module": True,
        }
    )
```

## Acceptance Criteria

- the audit makes it explicit where naming policy belongs and where it does not

## Docs To Update

- none directly

## Tests To Add/Update

- none directly

## Changelog Impact

- include in the parent TASK-154 changelog entry
