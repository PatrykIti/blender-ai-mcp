# TASK-140: Expand External Vision Contract Profiles Across Qwen, Anthropic, OpenAI, and NVIDIA

**Status:** ⏳ To Do
**Priority:** 🔴 High
**Category:** Vision Runtime / External Provider Reliability
**Estimated Effort:** Large
**Dependencies:** TASK-139

## Objective

Extend the external `vision_contract_profile` architecture introduced in
`TASK-139` beyond the current `generic_full` and
`google_family_compare` split so the runtime can choose prompt/schema/parser
behavior more precisely for additional multimodal model families.

This umbrella should cover the next docs-reviewed external targets:

- Qwen-VL families:
  - legacy `qwen-vl-plus` / `qwen-vl-max`
  - Qwen2.5-VL families
  - Qwen3-VL families and their instruct/thinking/plus/flash variants
  - adjacent newer multimodal Qwen families such as Qwen3.5-Plus when the
    docs position them as stronger multimodal successors to older Qwen-VL lines
  - OCR/document-oriented Qwen-VL variants when they are product-relevant
- Anthropic Claude vision-capable families
- OpenAI image-input model families
- NVIDIA VLM families that are plausible bounded-compare candidates

## Terminology Guardrail

In this task family:

- `provider` / `transport` still means the API protocol path and auth/header
  behavior
- `vision_contract_profile` means the bounded prompt/schema/parser behavior
  used by this repo for external vision compare/iterate flows

Do not collapse those two concepts again.

## Business Problem

After `TASK-139`, the repo has a correct architectural seam, but the profile
space is still too coarse.

The current model is:

- `generic_full`
- `google_family_compare`

That is enough to stop treating OpenRouter-hosted Google-family models as
generic OpenAI-compatible models, but it is not enough for the next wave of
external vision work because the upcoming families differ materially in:

- structured-output reliability
- OCR/document bias versus general image reasoning
- multi-image compare behavior
- reasoning-versus-instruction variants inside one model family
- truncation / near-JSON failure modes
- whether a model is even a credible staged compare candidate versus only a
  document, retrieval, or embedding-side visual model

If the repo keeps routing all of those through only one generic profile plus
one Google-family compare profile, we will recreate the same class of
mismatch:

- transport works
- the model can accept image input
- but the selected prompt/schema/parser contract is still wrong for the model
  family

## Docs-Reviewed Target Matrix

This umbrella should explicitly investigate and classify at least the
following docs-reviewed families:

### Qwen

- current Alibaba / Model Studio OpenAI-compatible Qwen-VL surfaces such as:
  - `qwen-vl-plus`
  - `qwen-vl-max`
  - Qwen2.5-VL-backed snapshots
  - `qwen3-vl-plus`
  - `qwen3-vl-flash`
  - Qwen3-VL instruct/thinking variants such as 8B / 32B / 30B / 235B lines
- adjacent multimodal Qwen families such as Qwen3.5-Plus if current docs
  position them as stronger successors for image/video understanding
- decide whether OCR/document-specialized variants belong:
  - in staged compare
  - in a separate document-oriented profile
  - or in explicit "not compare-suitable" exclusions

### Anthropic

- current Claude models that officially support image input
- determine whether Claude families can share one profile or need:
  - a broader compare profile
  - a stricter JSON-repair profile
  - or a transport/provider-specific parser boundary

### OpenAI

- current image-input OpenAI families such as:
  - GPT-4o
  - GPT-4.1
  - GPT-4o-mini
  - newer GPT-5 image-input families where relevant to the bounded compare path
- determine whether the existing generic contract is enough or whether
  OpenAI-backed compare flows deserve their own profile tuned for:
  - strict structured output
  - smaller/minified model variants
  - patch/tile-based image sizing behavior

### NVIDIA

- NVIDIA-hosted VLM families that are credible bounded compare candidates,
  such as:
  - Nemotron Nano VL
  - Cosmos Reason VLM lines
- explicitly classify document/retrieval/embedding-oriented NVIDIA visual
  models so the repo does not silently treat them as general staged-compare
  backends when they are actually:
  - OCR/document parsers
  - rerankers
  - embedders
  - retrieval components

## Business Outcome

If this umbrella is done correctly, the repo gains:

- a broader but still deliberate external `vision_contract_profile` vocabulary
- deterministic model-family routing for additional external multimodal models
- a documented distinction between:
  - compare-suitable families
  - document-specialized families
  - retrieval/embedding/rerank families that should not reuse compare profiles
- clearer harness/provider notes that separate:
  - docs-reviewed support
  - automated harness evidence
  - operator-reported behavior

## Scope

This umbrella covers:

- expanding the `vision_contract_profile` vocabulary beyond the initial
  two-profile split from `TASK-139`
- adding deterministic family/profile resolution for the next target families
- adding transport support only where it is necessary to exercise the profile
  system for documented provider APIs
- prompt/schema/request routing for those profiles
- parse/repair/diagnostic routing for those profiles
- harness evidence, provider notes, `.env.example`, launch helpers, and client
  config docs for the new profile matrix

This umbrella does **not** cover:

