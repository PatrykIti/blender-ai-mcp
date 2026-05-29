# TASK-183-01: Capability-Aware Response Schema And Curated Payload

**Parent:** [TASK-183](./TASK-183_Capability_Enriched_Vision_Schema_And_Deterministic_Cross_Check.md)
**Status:** ⏳ To Do
**Priority:** 🟡 Medium
**Follow-on After:** [TASK-140-06](./TASK-140-06_OpenRouter_Model_Capability_Aware_Vision_Runtime.md), [TASK-178-02](./TASK-178-02_Structured_Finding_Prompt_And_Response_Schema_Emission.md)
**Objective:** Thread `model_capabilities` into the response-schema builder so strong, grounding/structured-output models with ample completion budget get the richer per-finding/per-mark schema while weak/local models keep a lean schema; stop defaulting frontier hosted models to the field-dropping `google_family_compare` profile (or backfill its dropped fields); replace the bare-`json.dumps` default external payload with curated, task-framed, internal-ID-stripped scaffolding; and capture and surface provider token usage so truncation against the known completion cap is observable.
**Repository Touchpoints:** `server/adapters/mcp/vision/prompting.py`, `server/adapters/mcp/vision/runtime.py`, `server/adapters/mcp/vision/backends.py`, `server/adapters/mcp/vision/model_profiles/openrouter_openai.py`, `server/adapters/mcp/vision/config.py`, `tests/unit/adapters/mcp/test_vision_runtime_config.py`, `tests/unit/adapters/mcp/test_vision_prompting.py`, `tests/unit/adapters/mcp/test_contract_payload_parity.py`, `tests/unit/adapters/mcp/test_vision_external_backend.py`

**Acceptance Criteria:**
- `build_vision_response_json_schema(...)` accepts an optional `model_capabilities: VisionModelCapabilities | None` argument and selects the richer per-finding/per-mark schema only when the model advertises strong structured-output/grounding (`structured_outputs`/`response_format` in `supported_parameters`) **and** an ample `max_completion_tokens`; weak/unknown capabilities keep the current lean schema
- all three call sites in `vision/backends.py` (`:807`, `:826`, `:888`) pass `model_capabilities=self._external_config.model_capabilities`
- frontier hosted models no longer default to `google_family_compare` purely from a model-name marker, OR the `google_family_compare` schema (`vision/prompting.py:1245`) is backfilled so it no longer silently drops `visible_changes`/`likely_issues`/`recommended_checks`/`confidence`/`captures_used`; either way `expected_json_keys(...)` stays consistent with the emitted schema
- the default external payload (`vision/prompting.py:747-755`) is replaced with curated task-framed scaffolding that contains no raw internal `metadata` dict and no internal IDs, and is covered by a test asserting omission of leaked keys
- provider token usage (OpenAI-style `usage.completion_tokens`/`usage.total_tokens`, Gemini `usageMetadata`) is captured and a truncation/token-cap diagnostic is surfaced when a structured response is cut at the completion cap (the cap is already known via `model_max_completion_tokens` at `vision/backends.py:304`)
- all newly unlocked fields keep the advisory posture: `not_truth_source` / `requires_deterministic_checks_for_correctness` semantics are preserved and vision still cannot pass gates or unlock tools

## Implementation Notes

- The schema builder `build_vision_response_json_schema` (`vision/prompting.py:851`)
  currently takes only `vision_contract_profile`, `provider_name`, and `request`.
  Add `model_capabilities: VisionModelCapabilities | None = None` and gate the
  richer branch on a small, explicit capability predicate. Reuse the existing
  capability checks rather than inventing new ones: `vision/backends.py:66`
  defines `_supports_parameter(capabilities, parameter_name)` and the structured
  branch at `vision/backends.py:801` already keys on `structured_outputs` +
  `response_format`. The completion budget is `max_completion_tokens` on
  `VisionModelCapabilities` (`vision/config.py:41`), already surfaced into
  diagnostics at `vision/backends.py:304`.
- The capability gate is the consumer side of `TASK-140-06`. Read the reviewed
  profiles in `vision/model_profiles/openrouter_openai.py`: strong candidates
  such as `anthropic/claude-opus-4.6` (`max_completion_tokens=128000`,
  `structured_outputs` present), `openai/gpt-5.4` (128000), and the Gemini Pro
  families advertise both ample budget and structured outputs, while
  `rekaai/reka-edge` (16384) and the small Ministral profiles are the lean-schema
  cases. Do not add new catalog entries here; only read existing capability data.
- The richer schema fields themselves are owned by `TASK-178` (typed per-finding
  list, per-mark tables). This subtask owns the **gate** that decides whether
  that richer shape is emitted, not the finding shape. Keep the two coherent: the
  rich branch should match `TASK-178`'s contract, and `expected_json_keys(...)`
  (`vision/prompting.py:825`) must return the matching key set per branch so
  parse-repair stays aligned.
- Routing: `_resolve_vision_contract_profile` (`vision/runtime.py:54`) sends
  Google-family models, OpenAI-family models on OpenRouter (`:69`), and anything
  on `google_ai_studio` (`:71`) to `google_family_compare`. Two viable
  directions, pick the lower-risk one and document the choice:
  1. stop defaulting capability-strong models to `google_family_compare` (keep
     `generic_full` when capabilities are strong), or
  2. keep the routing but backfill the `google_family_compare` schema branch
     (`vision/prompting.py:1245`) so it no longer drops the five fields.
  Direction (2) is lower-risk for providers that genuinely prefer the narrow
  contract; direction (1) is better when the model is grounding-capable. The
  capability gate makes either decision data-driven instead of name-driven.
