# TASK-114-01: Public Tool Semantics and Docstring Audit

**Parent:** [TASK-114](./TASK-114_Existing_Tool_Surface_Audit_And_Alignment.md)  
**Status:** ✅ Done  
**Priority:** 🔴 High

**Completion Summary:** The first public-tool semantics audit is complete. The repo now has an explicit record of where current tool wording still reflects the old “mega-tool/flat-catalog/LLM-context-optimization” model instead of the newer `atomic / macro / workflow` and truth/verification model from `TASK-113`.

---

## Objective

Audit the actual MCP-facing tool descriptions and semantics for drift against the new layered product model.

---

## Repository Touchpoints

- `server/adapters/mcp/areas/*.py`
- `_docs/_MCP_SERVER/README.md`
- `_docs/AVAILABLE_TOOLS_SUMMARY.md`
- `README.md`

---

## Planned Work

- identify tool docstrings that still imply the old flat-catalog mindset
- identify tools described as more autonomous/open-ended than they should be
- identify tools whose wording should move toward:
  - atomic helper
  - macro tool
  - workflow tool
  - verification/measure/assert support

---

## Acceptance Criteria

- the repo has a concrete list of MCP-facing tool semantics that need rewriting
- the audit distinguishes wording drift from actual missing capability

## Audit Findings

### P0 Drift Areas

- public docs still frame core grouped tools primarily as “mega tools for LLM context optimization”
- that wording is still visible in:
  - `README.md`
  - `_docs/_MCP_SERVER/README.md`
  - `_docs/AVAILABLE_TOOLS_SUMMARY.md`
- this is the old rationale and should be rewritten toward:
  - macro tools as the default LLM-facing layer
  - workflow tools as bounded process tools
  - hidden atomic layer as normal infrastructure

### P1 Drift Areas

- several MCP docstrings still use legacy phrasing like:
  - “Preferred method”
  - “ALT TO”
  - generic “mega tool” wording
- these phrases are not always wrong, but many of them predate the new layered product model and need re-evaluation

### P1 Truth/Verification Drift

- some descriptions still imply tool choice or visual intuition without enough explicit verification discipline
- examples:
  - old “preferred method” modeling language
  - remaining public references that do not clearly distinguish execution policy vs truth layer

### Next Action

- rewrite the highest-signal user-facing tool wording first
- then re-audit MCP area docstrings capability by capability