- unbounded provider-catalog expansion for every multimodal API on the market
- ranking/recommending models before there is explicit harness evidence
- turning document/OCR/retrieval visual models into fake staged-compare
  candidates just because they accept images
- redesigning the truth-layer or hybrid-loop ownership model

## Acceptance Criteria

- the repo has a documented next-generation external
  `vision_contract_profile` matrix, not just `generic_full` plus one
  Google-family compare profile
- Qwen-VL families are classified explicitly enough that:
  - legacy `qwen-vl-plus` / `qwen-vl-max`
  - Qwen2.5-VL
  - Qwen3-VL
  do not all silently collapse into one unexamined generic profile
- Anthropic, OpenAI, and NVIDIA vision-capable families each have an explicit
  product decision:
  - supported with one profile
  - supported with several profiles
  - or documented as out of scope / not compare-suitable
- diagnostics and harness results expose the selected
  `vision_contract_profile`
- provider/model notes distinguish:
  - docs-reviewed support
  - harness-ranked evidence
  - operator-reported observations

## Repository Touchpoints

- `server/infrastructure/config.py`
- `server/adapters/mcp/vision/config.py`
- `server/adapters/mcp/vision/runtime.py`
- `server/adapters/mcp/vision/prompting.py`
- `server/adapters/mcp/vision/backends.py`
- `server/adapters/mcp/vision/parsing.py`
- `server/adapters/mcp/sampling/result_types.py`
- `tests/unit/adapters/mcp/test_vision_runtime_config.py`
- `tests/unit/adapters/mcp/test_vision_prompting.py`
- `tests/unit/adapters/mcp/test_vision_parsing.py`
- `tests/unit/adapters/mcp/test_vision_external_backend.py`
- `tests/e2e/vision/`
- `scripts/vision_harness.py`
- `scripts/run_streamable_openrouter.sh`
- `tests/unit/scripts/test_script_tooling.py`
- `.env.example`
- `README.md`
- `_docs/_VISION/README.md`
- `_docs/_VISION/HYBRID_LOOP_REAL_CREATURE_EVAL.md`
- `_docs/_VISION/REFERENCE_GUIDED_CREATURE_TEST_PROMPT.md`
- `_docs/_VISION/CROSS_DOMAIN_REFINEMENT_ROUTING_EVAL.md`
- `_docs/_MCP_SERVER/README.md`
- `_docs/_MCP_SERVER/MCP_CLIENT_CONFIG_EXAMPLES.md`
- `_docs/_TASKS/README.md`

## Docs To Update

- `.env.example`
- `README.md`
- `_docs/_VISION/README.md`
- `_docs/_VISION/HYBRID_LOOP_REAL_CREATURE_EVAL.md`
- `_docs/_VISION/REFERENCE_GUIDED_CREATURE_TEST_PROMPT.md`
- `_docs/_VISION/CROSS_DOMAIN_REFINEMENT_ROUTING_EVAL.md`
- `_docs/_MCP_SERVER/README.md`
- `_docs/_MCP_SERVER/MCP_CLIENT_CONFIG_EXAMPLES.md`
- `_docs/_TASKS/README.md`

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_vision_runtime_config.py`
- `tests/unit/adapters/mcp/test_vision_prompting.py`
- `tests/unit/adapters/mcp/test_vision_parsing.py`
- `tests/unit/adapters/mcp/test_vision_external_backend.py`
- `tests/unit/scripts/test_script_tooling.py`
- targeted `tests/e2e/vision/` coverage for each promoted external family

## Changelog Impact

- add one dedicated `_docs/_CHANGELOG/*` entry when the first implementation
  slice under this umbrella ships

## Status / Board Update

- track this as the next board-level follow-on after `TASK-139`
- keep it separate from generic provider-catalog work; this umbrella is about
  bounded compare-contract architecture and evidence discipline

## Execution Structure

| Order | Planned Slice | Purpose |
|------|---------------|---------|
| 1 | [TASK-140-01](./TASK-140-01_Qwen_Family_Contract_Profile_Matrix_And_Routing.md) | Classify Qwen multimodal families and route them through explicit compare/document/exclusion profiles instead of one generic bucket |
| 2 | [TASK-140-02](./TASK-140-02_Anthropic_Claude_Vision_Profiles_And_Transport_Integration.md) | Add Anthropic-specific provider/config/request/parser integration with explicit Claude profile policy |
| 3 | [TASK-140-03](./TASK-140-03_OpenAI_Image_Input_Profiles_And_Structured_Compare_Policy.md) | Decide whether OpenAI families can reuse generic behavior or need stricter family-specific compare profiles |
| 4 | [TASK-140-04](./TASK-140-04_NVIDIA_VLM_Support_And_Exclusion_Policy.md) | Classify NVIDIA VLMs into compare-capable versus document/retrieval-only paths and integrate only the bounded compare-suitable subset |
| 5 | [TASK-140-05](./TASK-140-05_Regression_Harness_Provider_Notes_And_Operator_Guidance_For_Expanded_Profiles.md) | Keep automated coverage, harness evidence, docs, launch helpers, `.env.example`, and client examples aligned with the broader profile matrix |
