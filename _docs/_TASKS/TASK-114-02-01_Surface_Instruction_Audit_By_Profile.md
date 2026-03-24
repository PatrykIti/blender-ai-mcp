# TASK-114-02-01: Surface Instruction Audit by Profile

**Parent:** [TASK-114-02](./TASK-114-02_Surface_Prompt_And_Goal_First_Audit.md)  
**Status:** ⏳ To Do  
**Priority:** 🔴 High

---

## Objective

Audit the active `surfaces.py` instruction strings profile by profile.

---

## Exact Audit Targets

- `legacy-manual`
- `legacy-flat`
- `llm-guided`
- `internal-debug`
- `code-mode-pilot`

---

## Focus

- does the profile describe its real role?
- does it align with `TASK-113` policy?
- does it overexpose manual/low-level thinking?
- does it under-specify verification expectations?
- does it correctly state whether goal-first is required or optional?

---

## Acceptance Criteria

- each profile gets a concrete audit result and follow-up action list
