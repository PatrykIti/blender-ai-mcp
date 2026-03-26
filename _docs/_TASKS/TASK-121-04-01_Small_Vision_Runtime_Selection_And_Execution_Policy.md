# TASK-121-04-01: Small Vision Runtime Selection and Execution Policy

**Parent:** [TASK-121-04](./TASK-121-04_Lightweight_Vision_Runtime_And_Evaluation.md)  
**Status:** 🚧 In Progress  
**Priority:** 🔴 High

**Progress Update:** The repo now has all three runtime families wired behind the same bounded contract path: `transformers_local`, `mlx_local`, and `openai_compatible_external`. `mlx_local` has also passed a first real smoke test on a small Apple-Silicon-friendly model path (`mlx-community/Qwen3-VL-2B-Instruct-4bit`), the repo now has a backend-comparison harness script, and local prompt/parse-repair helpers can already turn fenced or input-echo-style outputs into a bounded structured payload. Output quality and stronger eval policy still need work.

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
- do not load the selected model in the core MCP server bootstrap path
- treat vision as an adopted optional capability, not a mandatory baseline dependency like LaBSE
- prefer lazy backend/model initialization on first real vision use
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
- keep vision failure-tolerant:
  - unavailable/disabled backends must not break normal macro/workflow execution
  - startup without any vision runtime configured must remain a first-class supported mode

---

## Repository Touchpoints

- `server/infrastructure/config.py`
- `server/adapters/mcp/vision/`
- `server/adapters/mcp/sampling/`
- `scripts/`
- `_docs/_MCP_SERVER/README.md`
- `_docs/_TESTS/README.md`

---

## Acceptance Criteria

- one explicit lightweight runtime/model strategy is chosen
- runtime policy is documented before deep integration work continues
- the product can swap between local and external vision backends without changing the macro/workflow result contract
- server bootstrap remains lightweight and does not require loading a large local VLM to start the MCP stack

## Detailed Execution Breakdown

1. Runtime families
   - keep `transformers_local`, `mlx_local`, and `openai_compatible_external`
     behind one bounded interface
   - keep each backend optional and lazy

2. Debug harness
   - add one script that can run the same bundle/reference payload through
     multiple backends
   - print/store:
     - backend name
     - model name
     - raw output
     - parsed output
     - parse failure reason when relevant

3. Local prompt policy
   - tighten the system prompt for local models so they optimize for one small
     JSON object, not conversational explanation
   - allow backend-specific prompt variants when needed (`mlx_local` vs
     `transformers_local`)

4. Parse policy
   - accept:
     - direct JSON
     - fenced JSON
     - near-JSON text that can be deterministically repaired
   - reject:
     - prose-only outputs
     - truth claims beyond the contract boundary

5. Runtime-choice closure
   - compare at least one real smoke-test candidate per backend family
   - document whether the first favored local path is:
     - `mlx_local`
     - `transformers_local`
     - or external-first with local still experimental
