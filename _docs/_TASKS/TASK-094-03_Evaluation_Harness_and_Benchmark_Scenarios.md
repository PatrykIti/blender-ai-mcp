# TASK-094-03: Evaluation Harness and Benchmark Scenarios

**Parent:** [TASK-094](./TASK-094_Code_Mode_Exploration.md)  
**Status:** ⬜ Planned  
**Priority:** 🟡 Medium  
**Depends On:** [TASK-094-02](./TASK-094-02_Read_Only_Code_Mode_Pilot_Surface.md)

---

## Objective

Benchmark Code Mode against realistic read-heavy orchestration scenarios on explicit named baselines:

- `legacy-flat`
- `llm-guided`
- `code-mode-pilot`

If TASK-084 search-first discovery is already available, include it as an optional secondary comparison.
It is not a prerequisite for the primary Code Mode evaluation path.

---

## Layered Subtasks

| ID | Title | Focus |
|----|-------|-------|
| [TASK-094-03-01](./TASK-094-03-01_Core_Evaluation_Harness_Benchmark_Scenarios.md) | Core Evaluation Harness and Benchmark Scenarios | Core implementation layer |
| [TASK-094-03-02](./TASK-094-03-02_Tests_Evaluation_Harness_Benchmark_Scenarios.md) | Tests and Docs Evaluation Harness and Benchmark Scenarios | Tests, docs, and QA |

---

## Acceptance Criteria

- the repo has a measurable comparison for context cost and workflow quality across `legacy-flat`, `llm-guided`, and `code-mode-pilot`
