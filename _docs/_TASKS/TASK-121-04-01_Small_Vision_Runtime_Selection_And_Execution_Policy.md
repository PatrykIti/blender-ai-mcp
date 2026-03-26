# TASK-121-04-01: Small Vision Runtime Selection and Execution Policy

**Parent:** [TASK-121-04](./TASK-121-04_Lightweight_Vision_Runtime_And_Evaluation.md)  
**Status:** ⏳ To Do  
**Priority:** 🔴 High

---

## Objective

Choose the lightweight vision runtime/model path and define exactly how it may
run inside the product.

---

## Implementation Direction

- evaluate small vision-capable model/runtime options for:
  - before/after change interpretation
  - reference-image similarity guidance
  - likely-issue localization
- build the runtime as a pluggable backend layer with at least:
  - `transformers_local` for local Hugging Face-style models
  - `openai_compatible_external` for external OpenAI-compatible vision endpoints
- keep backend configuration explicit instead of loading “some file from a link”:
  - local backend should accept `model_id` or `model_path`
  - external backend should accept `base_url`, `model`, and auth config
- baseline evaluation matrix should cover:
  - local small/cheap candidate: `Qwen2.5-VL-3B-Instruct`
  - local medium candidate: `Qwen2.5-VL-7B-Instruct`
  - forward local path to newer family: `Qwen3-VL` small/medium variants
  - external comparator path: `Gemma 3` vision-capable endpoint
- define execution policy:
  - request-bound only vs optional background
  - time/token/image limits
  - when vision is allowed on `llm-guided`
  - what data may be sent and stored
- prefer request-bound foreground execution for the first release; no background authority
- align the runtime choice with repo ops constraints and product latency goals

---

## Repository Touchpoints

- `server/infrastructure/config.py`
- `server/adapters/mcp/sampling/`
- `_docs/_MCP_SERVER/README.md`
- `_docs/_TESTS/README.md`

---

## Acceptance Criteria

- one explicit lightweight runtime/model strategy is chosen
- runtime policy is documented before deep integration work continues
- the product can swap between local and external vision backends without changing the macro/workflow result contract
