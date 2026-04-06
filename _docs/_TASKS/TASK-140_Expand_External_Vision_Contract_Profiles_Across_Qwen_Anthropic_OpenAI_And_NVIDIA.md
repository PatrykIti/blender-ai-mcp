# TASK-140: Expand External Vision Contract Profiles Across Qwen, Anthropic, OpenAI, and NVIDIA

**Status:** ⏳ To Do
**Priority:** 🔴 High
**Category:** Vision Runtime / External Model-Family Reliability
**Estimated Effort:** Large
**Dependencies:** TASK-139

## Objective

Extend the external `vision_contract_profile` architecture introduced in
`TASK-139` beyond the current `generic_full` and
`google_family_compare` split so the runtime can choose prompt/schema/parser
behavior more precisely for additional multimodal model families routed through
the existing provider surface only, especially OpenRouter-hosted model ids on
the current `openai_compatible_external` path.

This umbrella should cover the next docs-reviewed external model-family
targets on the current provider surface:

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

## Execution Guardrail

`TASK-140` is about model-family contract selection only.

This umbrella may:

- add new `vision_contract_profile` values
- add deterministic model-family matching rules
- refine prompt/schema/parser/diagnostic behavior for those profiles
- document that some families remain on `generic_full` or are not compare-suitable
  on the current provider surface

This umbrella must **not**:

- add new `VISION_EXTERNAL_PROVIDER` values
- add new provider aliases or new provider-specific env/config families
- add new backend kinds or new first-class transport/provider branches
- turn unsupported family/provider combinations into provider-integration work

If a model family cannot be exercised correctly through the current provider
inventory, record that as a bounded follow-on or explicit unsupported boundary
instead of broadening provider scope inside `TASK-140`.

## Current Code Baseline

Current code intentionally starts from a small, closed vocabulary:

- `VISION_EXTERNAL_PROVIDER` / `VisionExternalProviderName`:
  - `generic`
  - `openrouter`
  - `google_ai_studio`
- `VISION_EXTERNAL_CONTRACT_PROFILE` / `VisionContractProfile`:
  - `generic_full`
  - `google_family_compare`

That baseline is the starting point for `TASK-140`.

Within this umbrella:

- provider vocabulary stays closed
- provider validators stay aligned with the existing three provider values
- typed-surface expansion happens through `VisionContractProfile` and
  `VisionAssistContract.vision_contract_profile`, not through new provider
  enums

## Backend Boundary

Current external backend wiring is also intentionally narrow:

- external family work stays on the shared
  `openai_compatible_external` backend path
- `google_ai_studio` is the only current dedicated transport/request branch in
  `server/adapters/mcp/vision/backends.py`
- `openrouter` stays on the same shared backend path and only adds
  provider-scoped headers plus strict JSON-schema response formatting
- the current tests in `tests/unit/adapters/mcp/test_vision_external_backend.py`
  already lock that boundary in place

Therefore `TASK-140` backend work is limited to:

- profile-aware prompt/schema/request behavior inside the current backend seam
- parser/diagnostic behavior keyed by `vision_contract_profile`
- family-specific evidence that a model/profile combination works or fails on
  the current shared backend path

`TASK-140` backend work does **not** include:

- first-class provider integration
- new transport branches for each model family
- moving profile-selection policy into backend/provider branching

## Business Problem

After `TASK-139`, the repo has a correct architectural seam, but the profile
space is still too coarse for the families we want to test on the current
provider inventory.

The current model is:

- `generic_full`
- `google_family_compare`

That is enough to stop treating OpenRouter-hosted Google-family models as
generic OpenAI-compatible models, but it is not enough for the next wave of
family-contract work because the upcoming families differ materially in:

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
  - or an explicitly documented "not reliable on the current external
    transport path" boundary

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
- deterministic model-family routing for additional multimodal models on the
  current provider surface
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
  on the existing provider surface, especially OpenRouter-hosted model ids
- carrying new profile vocabulary through the typed runtime and public result
  surfaces that expose `vision_contract_profile`
- prompt/schema/request routing for those profiles on the current external
  runtime path
- parse/repair/diagnostic routing for those profiles
- harness evidence, provider notes, `.env.example`, launch helpers, and client
  config docs for the new profile matrix

This umbrella does **not** cover:

- unbounded provider-catalog expansion for every multimodal API on the market
- first-class provider branches for additional vendors or model families
- new `VISION_EXTERNAL_PROVIDER` values, provider aliases, or provider-specific
  env/config families
