# TASK-123: Runtime Reliability Fixes for Vision Provider Startup and Task Terminality

**Priority:** 🔴 High  
**Category:** Product Reliability / Runtime Operations  
**Estimated Effort:** Medium  
**Dependencies:** TASK-088, TASK-093-02, TASK-121-04  
**Status:** ✅ Done

**Completion Summary:** The repo now preserves both runtime invariants targeted by this umbrella: explicit OpenRouter and Google AI Studio / Gemini selections can build a valid external vision profile from generic fallback model/auth env without failing startup, and timed-out server-local background tasks now keep a monotonic terminal state even if a worker thread emits late progress. Regression coverage was added at the vision runtime, job registry, and local task-bridge levels.

## Objective

Close two P1 regressions from recent runtime work so:

- valid explicit external vision-provider configurations still boot cleanly
- server-local background tasks keep a truthful terminal state after timeout

---

## Business Problem

Recent changes improved two important areas:

- provider-specific external vision runtime support
- local background-task execution for long-running server-side work

But the current branch still has two correctness regressions:

- explicit external-provider selection can fail startup when only the generic
  fallback model is configured
- timed-out local background jobs can later look `running` again if a worker
  thread emits late progress

These hit different code paths, but they break the same product promise:
runtime state must be deterministic and trustworthy.

---

## Business Outcome

If this task is done correctly, the repo regains:

- startup safety for valid external provider configurations
- monotonic terminal task states for local background work
- reliable operational diagnostics for task polling and failure analysis
- confidence that the recent vision/runtime work is safe to keep building on

---

## Scope

This umbrella covers:

- explicit selected-provider resolution for external vision runtime config
- generic fallback handling for provider-selected OpenRouter and Google AI
  Studio / Gemini paths
- terminal-state protection for server-local background task bookkeeping
- focused regression coverage for both startup and late-progress paths

This umbrella does **not** cover:

- adding new vision providers
- redesigning the full vision runtime contract
- force-killing Python worker threads used by `asyncio.to_thread(...)`
- replacing the current task bridge or registry model

---

## Success Criteria

- `VISION_EXTERNAL_PROVIDER=openrouter` plus `VISION_EXTERNAL_MODEL` boots
  without requiring `VISION_OPENROUTER_MODEL`
- `VISION_EXTERNAL_PROVIDER=google_ai_studio` plus `VISION_EXTERNAL_MODEL`
  boots without requiring `VISION_GEMINI_MODEL`
- explicit provider selection keeps precedence over conflicting env from the
  other provider
- timed-out server-local background tasks remain terminal and cannot be
  resurrected by late progress callbacks
- regression tests cover both failure modes directly

---

## Execution Structure

| Order | Subtask | Purpose |
|------|---------|---------|
| 1 | [TASK-123-01](./TASK-123-01_Explicit_External_Vision_Provider_Fallback_And_Precedence.md) | Fix explicit external-provider startup gating and fallback precedence for OpenRouter and Google AI Studio / Gemini |
| 2 | [TASK-123-02](./TASK-123-02_Local_Background_Task_Terminality_After_Timeout.md) | Keep server-local background task failures terminal even when worker threads emit late progress |
