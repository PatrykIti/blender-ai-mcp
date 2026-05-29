# TASK-175-02: Stage Docstring Read-Order And Authoritative Precedence

**Parent:** [TASK-175](./TASK-175_Vision_Contract_Field_Descriptions_And_Stage_Read_Order.md)
**Status:** ⏳ To Do
**Priority:** 🔴 High
**Follow-on After:** [TASK-160](./TASK-160_Guided_Client_Feedback_And_Streamable_HTTP_Recovery_UX.md), [TASK-166](./TASK-166_Hierarchical_Reference_Compare_Perceived_Evidence_And_Budget_Control.md)
**Objective:** Expand the reference stage / compare / iterate tool docstrings to enumerate the key returned fields, state authoritative-vs-advisory precedence, and instruct the client read-order (`reference_orchestrator_feedback` first, then deterministic truth, then advisory vision), without changing tool behavior, signatures, or returned payloads.
**Repository Touchpoints:** `server/adapters/mcp/areas/reference.py`, `server/adapters/mcp/areas/reference_feedback.py`, `tests/unit/adapters/mcp/test_public_surface_docs.py`, `_docs/_MCP_SERVER/README.md`, `_docs/_PROMPTS/REFERENCE_GUIDED_CREATURE_BUILD.md`
**Acceptance Criteria:**
- the five reference stage/compare/iterate tool docstrings each enumerate the
  key returned fields and state the authoritative-vs-advisory precedence:
  deterministic truth (`truth_bundle`, `truth_followup`, `silhouette_analysis`,
  gate statuses) is authoritative; `vision_assistant` output is advisory
- each docstring instructs the explicit client read-order:
  `reference_orchestrator_feedback` first, then deterministic truth, then
  advisory vision
- the docstring read-order matches what `reference_feedback.py` actually
  assembles into `ReferenceOrchestratorFeedbackContract`, so the guidance is
  accurate, not aspirational
- `test_public_surface_docs.py` asserts the new read-order / precedence
  substrings inside `areas/reference.py` source and in the canonical docs
- no tool signature, return type, behavior, visibility, or transport changes

## Implementation Notes

- The five docstrings to expand live in `server/adapters/mcp/areas/reference.py`:
  - `reference_images` (`:2208`): currently "Manage goal-scoped reference images
    for later vision/capture interpretation." Add that the response carries
    `reference_orchestrator_feedback` (read first) and
    `guided_reference_readiness`, and that attached refs are the trusted anchor
    for later compare ratios.
  - `reference_compare_checkpoint` (`:2237`) and
    `reference_compare_current_view` (`:2284`): note that `vision_assistant` is
    advisory interpretation and that `view_diagnostics_hints` / deterministic
    checks should be trusted over VLM prose.
  - `reference_compare_stage_checkpoint` (`:2325`): the docstring already mentions
    `compare_diagnostics` / `support_evidence` / `budget_control` (the existing
    `test_public_surface_docs.py` `test_reference_stage_public_transparency_is_documented`
    asserts `"bounded view/scope packets"` and
    `"Top-level compare_diagnostics remains the public access path"` are present
    in source). Extend it with the read-order and precedence text without
    removing those existing asserted substrings.
  - `reference_iterate_stage_checkpoint` (`:2362`): already mentions
    `loop_disposition` and `reference_orchestrator_feedback`; extend with the
    explicit read-order and "deterministic truth outranks advisory vision".
- The read-order must match the actual builder. `reference_feedback.py`
  (header at `:1-32`, importing `ReferenceOrchestratorFeedbackContract` and the
  compact projection helpers) is what assembles the compact orchestrator
  read-model; confirm the field list the docstring enumerates
  (`status`, `blocking_reasons`, `next_actions`, `next_checkpoint_tool`,
  `recommended_repair`, `correction_focus`, `loop_disposition`) matches the
  contract at `server/adapters/mcp/contracts/reference.py:336-366`.
- Precedence wording to standardize across all five docstrings:
  1. read `reference_orchestrator_feedback` first (compact, server-owned, safe
     next step);
  2. then deterministic truth (`truth_bundle`, `truth_followup`,
     `silhouette_analysis`, gate statuses / completion blockers) which is
     authoritative for scene correctness;
  3. then advisory `vision_assistant` (interpretation only, non-authoritative
     confidence, magnitudes are reference-relative ratios).
