# SPDX-FileCopyrightText: 2024-2026 Patryk Ciechański
# SPDX-License-Identifier: Apache-2.0

"""Reference-understanding gate proposal helpers."""

from __future__ import annotations

import re
from collections.abc import Mapping, Sequence
from typing import Any

_CREATURE_TAIL_PROFILE_LABEL_HINTS = ("tail", "appendage")
_CREATURE_TAIL_PROFILE_SHAPE_HINTS = (
    "arc",
    "arched",
    "bushy",
    "curl",
    "curled",
    "curve",
    "curved",
    "swept",
    "wrap",
    "wrapping",
)


def derive_tail_profile_gate_proposals(parts: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    """Derive generic shape-profile gates for reference parts with explicit tail-arc hints."""

    proposals: list[dict[str, Any]] = []
    seen_targets: set[str] = set()
    for item in parts:
        part_label = str(item.get("part_label") or "").strip()
        target_label = str(item.get("target_label") or part_label).strip() or "tail_profile"
        construction_hint = str(item.get("construction_hint") or "").strip()
        combined_label = " ".join((part_label, target_label)).lower()
        combined_profile_text = " ".join((part_label, target_label, construction_hint)).lower()
        if not any(hint in combined_label for hint in _CREATURE_TAIL_PROFILE_LABEL_HINTS):
            continue
        if not any(hint in combined_profile_text for hint in _CREATURE_TAIL_PROFILE_SHAPE_HINTS):
            continue

        gate_target = "tail_profile" if target_label in {"tail", "tail_mass", "tail_core"} else target_label
        if gate_target in seen_targets:
            continue
        seen_targets.add(gate_target)
        gate_slug = re.sub(r"[^a-z0-9]+", "_", gate_target.lower()).strip("_") or "tail_profile"
        proposals.append(
            {
                "gate_id": f"shape_profile_{gate_slug}",
                "gate_type": "shape_profile",
                "label": "Tail follows the curved reference profile",
                "target_kind": "reference_part",
                "target_label": gate_target,
                "priority": item.get("priority") or "normal",
                "allowed_correction_families": ["secondary_parts", "inspect_validate"],
                "evidence_requirements": [
                    {
                        "evidence_kind": "mesh_metric",
                        "required": True,
                        "reason": "Curved tail profile must be verified by deterministic mesh/profile evidence.",
                    }
                ],
                "rationale": construction_hint
                or "Reference understanding marked the tail as a curved or arched profile requirement.",
            }
        )
    return proposals