- Curated payload: replace the bare `json.dumps` at `vision/prompting.py:747-755`
  with explicit task-framed scaffolding (the local payload builder at
  `vision/prompting.py:758` is the house-style template to mirror). Strip the raw
  `request.metadata` dict and any internal identifiers; keep `goal`,
  `target_object`, `prompt_hint`, truth-summary lines, and per-image
  `role`/`label` only. Prefer symbolic relations + proportional ratios over raw
  coordinate tokens in the framing text.
- Token usage: `_extract_message_text` (`vision/backends.py:87`) reads only
  `choices[0].message.content` and discards `payload["usage"]`; the Gemini path
  ignores `usageMetadata`. Capture completion tokens alongside the text and, when
  `completion_tokens >= max_completion_tokens` (or `finish_reason == "length"`),
  attach a truncation diagnostic to the run summary so a malformed structured
  response reads as a cap event rather than an anonymous parse failure.

### Research basis

- **3DGen-Bench** (arXiv:2503.21745) — per-dimension evaluator; motivates a
  richer multi-field schema for capable models instead of one flat prose blob.
- **GPTEval3D** (arXiv:2401.04092) — rich per-criterion schema; supports
  capability-gated emission of more structured criteria.
- **VLM3D** (arXiv:2511.14271) — graded per-part magnitudes; the richer schema
  must keep these as proportional ratios, never absolute measurements.

## Pseudocode

```python
def _model_supports_rich_schema(capabilities: VisionModelCapabilities | None) -> bool:
    if capabilities is None:
        return False
    supported = set(capabilities.supported_parameters or ())
    grounding_ready = bool({"structured_outputs", "response_format"} & supported)
    budget = capabilities.max_completion_tokens or 0
    return grounding_ready and budget >= RICH_SCHEMA_MIN_COMPLETION_TOKENS


def build_vision_response_json_schema(
    *,
    vision_contract_profile=None,
    provider_name=None,
    request=None,
    model_capabilities=None,
):
    if _is_reference_classification_request(request):
        return _classification_schema(...)
    # ... other specialized request schemas unchanged ...
    if _uses_google_family_compare_contract(...) and not _model_supports_rich_schema(model_capabilities):
        return _google_family_compare_schema()        # lean, unchanged for weak models
    if _model_supports_rich_schema(model_capabilities):
        return _rich_finding_schema()                  # TASK-178 per-finding/per-mark shape
    return _generic_full_schema()                      # current default


def build_vision_payload_text(request, *, vision_contract_profile=None, provider_name=None):
    if _uses_google_family_compare_contract(...):
        return _build_gemini_compare_payload_text(request)
    # curated, ID-stripped, task-framed default (replaces bare json.dumps)
    lines = [
        "TASK: Compare the after capture(s) against the goal and any references.",
        f"GOAL: {request.goal}",
        f"TARGET_OBJECT: {request.target_object or 'none'}",
        f"PROMPT_HINT: {request.prompt_hint or 'none'}",
        "IMAGES:",
        *[f"- {img.role}: {img.label or img.role}" for img in request.images],
        *_truth_summary_lines(request.truth_summary),  # no raw metadata, no internal IDs
    ]
    return "\n".join(lines)
```

## Runtime / Security Contract Notes

- vision stays advisory: the richer schema is still VLM interpretation and must
  keep `not_truth_source` / `requires_deterministic_checks_for_correctness`;
  it must not mark gates complete or unlock tools
- magnitudes in any unlocked field are proportional ratios versus a trusted
  reference anchor, never authoritative absolute measurements
- do not emit raw coordinate tokens as primary evidence; prefer symbolic
  relations + ratios, coordinates on demand only
- do not add VLM-side chain-of-thought framing for spatial judgments; reasoning
  stays in the orchestrator
- the curated payload must not leak internal IDs/metadata to the provider; treat
  payload contents as externally visible
- do not reopen the `TASK-140-06` provider-capability substrate; only consume the
  already-resolved `VisionModelCapabilities`
- keep the existing fail-safe completion-token clip and over-budget rejection
  intact; the token-usage surfacing is additive diagnostics, not a new control

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_vision_prompting.py` — rich vs lean schema
  selection by capability; curated payload omits raw `metadata`/internal IDs;
  `expected_json_keys` matches the emitted branch
- `tests/unit/adapters/mcp/test_vision_runtime_config.py` — capability-strong
  hosted models stop defaulting to the field-dropping compare profile (or its
  schema is backfilled)
- `tests/unit/adapters/mcp/test_contract_payload_parity.py` — emitted schema and
  parsed/expected keys stay in parity across the rich and lean branches
- `tests/unit/adapters/mcp/test_vision_external_backend.py` — all schema call
  sites receive capabilities; truncation against the completion cap surfaces a
  token-cap diagnostic instead of an anonymous parse failure

## Docs To Update

- `_docs/_VISION/README.md`
- `_docs/_VISION/REFERENCE_UNDERSTANDING_ROADMAP.md`
- `_docs/_MCP_SERVER/README.md`

## Changelog Impact

- add/update the historical `_docs/_CHANGELOG/*` entry when this slice lands

## Status / Board Update

- board tracking remains on umbrella `TASK-183`
- no separate promoted board-row change is expected for this subtask unless it
  later becomes a standalone follow-on

## Validation Commands

- `git diff --check`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_vision_prompting.py tests/unit/adapters/mcp/test_vision_runtime_config.py tests/unit/adapters/mcp/test_contract_payload_parity.py tests/unit/adapters/mcp/test_vision_external_backend.py -q`
- `PYTHONPATH=. poetry run pytest ./tests/unit`
- `poetry run python scripts/run_e2e_tests.py` (when external request assembly or backend behavior changes are exercised against a live/staged provider)

## Validation Category

- capability-aware schema and curated-payload contract proof
