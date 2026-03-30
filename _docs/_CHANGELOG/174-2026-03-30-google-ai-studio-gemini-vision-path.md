# 174. Google AI Studio Gemini vision path

Date: 2026-03-30

## Summary

Added a first-class Google AI Studio / Gemini path for the bounded vision
layer.

## What Changed

- external vision config now supports:
  - `VISION_EXTERNAL_PROVIDER=google_ai_studio`
  - `VISION_GEMINI_MODEL`
  - `VISION_GEMINI_API_KEY`
  - `VISION_GEMINI_API_KEY_ENV`
  - optional `VISION_GEMINI_BASE_URL`
- the external backend now supports provider-specific Gemini behavior:
  - `models/<model>:generateContent` endpoint
  - Gemini `contents` / `inline_data` payload format
  - `candidates[].content.parts[].text` response parsing
  - `x-goog-api-key` authentication header
- `scripts/vision_harness.py` now supports Gemini-oriented flags

## Why

The project already had local MLX plus generic external/OpenRouter paths, but
Gemini remained a separate integration gap. This change makes Gemini available
through the same bounded vision contract for direct comparison and low-cost
experimentation.
