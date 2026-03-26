# TASK-120-03-02: Router and Search Bias Toward Macro Layer

**Parent:** [TASK-120-03](./TASK-120-03_Guided_Surface_Collapse_And_Discovery_Preference.md)  
**Status:** ✅ Done  
**Priority:** 🔴 High

**Completion Summary:** Discovery and router-side metadata now bias toward the macro layer before atomics. `macro_relative_layout` and `macro_finish_form` gained stronger multilingual intent metadata, `search_tools` regression coverage now proves macro-first ranking for Polish and English macro prompts, and the router intent classifier now consumes metadata descriptions plus related-tool hints so the same bias reaches classifier-driven routing.

---

## Objective

Ensure search, router recovery, and related-tool guidance prefer macro tools
before falling back to atomics.

---

## Implementation Direction

- adjust metadata and enrichment so macro tools rank well in discovery
- update `router_set_goal(...)` follow-up and recovery suggestions to prefer macro tools
- ensure `call_tool` and search-first flows still obey guided visibility
- keep macro preference deterministic and metadata-driven where possible

---

## Repository Touchpoints

- `server/router/infrastructure/tools_metadata/`
- `server/adapters/mcp/test_search_surface.py`
- `server/adapters/mcp/areas/router.py`
- `tests/unit/router/`

---

## Acceptance Criteria

- macro tools become the preferred discovered working layer on `llm-guided`
- atomic fallback remains available but no longer dominates discovery/recovery
