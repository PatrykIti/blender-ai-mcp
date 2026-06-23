# TASK-140: External Vision Contract Profiles Capability-First Closeout

**Status:** ✅ Done
**Priority:** 🔴 High
**Category:** Vision Runtime / External Model Capability Reliability
**Completion Date:** 2026-06-23
**Dependencies:** TASK-139
**Follow-up:** [TASK-187](./TASK-187_External_Vision_Model_Evidence_And_Profile_Promotion_Governance.md)

## Objective

Close the old broad family-profile expansion plan and record the current
capability-first runtime as the source of truth for external vision model
reliability.

The original `TASK-140` plan assumed that Qwen, Anthropic, OpenAI, and NVIDIA
families would each need separate `vision_contract_profile` expansion branches.
After the `TASK-140-06` / `TASK-184` implementation state, that is no longer the
right default. The shipped OpenRouter path is capability-first: it resolves
model metadata, uses reviewed fallback capability profiles only when needed,
chooses bounded request policy from those capabilities, and exposes diagnostics
without widening provider or profile vocabulary.

## Current Source Of Truth

The current runtime keeps the external provider vocabulary closed:

- `VisionExternalProviderName`: `generic`, `openrouter`,
  `google_ai_studio`
- `VisionContractProfile`: `generic_full`, `google_family_compare`

The implementation that supersedes the old family tree is:

- `server/adapters/mcp/vision/config.py`
  - closed provider/profile vocabulary
  - `VisionModelCapabilities`
  - effective model-aware output caps
  - Set-of-Mark capability gating through
    `visual_mark_overlays_supported`
- `server/adapters/mcp/vision/runtime.py`
  - explicit profile override precedence
  - reviewed OpenRouter fallback profile lookup
  - deterministic Google/OpenAI-family profile heuristics where they are still
    warranted by current behavior
- `server/adapters/mcp/vision/openrouter_models.py`
  - bounded lazy OpenRouter `/models` lookup
  - normalization of context length, provider max completion tokens,
    input/output modalities, and supported parameters
- `server/adapters/mcp/vision/model_profiles/`
  - reviewed fallback capability registry
  - candidate profile generation requires review before promotion
- `server/adapters/mcp/vision/backends.py`
  - image/text modality gating
  - capability-driven `json_schema` / `json_object` / no-response-format policy
  - bounded response-healing policy
  - request-policy logging with selected contract profile, request mode,
    effective caps, provider preferences, plugins, and capability source
- `server/adapters/mcp/sampling/result_types.py`
  - `VisionCapabilitySummaryContract`
  - public `VisionAssistContract.capability_summary`
- `server/adapters/mcp/vision/runner.py`
  - bounded capability summary from model metadata, request policy, usage, and
    finish reason
- `scripts/vision_harness.py`
  - harness `capability_summary` and diagnostics output for external model runs

## Completion Summary

`TASK-140` is complete as a capability-first reliability track:

- OpenRouter model metadata is the primary source when available.
- Reviewed fallback profiles are secondary operational knowledge, not a
  permanent truth source.
- Request policy is driven by resolved capabilities: output budget,
  response-format posture, response-healing, modality support, and structured
  findings/schema posture.
- Diagnostics are bounded and operator-visible through logs, public result
  contracts, and harness output.
- Set-of-Mark overlays require both operator enablement and positive model
  capability support.
- The old `TASK-140-01` through `TASK-140-05` family-profile branches are
  administratively superseded, not left open under this closed parent.
- `TASK-140-06` and its remaining policy/diagnostic leaves are closed as the
  shipped capability-aware runtime substrate.

No runtime code changed during the `TASK-140-07` closeout pass; this is a
docs/task-governance reconciliation with the already-shipped runtime.

## Non-Goals

- Do not add new `VISION_EXTERNAL_PROVIDER` values as part of this closeout.
- Do not add Qwen/Anthropic/OpenAI/NVIDIA-specific profile enums without
  evidence.
- Do not promote a model from provider docs, semantic similarity, or operator
  prose alone.
- Do not treat `vision_contract_profile` or model capability metadata as scene
  truth or quality-gate authority.

## Follow-on

Future model/profile promotion belongs to
[`TASK-187`](./TASK-187_External_Vision_Model_Evidence_And_Profile_Promotion_Governance.md).
That follow-up owns current provider-doc review, live harness smoke, operator
notes, regression fixtures, and the decision to add a concrete model fallback
profile or a new `VisionContractProfile` only when evidence proves a real
runtime contract difference.

## Acceptance Criteria

- `TASK-140` parent is closed as the historical capability-first reliability
  track.
- `TASK-140-06`, `TASK-140-06-02`, and `TASK-140-06-04` are closed with
  completion summaries tied to shipped runtime behavior.
- `TASK-140-01` through `TASK-140-05` and their descendants are marked
  `⏭️ Superseded` with `TASK-187` as the replacement.
- `TASK-187` exists as a standalone promoted follow-up with no `Parent` field.
- `_docs/_TASKS/README.md`, `_docs/_VISION/README.md`,
  `_docs/_MCP_SERVER/README.md`, and `_docs/_CHANGELOG/README.md` reflect the
  capability-first closeout.
- Validation records prove there are no open direct descendants under the
  closed `TASK-140` parent.

## Validation Commands

- `git diff --check`
- `rg -n "^\\*\\*Status:\\*\\* (⏳ To Do|🚧 In Progress)" _docs/_TASKS/TASK-140*.md`
- board count audit against `_docs/_TASKS/README.md`
- changelog index audit for entry `396`
- `PRE_COMMIT_HOME=/tmp/pre-commit-cache poetry run pre-commit run --all-files --show-diff-on-failure`

## Status / Board Update

- moved from board `In Progress` to `Done`
- `TASK-187` is the only promoted open follow-up created by this closeout
