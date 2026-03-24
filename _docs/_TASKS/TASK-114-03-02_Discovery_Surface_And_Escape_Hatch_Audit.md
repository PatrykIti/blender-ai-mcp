# TASK-114-03-02: Discovery Surface and Escape Hatch Audit

**Parent:** [TASK-114-03](./TASK-114-03_Metadata_Discovery_And_Public_Surface_Audit.md)  
**Status:** ⏳ To Do  
**Priority:** 🟡 Medium

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
