# 177. External provider precedence, loop scope, and task timeout

Date: 2026-04-01

## Summary

Fixed three reliability issues across external vision provider selection,
reference correction-loop state scoping, and background task timeout handling.

## What Changed

- explicit `VISION_EXTERNAL_PROVIDER` now wins over provider-specific model envs
  when building the external vision runtime config
- conflicting generic external envs for both OpenRouter and Gemini now fail
  fast instead of silently routing to the wrong provider
- `reference_iterate_stage_checkpoint(...)` loop reuse now also keys on:
  - `target_view`
  - `preset_profile`
- background task RPC polling now respects `MCP_TASK_TIMEOUT_SECONDS` end-to-end
  instead of looping forever if Blender never leaves `running`
- local server-side background operations now also respect
  `MCP_TASK_TIMEOUT_SECONDS`
- local background execution and formatting errors now mark the registry entry as
  `failed` instead of leaving task state in a non-terminal limbo

## Why

These fixes close three bad failure modes:

- wrong external provider chosen in mixed env setups
- repeated correction focus bleeding across different checkpoint perspectives
- background tasks hanging forever despite a configured task timeout
