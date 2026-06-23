# TASK-140-07: Task Hierarchy Audit And Capability-First Replan

**Parent:** [TASK-140](./TASK-140_Expand_External_Vision_Contract_Profiles_Across_Qwen_Anthropic_OpenAI_And_NVIDIA.md)
**Status:** ✅ Done
**Priority:** 🟠 High
**Completion Date:** 2026-06-23

## Objective

Audit `TASK-140` after the capability-aware OpenRouter runtime work and close
the stale family-profile hierarchy in favor of one capability-first follow-up.

## Repository Touchpoints

| Path | Ownership |
|---|---|
| `_docs/_TASKS/TASK-140*.md` | close parent, close capability-aware leaves, supersede old family-profile branches |
| `_docs/_TASKS/TASK-187_External_Vision_Model_Evidence_And_Profile_Promotion_Governance.md` | create standalone follow-up for future evidence-backed model/profile promotion |
| `_docs/_TASKS/README.md` | board status/count sync |
| `_docs/_VISION/README.md` | current capability-first external vision narrative |
| `_docs/_MCP_SERVER/README.md` | operator-facing MCP/runtime contract note |
| `_docs/_CHANGELOG/` | historical changelog entry and index |

## Runtime Proof Points

Read-only audit confirmed the current code is already capability-first:

- `server/adapters/mcp/vision/config.py`
  - closed `VisionExternalProviderName` vocabulary:
    `generic`, `openrouter`, `google_ai_studio`
  - closed `VisionContractProfile` vocabulary:
    `generic_full`, `google_family_compare`
  - `VisionModelCapabilities`
  - effective output-token caps from model caps, profile floors, and fail-safe
    limits
  - default-off `visual_mark_overlays_supported` and
    `effective_mark_overlay_enabled`
- `server/adapters/mcp/vision/runtime.py`
  - explicit contract-profile override precedence
  - reviewed OpenRouter fallback profile lookup
  - bounded model-family heuristics where still used
- `server/adapters/mcp/vision/openrouter_models.py`
  - bounded lazy OpenRouter `/models` metadata lookup
  - normalized context length, max completion tokens, modalities, and supported
    parameters
- `server/adapters/mcp/vision/model_profiles/`
  - provider-limited fallback registry
  - generated candidate profiles require review before runtime fallback
    promotion
- `server/adapters/mcp/vision/backends.py`
  - modality gating
  - capability-driven response-format policy
  - response-healing plugin policy
  - bounded request-policy summary logging
- `server/adapters/mcp/sampling/result_types.py`
  - `VisionCapabilitySummaryContract`
  - `VisionAssistContract.capability_summary`
- `server/adapters/mcp/vision/runner.py`
  - public capability summary from runtime capabilities, request policy, token
    usage, and finish reason
- `scripts/vision_harness.py`
  - harness capability summary and diagnostics output

## Decisions

- Close `TASK-140` as delivered by the shipped capability-aware runtime.
- Close `TASK-140-06`, `TASK-140-06-02`, and `TASK-140-06-04` as already
  covered by current runtime behavior and docs.
- Supersede `TASK-140-01` through `TASK-140-05` and their descendants because
  the old family-profile expansion tree is no longer the default direction.
- Create standalone `TASK-187` for future model/profile promotion governance.

## Notes

- No runtime code changed in this audit pass.
- The standalone harness already records a capability-summary path, but future
  live promotion work should continue to verify live-only OpenRouter metadata
  propagation before treating harness output as promotion evidence.
- `_docs/_VISION/README.md` now avoids implying that
  `VISION_OPENROUTER_REQUIRE_PARAMETERS=true` is required by default; strict
  provider filtering remains an explicit operator choice.

## Acceptance Criteria

- `TASK-140` closes as `✅ Done`.
- `TASK-140-06`, `TASK-140-06-02`, and `TASK-140-06-04` close as `✅ Done`.
- `TASK-140-01` through `TASK-140-05` and their descendants are
  `⏭️ Superseded` and point to `TASK-187`.
- `TASK-187` exists as a standalone `⏳ To Do` follow-up with
  `Follow-on After: TASK-140`.
- Board counts and changelog index are updated.
- Validation commands are recorded in this file and the final closeout.

## Validation

- `git diff --check` passed.
- `rg -n "^\\*\\*Status:\\*\\* (⏳ To Do|🚧 In Progress)" _docs/_TASKS/TASK-140*.md`
  returned no open `TASK-140` descendants.
- Board count audit matched the promoted rows:
  - `To Do: 6` (`TASK-148`, `TASK-137`, `TASK-138`, `TASK-185`, `TASK-186`,
    `TASK-187`)
  - `In Progress: 2` (`TASK-165`, `TASK-160`)
  - `Done: 116` with `TASK-140` added on `2026-06-23`
- Changelog index audit found entry `396`.
- `PRE_COMMIT_HOME=/tmp/pre-commit-cache poetry run pre-commit run --all-files --show-diff-on-failure`
  passed.

## Completion Summary

Completed the task hierarchy audit and capability-first replan. The stale
family-profile tree is historical, `TASK-140` is closed, and future model or
profile promotion is tracked by `TASK-187` with explicit evidence requirements.
