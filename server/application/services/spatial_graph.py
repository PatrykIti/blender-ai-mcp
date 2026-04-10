"""Shared spatial scope/relation builders for guided scene truth surfaces."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, Callable, Literal, Protocol

_ANCHOR_ROLE_HINTS: tuple[tuple[str, int], ...] = (
    ("body", 50),
    ("torso", 45),
    ("trunk", 45),
    ("head", 40),
    ("skull", 35),
    ("core", 30),
    ("root", 25),
    ("base", 20),
)
_ACCESSORY_ROLE_HINTS: tuple[str, ...] = (
    "ear",
    "eye",
    "nose",
    "snout",
    "paw",
    "foot",
    "tail",
    "horn",
    "antler",
    "whisker",
)
_HEAD_ROLE_HINTS: tuple[str, ...] = ("head", "skull", "face")
_BODY_ROLE_HINTS: tuple[str, ...] = ("body", "torso", "trunk", "chest", "abdomen", "pelvis", "hip")
_SNOUT_ROLE_HINTS: tuple[str, ...] = ("snout", "muzzle")
_NOSE_ROLE_HINTS: tuple[str, ...] = ("nose", "nostril")
_EYE_ROLE_HINTS: tuple[str, ...] = ("eye",)
_FACE_ATTACHMENT_HINTS: tuple[str, ...] = ("ear", "eye", "nose", "snout", "whisker")
_TAIL_ROLE_HINTS: tuple[str, ...] = ("tail",)
_LIMB_ROLE_HINTS: tuple[str, ...] = (
    "limb",
    "leg",
    "arm",
    "paw",
    "foot",
    "hand",
    "hoof",
    "thigh",
    "shin",
    "calf",
    "foreleg",
    "hindleg",
    "forelimb",
    "hindlimb",
    "forearm",
    "lowerarm",
    "upperarm",
    "lowerleg",
    "upperleg",
)
_DISTAL_LIMB_HINTS: tuple[str, ...] = (
    "paw",
    "foot",
    "hand",
    "hoof",
    "shin",
    "calf",
    "forearm",
    "lowerarm",
    "lowerleg",
)
_PROXIMAL_LIMB_HINTS: tuple[str, ...] = ("upperarm", "upperleg", "thigh", "arm", "leg", "forelimb", "hindlimb")
_SUPPORT_ROLE_HINTS: tuple[str, ...] = ("base", "floor", "ground", "pedestal", "stand", "platform", "support")
_SYMMETRY_GOAL_HINTS: tuple[str, ...] = ("symmetry", "symmetric", "mirror", "mirrored", "bilateral", "left", "right")
_SUPPORT_GOAL_HINTS: tuple[str, ...] = ("support", "supported", "ground", "floor", "feet", "legs", "seat", "rest")

_ScopeKind = Literal["single_object", "object_set", "collection", "scene"]
_ObjectRole = Literal[
    "anchor_core",
    "support_base",
    "attached_mass",
    "attached_appendage",
    "accessory_feature",
    "structural_peer",
    "scene_member",
]
_PairSource = Literal["required_creature_seam", "primary_to_other", "support_candidate", "symmetry_candidate"]
_PairingStrategy = Literal["none", "primary_to_others", "required_creature_seams", "guided_spatial_pairs"]
_CreatureRelationKind = Literal["embedded_attachment", "seated_attachment", "segment_attachment"]
_CreatureSeamKind = Literal["face_head", "nose_snout", "head_body", "tail_body", "limb_body", "limb_segment"]


class _SceneSpatialReader(Protocol):
    def get_bounding_box(self, object_name: str, world_space: bool = True) -> dict[str, Any]: ...

    def measure_gap(self, from_object: str, to_object: str, tolerance: float = 0.0001) -> dict[str, Any]: ...

    def measure_alignment(
        self,
        from_object: str,
        to_object: str,
        axes: list[str] | None = None,
        reference: str = "CENTER",
        tolerance: float = 0.0001,
    ) -> dict[str, Any]: ...

    def measure_overlap(self, from_object: str, to_object: str, tolerance: float = 0.0001) -> dict[str, Any]: ...

    def assert_contact(
        self,
        from_object: str,
        to_object: str,
        max_gap: float = 0.0001,
        allow_overlap: bool = False,
    ) -> dict[str, Any]: ...

    def assert_symmetry(
        self,
        left_object: str,
        right_object: str,
        axis: str = "X",
        mirror_coordinate: float = 0.0,
        tolerance: float = 0.0001,
    ) -> dict[str, Any]: ...


@dataclass(frozen=True)
class _PlannedCreatureSeam:
    part_object: str
    anchor_object: str
    relation_kind: _CreatureRelationKind
    seam_kind: _CreatureSeamKind


@dataclass(frozen=True)
class _PlannedRelationPair:
    from_object: str
    to_object: str
    pair_source: _PairSource
    seam: _PlannedCreatureSeam | None = None


def _dedupe_names(values: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for item in values:
        normalized = str(item).strip()
        key = normalized.lower()
        if not normalized or key in seen:
            continue
        seen.add(key)
        result.append(normalized)
    return result


def _name_role_tokens(object_name: str) -> list[str]:
    normalized = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", object_name.strip())
    return [token for token in re.split(r"[^a-zA-Z0-9]+", normalized.lower()) if token]


def _has_name_hint(object_name: str, hints: tuple[str, ...]) -> bool:
    normalized = object_name.strip().lower()
    return any(hint in normalized for hint in hints)


def _is_head_like(object_name: str) -> bool:
    return _has_name_hint(object_name, _HEAD_ROLE_HINTS)


def _is_body_like(object_name: str) -> bool:
    return _has_name_hint(object_name, _BODY_ROLE_HINTS)


def _is_snout_like(object_name: str) -> bool:
    return _has_name_hint(object_name, _SNOUT_ROLE_HINTS)


def _is_nose_like(object_name: str) -> bool:
    return _has_name_hint(object_name, _NOSE_ROLE_HINTS)


def _is_eye_like(object_name: str) -> bool:
    return _has_name_hint(object_name, _EYE_ROLE_HINTS)


def _is_face_attachment(object_name: str) -> bool:
    return _has_name_hint(object_name, _FACE_ATTACHMENT_HINTS)


def _is_tail_like(object_name: str) -> bool:
    return _has_name_hint(object_name, _TAIL_ROLE_HINTS)


def _is_limb_like(object_name: str) -> bool:
    if _has_name_hint(object_name, _LIMB_ROLE_HINTS):
        return True

    tokens = _name_role_tokens(object_name)
    if len(tokens) <= 3 and any(token in {"fore", "hind", "front", "rear", "back"} for token in tokens):
        if any(token in {"l", "r", "left", "right"} for token in tokens):
            return True
    return False


def _is_distal_limb_like(object_name: str) -> bool:
    return _has_name_hint(object_name, _DISTAL_LIMB_HINTS)


def _is_proximal_limb_like(object_name: str) -> bool:
    return _has_name_hint(object_name, _PROXIMAL_LIMB_HINTS) and not _is_distal_limb_like(object_name)


def _name_side_hint(object_name: str) -> Literal["left", "right"] | None:
    normalized = object_name.strip().lower()
    if (
        normalized.endswith("left")
        or normalized.endswith("_l")
        or normalized.endswith(".l")
        or re.search(r"(?:^|[_\-.])left(?:$|[_\-.])", normalized)
        or re.search(r"(?:^|[_\-.])l(?:$|[_\-.])", normalized)
    ):
        return "left"
    if (
        normalized.endswith("right")
        or normalized.endswith("_r")
        or normalized.endswith(".r")
        or re.search(r"(?:^|[_\-.])right(?:$|[_\-.])", normalized)
        or re.search(r"(?:^|[_\-.])r(?:$|[_\-.])", normalized)
    ):
        return "right"
    return None


def _strip_side_tokens(object_name: str) -> str:
    tokens = _name_role_tokens(object_name)
    filtered = [token for token in tokens if token not in {"left", "right", "l", "r"}]
    return "_".join(filtered)


def _limb_chain_hint(object_name: str) -> Literal["fore", "hind"] | None:
    normalized = object_name.strip().lower()
    if any(token in normalized for token in ("fore", "front")):
        return "fore"
    if any(token in normalized for token in ("hind", "rear", "back")):
        return "hind"
    return None


def _limb_match_score(part_object: str, anchor_object: str) -> tuple[int, int, int, str]:
    same_side = (
        1 if _name_side_hint(part_object) == _name_side_hint(anchor_object) and _name_side_hint(part_object) else 0
    )
    same_chain = (
        1 if _limb_chain_hint(part_object) == _limb_chain_hint(anchor_object) and _limb_chain_hint(part_object) else 0
    )
    proximal_bonus = 1 if _is_proximal_limb_like(anchor_object) else 0
    return (same_side, same_chain, proximal_bonus, anchor_object.lower())


def _select_limb_anchor_for_distal(part_object: str, candidate_objects: list[str]) -> str | None:
    if not candidate_objects:
        return None
    return max(candidate_objects, key=lambda name: _limb_match_score(part_object, name))


def _name_anchor_weight(object_name: str) -> int:
    normalized = object_name.strip().lower()
    tokens = _name_role_tokens(object_name)
    trailing_token = tokens[-1] if tokens else ""
    score = 0
    for token, weight in _ANCHOR_ROLE_HINTS:
        if trailing_token == token:
            score += weight * 3
        elif token in tokens:
            score += max(1, weight // 3)
        elif token in normalized:
            score += max(1, weight // 4)
    for token in _ACCESSORY_ROLE_HINTS:
        if trailing_token == token:
            score -= 40
        elif token in tokens:
            score -= 10
        elif token in normalized:
            score -= 15
    return score


def _bbox_payload_or_none(reader: _SceneSpatialReader, object_name: str) -> dict[str, Any] | None:
    try:
        payload = reader.get_bounding_box(object_name, world_space=True)
    except Exception:
        return None
    return payload if isinstance(payload, dict) else None


def _bbox_volume_or_zero(reader: _SceneSpatialReader, object_name: str) -> float:
    bbox = _bbox_payload_or_none(reader, object_name)
    dimensions = bbox.get("dimensions") if isinstance(bbox, dict) else None
    if not isinstance(dimensions, list) or len(dimensions) != 3:
        return 0.0
    try:
        return float(dimensions[0]) * float(dimensions[1]) * float(dimensions[2])
    except Exception:
        return 0.0


def _looks_like_accessory_anchor(object_name: str) -> bool:
    normalized = object_name.strip().lower()
    return any(token in normalized for token in _ACCESSORY_ROLE_HINTS)


def _select_scope_primary_target(reader: _SceneSpatialReader, object_names: list[str]) -> str | None:
    if not object_names:
        return None
    return max(
        object_names,
        key=lambda name: (
            0 if _looks_like_accessory_anchor(name) else 1,
            _name_anchor_weight(name),
            _bbox_volume_or_zero(reader, name),
            -object_names.index(name),
        ),
    )


def _select_role_anchor(reader: _SceneSpatialReader, object_names: list[str]) -> str | None:
    if not object_names:
        return None
    return _select_scope_primary_target(reader, object_names)


def _preferred_attachment_macro(
    relation_kind: _CreatureRelationKind,
) -> Literal["macro_attach_part_to_surface", "macro_align_part_with_contact"]:
    if relation_kind == "embedded_attachment":
        return "macro_attach_part_to_surface"
    return "macro_align_part_with_contact"


def _append_creature_seam(
    seams: list[_PlannedCreatureSeam],
    seen_pairs: set[tuple[str, str]],
    *,
    part_object: str,
    anchor_object: str,
    relation_kind: _CreatureRelationKind,
    seam_kind: _CreatureSeamKind,
) -> None:
    pair_key = (part_object, anchor_object)
    if part_object == anchor_object or pair_key in seen_pairs:
        return
    seen_pairs.add(pair_key)
    seams.append(
        _PlannedCreatureSeam(
            part_object=part_object,
            anchor_object=anchor_object,
            relation_kind=relation_kind,
            seam_kind=seam_kind,
        )
    )


def _required_creature_seams(reader: _SceneSpatialReader, object_names: list[str]) -> list[_PlannedCreatureSeam]:
    if len(object_names) < 2:
        return []

    heads = [name for name in object_names if _is_head_like(name)]
    bodies = [name for name in object_names if _is_body_like(name)]
    snouts = [name for name in object_names if _is_snout_like(name)]
    noses = [name for name in object_names if _is_nose_like(name)]
    tails = [name for name in object_names if _is_tail_like(name)]
    eyes = [name for name in object_names if _is_eye_like(name)]
    face_attachments = [
        name
        for name in object_names
        if _is_face_attachment(name) and not _is_eye_like(name) and not _is_nose_like(name) and not _is_snout_like(name)
    ]
    limbs = [name for name in object_names if _is_limb_like(name)]

    head_anchor = _select_role_anchor(reader, heads)
    body_anchor = _select_role_anchor(reader, bodies)
    snout_anchor = _select_role_anchor(reader, snouts)

    seams: list[_PlannedCreatureSeam] = []
    seen_pairs: set[tuple[str, str]] = set()

    if head_anchor is not None and body_anchor is not None:
        _append_creature_seam(
            seams,
            seen_pairs,
            part_object=head_anchor,
            anchor_object=body_anchor,
            relation_kind="segment_attachment",
            seam_kind="head_body",
        )

    if head_anchor is not None:
        for eye_name in eyes:
            _append_creature_seam(
                seams,
                seen_pairs,
                part_object=eye_name,
                anchor_object=head_anchor,
                relation_kind="seated_attachment",
                seam_kind="face_head",
            )
        for face_name in face_attachments:
            _append_creature_seam(
                seams,
                seen_pairs,
                part_object=face_name,
                anchor_object=head_anchor,
                relation_kind="embedded_attachment",
                seam_kind="face_head",
            )
        for snout_name in snouts:
            _append_creature_seam(
                seams,
                seen_pairs,
                part_object=snout_name,
                anchor_object=head_anchor,
                relation_kind="embedded_attachment",
                seam_kind="face_head",
            )
        if snout_anchor is None:
            for nose_name in noses:
                _append_creature_seam(
                    seams,
                    seen_pairs,
                    part_object=nose_name,
                    anchor_object=head_anchor,
                    relation_kind="embedded_attachment",
                    seam_kind="face_head",
                )

    if snout_anchor is not None:
        for nose_name in noses:
            _append_creature_seam(
                seams,
                seen_pairs,
                part_object=nose_name,
                anchor_object=snout_anchor,
                relation_kind="embedded_attachment",
                seam_kind="nose_snout",
            )

    if body_anchor is not None:
        for tail_name in tails:
            _append_creature_seam(
                seams,
                seen_pairs,
                part_object=tail_name,
                anchor_object=body_anchor,
                relation_kind="segment_attachment",
                seam_kind="tail_body",
            )

    distal_limbs = [name for name in limbs if _is_distal_limb_like(name)]
    proximal_limbs = [name for name in limbs if _is_proximal_limb_like(name)]
    remaining_limb_bodies: list[str] = []

    for limb_name in limbs:
        if limb_name in distal_limbs:
            anchor_name = _select_limb_anchor_for_distal(
                limb_name,
                [candidate for candidate in proximal_limbs if candidate != limb_name],
            )
            if anchor_name is not None:
                _append_creature_seam(
                    seams,
                    seen_pairs,
                    part_object=limb_name,
                    anchor_object=anchor_name,
                    relation_kind="segment_attachment",
                    seam_kind="limb_segment",
                )
                continue
        remaining_limb_bodies.append(limb_name)

    if body_anchor is not None:
        for limb_name in remaining_limb_bodies:
            _append_creature_seam(
                seams,
                seen_pairs,
                part_object=limb_name,
                anchor_object=body_anchor,
                relation_kind="segment_attachment",
                seam_kind="limb_body",
            )

    seam_priority = {
        "head_body": 60,
        "tail_body": 50,
        "limb_segment": 45,
        "limb_body": 40,
        "face_head": 30,
        "nose_snout": 25,
    }
    return sorted(
        seams,
        key=lambda seam: (
            -seam_priority.get(seam.seam_kind, 0),
            seam.part_object.lower(),
            seam.anchor_object.lower(),
        ),
    )


def _attachment_relation(from_object: str, to_object: str) -> tuple[_CreatureRelationKind, str, str] | None:
    if _is_nose_like(from_object) and _is_snout_like(to_object):
        return "embedded_attachment", from_object, to_object
    if _is_nose_like(to_object) and _is_snout_like(from_object):
        return "embedded_attachment", to_object, from_object
    if _is_face_attachment(from_object) and _is_head_like(to_object):
        relation_kind: _CreatureRelationKind = (
            "seated_attachment" if _is_eye_like(from_object) else "embedded_attachment"
        )
        return relation_kind, from_object, to_object
    if _is_face_attachment(to_object) and _is_head_like(from_object):
        relation_kind = "seated_attachment" if _is_eye_like(to_object) else "embedded_attachment"
        return relation_kind, to_object, from_object
    if _is_head_like(from_object) and _is_body_like(to_object):
        return "segment_attachment", from_object, to_object
    if _is_head_like(to_object) and _is_body_like(from_object):
        return "segment_attachment", to_object, from_object
    if _is_tail_like(from_object) and _is_body_like(to_object):
        return "segment_attachment", from_object, to_object
    if _is_tail_like(to_object) and _is_body_like(from_object):
        return "segment_attachment", to_object, from_object
    if _is_limb_like(from_object) and (_is_body_like(to_object) or _is_limb_like(to_object)):
        return "segment_attachment", from_object, to_object
    if _is_limb_like(to_object) and (_is_body_like(from_object) or _is_limb_like(from_object)):
        if _is_distal_limb_like(from_object) and not _is_distal_limb_like(to_object):
            return "segment_attachment", from_object, to_object
        return "segment_attachment", to_object, from_object
    return None


def _attachment_seam_kind(part_object: str, anchor_object: str) -> _CreatureSeamKind:
    if _is_nose_like(part_object) and _is_snout_like(anchor_object):
        return "nose_snout"
    if _is_head_like(part_object) and _is_body_like(anchor_object):
        return "head_body"
    if _is_tail_like(part_object) and _is_body_like(anchor_object):
        return "tail_body"
    if _is_limb_like(part_object) and _is_limb_like(anchor_object):
        return "limb_segment"
    if _is_limb_like(part_object) and _is_body_like(anchor_object):
        return "limb_body"
    return "face_head"


def _goal_contains_any(goal_hint: str | None, hints: tuple[str, ...]) -> bool:
    normalized = str(goal_hint or "").strip().lower()
    return any(token in normalized for token in hints)


def _coerce_scope_kind(
    *,
    primary_target: str | None,
    object_names: list[str],
    collection_name: str | None,
) -> _ScopeKind:
    if collection_name:
        return "collection"
    if len(object_names) > 1:
        return "object_set"
    if primary_target:
        return "single_object"
    return "scene"


def _role_for_object(
    *,
    object_name: str,
    primary_target: str | None,
) -> tuple[_ObjectRole, list[str]]:
    signals: list[str] = []
    if object_name == primary_target:
        signals.append("primary_target")
    if _has_name_hint(object_name, _SUPPORT_ROLE_HINTS):
        signals.append("support_name_hint")
        return ("support_base" if object_name != primary_target else "anchor_core"), signals
    if _is_tail_like(object_name) or _is_limb_like(object_name):
        signals.append("appendage_name_hint")
        return ("attached_appendage" if object_name != primary_target else "anchor_core"), signals
    if _is_face_attachment(object_name):
        signals.append("accessory_name_hint")
        return ("accessory_feature" if object_name != primary_target else "anchor_core"), signals
    if _is_head_like(object_name):
        signals.append("head_name_hint")
        return ("anchor_core" if object_name == primary_target else "attached_mass"), signals
    if _is_body_like(object_name):
        signals.append("body_name_hint")
        return ("anchor_core" if object_name == primary_target else "structural_peer"), signals
    if object_name == primary_target:
        return "anchor_core", signals or ["fallback_primary"]
    return "structural_peer", signals or ["fallback_peer"]


def _symmetry_candidate_pairs(object_names: list[str], *, goal_hint: str | None) -> list[tuple[str, str]]:
    if len(object_names) < 2:
        return []
    if not _goal_contains_any(goal_hint, _SYMMETRY_GOAL_HINTS):
        strong_name_matches = [name for name in object_names if _name_side_hint(name) is not None]
        if len(strong_name_matches) < 2:
            return []

    by_stem: dict[str, dict[str, str]] = {}
    for object_name in object_names:
        side = _name_side_hint(object_name)
        if side is None:
            continue
        stem = _strip_side_tokens(object_name)
        if not stem:
            continue
        by_stem.setdefault(stem, {})[side] = object_name

    pairs: list[tuple[str, str]] = []
    for stem, side_map in sorted(by_stem.items()):
        left = side_map.get("left")
        right = side_map.get("right")
        if left and right:
            pairs.append((left, right))
    return pairs


def _resolve_support_pairs(
    *,
    primary_target: str | None,
    object_roles: list[dict[str, Any]],
    symmetry_pairs: list[tuple[str, str]],
    goal_hint: str | None,
) -> list[tuple[str, str]]:
    support_objects = [item["object_name"] for item in object_roles if item["role"] == "support_base"]
    if not support_objects:
        return []
    if len(support_objects) > 1 and not _goal_contains_any(goal_hint, _SUPPORT_GOAL_HINTS):
        return []

    support_object = support_objects[0]
    pairs: list[tuple[str, str]] = []
    for left_object, right_object in symmetry_pairs:
        for object_name in (left_object, right_object):
            if object_name != support_object:
                pairs.append((object_name, support_object))
    if not pairs and primary_target is not None and primary_target != support_object:
        pairs.append((primary_target, support_object))
    return pairs[:4]


def _pair_id(from_object: str, to_object: str) -> str:
    return re.sub(r"[^a-z0-9_]+", "_", f"{from_object.lower()}__{to_object.lower()}")


def _measurement_basis(
    gap_payload: dict[str, Any] | None,
    overlap_payload: dict[str, Any] | None,
    contact_assertion: dict[str, Any] | None,
) -> Literal["mesh_surface", "bounding_box", "mixed", "unknown"]:
    candidates = {
        str((gap_payload or {}).get("measurement_basis") or "").strip(),
        str((overlap_payload or {}).get("measurement_basis") or "").strip(),
        str(((contact_assertion or {}).get("details") or {}).get("measurement_basis") or "").strip(),
    }
    resolved = {item for item in candidates if item}
    if not resolved:
        return "unknown"
    if len(resolved) == 1:
        only = resolved.pop()
        if only == "mesh_surface":
            return "mesh_surface"
        if only == "bounding_box":
            return "bounding_box"
        return "unknown"
    return "mixed"


def _attachment_verdict(
    *,
    gap_payload: dict[str, Any] | None,
    alignment_payload: dict[str, Any] | None,
    overlap_payload: dict[str, Any] | None,
    contact_assertion: dict[str, Any] | None,
) -> Literal["seated_contact", "floating_gap", "intersecting", "misaligned_attachment", "needs_followup"]:
    if overlap_payload is not None and bool(overlap_payload.get("overlaps")):
        return "intersecting"
    if contact_assertion is not None:
        if bool(contact_assertion.get("passed")):
            if alignment_payload is not None and not bool(alignment_payload.get("is_aligned")):
                return "misaligned_attachment"
            return "seated_contact"
        actual_relation = str(((contact_assertion.get("actual") or {}).get("relation")) or "").lower()
        if actual_relation == "separated":
            return "floating_gap"
        if actual_relation == "overlapping":
            return "intersecting"
    if gap_payload is not None and str(gap_payload.get("relation") or "").lower() == "separated":
        return "floating_gap"
    if alignment_payload is not None and not bool(alignment_payload.get("is_aligned")):
        return "misaligned_attachment"
    return "needs_followup"


def _support_semantics(
    *,
    from_object: str,
    to_object: str,
    pair_source: _PairSource,
    reader: _SceneSpatialReader,
    gap_payload: dict[str, Any] | None,
) -> dict[str, Any] | None:
    if pair_source != "support_candidate":
        return None
    from_bbox = _bbox_payload_or_none(reader, from_object)
    to_bbox = _bbox_payload_or_none(reader, to_object)
    if from_bbox is None or to_bbox is None:
        return None

    from_min = from_bbox.get("min") or [0.0, 0.0, 0.0]
    from_max = from_bbox.get("max") or [0.0, 0.0, 0.0]
    to_min = to_bbox.get("min") or [0.0, 0.0, 0.0]
    to_max = to_bbox.get("max") or [0.0, 0.0, 0.0]

    from_over_to = abs(float(from_min[2]) - float(to_max[2]))
    to_over_from = abs(float(to_min[2]) - float(from_max[2]))
    if from_over_to <= to_over_from:
        supported_object = from_object
        support_object = to_object
    else:
        supported_object = to_object
        support_object = from_object

    relation = str((gap_payload or {}).get("relation") or "").lower()
    verdict: Literal["supported", "unsupported"] = "supported" if relation in {"contact", "touching"} else "unsupported"
    return {
        "supported_object": supported_object,
        "support_object": support_object,
        "axis": "Z",
        "verdict": verdict,
    }


def _symmetry_semantics(
    *,
    from_object: str,
    to_object: str,
    pair_source: _PairSource,
    reader: _SceneSpatialReader,
) -> dict[str, Any] | None:
    if pair_source != "symmetry_candidate":
        return None
    left_object, right_object = (
        (from_object, to_object) if _name_side_hint(from_object) == "left" else (to_object, from_object)
    )
    left_bbox = _bbox_payload_or_none(reader, left_object)
    right_bbox = _bbox_payload_or_none(reader, right_object)
    if left_bbox is None or right_bbox is None:
        return None
    left_center = left_bbox.get("center") or [0.0, 0.0, 0.0]
    right_center = right_bbox.get("center") or [0.0, 0.0, 0.0]
    mirror_coordinate = (float(left_center[0]) + float(right_center[0])) / 2.0
    try:
        assertion = reader.assert_symmetry(left_object, right_object, axis="X", mirror_coordinate=mirror_coordinate)
    except Exception:
        assertion = {"passed": False}
    return {
        "left_object": left_object,
        "right_object": right_object,
        "axis": "X",
        "mirror_coordinate": mirror_coordinate,
        "verdict": "symmetric" if bool(assertion.get("passed")) else "asymmetric",
    }


def _alignment_status(alignment_payload: dict[str, Any] | None) -> Literal["aligned", "misaligned", "unknown"]:
    if alignment_payload is None:
        return "unknown"
    return "aligned" if bool(alignment_payload.get("is_aligned")) else "misaligned"


def _build_relation_kinds(
    *,
    gap_payload: dict[str, Any] | None,
    alignment_payload: dict[str, Any] | None,
    overlap_payload: dict[str, Any] | None,
    attachment_semantics: dict[str, Any] | None,
    support_semantics: dict[str, Any] | None,
    symmetry_semantics: dict[str, Any] | None,
) -> list[str]:
    kinds: list[str] = []
    if gap_payload is not None:
        kinds.extend(["contact", "gap"])
    if overlap_payload is not None:
        kinds.append("overlap")
    if alignment_payload is not None:
        kinds.append("alignment")
    if attachment_semantics is not None:
        kinds.append("attachment")
    if support_semantics is not None:
        kinds.append("support")
    if symmetry_semantics is not None:
        kinds.append("symmetry")
    return list(dict.fromkeys(kinds))


def _build_relation_verdicts(
    *,
    gap_payload: dict[str, Any] | None,
    alignment_payload: dict[str, Any] | None,
    overlap_payload: dict[str, Any] | None,
    attachment_semantics: dict[str, Any] | None,
    support_semantics: dict[str, Any] | None,
    symmetry_semantics: dict[str, Any] | None,
) -> list[str]:
    verdicts: list[str] = []
    gap_relation = str((gap_payload or {}).get("relation") or "").strip().lower()
    if gap_relation:
        verdicts.append(gap_relation)
    overlap_relation = str((overlap_payload or {}).get("relation") or "").strip().lower()
    if overlap_relation:
        verdicts.append(overlap_relation)
    verdicts.append(_alignment_status(alignment_payload))
    if attachment_semantics is not None:
        verdicts.append(str(attachment_semantics.get("attachment_verdict") or "needs_followup"))
    if support_semantics is not None:
        verdicts.append(str(support_semantics.get("verdict") or "unsupported"))
    if symmetry_semantics is not None:
        verdicts.append(str(symmetry_semantics.get("verdict") or "asymmetric"))
    return list(dict.fromkeys(item for item in verdicts if item and item != "unknown"))


class SpatialGraphService:
    """Builds compact scope/relation artifacts from existing scene truth primitives."""

    def build_scope_graph(
        self,
        *,
        reader: _SceneSpatialReader,
        target_object: str | None,
        target_objects: list[str] | None,
        collection_name: str | None,
        list_collection_objects: Callable[[str], list[str]] | None = None,
    ) -> dict[str, Any]:
        object_names = _dedupe_names(list(target_objects or []))
        if target_object:
            object_names = _dedupe_names([target_object, *object_names])
        if collection_name and list_collection_objects is not None:
            object_names = _dedupe_names([*object_names, *list_collection_objects(collection_name)])

        primary_target: str | None
        if len(object_names) == 1:
            primary_target = target_object or object_names[0]
        else:
            primary_target = _select_scope_primary_target(reader, object_names)

        object_roles: list[dict[str, Any]] = []
        for object_name in object_names:
            role, signals = _role_for_object(object_name=object_name, primary_target=primary_target)
            if object_name == primary_target and "bbox_volume_anchor" not in signals:
                signals = [*signals, "bbox_volume_anchor"]
            object_roles.append(
                {
                    "object_name": object_name,
                    "role": role,
                    "is_primary": object_name == primary_target,
                    "signals": signals,
                }
            )

        return {
            "scope_kind": _coerce_scope_kind(
                primary_target=primary_target,
                object_names=object_names,
                collection_name=collection_name,
            ),
            "primary_target": primary_target,
            "object_names": object_names,
            "object_count": len(object_names),
            "collection_name": collection_name,
            "part_groups": [],
            "object_roles": object_roles,
        }

    def build_relation_graph(
        self,
        *,
        reader: _SceneSpatialReader,
        scope_graph: dict[str, Any],
        goal_hint: str | None = None,
        include_truth_payloads: bool = False,
        include_guided_pairs: bool = True,
    ) -> dict[str, Any]:
        object_names = list(scope_graph.get("object_names") or [])
        if len(object_names) < 2:
            return {
                "scope": scope_graph,
                "summary": {
                    "pairing_strategy": "none",
                    "pair_count": 0,
                    "evaluated_pairs": 0,
                    "failing_pairs": 0,
                    "attachment_pairs": 0,
                    "support_pairs": 0,
                    "symmetry_pairs": 0,
                },
                "pairs": [],
            }

        planned_pairs: list[_PlannedRelationPair] = []
        seen_pairs: set[tuple[str, str]] = set()
        required_seams = _required_creature_seams(reader, object_names)
        if required_seams:
            for required_seam in required_seams:
                pair_key = (required_seam.part_object, required_seam.anchor_object)
                seen_pairs.add(pair_key)
                planned_pairs.append(
                    _PlannedRelationPair(
                        from_object=required_seam.part_object,
                        to_object=required_seam.anchor_object,
                        pair_source="required_creature_seam",
                        seam=required_seam,
                    )
                )
        else:
            primary_target = scope_graph.get("primary_target")
            if isinstance(primary_target, str) and primary_target:
                for object_name in object_names:
                    if object_name == primary_target:
                        continue
                    pair_key = (primary_target, object_name)
                    seen_pairs.add(pair_key)
                    planned_pairs.append(
                        _PlannedRelationPair(
                            from_object=primary_target,
                            to_object=object_name,
                            pair_source="primary_to_other",
                        )
                    )

        symmetry_pairs: list[tuple[str, str]] = []
        if include_guided_pairs:
            symmetry_pairs = _symmetry_candidate_pairs(object_names, goal_hint=goal_hint)
            for left_object, right_object in symmetry_pairs:
                pair_key = (left_object, right_object)
                if pair_key in seen_pairs:
                    continue
                seen_pairs.add(pair_key)
                planned_pairs.append(
                    _PlannedRelationPair(
                        from_object=left_object,
                        to_object=right_object,
                        pair_source="symmetry_candidate",
                    )
                )

            support_pairs = _resolve_support_pairs(
                primary_target=scope_graph.get("primary_target"),
                object_roles=list(scope_graph.get("object_roles") or []),
                symmetry_pairs=symmetry_pairs,
                goal_hint=goal_hint,
            )
            for supported_object, support_object in support_pairs:
                pair_key = (supported_object, support_object)
                if pair_key in seen_pairs:
                    continue
                seen_pairs.add(pair_key)
                planned_pairs.append(
                    _PlannedRelationPair(
                        from_object=supported_object,
                        to_object=support_object,
                        pair_source="support_candidate",
                    )
                )

        relation_pairs: list[dict[str, Any]] = []
        for pair in planned_pairs:
            gap_payload: dict[str, Any] | None = None
            alignment_payload: dict[str, Any] | None = None
            overlap_payload: dict[str, Any] | None = None
            contact_assertion: dict[str, Any] | None = None
            error: str | None = None
            try:
                gap_payload = reader.measure_gap(pair.from_object, pair.to_object)
                alignment_payload = reader.measure_alignment(
                    pair.from_object, pair.to_object, ["X", "Y", "Z"], "CENTER"
                )
                overlap_payload = reader.measure_overlap(pair.from_object, pair.to_object)
                contact_assertion = reader.assert_contact(pair.from_object, pair.to_object)
            except RuntimeError as exc:
                error = str(exc)

            pair_seam: _PlannedCreatureSeam | None = pair.seam
            attachment_relation = _attachment_relation(pair.from_object, pair.to_object) if pair_seam is None else None
            attachment_semantics: dict[str, Any] | None = None
            if pair_seam is not None or attachment_relation is not None:
                relation_kind: _CreatureRelationKind
                part_object: str
                anchor_object: str
                seam_kind: _CreatureSeamKind
                is_required_seam: bool
                if pair_seam is not None:
                    relation_kind = pair_seam.relation_kind
                    part_object = pair_seam.part_object
                    anchor_object = pair_seam.anchor_object
                    seam_kind = pair_seam.seam_kind
                    is_required_seam = True
                else:
                    relation_kind, part_object, anchor_object = attachment_relation  # type: ignore[misc]
                    seam_kind = _attachment_seam_kind(part_object, anchor_object)
                    is_required_seam = False
                attachment_semantics = {
                    "relation_kind": relation_kind,
                    "seam_kind": seam_kind,
                    "part_object": part_object,
                    "anchor_object": anchor_object,
                    "required_seam": is_required_seam,
                    "preferred_macro": _preferred_attachment_macro(relation_kind),
                    "attachment_verdict": _attachment_verdict(
                        gap_payload=gap_payload,
                        alignment_payload=alignment_payload,
                        overlap_payload=overlap_payload,
                        contact_assertion=contact_assertion,
                    ),
                }

            support_semantics = _support_semantics(
                from_object=pair.from_object,
                to_object=pair.to_object,
                pair_source=pair.pair_source,
                reader=reader,
                gap_payload=gap_payload,
            )
            symmetry_semantics = _symmetry_semantics(
                from_object=pair.from_object,
                to_object=pair.to_object,
                pair_source=pair.pair_source,
                reader=reader,
            )

            relation_pair = {
                "pair_id": _pair_id(pair.from_object, pair.to_object),
                "from_object": pair.from_object,
                "to_object": pair.to_object,
                "pair_source": pair.pair_source,
                "relation_kinds": _build_relation_kinds(
                    gap_payload=gap_payload,
                    alignment_payload=alignment_payload,
                    overlap_payload=overlap_payload,
                    attachment_semantics=attachment_semantics,
                    support_semantics=support_semantics,
                    symmetry_semantics=symmetry_semantics,
                ),
                "relation_verdicts": _build_relation_verdicts(
                    gap_payload=gap_payload,
                    alignment_payload=alignment_payload,
                    overlap_payload=overlap_payload,
                    attachment_semantics=attachment_semantics,
                    support_semantics=support_semantics,
                    symmetry_semantics=symmetry_semantics,
                ),
                "gap_relation": (gap_payload or {}).get("relation"),
                "gap_distance": (gap_payload or {}).get("gap"),
                "overlap_relation": (overlap_payload or {}).get("relation"),
                "contact_passed": None if contact_assertion is None else bool(contact_assertion.get("passed")),
                "alignment_status": _alignment_status(alignment_payload),
                "aligned_axes": list((alignment_payload or {}).get("aligned_axes") or []),
                "measurement_basis": _measurement_basis(gap_payload, overlap_payload, contact_assertion),
                "attachment_semantics": attachment_semantics,
                "support_semantics": support_semantics,
                "symmetry_semantics": symmetry_semantics,
                "error": error,
            }
            if include_truth_payloads:
                relation_pair["truth_payloads"] = {
                    "gap": gap_payload,
                    "alignment": alignment_payload,
                    "overlap": overlap_payload,
                    "contact_assertion": contact_assertion,
                }
            relation_pairs.append(relation_pair)

        if not relation_pairs:
            pairing_strategy: _PairingStrategy = "none"
        elif required_seams and len(relation_pairs) == len(required_seams):
            pairing_strategy = "required_creature_seams"
        elif all(pair["pair_source"] == "primary_to_other" for pair in relation_pairs):
            pairing_strategy = "primary_to_others"
        else:
            pairing_strategy = "guided_spatial_pairs"

        return {
            "scope": scope_graph,
            "summary": {
                "pairing_strategy": pairing_strategy,
                "pair_count": len(relation_pairs),
                "evaluated_pairs": sum(1 for item in relation_pairs if item.get("error") is None),
                "failing_pairs": sum(
                    1
                    for item in relation_pairs
                    if item.get("error")
                    or "floating_gap" in item.get("relation_verdicts", [])
                    or "intersecting" in item.get("relation_verdicts", [])
                    or item.get("alignment_status") == "misaligned"
                    or item.get("contact_passed") is False
                    or (item.get("support_semantics") or {}).get("verdict") == "unsupported"
                    or (item.get("symmetry_semantics") or {}).get("verdict") == "asymmetric"
                ),
                "attachment_pairs": sum(1 for item in relation_pairs if item.get("attachment_semantics") is not None),
                "support_pairs": sum(1 for item in relation_pairs if item.get("support_semantics") is not None),
                "symmetry_pairs": sum(1 for item in relation_pairs if item.get("symmetry_semantics") is not None),
            },
            "pairs": relation_pairs,
        }


_spatial_graph_service: SpatialGraphService | None = None


def get_spatial_graph_service() -> SpatialGraphService:
    """Return the shared spatial graph service instance."""

    global _spatial_graph_service
    if _spatial_graph_service is None:
        _spatial_graph_service = SpatialGraphService()
    return _spatial_graph_service
