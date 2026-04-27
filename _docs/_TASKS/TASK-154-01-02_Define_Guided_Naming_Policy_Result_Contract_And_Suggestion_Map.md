# TASK-154-01-02: Define Guided Naming Policy Result Contract And Suggestion Map

**Parent:** [TASK-154-01](./TASK-154-01_Naming_Policy_Contract_And_Role_Based_Suggestion_Vocabulary.md)
**Depends On:** [TASK-154-01-01](./TASK-154-01-01_Audit_Current_Naming_Drift_And_Runtime_Hook_Points.md)
**Status:** ✅ Done
**Priority:** 🔴 High

## Objective

Define the shared result envelope for guided naming decisions and the
role/domain-aware suggestion map that powers warnings and blocks.

## Repository Touchpoints

- `server/adapters/mcp/guided_naming_policy.py`
- `server/adapters/mcp/session_capabilities.py`
- `_docs/_MCP_SERVER/README.md`
- `_docs/_PROMPTS/README.md`
- `tests/unit/adapters/mcp/test_guided_flow_domain_profiles.py`

## Planned Code Shape

```python
@dataclass(frozen=True)
class GuidedNamingPolicyDecision:
    status: Literal["allowed", "warning", "blocked"]
    message: str | None
    reason_code: str | None
    suggested_names: tuple[str, ...]
    canonical_pattern: str | None
    role: str | None
    domain_profile: str | None
```

## Detailed Implementation Notes

- the result contract should be rich enough for:
  - direct user/model-facing error/warning messages
  - transport/E2E assertions
  - future telemetry or troubleshooting
- the suggestion map should be explicit, not inferred from raw role ids at
  render time
- example suggestions:
  - `body_core` -> `Body`
  - `head_mass` -> `Head`
  - `foreleg_pair` -> `ForeLeg_L`, `ForeLeg_R`
  - `hindleg_pair` -> `HindLeg_L`, `HindLeg_R`
  - `tail_mass` -> `Tail`
  - `snout_mass` -> `Snout`
  - `roof_mass` -> `Roof`
  - `main_volume` -> `MainVolume`
  - `footprint_mass` -> `Footprint`
  - `facade_opening` -> `WindowOpening_A`, `DoorOpening_A`
  - `support_element` -> `Support_A`, `Support_B`
  - `detail_element` -> `Detail_A`

## Pseudocode Sketch

```python
SUGGESTED_NAMES = {
    "creature": {
        "body_core": ("Body",),
        "head_mass": ("Head",),
        "foreleg_pair": ("ForeLeg_L", "ForeLeg_R"),
    },
    "building": {
        "main_volume": ("MainVolume",),
        "roof_mass": ("Roof",),
        "facade_opening": ("WindowOpening_A", "DoorOpening_A"),
    },
}
```

## Planned Unit Test Scenarios

- every primary creature role has at least one canonical suggestion
- every primary building role has at least one canonical suggestion
- pair roles return multiple suggestions in stable order
- unknown role/domain falls back to a bounded generic decision instead of
  exploding
- reason codes are deterministic enough for transport assertions

## Acceptance Criteria

- the policy result contract and suggestion map are explicit and documented

## Docs To Update

- `_docs/_MCP_SERVER/README.md`
- `_docs/_PROMPTS/README.md`

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_guided_naming_policy.py`
- `tests/unit/adapters/mcp/test_guided_flow_domain_profiles.py`

## Changelog Impact

- include in the parent TASK-154 changelog entry

## Completion Summary

- delivered the structured naming decision contract, canonical patterns, reason
  codes, and role/domain-specific suggested names
