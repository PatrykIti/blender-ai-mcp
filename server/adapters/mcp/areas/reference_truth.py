# SPDX-FileCopyrightText: 2024-2026 Patryk Ciechański
# SPDX-License-Identifier: Apache-2.0

"""Truth and follow-up helpers for staged reference compare responses."""

from __future__ import annotations

import re
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any, Literal, cast

from server.adapters.mcp.contracts.scene import (
    SceneAssembledTargetScopeContract,
    SceneAssertionPayloadContract,
    SceneAttachmentSemanticsContract,
    SceneCorrectionTruthBundleContract,
    SceneCorrectionTruthPairContract,
    SceneCorrectionTruthSummaryContract,
    SceneRelationKindLiteral,
    SceneRelationVerdictLiteral,
    SceneRepairMacroCandidateContract,
    SceneSupportSemanticsContract,
    SceneSymmetrySemanticsContract,
    SceneTruthFollowupContract,
    SceneTruthFollowupItemContract,
)
from server.infrastructure.di import get_scene_handler

ANCHOR_ROLE_HINTS: tuple[tuple[str, int], ...] = (
    ("body", 50),
    ("torso", 45),
    ("trunk", 45),
    ("head", 40),
    ("skull", 35),
    ("core", 30),
    ("root", 25),
    ("base", 20),
)
ACCESSORY_ROLE_HINTS: tuple[str, ...] = (
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
HEAD_ROLE_HINTS: tuple[str, ...] = ("head", "skull", "face")
BODY_ROLE_HINTS: tuple[str, ...] = ("body", "torso", "trunk", "chest", "abdomen", "pelvis", "hip")
SNOUT_ROLE_HINTS: tuple[str, ...] = ("snout", "muzzle")
NOSE_ROLE_HINTS: tuple[str, ...] = ("nose", "nostril")
EYE_ROLE_HINTS: tuple[str, ...] = ("eye",)
FACE_ATTACHMENT_HINTS: tuple[str, ...] = ("ear", "eye", "nose", "snout", "whisker")
TAIL_ROLE_HINTS: tuple[str, ...] = ("tail",)
ROOF_ROLE_HINTS: tuple[str, ...] = ("roof",)
BUILDING_MASS_HINTS: tuple[str, ...] = ("wall", "facade", "volume", "shell")
LIMB_ROLE_HINTS: tuple[str, ...] = (
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
DISTAL_LIMB_HINTS: tuple[str, ...] = ("paw", "foot", "hand", "hoof", "shin", "calf", "forearm", "lowerarm", "lowerleg")
PROXIMAL_LIMB_HINTS: tuple[str, ...] = ("upperarm", "upperleg", "thigh", "arm", "leg", "forelimb", "hindlimb")

_CreatureRelationKind = Literal["embedded_attachment", "seated_attachment", "segment_attachment"]
_CreatureSeamKind = Literal[
    "face_head", "nose_snout", "head_body", "tail_body", "limb_body", "limb_segment", "roof_wall"
]


@dataclass(frozen=True)
class _PlannedCreatureSeam:
    part_object: str
    anchor_object: str
    relation_kind: _CreatureRelationKind
    seam_kind: _CreatureSeamKind


@dataclass(frozen=True)
class _PlannedTruthPair:
    from_object: str
    to_object: str
    seam: _PlannedCreatureSeam | None = None


def dedupe_names(values: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for item in values:
        normalized = item.strip()
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
    return _has_name_hint(object_name, HEAD_ROLE_HINTS)


def _is_body_like(object_name: str) -> bool:
    return _has_name_hint(object_name, BODY_ROLE_HINTS)


def _is_snout_like(object_name: str) -> bool:
    return _has_name_hint(object_name, SNOUT_ROLE_HINTS)


def _is_nose_like(object_name: str) -> bool:
    return _has_name_hint(object_name, NOSE_ROLE_HINTS)


def _is_eye_like(object_name: str) -> bool:
    return _has_name_hint(object_name, EYE_ROLE_HINTS)


def _is_face_attachment(object_name: str) -> bool:
    return _has_name_hint(object_name, FACE_ATTACHMENT_HINTS)


def _is_tail_like(object_name: str) -> bool:
    return _has_name_hint(object_name, TAIL_ROLE_HINTS)


def _is_roof_like(object_name: str) -> bool:
    return _has_name_hint(object_name, ROOF_ROLE_HINTS)


def _is_building_mass_like(object_name: str) -> bool:
    return _has_name_hint(object_name, BUILDING_MASS_HINTS)


def _is_limb_like(object_name: str) -> bool:
    if _has_name_hint(object_name, LIMB_ROLE_HINTS):
        return True

    tokens = _name_role_tokens(object_name)
    directional_tokens = {"fore", "hind"}
    side_tokens = {"l", "r", "left", "right"}
    if not any(token in directional_tokens for token in tokens) or not any(token in side_tokens for token in tokens):
        return False
    return all(token in directional_tokens or token in side_tokens or token.isdigit() for token in tokens)


def _is_distal_limb_like(object_name: str) -> bool:
    return _has_name_hint(object_name, DISTAL_LIMB_HINTS)


def _is_proximal_limb_like(object_name: str) -> bool:
    return _has_name_hint(object_name, PROXIMAL_LIMB_HINTS) and not _is_distal_limb_like(object_name)


def _select_role_anchor(object_names: list[str]) -> str | None:
    if not object_names:
        return None
    return _select_scope_primary_target(object_names)


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


def _required_creature_seams(scope: SceneAssembledTargetScopeContract) -> list[_PlannedCreatureSeam]:
    object_names = list(scope.object_names or [])
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

    head_anchor = _select_role_anchor(heads)
    body_anchor = _select_role_anchor(bodies)
    snout_anchor = _select_role_anchor(snouts)

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


def _attachment_relation(
    from_object: str,
    to_object: str,
) -> tuple[_CreatureRelationKind, str, str] | None:
    if _is_nose_like(from_object) and _is_snout_like(to_object):
        return "embedded_attachment", from_object, to_object
    if _is_nose_like(to_object) and _is_snout_like(from_object):
        return "embedded_attachment", to_object, from_object
    if _is_face_attachment(from_object) and _is_head_like(to_object):
        relation_kind: _CreatureRelationKind
        relation_kind = "seated_attachment" if _is_eye_like(from_object) else "embedded_attachment"
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
    if _is_roof_like(from_object) and _is_building_mass_like(to_object):
        return "seated_attachment", from_object, to_object
    if _is_roof_like(to_object) and _is_building_mass_like(from_object):
        return "seated_attachment", to_object, from_object
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
    if _is_roof_like(part_object) and _is_building_mass_like(anchor_object):
        return "roof_wall"
    if _is_limb_like(part_object) and _is_limb_like(anchor_object):
        return "limb_segment"
    if _is_limb_like(part_object) and _is_body_like(anchor_object):
        return "limb_body"
    return "face_head"


def _attachment_item_summary(
    *,
    pair_label: str,
    relation_kind: Literal["embedded_attachment", "seated_attachment", "segment_attachment"],
    has_overlap: bool,
    has_gap: bool,
    has_contact_failure: bool,
    has_alignment_issue: bool,
) -> str:
    if has_overlap:
        if relation_kind == "embedded_attachment":
            return (
                f"{pair_label} is an embedded attachment relation; generic overlap cleanup alone is not enough "
                "to seat the part correctly into the anchor mass."
            )
        return (
            f"{pair_label} is an attachment relation; the pair should stay seated/attached, not just be "
            "pushed apart until overlap reaches zero."
        )
    if has_gap or has_contact_failure:
        return f"{pair_label} is still floating or detached for this attachment relation."
    if has_alignment_issue:
        return f"{pair_label} is still seated on the wrong attachment line for this attachment relation."
    return f"{pair_label} still has wrong attachment semantics."


def _support_item_summary(
    *,
    pair_label: str,
    support_semantics: SceneSupportSemanticsContract,
) -> str:
    return (
        f"{pair_label} is not yet supported as expected on {support_semantics.axis}; "
        "the supported object still needs a stable base/contact relation."
    )


def _symmetry_item_summary(
    *,
    pair_label: str,
    symmetry_semantics: SceneSymmetrySemanticsContract,
) -> str:
    return (
        f"{pair_label} is still asymmetric across {symmetry_semantics.axis}; "
        "the mirrored pair needs another bounded symmetry correction."
    )


def resolve_capture_scope(
    *,
    target_object: str | None,
    target_objects: list[str] | None,
    collection_name: str | None,
    get_collection_handler: Callable[[], Any],
) -> tuple[str | None, list[str], str | None]:
    resolved_target_objects = dedupe_names(list(target_objects or []))
    if target_object:
        resolved_target_objects = dedupe_names([target_object, *resolved_target_objects])

    if collection_name:
        collection_payload = get_collection_handler().list_objects(
            collection_name=collection_name,
            recursive=True,
            include_hidden=False,
        )
        collection_objects = [
            str(item.get("name")).strip()
            for item in collection_payload.get("objects", [])
            if isinstance(item, dict) and str(item.get("name") or "").strip()
        ]
        resolved_target_objects = dedupe_names([*resolved_target_objects, *collection_objects])

    normalized_primary = (
        target_object if target_object else (resolved_target_objects[0] if len(resolved_target_objects) == 1 else None)
    )
    return normalized_primary, resolved_target_objects, collection_name


def _name_anchor_weight(object_name: str) -> int:
    normalized = object_name.strip().lower()
    tokens = _name_role_tokens(object_name)
    trailing_token = tokens[-1] if tokens else ""
    score = 0
    for token, weight in ANCHOR_ROLE_HINTS:
        if trailing_token == token:
            score += weight * 3
        elif token in tokens:
            score += max(1, weight // 3)
        elif token in normalized:
            score += max(1, weight // 4)
    for token in ACCESSORY_ROLE_HINTS:
        if trailing_token == token:
            score -= 40
        elif token in tokens:
            score -= 10
        elif token in normalized:
            score -= 15
    return score


def _bbox_volume_or_zero(object_name: str) -> float:
    try:
        bbox = get_scene_handler().get_bounding_box(object_name, world_space=True)
    except Exception:
        return 0.0
    dimensions = bbox.get("dimensions") if isinstance(bbox, dict) else None
    if not isinstance(dimensions, list) or len(dimensions) != 3:
        return 0.0
    try:
        return float(dimensions[0]) * float(dimensions[1]) * float(dimensions[2])
    except Exception:
        return 0.0


def _looks_like_accessory_anchor(object_name: str) -> bool:
    normalized = object_name.strip().lower()
    return any(token in normalized for token in ACCESSORY_ROLE_HINTS)


def _select_scope_primary_target(object_names: list[str]) -> str | None:
    if not object_names:
        return None
    return max(
        object_names,
        key=lambda name: (
            0 if _looks_like_accessory_anchor(name) else 1,
            _name_anchor_weight(name),
            _bbox_volume_or_zero(name),
            -object_names.index(name),
        ),
    )


def assembled_target_scope(
    *,
    target_object: str | None,
    target_objects: list[str] | None,
    collection_name: str | None,
    get_collection_handler: Callable[[], Any],
    get_scene_handler: Callable[[], Any],
    get_spatial_graph_service: Callable[[], Any],
) -> SceneAssembledTargetScopeContract:
    def _list_collection_objects(name: str) -> list[str]:
        payload = get_collection_handler().list_objects(
            collection_name=name,
            recursive=True,
            include_hidden=False,
        )
        return [
            str(item.get("name")).strip()
            for item in payload.get("objects", [])
            if isinstance(item, dict) and str(item.get("name") or "").strip()
        ]

    scope_payload = get_spatial_graph_service().build_scope_graph(
        reader=get_scene_handler(),
        target_object=target_object,
        target_objects=target_objects,
        collection_name=collection_name,
        list_collection_objects=_list_collection_objects,
        allow_scene_scope=True,
    )
    return SceneAssembledTargetScopeContract.model_validate(scope_payload)


def truth_bundle_pairs(
    scope: SceneAssembledTargetScopeContract,
) -> tuple[Literal["none", "primary_to_others", "required_creature_seams"], list[_PlannedTruthPair]]:
    object_names = list(scope.object_names or [])
    if len(object_names) < 2:
        return "none", []

    required_seams = _required_creature_seams(scope)
    if required_seams:
        return (
            "required_creature_seams",
            [
                _PlannedTruthPair(
                    from_object=seam.part_object,
                    to_object=seam.anchor_object,
                    seam=seam,
                )
                for seam in required_seams
            ],
        )

    if scope.primary_target is None:
        return "none", []
    anchor = scope.primary_target
    pairs = [_PlannedTruthPair(from_object=anchor, to_object=name) for name in object_names if name != anchor]
    return ("primary_to_others", pairs) if pairs else ("none", [])


def build_correction_truth_bundle(
    scene_handler: Any,
    scope: SceneAssembledTargetScopeContract,
    *,
    goal_hint: str | None = None,
    get_spatial_graph_service: Callable[[], Any],
) -> tuple[SceneCorrectionTruthBundleContract, dict[str, Any]]:
    relation_graph = get_spatial_graph_service().build_relation_graph(
        reader=scene_handler,
        scope_graph=scope.model_dump(mode="json"),
        goal_hint=goal_hint,
        include_truth_payloads=True,
        include_guided_pairs=True,
    )
    relation_pairs = list(relation_graph.get("pairs") or [])
    truth_pairs = relation_pairs
    if not truth_pairs:
        pairing_strategy: Literal["none", "primary_to_others", "required_creature_seams", "guided_spatial_pairs"] = (
            "none"
        )
    elif any(str(pair.get("pair_source") or "") == "required_creature_seam" for pair in truth_pairs):
        pairing_strategy = "required_creature_seams"
    elif all(str(pair.get("pair_source") or "") == "primary_to_other" for pair in truth_pairs):
        pairing_strategy = "primary_to_others"
    else:
        pairing_strategy = "guided_spatial_pairs"
    checks: list[SceneCorrectionTruthPairContract] = []
    contact_failures = 0
    overlap_pairs = 0
    separated_pairs = 0
    misaligned_pairs = 0

    for pair in truth_pairs:
        from_object = str(pair.get("from_object") or "")
        to_object = str(pair.get("to_object") or "")
        truth_payloads = pair.get("truth_payloads") or {}
        error = cast(str | None, pair.get("error"))
        gap = cast(dict[str, Any] | None, truth_payloads.get("gap"))
        alignment = cast(dict[str, Any] | None, truth_payloads.get("alignment"))
        overlap = cast(dict[str, Any] | None, truth_payloads.get("overlap"))
        contact_assertion_payload = truth_payloads.get("contact_assertion")
        contact_assertion = (
            SceneAssertionPayloadContract.model_validate(contact_assertion_payload)
            if isinstance(contact_assertion_payload, dict)
            else None
        )

        if gap is not None and str(gap.get("relation") or "").lower() == "separated":
            separated_pairs += 1
        if overlap is not None and bool(overlap.get("overlaps")):
            overlap_pairs += 1
        if (
            alignment is not None
            and not bool(alignment.get("is_aligned"))
            and not (contact_assertion is not None and contact_assertion.passed)
        ):
            misaligned_pairs += 1
        if contact_assertion is not None and not contact_assertion.passed:
            contact_failures += 1

        attachment_payload = pair.get("attachment_semantics")
        support_payload = pair.get("support_semantics")
        symmetry_payload = pair.get("symmetry_semantics")
        semantics_contract = (
            SceneAttachmentSemanticsContract.model_validate(attachment_payload)
            if isinstance(attachment_payload, dict)
            else None
        )
        support_contract = (
            SceneSupportSemanticsContract.model_validate(support_payload) if isinstance(support_payload, dict) else None
        )
        symmetry_contract = (
            SceneSymmetrySemanticsContract.model_validate(symmetry_payload)
            if isinstance(symmetry_payload, dict)
            else None
        )

        checks.append(
            SceneCorrectionTruthPairContract(
                from_object=from_object,
                to_object=to_object,
                relation_pair_id=cast(str | None, pair.get("pair_id")),
                relation_kinds=cast(list[SceneRelationKindLiteral], list(pair.get("relation_kinds") or [])),
                relation_verdicts=cast(
                    list[SceneRelationVerdictLiteral],
                    list(pair.get("relation_verdicts") or []),
                ),
                gap=gap,
                alignment=alignment,
                overlap=overlap,
                contact_assertion=contact_assertion,
                attachment_semantics=semantics_contract,
                support_semantics=support_contract,
                symmetry_semantics=symmetry_contract,
                error=error,
            )
        )

    return (
        SceneCorrectionTruthBundleContract(
            scope=scope,
            summary=SceneCorrectionTruthSummaryContract(
                pairing_strategy=pairing_strategy,
                pair_count=len(truth_pairs),
                evaluated_pairs=sum(1 for item in checks if item.error is None),
                contact_failures=contact_failures,
                overlap_pairs=overlap_pairs,
                separated_pairs=separated_pairs,
                misaligned_pairs=misaligned_pairs,
            ),
            checks=checks,
        ),
        relation_graph,
    )


def pair_label(from_object: str, to_object: str) -> str:
    return f"{from_object} -> {to_object}"


def _contact_semantics_note(
    *,
    gap_payload: dict[str, Any] | None,
    contact_assertion: SceneAssertionPayloadContract | None,
) -> str | None:
    if contact_assertion is None:
        return None

    details = contact_assertion.details or {}
    actual = contact_assertion.actual or {}
    measurement_basis = str(details.get("measurement_basis") or (gap_payload or {}).get("measurement_basis") or "")
    bbox_relation = str(details.get("bbox_relation") or (gap_payload or {}).get("bbox_relation") or "")
    measured_relation = str(actual.get("relation") or (gap_payload or {}).get("relation") or "")

    if (
        measurement_basis == "mesh_surface"
        and bbox_relation in {"contact", "touching"}
        and measured_relation == "separated"
    ):
        return "Bounding boxes touch, but the measured mesh surfaces still have a real gap."
    return None


def _attachment_verdict(
    *,
    relation_kind: _CreatureRelationKind | None = None,
    seam_kind: _CreatureSeamKind | None = None,
    gap_payload: dict[str, Any] | None,
    alignment_payload: dict[str, Any] | None,
    overlap_payload: dict[str, Any] | None,
    contact_assertion: SceneAssertionPayloadContract | None,
) -> Literal["seated_contact", "floating_gap", "intersecting", "misaligned_attachment", "needs_followup"]:
    if overlap_payload is not None and bool(overlap_payload.get("overlaps")):
        return "intersecting"
    if contact_assertion is not None:
        if contact_assertion.passed:
            return "seated_contact"
        actual_relation = str((contact_assertion.actual or {}).get("relation") or "").lower()
        if actual_relation == "separated":
            return "floating_gap"
        if actual_relation == "overlapping":
            return "intersecting"
    if gap_payload is not None and str(gap_payload.get("relation") or "").lower() == "separated":
        return "floating_gap"
    if alignment_payload is not None and not bool(alignment_payload.get("is_aligned")):
        return "misaligned_attachment"
    return "needs_followup"


def _has_actionable_attachment_alignment_issue(
    *,
    attachment_semantics: SceneAttachmentSemanticsContract | None,
    alignment_payload: dict[str, Any] | None,
    contact_assertion: SceneAssertionPayloadContract | None,
) -> bool:
    """Return True only when alignment drift should remain an attachment finding."""

    if alignment_payload is None or bool(alignment_payload.get("is_aligned")):
        return False
    if contact_assertion is not None and contact_assertion.passed:
        return False
    return attachment_semantics is None or attachment_semantics.attachment_verdict == "misaligned_attachment"


def _preferred_attach_surface_axis(
    *,
    gap_payload: dict[str, Any] | None,
    alignment_payload: dict[str, Any] | None,
) -> Literal["X", "Y", "Z"]:
    axis_gap = (gap_payload or {}).get("axis_gap")
    if isinstance(axis_gap, dict) and axis_gap:
        axis_by_gap = sorted(
            ((str(axis_name).upper(), float(axis_value)) for axis_name, axis_value in axis_gap.items()),
            key=lambda item: (item[1], item[0]),
            reverse=True,
        )
        if axis_by_gap and axis_by_gap[0][1] > 1e-6 and axis_by_gap[0][0] in {"X", "Y", "Z"}:
            return cast(Literal["X", "Y", "Z"], axis_by_gap[0][0])

    deltas = (alignment_payload or {}).get("deltas")
    if isinstance(deltas, dict) and deltas:
        axis_by_delta = sorted(
            ((str(axis_name).upper(), abs(float(axis_value))) for axis_name, axis_value in deltas.items()),
            key=lambda item: (item[1], item[0]),
            reverse=True,
        )
        if axis_by_delta and axis_by_delta[0][0] in {"X", "Y", "Z"}:
            return cast(Literal["X", "Y", "Z"], axis_by_delta[0][0])

    return "X"


def _preferred_attach_surface_side(
    *,
    axis_name: Literal["X", "Y", "Z"],
    alignment_payload: dict[str, Any] | None,
) -> Literal["positive", "negative"]:
    deltas = (alignment_payload or {}).get("deltas")
    if not isinstance(deltas, dict):
        return "positive"
    axis_delta = deltas.get(axis_name.lower())
    if axis_delta is None:
        return "positive"
    return "negative" if float(axis_delta) >= 0.0 else "positive"


def build_truth_followup(bundle: SceneCorrectionTruthBundleContract) -> SceneTruthFollowupContract:
    if bundle.summary.pair_count == 0:
        return SceneTruthFollowupContract(
            scope=bundle.scope,
            continue_recommended=False,
            message="No pairwise truth checks are available for this assembled target scope yet.",
            focus_pairs=[],
            items=[],
            macro_candidates=[],
        )

    items: list[SceneTruthFollowupItemContract] = []
    macro_candidates: list[SceneRepairMacroCandidateContract] = []
    focus_pairs: list[str] = []
    seen_pairs: set[str] = set()
    pair_issue_kinds: dict[str, set[str]] = {}
    pair_attachment_semantics: dict[str, SceneAttachmentSemanticsContract] = {}
    pair_support_semantics: dict[str, SceneSupportSemanticsContract] = {}
    pair_symmetry_semantics: dict[str, SceneSymmetrySemanticsContract] = {}
    pair_checks_by_label: dict[str, SceneCorrectionTruthPairContract] = {}

    for check in bundle.checks:
        current_pair_label = pair_label(check.from_object, check.to_object)
        pair_checks_by_label[current_pair_label] = check
        pair_items: list[SceneTruthFollowupItemContract] = []
        if check.error:
            pair_items.append(
                SceneTruthFollowupItemContract(
                    kind="measurement_error",
                    summary=f"Truth checks failed for {current_pair_label}: {check.error}",
                    priority="high",
                    from_object=check.from_object,
                    to_object=check.to_object,
                    relation_pair_id=check.relation_pair_id,
                    relation_kinds=list(check.relation_kinds or []),
                    relation_verdicts=list(check.relation_verdicts or []),
                )
            )
        else:
            contact_note = _contact_semantics_note(gap_payload=check.gap, contact_assertion=check.contact_assertion)
            attachment_semantics = check.attachment_semantics
            attachment_relation = _attachment_relation(check.from_object, check.to_object)
            if attachment_semantics is None and attachment_relation is not None:
                relation_kind, part_object, anchor_object = attachment_relation
                attachment_semantics = SceneAttachmentSemanticsContract(
                    relation_kind=relation_kind,
                    seam_kind=_attachment_seam_kind(part_object, anchor_object),
                    part_object=part_object,
                    anchor_object=anchor_object,
                    required_seam=False,
                    preferred_macro=_preferred_attachment_macro(relation_kind),
                    attachment_verdict=_attachment_verdict(
                        relation_kind=relation_kind,
                        seam_kind=_attachment_seam_kind(part_object, anchor_object),
                        gap_payload=check.gap,
                        alignment_payload=check.alignment,
                        overlap_payload=check.overlap,
                        contact_assertion=check.contact_assertion,
                    ),
                )
            has_contact_failure = check.contact_assertion is not None and not check.contact_assertion.passed
            has_gap = check.gap is not None and str(check.gap.get("relation") or "").lower() == "separated"
            has_overlap = check.overlap is not None and bool(check.overlap.get("overlaps"))
            has_alignment_issue = _has_actionable_attachment_alignment_issue(
                attachment_semantics=attachment_semantics,
                alignment_payload=check.alignment,
                contact_assertion=check.contact_assertion,
            )
            if attachment_semantics is not None and (
                has_contact_failure or has_gap or has_overlap or has_alignment_issue
            ):
                pair_attachment_semantics[current_pair_label] = attachment_semantics
                pair_items.append(
                    SceneTruthFollowupItemContract(
                        kind="attachment",
                        summary=_attachment_item_summary(
                            pair_label=current_pair_label,
                            relation_kind=attachment_semantics.relation_kind,
                            has_overlap=has_overlap,
                            has_gap=has_gap,
                            has_contact_failure=has_contact_failure,
                            has_alignment_issue=has_alignment_issue,
                        ),
                        priority="high",
                        from_object=check.from_object,
                        to_object=check.to_object,
                        tool_name="scene_assert_contact",
                        relation_pair_id=check.relation_pair_id,
                        relation_kinds=list(check.relation_kinds or []),
                        relation_verdicts=list(check.relation_verdicts or []),
                    )
                )
            if check.support_semantics is not None and check.support_semantics.verdict != "supported":
                pair_support_semantics[current_pair_label] = check.support_semantics
                pair_items.append(
                    SceneTruthFollowupItemContract(
                        kind="support",
                        summary=_support_item_summary(
                            pair_label=current_pair_label,
                            support_semantics=check.support_semantics,
                        ),
                        priority="high",
                        from_object=check.from_object,
                        to_object=check.to_object,
                        tool_name="scene_relation_graph",
                        relation_pair_id=check.relation_pair_id,
                        relation_kinds=list(check.relation_kinds or []),
                        relation_verdicts=list(check.relation_verdicts or []),
                    )
                )
            if check.symmetry_semantics is not None and check.symmetry_semantics.verdict != "symmetric":
                pair_symmetry_semantics[current_pair_label] = check.symmetry_semantics
                pair_items.append(
                    SceneTruthFollowupItemContract(
                        kind="symmetry",
                        summary=_symmetry_item_summary(
                            pair_label=current_pair_label,
                            symmetry_semantics=check.symmetry_semantics,
                        ),
                        priority="high",
                        from_object=check.from_object,
                        to_object=check.to_object,
                        tool_name="scene_assert_symmetry",
                        relation_pair_id=check.relation_pair_id,
                        relation_kinds=list(check.relation_kinds or []),
                        relation_verdicts=list(check.relation_verdicts or []),
                    )
                )
            if check.contact_assertion is not None and not check.contact_assertion.passed:
                pair_items.append(
                    SceneTruthFollowupItemContract(
                        kind="contact_failure",
                        summary=(
                            f"{current_pair_label} failed the contact assertion: {contact_note}"
                            if contact_note
                            else f"{current_pair_label} failed the contact assertion."
                        ),
                        priority="high",
                        from_object=check.from_object,
                        to_object=check.to_object,
                        tool_name="scene_assert_contact",
                        relation_pair_id=check.relation_pair_id,
                        relation_kinds=list(check.relation_kinds or []),
                        relation_verdicts=list(check.relation_verdicts or []),
                    )
                )
            if check.gap is not None and str(check.gap.get("relation") or "").lower() == "separated":
                pair_items.append(
                    SceneTruthFollowupItemContract(
                        kind="gap",
                        summary=(
                            f"{current_pair_label} still has measurable surface separation. {contact_note}"
                            if contact_note
                            else f"{current_pair_label} still has measurable separation."
                        ),
                        priority="normal",
                        from_object=check.from_object,
                        to_object=check.to_object,
                        tool_name="scene_measure_gap",
                        relation_pair_id=check.relation_pair_id,
                        relation_kinds=list(check.relation_kinds or []),
                        relation_verdicts=list(check.relation_verdicts or []),
                    )
                )
            if check.overlap is not None and bool(check.overlap.get("overlaps")):
                pair_items.append(
                    SceneTruthFollowupItemContract(
                        kind="overlap",
                        summary=f"{current_pair_label} still overlaps.",
                        priority="high",
                        from_object=check.from_object,
                        to_object=check.to_object,
                        tool_name="scene_measure_overlap",
                        relation_pair_id=check.relation_pair_id,
                        relation_kinds=list(check.relation_kinds or []),
                        relation_verdicts=list(check.relation_verdicts or []),
                    )
                )
            if has_alignment_issue:
                pair_items.append(
                    SceneTruthFollowupItemContract(
                        kind="alignment",
                        summary=f"{current_pair_label} is still misaligned.",
                        priority="normal",
                        from_object=check.from_object,
                        to_object=check.to_object,
                        tool_name="scene_measure_alignment",
                        relation_pair_id=check.relation_pair_id,
                        relation_kinds=list(check.relation_kinds or []),
                        relation_verdicts=list(check.relation_verdicts or []),
                    )
                )
        items.extend(pair_items)

        if any(item.from_object == check.from_object and item.to_object == check.to_object for item in items):
            if current_pair_label not in seen_pairs:
                seen_pairs.add(current_pair_label)
                focus_pairs.append(current_pair_label)
            pair_issue_kinds[current_pair_label] = {item.kind for item in pair_items}

    for current_pair_label in focus_pairs:
        issue_kinds = pair_issue_kinds.get(current_pair_label, set())
        if not issue_kinds:
            continue
        if "measurement_error" in issue_kinds:
            continue
        from_object, to_object = current_pair_label.split(" -> ", 1)
        pair_check = pair_checks_by_label.get(current_pair_label)
        attachment_semantics = pair_attachment_semantics.get(current_pair_label)
        if attachment_semantics is not None:
            preferred_macro = attachment_semantics.preferred_macro or _preferred_attachment_macro(
                attachment_semantics.relation_kind
            )
            if attachment_semantics.attachment_verdict == "intersecting" and attachment_semantics.relation_kind in {
                "segment_attachment",
                "seated_attachment",
            }:
                preferred_macro = "macro_attach_part_to_surface"
            if preferred_macro == "macro_attach_part_to_surface":
                surface_axis = _preferred_attach_surface_axis(
                    gap_payload=pair_check.gap if pair_check is not None else None,
                    alignment_payload=pair_check.alignment if pair_check is not None else None,
                )
                surface_side = _preferred_attach_surface_side(
                    axis_name=surface_axis,
                    alignment_payload=pair_check.alignment if pair_check is not None else None,
                )
                macro_candidates.append(
                    SceneRepairMacroCandidateContract(
                        macro_name="macro_attach_part_to_surface",
                        reason=(
                            "Use a bounded surface-seating move for this attachment seam instead of treating "
                            "intersecting parts as a generic side-push cleanup."
                        ),
                        priority="high",
                        arguments_hint={
                            "part_object": attachment_semantics.part_object,
                            "surface_object": attachment_semantics.anchor_object,
                            "surface_axis": surface_axis,
                            "surface_side": surface_side,
                            "align_mode": "center",
                            "gap": 0.0,
                        },
                    )
                )
                continue
            macro_candidates.append(
                SceneRepairMacroCandidateContract(
                    macro_name="macro_align_part_with_contact",
                    reason=(
                        "Use a bounded attachment/contact repair for this seam instead of relying on generic "
                        "overlap cleanup alone."
                    ),
                    priority="high",
                    arguments_hint={
                        "part_object": attachment_semantics.part_object,
                        "reference_object": attachment_semantics.anchor_object,
                        "target_relation": "contact",
                        "align_mode": "none",
                        "preserve_side": True,
                    },
                )
            )
            continue
        support_semantics = pair_support_semantics.get(current_pair_label)
        if support_semantics is not None:
            macro_candidates.append(
                SceneRepairMacroCandidateContract(
                    macro_name="macro_place_supported_pair",
                    reason=(
                        "Use a bounded support-placement move so the supported object rests on the intended base "
                        "instead of relying on free-form transforms."
                    ),
                    priority="high",
                    arguments_hint={
                        "supported_object": support_semantics.supported_object,
                        "support_object": support_semantics.support_object,
                        "axis": support_semantics.axis,
                        "gap": 0.0,
                    },
                )
            )
            continue
        symmetry_semantics = pair_symmetry_semantics.get(current_pair_label)
        if symmetry_semantics is not None:
            macro_candidates.append(
                SceneRepairMacroCandidateContract(
                    macro_name="macro_place_symmetry_pair",
                    reason=(
                        "Use a bounded symmetry placement move so the pair is re-mirrored instead of relying on "
                        "free-form manual offsets."
                    ),
                    priority="high",
                    arguments_hint={
                        "left_object": symmetry_semantics.left_object,
                        "right_object": symmetry_semantics.right_object,
                        "axis": symmetry_semantics.axis,
                    },
                )
            )
            continue
        if "overlap" in issue_kinds:
            macro_candidates.append(
                SceneRepairMacroCandidateContract(
                    macro_name="macro_cleanup_part_intersections",
                    reason="Use a bounded cleanup push to separate the overlapping pair without broad manual re-placement.",
                    priority="high",
                    arguments_hint={
                        "part_object": from_object,
                        "reference_object": to_object,
                        "gap": 0.0,
                        "preserve_side": True,
                    },
                )
            )
            continue
        if not issue_kinds.intersection({"contact_failure", "gap", "alignment"}):
            continue
        macro_candidates.append(
            SceneRepairMacroCandidateContract(
                macro_name="macro_align_part_with_contact",
                reason="Use a bounded repair nudge to restore contact/alignment without re-placing the pair from scratch.",
                priority="high" if "contact_failure" in issue_kinds else "normal",
                arguments_hint={
                    "part_object": from_object,
                    "reference_object": to_object,
                    "target_relation": "contact",
                    "align_mode": "none",
                    "preserve_side": True,
                },
            )
        )

    return SceneTruthFollowupContract(
        scope=bundle.scope,
        continue_recommended=bool(items),
        message=(
            f"Truth follow-up identified {len(items)} actionable finding(s), plus {len(macro_candidates)} repair macro candidate(s), across {len(focus_pairs)} pair(s)."
            if items
            else "Truth follow-up found no actionable pairwise issues for the current assembled target scope."
        ),
        focus_pairs=focus_pairs,
        items=items,
        macro_candidates=macro_candidates,
    )
