# TASK-177-01: Decouple Capture From Transmission And Budget-Aware Selection

**Parent:** [TASK-177](./TASK-177_Reachable_Rich_Multi_View_Capture_And_Top_View_Default.md)
**Status:** ✅ Done
**Completed:** 2026-05-30
**Priority:** 🟡 Medium
**Follow-on After:** [TASK-172](./TASK-172_Optional_Vision_Capability_Runtime_And_Localized_Perception.md), [TASK-166-05](./TASK-166-05_Configurable_Vision_Assist_Budgets_And_Runtime_Overrides.md)
**Objective:** Separate which views are CAPTURED from which are TRANSMITTED so a richer capture set can be produced deterministically and the best-N selected within the effective image budget, instead of the capture profile being blocked outright by the preset-gate arithmetic in `choose_capture_preset_profile`. Capture richer, transmit bounded.
**Repository Touchpoints:** `server/adapters/mcp/vision/policy.py`, `server/adapters/mcp/vision/runner.py`, `server/adapters/mcp/vision/capture_runtime.py`, `server/adapters/mcp/vision/config.py`, `server/infrastructure/config.py`, `tests/unit/adapters/mcp/test_vision_policy.py`, `tests/unit/adapters/mcp/test_vision_runtime_config.py`, `tests/unit/adapters/mcp/test_vision_capture_runtime.py`, `tests/unit/adapters/mcp/test_reference_images.py`
**Acceptance Criteria:**
- the capture path can produce a richer candidate view-set even when
  `choose_capture_preset_profile(...)` would currently return `"compact"` under
  default `max_images`, because capture is no longer gated by the
  transmit-budget arithmetic
- a deterministic budget-aware selection step picks the best-N candidate captures
  so the transmitted count stays `<= runtime.effective_max_images` and the runner
  never rejects the bundle with `rejection_reason="image_budget_exceeded"`
  (`runner.py:170-179`)
- when only after-captures ship (stage-checkpoint path), selection thresholds
  against a single-stage budget of 8 rather than the doubled `8 * 2`
  rich-bundle arithmetic in `choose_capture_preset_profile` (`policy.py:20`)
- selection is deterministic, order-stable, and always retains the
  highest-value views (context wide plus the orthographic top and, when budget
  allows, an oblique), and the selection rationale is recorded per capture
- no fail-safe cap is raised: `VISION_FAIL_SAFE_MAX_IMAGES = 12`
  (`config.py:28`) and `effective_max_images` (`config.py:132-136`) are unchanged

## Implementation Notes

- Root cause is that `choose_capture_preset_profile`
  (`server/adapters/mcp/vision/policy.py:13-25`) conflates two decisions:
  *how many views to capture* and *how many to transmit*. It returns `"rich"`
  only when `max_images >= 8 * 2 + max(1, reference_image_count)` (i.e. >= 16 +
  refs), but `VISION_MAX_IMAGES` defaults to `8`
  (`server/infrastructure/config.py:59`) / runtime `max_images=8`
  (`config.py:121`), and `effective_max_images` clips to `12`
  (`config.py:28`/`:136`). So `"rich"` is unreachable by default and the runner
  would reject the rich profile's 16 capture contracts anyway
  (`runner.py:170-179`).
- The fix is a capture-vs-transmit split:
  - introduce an explicit *capture profile* choice that can prefer a richer
    candidate set regardless of the transmit budget (capture is local file work,
    not a transmitted-image cost)
  - add a deterministic *budget-aware selection* step that ranks candidate
    captures by a fixed view-value priority and trims to the effective transmit
    budget before the request reaches the runner's `effective_max_images` check
- Keep `choose_capture_preset_profile` as the *transmit-shape* hint, or rename
  the gate intent so the rich/compact decision no longer pretends to bound
  capture. A backward-compatible approach: keep the existing function signature
  and add a sibling `choose_capture_set(...)` returning `(capture_profile,
  transmit_budget)` so existing callers/tests in
  `tests/unit/adapters/mcp/test_vision_policy.py` keep passing.
- Selection priority should be deterministic and symbolic, not coordinate-based:
  rank by `view_kind` and `preset_name` (e.g. `context_wide` > orthographic
  `target_top`/`target_front`/`target_side` > oblique > detail), so the cut is
  auditable and reproducible. This intentionally avoids any learned/embedding
  ranker here; heavier perceptual scorers stay default-off under the `TASK-172`
  seam.