- new backend kinds beyond the current runtime inventory
- ranking/recommending models before there is explicit harness evidence
- turning document/OCR/retrieval visual models into fake staged-compare
  candidates just because they accept images
- redesigning the truth-layer or hybrid-loop ownership model

## Acceptance Criteria

- the repo has a documented next-generation external
  `vision_contract_profile` matrix, not just `generic_full` plus one
  Google-family compare profile
- any newly introduced external `vision_contract_profile` values are carried
  through the full typed surface:
  - `VisionContractProfile` runtime/config vocabulary and validators
  - public `VisionAssistContract.vision_contract_profile` result contracts
  - automated regression coverage for those public result surfaces
- if `server/infrastructure/config.py` or `server/adapters/mcp/vision/config.py`
  change under this umbrella, those changes are limited to
  `VISION_EXTERNAL_CONTRACT_PROFILE` / `VisionContractProfile` handling; the
  `VISION_EXTERNAL_PROVIDER` vocabulary remains `generic`, `openrouter`, and
  `google_ai_studio`
- if `server/adapters/mcp/vision/backends.py` changes under this umbrella,
  those changes stay inside the current shared
  `openai_compatible_external` backend seam:
  - `google_ai_studio` remains the only dedicated transport branch
  - `openrouter` remains a shared-path backend with provider headers and strict
    schema, not a new provider integration path
  - family behavior stays driven by `vision_contract_profile` plus
    prompting/parsing policy
- the `TASK-139` precedence model remains intact:
  - explicit override still wins
  - recognized family/model-id routing can select a stricter profile
  - unknown or not-yet-classified families still fall back to `generic_full`
- `TASK-140` can be completed without adding any new provider branch:
  - current provider inventory remains the boundary
  - unsupported combinations are documented explicitly instead of expanding
    provider scope
- Qwen-VL families are classified explicitly enough that:
  - legacy `qwen-vl-plus` / `qwen-vl-max`
  - Qwen2.5-VL
  - Qwen3-VL
  do not all silently collapse into one unexamined generic profile
- Anthropic, OpenAI, and NVIDIA vision-capable families each have an explicit
  product decision:
  - supported on the current external runtime path with one profile
  - supported on the current external runtime path with several profiles
  - or documented as out of scope / not compare-suitable on that path
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
- `tests/unit/adapters/mcp/test_vision_result_types.py`
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
- `tests/unit/adapters/mcp/test_vision_result_types.py`
- `tests/unit/scripts/test_script_tooling.py`
- targeted `tests/e2e/vision/` coverage for each promoted external family

## Changelog Impact

- add one dedicated `_docs/_CHANGELOG/*` entry when the first implementation
  slice under this umbrella ships

## Status / Board Update

- track this as the next board-level follow-on after `TASK-139`
- keep it separate from generic provider-catalog or new-provider integration
  work; this umbrella is about bounded compare-contract architecture and
  evidence discipline for model families on the existing provider surface

## Execution Structure

| Order | Planned Slice | Purpose |
|------|---------------|---------|
| 1 | [TASK-140-01](./TASK-140-01_Qwen_Family_Contract_Profile_Matrix_And_Routing.md) | Classify Qwen multimodal families and route them through explicit compare/document/exclusion profiles on the existing provider surface instead of one generic bucket |
| 2 | [TASK-140-02](./TASK-140-02_Anthropic_Claude_Family_Contracts_On_The_Existing_Provider_Surface.md) | Define Claude-family contract routing and diagnostics on the current provider surface instead of defaulting to one generic contract or expanding provider scope |
| 3 | [TASK-140-03](./TASK-140-03_OpenAI_Image_Input_Profiles_And_Structured_Compare_Policy.md) | Decide whether OpenAI families can reuse generic behavior or need stricter family-specific compare profiles on the existing provider surface |
| 4 | [TASK-140-04](./TASK-140-04_NVIDIA_VLM_Support_And_Exclusion_Policy.md) | Classify NVIDIA VLMs into compare-capable versus document/retrieval-only paths and integrate only the bounded compare-suitable subset on the existing provider surface |
| 5 | [TASK-140-05](./TASK-140-05_Regression_Harness_Provider_Notes_And_Operator_Guidance_For_Expanded_Profiles.md) | Keep automated coverage, harness evidence, docs, launch helpers, `.env.example`, and client examples aligned with the broader profile matrix |
