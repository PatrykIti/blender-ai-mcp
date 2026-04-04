# TASK-127-01: `scene_clean_scene` Public Contract and Compatibility Policy

**Parent:** [TASK-127](./TASK-127_Guided_Utility_Public_Contract_Hardening_For_Scene_Clean_Scene.md)
**Status:** ⏳ To Do
**Priority:** 🔴 High

## Objective

Define one explicit public contract for `scene_clean_scene(...)` on
`llm-guided`, including the policy for the older `keep_lights` /
`keep_cameras` split flags.

## Repository Touchpoints

- `server/adapters/mcp/areas/scene.py`
- `server/router/infrastructure/tools_metadata/scene/scene_clean_scene.json`
- `_docs/_MCP_SERVER/README.md`
- `_docs/_PROMPTS/README.md`

## Acceptance Criteria

- the canonical public argument shape is documented explicitly
- the compatibility policy for old split flags is written down clearly
- later implementation leaves have one unambiguous target behavior

## Docs To Update

- `_docs/_MCP_SERVER/README.md`
- `_docs/_PROMPTS/README.md`

## Tests To Add/Update

- docs/contract coverage as needed

## Changelog Impact

- include in the parent task changelog entry when shipped
