# TASK-139: Model-Family-Specific Vision Contract Profiles for External Runtimes

**Status:** ✅ Done
**Priority:** 🔴 High
**Category:** Vision Runtime / External Provider Reliability
**Estimated Effort:** Large
**Dependencies:** TASK-121-04-01-03, TASK-121-04-01-04, TASK-121-04-01-05, TASK-123-01

**Completion Summary:** External vision runtimes now resolve one explicit
`vision_contract_profile` independently from transport/provider identity.
OpenRouter-hosted Google-family models can reuse the narrow staged-compare
prompt/schema/parser path without pretending to be Google AI Studio, while
operator docs, harness config, diagnostics, and MCP client examples now expose
the same override/auto-match story.

## Terminology Guardrail

In this task family, "vision contract profile" means the prompt/schema/parser
behavior selected for the external vision runtime. It is intentionally separate
from MCP surface contract profiles / contract lines used elsewhere in the repo.

When this wave lands, prefer names such as:

- `VisionContractProfile`
- `vision_contract_profile`
- `VISION_EXTERNAL_CONTRACT_PROFILE`

## Objective

Decouple external vision contract behavior from transport-provider selection so
the MCP server can choose prompt/schema/parse-repair behavior by model family
or explicit vision contract profile, not only by provider name.

The immediate goal is to stop treating all OpenRouter models as one behavioral
class and to support narrower staged-compare contracts for Google-family models
served through OpenRouter, such as Gemma, when current evidence shows the
generic contract is too brittle.

## Business Problem

The current external vision path works at the transport level, but its
structured-output behavior is still routed too coarsely.

Current code audit shows:

- `Config` exposes the current external vision env/config surface, but has no
  first-class `VISION_EXTERNAL_CONTRACT_PROFILE` override field yet
- `VisionOpenAICompatibleConfig` models the external runtime by provider name,
  base URL, model, and auth, but has no explicit `vision_contract_profile`
  concept
- `build_vision_runtime_config(...)` resolves runtime behavior by provider
  identity and model presence, not by model family/capability-based vision
  contract profile
- `build_vision_system_prompt(...)` and `build_vision_payload_text(...)` only
  enable the narrow staged compare contract when
  `provider_name == "google_ai_studio"`
- `parse_vision_output_text(...)` and `diagnose_vision_output_text(...)` only
  enable provider-specific repair for `google_ai_studio`
- `OpenAICompatibleVisionBackend` therefore treats OpenRouter Google-family
  models the same as generic OpenAI-compatible models, even when those models
  would benefit from the narrower compare contract and the same JSON-repair
  behavior already built for Gemini

That leaves the product with an avoidable failure mode:

- the transport/provider works
- JSON validation still works and correctly rejects prose
- but the selected prompt/schema/parser contract is wrong for the model family
- so structured staged loops fail even though a better contract path already
  exists elsewhere in the codebase

## Current Runtime Baseline

The repo already has a useful bounded vision architecture:

This umbrella builds on the already-delivered baseline from:

- `TASK-121-04-01-03` for the OpenRouter provider path
- `TASK-121-04-01-04` for the Google AI Studio / Gemini provider path
- `TASK-121-04-01-05` for the Gemini narrow compare contract and parse-repair
- `TASK-123-01` for explicit external-provider precedence and generic-fallback
  resolution

- typed runtime config for local, MLX, and external providers
- provider-specific transport handling for OpenRouter and Google AI Studio
- a provider-specific narrow compare contract for Gemini / Google AI Studio
- JSON diagnostics that classify `container_shape` and `payload_shape`
- staged compare and iterate flows that fail loudly when the backend does not
  return valid JSON

That baseline matters because this umbrella should refine contract/profile
selection, not redesign the whole vision stack.

## Current Drift To Resolve

The remaining drift is now architectural rather than transport-level:

- contract selection is still tied to provider identity instead of model
  behavior/capability
- Google-family models behind OpenRouter cannot opt into the narrower compare
  contract without pretending to be a different provider
- parse-repair for near-JSON / truncated compare output is not reusable across
  providers when the model family would benefit from the same vision contract
  profile behavior
- diagnostics expose the failure clearly, but they do not yet say which
  `vision_contract_profile` was selected and whether that profile was likely
  mismatched
- operator guidance and provider notes can record instability, but the runtime
  still lacks a first-class mechanism for turning those observations into
  vision-contract-profile selection

## Business Outcome

If this umbrella is done correctly, the repo gains:

- one explicit concept of external vision contract profiles, separate from
  transport-provider identity
- deterministic routing of prompt/schema/parse-repair behavior by explicit
  override or model-family match
- a credible path for OpenRouter Google-family models to use the same narrow
  staged-compare contract already proven useful on Google AI Studio / Gemini
