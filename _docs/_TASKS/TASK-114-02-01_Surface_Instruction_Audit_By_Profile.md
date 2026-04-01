# TASK-114-02-01: Surface Instruction Audit by Profile

**Parent:** [TASK-114-02](./TASK-114-02_Surface_Prompt_And_Goal_First_Audit.md)  
**Status:** ✅ Done  
**Priority:** 🔴 High

**Completion Summary:** The active profile instructions were reviewed against `TASK-113`. The main production gap is no longer architectural confusion, but remaining wording polish around macro/workflow-first behavior and exception surfaces.

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

## Audit Result

- `legacy-manual`
  - acceptable as a manual/maintainer exception surface
  - later wording cleanup should reduce any implication that this is a normal product path

- `legacy-flat`
  - acceptable as compatibility/control
  - later wording cleanup should keep it clearly outside the preferred production path

- `llm-guided`
  - now aligned with goal-first
  - later wording cleanup should strengthen macro/workflow-first semantics

- `internal-debug`
  - aligned as maintainer/debug

- `code-mode-pilot`
  - aligned as experimental/read-only
