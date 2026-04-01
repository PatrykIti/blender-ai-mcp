# TASK-114-03-02: Discovery Surface and Escape Hatch Audit

**Parent:** [TASK-114-03](./TASK-114-03_Metadata_Discovery_And_Public_Surface_Audit.md)  
**Status:** ✅ Done  
**Priority:** 🟡 Medium

**Completion Summary:** Discovery/public-surface wording drift is now identified. The technical shaping is mostly right; the main issue is that docs still over-normalize broad grouped catalogs instead of explicitly reinforcing the hidden atomic + explicit escape-hatch model.

---

## Objective

Audit whether discovery/search/public examples still over-normalize broad catalogs and low-level choices.

---

## Exact Audit Targets

- `_docs/_MCP_SERVER/README.md`
- `_docs/AVAILABLE_TOOLS_SUMMARY.md`
- search/discovery-related unit-test expectations where wording matters

---

## Focus

- hidden atomic leakage in docs/examples
- weakly defined escape-hatch usage
- old “everything is a normal public candidate” mindset

---

## Acceptance Criteria

- discovery/public-surface wording drift is explicitly documented before further surface-fix waves

## Audit Result

### Key Drift

- `README.md`
- `_docs/_MCP_SERVER/README.md`
- `_docs/AVAILABLE_TOOLS_SUMMARY.md`

still contain older discovery-friendly framing such as:

- “mega tools for LLM context optimization”
- “total savings” language
- “deprecated (now internal, use mega tools)” blocks

These are not wrong historically, but they no longer match the new product
story as well as:

- hidden atomic layer
- macro/workflow-first public surface
- explicit public escape hatches

### Priority

- `P0`: rewrite the framing sections
- `P1`: normalize remaining “deprecated/internal/mega tool” wording
