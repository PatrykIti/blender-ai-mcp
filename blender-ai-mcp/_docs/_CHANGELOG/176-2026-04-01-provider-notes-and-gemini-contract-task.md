# 176. Provider notes and Gemini contract follow-up

Date: 2026-04-01

## Summary

Documented the current provider/model status for the vision layer and added a
follow-on task for Gemini-specific structured output stabilization.

## What Changed

- added a `Provider Notes` section to:
  - `README.md`
  - `_docs/_VISION/README.md`
  - `_docs/_MCP_SERVER/README.md` (link/mention)
- documented current branch-level provider notes for:
  - `mlx_local`
  - OpenRouter / Grok
  - OpenRouter / Qwen VL
  - Google AI Studio / Gemini
- added follow-on task:
  - `TASK-121-04-01-05_Google_AI_Studio_Gemini_Structured_Output_Contract_And_Prompting.md`

## Why

The provider transport layer is now broad enough that repo users need a clear
current-state table, not just raw implementation docs. Gemini also now needs a
dedicated follow-up task because the generic external contract remains too
heavy for stable iterative compare flows.
