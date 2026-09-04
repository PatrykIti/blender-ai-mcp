# TASK-094-04: Decision Memo and Documentation

**Parent:** [TASK-094](./TASK-094_Code_Mode_Exploration.md)  
**Status:** ✅ Done  
**Priority:** 🟡 Medium  
**Depends On:** [TASK-094-03](./TASK-094-03_Evaluation_Harness_and_Benchmark_Scenarios.md)

---

## Objective

Record the final recommendation on where Code Mode helps and where it should stay out of the critical path.

---

## Layered Subtasks

| ID | Title | Focus |
|----|-------|-------|
| [TASK-094-04-01](./TASK-094-04-01_Core_Decision_Memo_Documentation.md) | Core Decision Memo and Documentation | Core implementation layer |
| [TASK-094-04-02](./TASK-094-04-02_Tests_Decision_Memo_Documentation.md) | Tests and Docs Decision Memo and Documentation | Tests, docs, and QA |

---

## Acceptance Criteria

- there is one explicit product recommendation grounded in experiment results

---

## Current Recommendation

Go decision:

- keep `code-mode-pilot` as an experimental read-only surface

No-go decisions:

- do not make Code Mode the default product path
- do not use Code Mode as the primary path for geometry-destructive or write-heavy Blender operations

Evidence basis:

- `legacy-flat` remains the broad compatibility/control baseline
- `llm-guided` remains the primary production baseline
- `code-mode-pilot` materially reduces the catalog/round-trip shape for read-heavy orchestration by collapsing the visible surface to discovery meta-tools plus prompt bridge helpers