- clearer diagnostics and operator guidance when a model/provider combination is
  still unstable

## Scope

This umbrella covers:

- introducing one explicit flat config/env surface for a vision-contract-profile
  override via `VISION_EXTERNAL_CONTRACT_PROFILE`, then carrying that choice
  into typed runtime config
- introducing a typed `vision_contract_profile` concept for external vision
  runtimes
- deterministic vision-contract-profile selection and precedence rules
- prompt/schema routing by vision contract profile instead of provider only
- parse/repair/diagnostics routing by vision contract profile instead of
  provider only
- regression harness/docs updates for operator-visible provider/model notes

This umbrella does **not** cover:

- redesigning local MLX or Transformers transport paths
- changing the truth-layer ownership model
- turning prose responses into accepted success payloads
- broad provider-catalog ranking work outside the bounded vision compare path

## Acceptance Criteria

- the external vision runtime has one explicit `vision_contract_profile`
  concept
- explicit `VISION_EXTERNAL_CONTRACT_PROFILE` override has one first-class
  config/env surface that feeds runtime resolution deterministically
- vision-contract-profile selection can be driven by explicit override and by
  deterministic model-family matching rules
- OpenRouter Google-family models can use a narrow staged-compare profile
  without being forced into the Google AI Studio transport path
- parse-repair for compare flows is reusable by `vision_contract_profile`
  rather than being hard-coded only to `google_ai_studio`
- the harness config/build path and operator-facing provider notes reflect the
  same vision-contract-profile assumptions as the runtime/docs path
- operator-facing launch helpers such as
  `scripts/run_streamable_openrouter.sh` reflect the same
  vision-contract-profile-sensitive env/config guidance as the runtime docs and
  client examples
- diagnostics, tests, and docs make the selected `vision_contract_profile` and
  its known limitations visible

## Repository Touchpoints

- `server/infrastructure/config.py`
- `server/adapters/mcp/vision/config.py`
- `server/adapters/mcp/vision/runtime.py`
- `server/adapters/mcp/vision/prompting.py`
- `server/adapters/mcp/vision/backends.py`
- `server/adapters/mcp/vision/parsing.py`
- `tests/unit/adapters/mcp/test_vision_runtime_config.py`
- `tests/unit/adapters/mcp/test_vision_prompting.py`
- `tests/unit/adapters/mcp/test_vision_parsing.py`
- `tests/unit/adapters/mcp/test_vision_external_backend.py`
- `scripts/vision_harness.py`
- `scripts/run_streamable_openrouter.sh`
- `tests/unit/scripts/test_script_tooling.py`
- `tests/e2e/vision/`
- `_docs/_VISION/README.md`
- `_docs/_MCP_SERVER/README.md`
- `_docs/_MCP_SERVER/MCP_CLIENT_CONFIG_EXAMPLES.md`
- `README.md`
- `_docs/_TASKS/README.md`

## Docs To Update

- `_docs/_VISION/README.md`
- `_docs/_MCP_SERVER/README.md`
- `_docs/_MCP_SERVER/MCP_CLIENT_CONFIG_EXAMPLES.md`
- `README.md`
- `_docs/_TASKS/README.md`

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_vision_runtime_config.py`
- `tests/unit/adapters/mcp/test_vision_prompting.py`
- `tests/unit/adapters/mcp/test_vision_parsing.py`
- `tests/unit/adapters/mcp/test_vision_external_backend.py`
- `tests/unit/scripts/test_script_tooling.py`
- focused `tests/e2e/vision/` compare-loop coverage for affected profiles

## Changelog Impact

- add a dedicated `_docs/_CHANGELOG/*` entry when the first implementation
  slice under this umbrella ships

## Status / Board Update

- promote this as a board-level follow-on under the Vision & Hybrid Loop track
- keep it separate from domain reconstruction umbrellas; this is contract
  architecture for the vision stack itself

## Execution Structure

| Order | Subtask | Purpose |
|------|---------|---------|
| 1 | [TASK-139-01](./TASK-139-01_Runtime_Contract_Profile_Model_And_Resolution.md) | Add a typed `vision_contract_profile` concept and deterministic runtime/profile selection rules |
| 2 | [TASK-139-02](./TASK-139-02_Prompt_Schema_And_Request_Routing_By_Contract_Profile.md) | Route prompt/schema/request behavior by the selected vision contract profile instead of provider-only gates |
| 3 | [TASK-139-03](./TASK-139-03_Parser_Repair_And_Diagnostics_By_Contract_Profile.md) | Reuse parse/repair/diagnostic behavior by vision contract profile, including OpenRouter Google-family compare flows |
| 4 | [TASK-139-04](./TASK-139-04_Regression_Harness_And_Documentation_For_Contract_Profiles.md) | Add focused runtime regressions, harness evidence, and provider-note/doc updates |
