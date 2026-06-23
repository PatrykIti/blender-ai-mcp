# TASK-187: External Vision Model Evidence And Profile Promotion Governance

**Follow-on After:** [TASK-140](./TASK-140_Expand_External_Vision_Contract_Profiles_Across_Qwen_Anthropic_OpenAI_And_NVIDIA.md)
**Status:** ⏳ To Do
**Priority:** 🔴 High
**Category:** Vision Runtime / External Model Governance

## Objective

Create the evidence lane for promoting external vision models, reviewed
fallback capability profiles, or new `VisionContractProfile` values after the
`TASK-140` capability-first closeout.

Future Qwen, Anthropic, OpenAI, NVIDIA, or other model-family work should start
here instead of reopening the old `TASK-140-01` through `TASK-140-05` planning
tree.

## Repository Touchpoints

| Path | Expected Ownership |
|---|---|
| `server/adapters/mcp/vision/config.py` | add or preserve typed capability/profile vocabulary only when evidence proves a real contract delta |
| `server/adapters/mcp/vision/runtime.py` | adjust profile/fallback precedence if promoted evidence requires it |
| `server/adapters/mcp/vision/backends.py` | keep request policy capability-driven and bounded |
| `server/adapters/mcp/vision/model_profiles/` | promote reviewed fallback profiles after docs/harness/operator evidence |
| `server/adapters/mcp/sampling/result_types.py` | keep public profile/capability summaries aligned with any promoted vocabulary |
| `scripts/vision_harness.py` | record repeatable live or fixture-backed capability and output evidence |
| `tests/unit/adapters/mcp/` | cover new fallback/profile/request-policy behavior |
| `tests/e2e/vision/` | add gated live or fixture-backed coverage when Blender/runtime behavior changes |
| `_docs/_VISION/README.md` | provider/model notes and promotion status |
| `_docs/_MCP_SERVER/README.md` | operator-facing config/runtime contract changes |

## Evidence Requirements

Promotion requires more than provider marketing text or an anecdotal success.
For each candidate model/profile change, collect:

- current provider docs or catalog metadata, with the exact model id
- OpenRouter API metadata when the model is routed through OpenRouter
- reviewed fallback profile fields only when live metadata is unavailable,
  incomplete, or intentionally bypassed
- at least one bounded `scripts/vision_harness.py` smoke or repo-tracked test
  fixture for the target contract shape
- operator notes only as supporting context, not as sole promotion evidence
- regression fixtures for previously observed failure modes such as prose-only
  output, near-JSON drift, truncation, missing image modality, unsupported
  structured output, or mark-id hallucination

## Contract Rules

- Keep `VISION_EXTERNAL_PROVIDER` closed unless a separate provider-integration
  task explicitly owns a new transport branch.
- Prefer capability-driven request policy over family-specific profile
  expansion.
- Add a new `VisionContractProfile` only when tests or harness evidence shows
  the existing `generic_full` / `google_family_compare` split cannot express a
  real runtime contract difference.
- Preserve explicit operator overrides.
- Treat `vision_contract_profile` and model capability summaries as routing and
  diagnostics, not scene truth or quality-gate authority.
- Do not use LaBSE, provider claims, or semantic similarity as evidence that a
  Blender result is correct.

## Tests To Add/Update

- Unit tests for every promoted fallback-profile field or request-policy
  branch.
- Result-contract tests when public capability/profile diagnostics change.
- Harness or fixture-backed tests for model-specific structured-output behavior.
- Optional live OpenRouter smoke only behind explicit env flags and API keys.
- E2E coverage when the change affects Blender scene state, visual marks,
  capture payloads, guided visibility, or client-facing runtime behavior.

## Docs To Update

- `_docs/_VISION/README.md`
- `_docs/_MCP_SERVER/README.md`
- `_docs/_MCP_SERVER/MCP_CLIENT_CONFIG_EXAMPLES.md` when operator config changes
- `_docs/_TASKS/README.md` when the task advances or closes
- `_docs/_CHANGELOG/` when a meaningful promotion or runtime contract change
  ships

## Changelog Impact

Add a dedicated `_docs/_CHANGELOG/*` entry for every promoted runtime contract,
fallback profile batch, or public diagnostics change.

## Acceptance Criteria

- each promoted model/profile decision has current docs/catalog evidence,
  runtime capability evidence, and a repeatable test or harness proof
- unsupported or unstable models are documented explicitly instead of being
  routed silently through a generic optimistic path
- fallback registry entries remain reviewed operational knowledge and stay
  secondary to live OpenRouter metadata when available
- public docs distinguish docs-reviewed support, harness-ranked evidence, live
  smoke, and operator-reported observations
- no model-specific change widens provider vocabulary or scene-truth authority
  by accident

## Validation Commands

- `git diff --check`
- targeted unit tests for the changed runtime/request-policy/result-contract
  area
- targeted harness or fixture run proving the promoted model/profile behavior
- `PYTHONPATH=. poetry run pytest ./tests/unit` before closing implementation
  work
