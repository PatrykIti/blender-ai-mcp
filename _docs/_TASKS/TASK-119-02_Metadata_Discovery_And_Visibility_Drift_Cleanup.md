# TASK-119-02: Metadata, Discovery, and Visibility Drift Cleanup

**Parent:** [TASK-119](./TASK-119_Existing_Public_Surface_Hardening_After_TASK-113.md)  
**Status:** ⏳ To Do  
**Priority:** 🔴 High

---

## Objective

Bring router metadata, discovery wording, and guided-surface visibility rules
into tighter alignment with the intended product model.

---

## Repository Touchpoints

- `server/router/infrastructure/tools_metadata/`
- `server/adapters/mcp/transforms/visibility_policy.py`
- `server/adapters/mcp/transforms/prompts_bridge.py`
- `server/adapters/mcp/surfaces.py`
- `tests/unit/router/infrastructure/`
- `tests/unit/adapters/mcp/test_search_surface.py`
- `tests/unit/adapters/mcp/test_visibility_policy.py`

---

## Leaf Breakdown

| Leaf | Purpose |
|------|---------|
| [TASK-119-02-01](./TASK-119-02-01_Router_Metadata_Keyword_And_Example_Normalization.md) | Normalize metadata keywords, sample prompts, and related-tool hints toward the intended abstraction layer |
| [TASK-119-02-02](./TASK-119-02-02_Guided_Visibility_And_Escape_Hatch_Cleanup.md) | Tighten guided visibility, escape hatches, and discovery bias so hidden atomics stay hidden by default |

---

## Acceptance Criteria

- metadata no longer teaches stale manual-first or flat-catalog behavior
- guided visibility and discovery behavior match the documented product surface
