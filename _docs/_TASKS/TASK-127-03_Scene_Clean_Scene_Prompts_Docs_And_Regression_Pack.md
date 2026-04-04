# TASK-127-03: `scene_clean_scene` Prompts, Docs, and Regression Pack

**Parent:** [TASK-127](./TASK-127_Guided_Utility_Public_Contract_Hardening_For_Scene_Clean_Scene.md)
**Status:** ⏳ To Do
**Priority:** 🟡 Medium

## Objective

Align prompts/docs/examples with the finalized cleanup contract and add focused
regression coverage so guided utility flows stop teaching one argument shape
while the runtime expects another.

## Repository Touchpoints

- `README.md`
- `_docs/_MCP_SERVER/README.md`
- `_docs/_PROMPTS/README.md`
- `tests/unit/adapters/mcp/test_public_surface_docs.py`
- `tests/unit/adapters/mcp/test_search_surface.py`

## Acceptance Criteria

- prompt/docs snippets use the canonical cleanup shape
- regression coverage protects against reintroducing the split-flag mismatch
- operators can infer the correct cleanup call without hitting a validation
  failure first

## Docs To Update

- `README.md`
- `_docs/_MCP_SERVER/README.md`
- `_docs/_PROMPTS/README.md`

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_public_surface_docs.py`
- `tests/unit/adapters/mcp/test_search_surface.py`

## Changelog Impact

- include in the parent task changelog entry when shipped
