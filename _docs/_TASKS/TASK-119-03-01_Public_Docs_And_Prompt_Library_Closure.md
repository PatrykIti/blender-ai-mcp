# TASK-119-03-01: Public Docs and Prompt Library Closure

**Parent:** [TASK-119-03](./TASK-119-03_Docs_Prompts_And_Regression_Hardening.md)  
**Status:** ✅ Done  
**Priority:** 🔴 High

**Completion Summary:** Public docs and prompt assets were aligned with the hardened guided surface, including alias updates, narrower escape-hatch guidance, and removal of stale internal-path recommendations from workflow-first prompts.

---

## Objective

Finish the user-facing closure of the hardening wave across docs, prompts, and
surface instructions.

---

## Implementation Direction

- align `README.md`, `_docs/_MCP_SERVER/README.md`, and
  `_docs/AVAILABLE_TOOLS_SUMMARY.md` to the same surface story
- align `_docs/_PROMPTS` examples with:
  - grouped tools
  - explicit goal-first flow
  - verification-aware follow-up
- remove wording that still treats broad low-level access as the preferred
  production model

---

## Repository Touchpoints

- `README.md`
- `_docs/_MCP_SERVER/README.md`
- `_docs/AVAILABLE_TOOLS_SUMMARY.md`
- `_docs/_PROMPTS/*.md`
- `tests/unit/adapters/mcp/test_public_surface_docs.py`

---

## Acceptance Criteria

- docs and prompts tell the same public-surface story as the code
- high-signal examples prefer the intended public abstraction layer
