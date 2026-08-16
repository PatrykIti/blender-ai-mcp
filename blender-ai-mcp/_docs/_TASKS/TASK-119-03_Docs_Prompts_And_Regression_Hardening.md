# TASK-119-03: Docs, Prompts, and Regression Hardening

**Parent:** [TASK-119](./TASK-119_Existing_Public_Surface_Hardening_After_TASK-113.md)  
**Status:** ✅ Done  
**Priority:** 🔴 High

**Completion Summary:** Public docs/prompts were aligned with the hardened guided surface and the resulting behavior is now protected by an explicit regression/benchmark pack.

---

## Objective

Finish the hardening wave by bringing user-facing docs/prompts into alignment
with the cleaned surface and protecting that state with regression coverage.

---

## Repository Touchpoints

- `README.md`
- `_docs/_MCP_SERVER/README.md`
- `_docs/AVAILABLE_TOOLS_SUMMARY.md`
- `_docs/_PROMPTS/`
- `_docs/_TESTS/README.md`
- `tests/unit/adapters/mcp/`

---

## Leaf Breakdown

| Leaf | Purpose |
|------|---------|
| [TASK-119-03-01](./TASK-119-03-01_Public_Docs_And_Prompt_Library_Closure.md) | Close remaining docs/prompt drift after the surface hardening changes |
| [TASK-119-03-02](./TASK-119-03-02_Surface_Regression_And_Benchmark_Pack.md) | Protect the hardened public surface with docs tests, visibility tests, and benchmark baselines |

---

## Acceptance Criteria

- public docs/prompts no longer teach the wrong abstraction layer
- the hardened public surface is protected by automated regression checks
