# 181. Gemini compare contract hardening

Date: 2026-04-01

## Summary

Completed the Gemini follow-on task by adding a provider-specific narrow
compare contract, prompting path, and parse-repair behavior for staged
reference-guided compare flows.

## What Changed

- added a Google AI Studio / Gemini specific compare-contract path for
  reference-guided checkpoint and staged iterative compare flows
- narrowed the Gemini compare schema/prompt surface to the fields that have
  proved stable on this provider:
  - `goal_summary`
  - `reference_match_summary`
  - `shape_mismatches`
  - `proportion_mismatches`
  - `correction_focus`
  - `next_corrections`
- added Gemini-specific parse repair for near-JSON / truncated compare
  responses while keeping downstream normalization on the canonical bounded
  vision payload
- updated provider notes and task tracking/docs to reflect that the Gemini
  compare hardening follow-on is now complete

## Why

The generic external vision contract was still too broad for Gemini on harder
staged compare flows. Narrowing the contract only for the Gemini compare path
improves reliability without regressing the existing OpenRouter or local model
paths.
