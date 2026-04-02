# 196. Reference-guided creature test prompt doc

Date: 2026-04-02

## Summary

Added a separate operator/test prompt document for the hybrid creature loop
outside the MCP-served `_docs/_PROMPTS/` catalog.

## What Changed

- added `_docs/_VISION/REFERENCE_GUIDED_CREATURE_TEST_PROMPT.md`
- captured an updated staged squirrel prompt that now explicitly references:
  - `correction_candidates`
  - `truth_followup`
  - optional `scene_get_viewport(...)` camera/viewport review captures
- linked that document from the vision/test regression guidance docs

## Why

The project needed one richer manual-eval prompt that can evolve with hybrid
loop behavior without changing the prompt assets exposed through the MCP server.
