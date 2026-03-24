# TASK-114-01-02: Public Inventory and User-Facing Wording Audit

**Parent:** [TASK-114-01](./TASK-114-01_Public_Tool_Semantics_And_Docstring_Audit.md)  
**Status:** ✅ Done  
**Priority:** 🟡 Medium

**Completion Summary:** User-facing wording drift is now identified. The highest-signal docs still contain old “mega tools for LLM context optimization” framing and need a later rewrite wave to match the new macro/workflow-first product model.

---

## Objective

Audit user-facing summaries/tables for wording that still reflects the old architecture.

---

## Exact Audit Targets

- `README.md`
- `_docs/_MCP_SERVER/README.md`
- `_docs/AVAILABLE_TOOLS_SUMMARY.md`

---

## Focus

- “mega tool” wording that needs narrowing
- descriptions that still sound like low-level flat-catalog usage is normal
- stale notes like “preferred method” that should be re-evaluated under `TASK-113`
- places where a tool should now be described as macro/workflow/verification support instead

---

## Acceptance Criteria

- user-facing wording drift is identified separately from internal docstring drift

## Audit Result

### Highest-Signal Drift

- `README.md`
  - still contains the old `LLM Context Optimization` / `mega tools` framing
- `_docs/_MCP_SERVER/README.md`
  - still contains older mega-tool explanation blocks and “total savings” framing
- `_docs/AVAILABLE_TOOLS_SUMMARY.md`
  - still treats the grouped tools primarily as “LLM context optimization” rather than macro/workflow architecture

### Why This Matters

This wording is not just cosmetic. It reinforces the older product model:

- optimize context by collapsing tools
- think in terms of grouped wrappers

instead of the new product model:

- expose macro tools as the normal layer
- keep atomic tools mostly hidden
- use workflow tools as bounded process tools
- tie execution to verification and goal context

### Fix Priorities

- `P0`: rewrite the framing sections in `README.md`, `_docs/_MCP_SERVER/README.md`, and `_docs/AVAILABLE_TOOLS_SUMMARY.md`
- `P1`: normalize remaining “deprecated / now internal / use mega tools” wording to the new policy language
