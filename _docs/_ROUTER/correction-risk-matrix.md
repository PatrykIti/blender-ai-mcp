# Correction Risk Matrix

Code-backed matrix for `TASK-096-01`.

This matrix classifies current router correction behavior by type and blast radius.

## Matrix

| Category | Current signal examples | Risk | Auto-safe | Rationale |
|---|---|---|---|---|
| `precondition_mode` | `mode_switch:OBJECT->EDIT`, `injected_mode_switch` | `low` | yes | Deterministic mode repair with narrow operational blast radius |
| `precondition_selection` | `auto_select_all`, `injected_selection` | `medium` | no | Selection injection changes execution target and may affect unintended geometry |
| `parameter_alias` | `alias_width->offset`, `alias_depth->move` | `low` | yes | Alias normalization preserves intent while translating to canonical parameters |
| `parameter_clamp` | `clamp_offset:100->1`, `clamp_number_cuts:100->6` | `medium` | no | Clamping changes user-supplied magnitude and can materially alter the resulting shape |
| `firewall_modification` | `firewall_auto_fix`, `firewall_modified` | `high` | no | Firewall-driven rewrites protect execution but materially change the requested path |
| `tool_override` | `override:extrude_for_screen` | `high` | no | Tool substitution replaces the requested action with a different execution path |
| `workflow_expansion` | `workflow:<name>:step_n` | `high` | no | Workflow expansion fans one intent into multiple steps with broad scene impact |
| `block` | firewall `block` action | `critical` | no | Blocking signals unsafe or unacceptable execution conditions |
| `unknown` | any uncatalogued signal | `high` | no | Unknown correction types must not be auto-applied by default |

## Current Code Sources

### ToolCorrectionEngine

File:
- `server/router/application/engines/tool_correction_engine.py`

Observed signal families:
- `mode_switch:*`
- `auto_select_all`
- `alias_*`
- `clamp_*`
- `injected_mode_switch`
- `injected_selection`

### ErrorFirewall

File:
- `server/router/application/engines/error_firewall.py`

Observed action families:
- `allow`
- `auto_fix`
- `modify`
- `block`

### ToolOverrideEngine

File:
- `server/router/application/engines/tool_override_engine.py`

Observed signal family:
- `override:<rule_name>`

### Workflow Expansion

File:
- `server/router/application/router.py`

Observed signal family:
- `workflow:<workflow_name>:step_n`

## Policy Implication

This matrix is intentionally conservative:

- only low-risk deterministic translations should be considered auto-safe by default
- medium-risk corrections should generally move toward clarification unless later policy explicitly allows them
- high-risk and critical categories must not rely on raw semantic confidence alone

This matrix is the input for:

- `TASK-096-02` confidence normalization
- `TASK-096-03` auto-fix / ask / block policy decisions