- The single-stage vs before/after distinction matters: `capture_stage_images`
  (`capture_runtime.py:186-262`) produces one stage's captures; a before/after
  bundle doubles them. The selection budget must be applied per the actual
  transmitted shape — `8` when only after-captures ship (stage checkpoint), and
  the doubled count only when both stages transmit.
- Research basis (cite by name + arXiv id): **DiffuRank (arXiv:2404.07984)**
  found a well-chosen 6-view set can outperform a naive 28-view set, which is the
  direct justification for "capture richer, then select a small high-value subset"
  rather than transmitting everything. **VSI-Bench (arXiv:2412.14171)** motivates
  keeping the top-down view in the retained subset (top-down map representations
  improved spatial QA by roughly +20-32% in that benchmark). Treat both as
  indoor-scan/video-QA evidence and re-measure on `tests/fixtures/vision_eval`.

## Pseudocode

```python
def choose_capture_set(*, reference_image_count, max_images, single_stage):
    # Capture richer than we transmit. Capture is local, transmission is budgeted.
    capture_profile = "rich"  # always capture the richer candidate set
    # Transmit budget is the per-request image cap minus reserved references.
    reserved_refs = max(0, reference_image_count)
    transmit_budget = max(1, max_images - reserved_refs)
    return capture_profile, transmit_budget


def select_transmitted_captures(captures, *, transmit_budget):
    # Deterministic, symbolic, order-stable view-value ranking (no coordinates).
    priority = {
        "context_wide": 0,
        "target_top": 1,        # orthographic overhead retained early
        "target_front": 2,
        "target_side": 3,
        "target_oblique_left": 4,
        "target_oblique_right": 5,
        "target_focus": 6,
        "target_detail": 7,
    }
    ranked = sorted(
        enumerate(captures),
        key=lambda item: (priority.get(item[1].preset_name, 99), item[0]),
    )
    kept = [capture for _index, capture in ranked[: transmit_budget]]
    # Re-emit in stable capture order so downstream labeling stays predictable.
    kept_ids = {id(capture) for capture in kept}
    return [capture for capture in captures if id(capture) in kept_ids]
```

## Runtime / Security Contract Notes

- This step changes only *which deterministic captures are transmitted*; it adds
  no new authority. Selection metadata and the captures themselves stay
  advisory-only and keep `not_truth_source` /
  `requires_deterministic_checks_for_correctness`. Selection must not mark any
  gate complete or unlock any tool.
- The runner image-budget rejection (`runner.py:170-179`) remains the hard guard;
  selection runs before it and must guarantee the transmitted count never
  exceeds `runtime.effective_max_images`. Fail closed: if selection cannot bound
  the set, drop to the existing compact behavior rather than over-transmitting.
- Do not raise `VISION_FAIL_SAFE_MAX_IMAGES` or any fail-safe cap.
- No coordinate tokens are emitted as primary evidence; ranking is symbolic by
  `preset_name` / `view_kind` only.

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_vision_policy.py`
- `tests/unit/adapters/mcp/test_vision_runtime_config.py`
- `tests/unit/adapters/mcp/test_vision_capture_runtime.py`
- `tests/unit/adapters/mcp/test_reference_images.py`

## Docs To Update

- `_docs/_VISION/README.md`
- `_docs/_VISION/MULTI_VIEW_CAPTURE_PLAN.md`
- `_docs/_VISION/REFERENCE_UNDERSTANDING_ROADMAP.md`

## Changelog Impact

- add/update one `_docs/_CHANGELOG/*` entry when this slice lands

## Status / Board Update

- board tracking remains on umbrella `TASK-177`
- no separate promoted board-row change is expected for this subtask unless it
  later becomes a standalone follow-on

## Validation Commands

- `git diff --check`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_vision_policy.py tests/unit/adapters/mcp/test_vision_runtime_config.py tests/unit/adapters/mcp/test_vision_capture_runtime.py -q`
- `PYTHONPATH=. poetry run pytest ./tests/unit`

## Validation Category

- capture-vs-transmit decoupling and budget-aware selection proof