- Keep docstring additions short and English. The router tool metadata JSON
  (`server/router/infrastructure/tools_metadata/reference/reference_compare_stage_checkpoint.json`
  and `..._iterate_stage_checkpoint.json`) is asserted by
  `test_reference_stage_public_transparency_is_documented`; if the docstring is
  mirrored into those descriptions, keep the already-asserted substrings intact
  and update both RPC sides consistently.
- Research basis to cite inline when the slice lands: Structured Interfaces /
  GraphRAG schema framing (arXiv:2510.16643) motivates telling the consumer how
  to traverse a structured result; Descrip3D (arXiv:2507.14555) motivates
  description-rich, role-explicit surfaces for 3D-scene understanding. RESEARCH
  CAVEAT: both are indoor-scan / synthetic, not Blender-vs-reference; re-measure
  on `tests/fixtures/vision_eval` before promoting any orchestration gain.

## Pseudocode

```python
async def reference_iterate_stage_checkpoint(ctx, ...):
    """Run one session-aware packeted reference-compare iteration.

    Read-order for the client / orchestrator:
      1. reference_orchestrator_feedback  (read first; compact safe next step)
      2. deterministic truth              (truth_bundle, truth_followup,
                                           silhouette_analysis, gate statuses,
                                           completion_blockers) -- AUTHORITATIVE
                                           for scene correctness
      3. vision_assistant                 (ADVISORY interpretation only;
                                           confidence is non-authoritative;
                                           magnitudes are reference-relative ratios)

    Vision never marks a gate complete or unlocks a tool. Top-level
    compare_diagnostics remains the public access path for rich delivery.
    """
```

## Runtime / Security Contract Notes

- This slice is docstring / description text only: no signature, behavior,
  visibility, gate, or transport change, so it is reversible by reverting text.
  No Blender / addon main-thread or `capture_scene_state` / `restore_scene_state`
  work is needed.
- The precedence text must keep vision ADVISORY: deterministic inspection /
  assertion / silhouette own scene truth, and the docstrings must state that
  vision cannot mark gates complete or unlock tools, with non-authoritative
  confidence and reference-relative (never absolute) magnitudes.
- Do not introduce raw-coordinate-first guidance; the read-order points the
  client at symbolic relations + ratios and compact feedback before any
  coordinate-bearing optional evidence.
- Do not reopen the optional heavy-sidecar runtime (`TASK-172`) or the
  `TASK-140-06` provider-capability substrate; the docstrings only describe how
  to consume existing output.
- If docstring text is mirrored into router tool metadata JSON, both RPC sides
  plus the asserting tests and docs must move together.

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_public_surface_docs.py` (extend the existing
  source / docs substring assertions to require the read-order
  "reference_orchestrator_feedback first" and the
  "deterministic truth outranks advisory vision" precedence wording, while
  keeping the existing `"bounded view/scope packets"` /
  `"Top-level compare_diagnostics remains the public access path"` asserts)
- `tests/unit/adapters/mcp/test_contract_docs.py` (optional: confirm the docs
  describe the read-order if the doc text is asserted there)

## Docs To Update

- `_docs/_MCP_SERVER/README.md`
- `_docs/_VISION/README.md`
- `_docs/_VISION/REFERENCE_UNDERSTANDING_ROADMAP.md`
- `_docs/_PROMPTS/REFERENCE_GUIDED_CREATURE_BUILD.md`

## Changelog Impact

- add/update the historical `_docs/_CHANGELOG/*` entry when this slice lands

## Status / Board Update

- board tracking remains on umbrella `TASK-175`
- no separate promoted board-row change is expected for this subtask unless it
  later becomes a standalone follow-on

## Validation Commands

- `git diff --check`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_public_surface_docs.py tests/unit/adapters/mcp/test_contract_docs.py -q`
- `PYTHONPATH=. poetry run pytest ./tests/unit`

## Validation Category

- additive docstring read-order and precedence proof
