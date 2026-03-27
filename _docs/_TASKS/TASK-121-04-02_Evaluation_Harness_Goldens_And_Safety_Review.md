# TASK-121-04-02: Evaluation Harness, Goldens, and Safety Review

**Parent:** [TASK-121-04](./TASK-121-04_Lightweight_Vision_Runtime_And_Evaluation.md)  
**Status:** 🚧 In Progress  
**Priority:** 🔴 High

**Progress Update:** The repo now has a first-pass evaluation harness path: `scripts/vision_harness.py` accepts repo-tracked `golden.json` scenarios, scores backend outputs against a reusable matrix, and synthetic golden scenarios exist for improvement, no-change, and reference-mismatch coverage. The next step is to push this beyond synthetic checks into real macro capture bundles and explicit governance verdicts.

---

## Objective

Add enough evaluation and governance for the vision-assist layer to be safely
iterated later.

---

## Implementation Direction

- build a small evaluation harness around representative scenarios:
  - visible improvement
  - visible regression
  - no meaningful change
  - mismatch against reference image
- run the harness against a model/backend matrix, not only one candidate:
  - local 3B baseline
  - local 7B baseline
  - newer local family candidate when available
  - external Gemma-comparator path
- keep goldens around:
  - capture bundles
  - expected likely-issue categories
  - expected recommended deterministic checks
- score models on product-relevant tasks, not generic VLM hype:
  - can it distinguish before vs after?
  - can it identify the dominant visible problem category?
  - can it recommend the right deterministic next checks?
  - does it avoid over-claiming geometric truth from images alone?
- review safety/governance around:
  - false confidence
  - privacy of uploaded references
  - accidental use as truth source

---

## Repository Touchpoints

- `tests/unit/adapters/mcp/`
- `tests/e2e/`
- `scripts/`
- `_docs/_VISION/`
- `_docs/_TESTS/README.md`
- `_docs/_ROUTER/RESPONSIBILITY_BOUNDARIES.md`

---

## Acceptance Criteria

- the vision layer has a real evaluation harness, not only qualitative demos
- governance risks are documented before broad rollout

## Detailed Execution Breakdown

1. Backend comparison harness
   - run the same deterministic bundle against:
     - `mlx_local`
     - `transformers_local`
     - `openai_compatible_external`
   - capture both raw and parsed outputs

2. Golden scenarios
   - minimal synthetic smoke image
   - one macro finish bundle
   - one macro layout bundle
   - one regression / no-meaningful-change bundle
   - one reference-mismatch bundle

3. Scoring dimensions
   - JSON validity
   - field completeness
   - issue usefulness
   - deterministic-check usefulness
   - tendency to hallucinate scene truth

4. Parse-repair evaluation
   - measure how often local models return:
     - valid JSON directly
     - fenced JSON
     - recoverable malformed JSON
     - unrecoverable prose

5. Governance notes
   - document which backend/model combinations are:
     - stable enough for local experiments
     - stable enough for guarded feature use
     - still smoke-test-only
