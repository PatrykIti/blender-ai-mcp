# TASK-113-04: Macro and Workflow Tool Design Rules

**Parent:** [TASK-113](./TASK-113_Tool_Layering_Goal_First_And_Vision_Assertion_Strategy.md)  
**Status:** ✅ Done  
**Priority:** 🔴 High  
**Depends On:** TASK-113-01, TASK-113-02, TASK-113-03

---

## Objective

Define what a good macro tool is, what a good workflow/mega tool is, and how they should differ from both atomic tools and “do everything” anti-patterns.

---

## Repository Touchpoints

- `_docs/_MCP_SERVER/README.md`
- `_docs/AVAILABLE_TOOLS_SUMMARY.md`
- any existing mega-tool docs
- `README.md`

---

## Planned Work

- define macro-tool boundaries
- define workflow/mega-tool boundaries
- define required structured result/report patterns
- define when before/after capture/verification is mandatory inside a workflow tool

---

## Acceptance Criteria

- macro vs workflow distinction is explicit
- future mega-tool work stops drifting into “one giant ambiguous tool”
- structured workflow reports become part of the design rule
**Completion Summary:** The canonical policy docs now define macro tools as the preferred default LLM-facing layer, workflow/mega tools as bounded process tools, and structured workflow reporting as part of the product rule instead of an optional nice-to-have.
