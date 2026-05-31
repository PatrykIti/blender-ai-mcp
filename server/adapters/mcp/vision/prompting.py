# SPDX-FileCopyrightText: 2024-2026 Patryk Ciechański
# SPDX-License-Identifier: Apache-2.0

"""Prompt-building helpers for bounded vision backends."""

from __future__ import annotations

import json

from .backend import VisionImageInput, VisionRequest
from .config import VisionContractProfile, VisionModelCapabilities

# Canonical view tokens that may appear inside a deterministic capture label
# (e.g. ``target_front_after``). Ordered longest-first so multi-word tokens win.
_CAPTION_VIEW_TOKENS = (
    "oblique_left",
    "oblique_right",
    "overhead",
    "front",
    "side",
    "back",
    "left",
    "right",
    "top",
    "bottom",
    "detail",
    "focus",
    "wide",
    "grid",
    "depth",
    "normal",
    "object_id",
)
_AUXILIARY_CAPTION_CHANNELS: dict[str, str] = {
    "depth": "relative_depth",
    "normal": "surface_normal",
    "object_id": "object_id_mask",
}


def _derive_caption_view(label: str | None) -> str | None:
    """Derive the canonical view hint from a deterministic capture label.

    Capture labels are built upstream as ``f"{preset.name}_{stage}"`` (for
    example ``target_front_after`` or ``context_wide_before``). The view token is
    an advisory grounding hint only; when it cannot be derived it is omitted
    rather than guessed. The before/after stage is intentionally not echoed: it
    is already carried by ``role`` and by the label text itself.
    """

    if not label:
        return None
    lowered = label.lower()
    for candidate in _CAPTION_VIEW_TOKENS:
        if candidate in lowered:
            return candidate
    return None


def format_image_caption(image: VisionImageInput) -> str:
    """Return one deterministic, symbolic identity caption for an image.

    This single format is reused both as the per-image caption interleaved
    immediately before each image part in the transmitted request payload and as
    the flat image-roster line, so the orchestrating VLM sees the same identity
    string in both places and can bind each blob to its role/view instead of
    guessing positionally. The caption stays symbolic: it names only the label,
    role, and the view token derivable from the label. It never emits raw
    coordinates, absolute metric magnitudes, or chain-of-thought.
    """

    label = image.label or image.role
    parts = [f"image: {label}", f"role={image.role}"]
    view = image.view_kind or _derive_caption_view(image.label)
    if view is not None:
        parts.append(f"view={view}")
        if image.projection is not None:
            parts.append(f"projection={image.projection}")
        auxiliary_channel = _AUXILIARY_CAPTION_CHANNELS.get(view)
        if auxiliary_channel is not None:
            parts.append(f"channel={auxiliary_channel}")
            parts.append("advisory=geometric_enrichment_not_truth_source")
    return "[" + " | ".join(parts) + "]"


def format_image_roster_line(image: VisionImageInput) -> str:
    """Return the flat roster line for an image.

    Kept deliberately lean (``- role: label``): the richer bracketed identity
    string from ``format_image_caption`` is interleaved directly before each image
    in the external request payload, but small local (MLX) models are sensitive to
    the more verbose roster wording, so the roster keeps its baseline format.
    """

    return f"- {image.role}: {image.label or image.role}"


def _image_roster_lines(request: VisionRequest) -> list[str]:
    """Return the per-image roster lines for a request's images."""

    return [format_image_roster_line(image) for image in request.images]


def _mark_overlay_lines(request: VisionRequest) -> list[str]:
    """Return symbolic Set-of-Mark legend lines from request metadata."""

    overlays = request.metadata.get("mark_overlays") if isinstance(request.metadata, dict) else None
    lines: list[str] = []
    if isinstance(overlays, list):
        for overlay in overlays:
            if not isinstance(overlay, dict):
                continue
            label = str(overlay.get("label") or "overlay").strip()
            marks = overlay.get("marks")
            if not isinstance(marks, list):
                continue
            for mark in marks:
                if not isinstance(mark, dict):
                    continue
                mark_id = mark.get("mark_id")
                object_name = str(mark.get("object_name") or "").strip()
                status = str(mark.get("status") or "placed").strip()
                source = str(mark.get("source") or "deterministic_projection").strip()
                image_side = str(mark.get("image_side") or "render").strip()
                if not isinstance(mark_id, int) or isinstance(mark_id, bool) or not object_name:
                    continue
                if status != "placed":
                    continue
                lines.append(f"- {label}: mark {mark_id} -> {object_name} ({image_side}, {source})")
    reference_marks = request.metadata.get("reference_marks") if isinstance(request.metadata, dict) else None
    if isinstance(reference_marks, list):
        for mark in reference_marks:
            if not isinstance(mark, dict):
                continue
            mark_id = mark.get("mark_id")
            object_name = str(mark.get("object_name") or "").strip()
            status = str(mark.get("status") or "placed").strip()
            source = str(mark.get("source") or "grounded_sam_sidecar").strip()
            if not isinstance(mark_id, int) or isinstance(mark_id, bool) or not object_name:
                continue
            if status != "placed":
                continue
            lines.append(f"- reference: mark {mark_id} -> {object_name} (reference, {source})")
    if not lines:
        mark_id_map = request.metadata.get("packet_mark_id_map") if isinstance(request.metadata, dict) else None
        if isinstance(mark_id_map, dict):
            for object_name, mark_id in sorted(mark_id_map.items(), key=lambda item: (item[1], item[0])):
                if isinstance(mark_id, int) and not isinstance(mark_id, bool) and str(object_name).strip():
                    lines.append(f"- packet_map: mark {mark_id} -> {object_name} (render, deterministic_projection)")
    return lines


def _dominant_relation_phrase(pair: dict[str, object]) -> str | None:
    """Pick the single most informative symbolic relation for one graph pair."""

    gap_relation = pair.get("gap_relation")
    if isinstance(gap_relation, str) and gap_relation:
        return gap_relation
    if pair.get("contact_passed") is True:
        return "contact"
    overlap_relation = pair.get("overlap_relation")
    if isinstance(overlap_relation, str) and overlap_relation in {"overlap", "contained"}:
        return overlap_relation
    relation_kinds = pair.get("relation_kinds")
    if isinstance(relation_kinds, list):
        for kind in relation_kinds:
            if isinstance(kind, str) and kind.strip():
                return kind.strip()
    if pair.get("alignment_status") == "misaligned":
        return "misaligned"
    return None


def serialize_relation_triplets(pairs: object, *, max_per_object: int = 4) -> list[str]:
    """Serialize a deterministic scene relation graph as symbolic ``a relation b``
    triplets, grouped per subject object and capped per object.

    This is the relations-not-coordinates representation: it emits the structural
    relationships between parts (contact / gap / overlap / symmetry / alignment),
    never raw coordinates, because symbolic relations ground an LLM's spatial
    reasoning far better than coordinate tokens. Accepts the list of pair dicts
    from a relation-graph payload (e.g. ``truth_summary['relation_graph']['pairs']``).
    """

    if not isinstance(pairs, list):
        return []
    per_object_count: dict[str, int] = {}
    triplets: list[str] = []
    for pair in pairs:
        if not isinstance(pair, dict):
            continue
        from_object = str(pair.get("from_object") or "").strip()
        to_object = str(pair.get("to_object") or "").strip()
        if not from_object or not to_object:
            continue
        relation = _dominant_relation_phrase(pair)
        if relation is None:
            continue
        if per_object_count.get(from_object, 0) >= max_per_object:
            continue
        per_object_count[from_object] = per_object_count.get(from_object, 0) + 1
        triplets.append(f"{from_object} {relation} {to_object}")
    return triplets


def _relation_triplet_lines_from_truth(truth_summary: object) -> list[str]:
    """Extract relation-graph pairs from a truth summary (in either of the common
    locations) and serialize them as symbolic triplets, or return []."""

    if not isinstance(truth_summary, dict):
        return []
    pairs = truth_summary.get("pairs")
    if not isinstance(pairs, list):
        relation_graph = truth_summary.get("relation_graph")
        if isinstance(relation_graph, dict):
            pairs = relation_graph.get("pairs")
    return serialize_relation_triplets(pairs)


_EXPECTED_KEYS = (
    "goal_summary",
    "reference_match_summary",
    "visible_changes",
    "shape_mismatches",
    "proportion_mismatches",
    "correction_focus",
    "likely_issues",
    "next_corrections",
    "recommended_checks",
    "findings",
    "confidence",
    "captures_used",
)
_PACKET_COMPARE_EXPECTED_KEYS = (
    "goal_summary",
    "reference_match_summary",
    "visible_changes",
    "shape_mismatches",
    "proportion_mismatches",
    "correction_focus",
    "likely_issues",
    "next_corrections",
    "recommended_checks",
    "findings",
    "packet_guidance",
    "confidence",
    "captures_used",
)

# Strict-mode JSON Schema for the additive structured per-finding compare channel
# (TASK-178). Every property is required with a nullable type so strict providers
# accept it; the model populates view/object/axis/proportional-magnitude when it
# can and uses null otherwise. Parallel to the string lists, advisory only.
_FINDINGS_SCHEMA: dict[str, object] = {
    "type": "array",
    "items": {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "finding": {"type": "string"},
            "view_id": {"type": ["string", "null"]},
            "target_label": {"type": ["string", "null"]},
            "axis": {"type": ["string", "null"], "enum": ["x", "y", "z", "none", None]},
            "direction": {"type": ["string", "null"], "enum": ["increase", "decrease", "none", None]},
            "magnitude_ratio": {"type": ["number", "null"]},
            "reference_id": {"type": ["string", "null"]},
            "confidence": {"type": ["number", "null"]},
            "mark_id": {"type": ["integer", "null"]},
        },
        "required": [
            "finding",
            "view_id",
            "target_label",
            "axis",
            "direction",
            "magnitude_ratio",
            "reference_id",
            "confidence",
            "mark_id",
        ],
    },
}
_GEMINI_COMPARE_EXPECTED_KEYS = (
    "goal_summary",
    "reference_match_summary",
    "shape_mismatches",
    "proportion_mismatches",
    "correction_focus",
    "next_corrections",
    "findings",
)
_REFERENCE_UNDERSTANDING_EXPECTED_KEYS = (
    "subject",
    "style",
    "views",
    "required_parts",
    "mass_recipe",
    "attachment_plan",
    "contact_expectations",
    "shape_profile_hints",
    "silhouette_landmarks",
    "part_order",
    "must_seat_before_next_stage",
    "non_goals",
    "construction_strategy",
    "router_handoff_hints",
    "gate_proposals",
    "visual_evidence_refs",
    "verification_requirements",
)
_REFERENCE_CLASSIFICATION_EXPECTED_KEYS = ("classification_scores",)

_REFERENCE_GUIDED_CHECKPOINT_MODES = (
    "comparison_mode=checkpoint_vs_reference",
    "comparison_mode=current_view_checkpoint",
    "comparison_mode=stage_checkpoint_vs_reference",
)
_DEFAULT_VISION_CONTRACT_PROFILE: VisionContractProfile = "generic_full"


def _is_reference_guided_checkpoint(request: VisionRequest) -> bool:
    prompt_hint = (request.prompt_hint or "").lower()
    has_reference = any(image.role == "reference" for image in request.images)
    return has_reference and any(mode in prompt_hint for mode in _REFERENCE_GUIDED_CHECKPOINT_MODES)


def _is_reference_understanding_request(request: VisionRequest | None) -> bool:
    if request is None:
        return False
    mode = str(request.metadata.get("mode") or "").strip().lower()
    return mode == "reference_understanding"


def _is_reference_classification_request(request: VisionRequest | None) -> bool:
    if request is None:
        return False
    mode = str(request.metadata.get("mode") or "").strip().lower()
    return mode == "reference_classification"


def _is_reference_packet_compare_request(request: VisionRequest | None) -> bool:
    if request is None:
        return False
    mode = str(request.metadata.get("mode") or "").strip().lower()
    return mode == "reference_compare_packet"


def _reference_packet_compare_phase(request: VisionRequest | None) -> str:
    if request is None:
        return "packet_extraction"
    phase = str(request.metadata.get("compare_phase") or "").strip().lower()
    if phase in {"packet_extraction", "packet_ranking"}:
        return phase
    return "packet_extraction"


def resolve_vision_contract_profile(
    *,
    vision_contract_profile: VisionContractProfile | None = None,
    provider_name: str | None = None,
) -> VisionContractProfile:
    """Resolve one prompt/parser contract profile with backward-compatible provider fallback."""

    if vision_contract_profile is not None:
        return vision_contract_profile
    if provider_name == "google_ai_studio":
        return "google_family_compare"
    return _DEFAULT_VISION_CONTRACT_PROFILE


def _uses_google_family_compare_contract(
    *,
    vision_contract_profile: VisionContractProfile | None,
    provider_name: str | None,
    request: VisionRequest | None,
) -> bool:
    resolved_profile = resolve_vision_contract_profile(
        vision_contract_profile=vision_contract_profile,
        provider_name=provider_name,
    )
    return (
        resolved_profile == "google_family_compare" and request is not None and _is_reference_guided_checkpoint(request)
    )


def _local_output_template(request: VisionRequest) -> str:
    labels = [image.label or image.role for image in request.images]
    template: dict[str, object] = {
        "goal_summary": "One short sentence about whether the after images move toward the goal/reference.",
        "reference_match_summary": None,
        "visible_changes": [],
        "shape_mismatches": [],
        "proportion_mismatches": [],
        "correction_focus": [],
        "likely_issues": [],
        "next_corrections": [],
        "recommended_checks": [],
        "confidence": None,
        "captures_used": labels,
    }
    return json.dumps(template, ensure_ascii=True, indent=2)


def _gemini_compare_output_template() -> str:
    template: dict[str, object] = {
        "goal_summary": "One short sentence about whether the current checkpoint moves toward the goal/reference.",
        "reference_match_summary": None,
        "shape_mismatches": [],
        "proportion_mismatches": [],
        "correction_focus": [],
        "next_corrections": [],
    }
    return json.dumps(template, ensure_ascii=True, indent=2)


def _packet_compare_output_template(request: VisionRequest) -> str:
    labels = [image.label or image.role for image in request.images]
    template: dict[str, object] = {
        "goal_summary": "One short sentence about the packet-local compare outcome.",
        "reference_match_summary": None,
        "visible_changes": [],
        "shape_mismatches": [],
        "proportion_mismatches": [],
        "correction_focus": [],
        "likely_issues": [],
        "next_corrections": [],
        "recommended_checks": [],
        "packet_guidance": {
            "packet_status": "ready",
            "status_reason": None,
            "ranking_recommendation": "rank",
        },
        "confidence": None,
        "captures_used": labels,
    }
    return json.dumps(template, ensure_ascii=True, indent=2)


def _reference_understanding_output_template() -> str:
    template: dict[str, object] = {
        "subject": {
            "label": "low poly squirrel",
            "category": "creature",
            "confidence": 0.8,
            "uncertainty_notes": [],
        },
        "style": {
            "style_label": "low_poly_faceted",
            "confidence": 0.8,
            "notes": [],
        },
        "views": [
            {
                "view_id": "front",
                "detected": True,
                "confidence": 0.9,
                "reference_ids": [],
                "key_features": [],
            }
        ],
        "required_parts": [
            {
                "part_label": "body core",
                "target_label": "body_core",
                "construction_hint": "Start with a simple faceted primary mass.",
                "priority": "high",
                "source_reference_ids": [],
            }
        ],
        "mass_recipe": [
            {
                "target_label": "body_core",
                "geometry_family": "box_mass",
                "construction_hint": "Start with the main torso block before appendages.",
                "anchor_role_candidates": [],
                "support_surface_candidates": [],
                "contact_expectations": [],
                "source_reference_ids": [],
            }
        ],
        "attachment_plan": [
            {
                "target_label": "head_mass",
                "anchor_role_candidates": ["body_core"],
                "required_relation": "segment_attachment",
                "support_surface_candidates": ["body_core_front_top"],
                "contact_expectations": ["seat head mass flush against the body front."],
                "notes": [],
            }
        ],
        "contact_expectations": [
            {
                "target_label": "tail_mass",
                "expected_contacts": ["body_core_rear"],
                "avoid_contacts": ["ground_plane"],
                "notes": [],
            }
        ],
        "shape_profile_hints": [
            {
                "target_label": "tail_mass",
                "summary": "Keep the tail arc readable as one low-poly silhouette move.",
                "reference_id": None,
            }
        ],
        "silhouette_landmarks": [
            {
                "landmark_id": "ear_tip_pair",
                "target_label": "ear_pair",
                "view_id": "front",
                "summary": "Ear tips should stay readable above the head silhouette.",
            }
        ],
        "part_order": ["body_core", "head_mass", "tail_mass", "snout_mass", "ear_pair"],
        "must_seat_before_next_stage": ["tail_mass", "snout_mass"],
        "non_goals": [],
        "construction_strategy": {
            "construction_path": "low_poly_facet",
            "primary_family": "modeling_mesh",
            "allowed_families": ["macro", "modeling_mesh", "inspect_only"],
            "stage_sequence": ["primary_masses", "secondary_parts", "inspect_validate"],
            "finish_policy": "preserve_facets",
        },
        "router_handoff_hints": {
            "preferred_family": "modeling_mesh",
            "allowed_guided_families": ["reference_context", "primary_masses", "secondary_parts", "inspect_validate"],
            "sculpt_policy": "hidden",
        },
        "gate_proposals": [],
        "visual_evidence_refs": [],
        "verification_requirements": [],
    }
    return json.dumps(template, ensure_ascii=True, indent=2)


def _reference_classification_output_template() -> str:
    template: dict[str, object] = {
        "classification_scores": [
            {"label": "low_poly_faceted", "score": 0.92},
            {"label": "creature_blockout", "score": 0.61},
        ]
    }
    return json.dumps(template, ensure_ascii=True, indent=2)


def build_vision_system_prompt(
    *,
    backend_kind: str,
    vision_contract_profile: VisionContractProfile | None = None,
    provider_name: str | None = None,
    request: VisionRequest | None = None,
) -> str:
    """Return the bounded system prompt, tuned slightly by backend family."""

    if _is_reference_packet_compare_request(request):
        packet_phase = _reference_packet_compare_phase(request)
        if packet_phase == "packet_ranking":
            return (
                "You are a bounded packet-ranking vision assistant for Blender modeling.\n\n"
                "This request is the second staged compare phase for one packet only.\n"
                "The packet already has bounded extraction evidence. Use the provided extraction summary to rank the "
                "most important correction focus and next corrections. Do not rediscover the whole packet from scratch.\n"
                "You are not the truth source. Do not infer scene-wide conclusions from this packet alone.\n\n"
                "Return exactly one JSON object with only these keys:\n"
                "- goal_summary\n"
                "- reference_match_summary\n"
                "- visible_changes\n"
                "- shape_mismatches\n"
                "- proportion_mismatches\n"
                "- correction_focus\n"
                "- likely_issues\n"
                "- next_corrections\n"
                "- recommended_checks\n"
                "- packet_guidance\n"
                "- confidence\n"
                "- captures_used\n\n"
                "packet_guidance must be an object with exactly these keys:\n"
                '- packet_status: "ready" | "clean" | "low_information" | "blocked"\n'
                "- status_reason: string or null\n"
                '- ranking_recommendation: "rank" | "skip_clean" | "skip_low_information" | "skip_blocked"\n\n'
                "Rules:\n"
                "- treat the extracted mismatches as the source material to rank and phrase cleanly\n"
                "- keep correction_focus and next_corrections bounded to 0-3 items each\n"
                "- preserve packet_status=ready unless the supplied extraction evidence itself is too weak or blocked\n"
                "- do not inflate new mismatch classes that were not justified by the extraction evidence\n"
                "- use recommended_checks only for canonical MCP tool ids\n"
                "- do not echo the input payload and do not wrap the result in markdown\n"
            )
        return (
            "You are a bounded packet-compare vision assistant for Blender modeling.\n\n"
            "This request is one staged compare packet only. Work only on the provided packet-local captures, "
            "references, and deterministic truth slice.\n"
            "You are not the truth source. Do not infer scene-wide conclusions from this packet alone.\n"
            "Keep the extraction result bounded to 0-3 concrete mismatches and 0-3 conservative next corrections.\n\n"
            "Return exactly one JSON object with only these keys:\n"
            "- goal_summary\n"
            "- reference_match_summary\n"
            "- visible_changes\n"
            "- shape_mismatches\n"
            "- proportion_mismatches\n"
            "- correction_focus\n"
            "- likely_issues\n"
            "- next_corrections\n"
            "- recommended_checks\n"
            "- packet_guidance\n"
            "- confidence\n"
            "- captures_used\n\n"
            "packet_guidance must be an object with exactly these keys:\n"
            '- packet_status: "ready" | "clean" | "low_information" | "blocked"\n'
            "- status_reason: string or null\n"
            '- ranking_recommendation: "rank" | "skip_clean" | "skip_low_information" | "skip_blocked"\n\n'
            "Rules:\n"
            "- packet_status=ready only when the packet contains enough signal for bounded mismatch extraction\n"
            "- packet_status=clean when the packet looks visually acceptable and no ranking pass is needed\n"
            "- packet_status=low_information when the packet is too weak, ambiguous, or incomplete\n"
            "- packet_status=blocked when the packet cannot be interpreted because the required packet-local evidence is missing\n"
            "- ranking_recommendation must match packet_status\n"
            "- if packet_status is clean, low_information, or blocked, keep correction_focus and next_corrections conservative\n"
            "- use recommended_checks only for canonical MCP tool ids\n"
            "- do not echo the input payload and do not wrap the result in markdown\n"
        )

    if _is_reference_classification_request(request):
        return (
            "You are a bounded reference-classification assistant for Blender modeling.\n\n"
            "Interpret only the attached reference images and the build goal.\n"
            "You are advisory only. You are not the truth source, may not unlock tools, and may not mark gates passed.\n"
            "Return exactly one JSON object with only this key:\n"
            "- classification_scores\n\n"
            "classification_scores must be an array of 1-5 objects sorted from strongest to weakest.\n"
            "Each item must contain:\n"
            "- label: string\n"
            "- score: number between 0.0 and 1.0\n\n"
            "Prefer labels that help Blender build-strategy choice, such as:\n"
            "- low_poly_faceted\n"
            "- creature_blockout\n"
            "- smooth_organic\n"
            "- hard_surface\n"
            "- architectural_mass\n"
            "- dental_surface\n"
            "- organic_sculpt\n"
        )

    if _is_reference_understanding_request(request):
        return (
            "You are a bounded reference-understanding assistant for Blender modeling.\n\n"
            "Interpret only the attached reference images and the build goal.\n"
            "You are advisory only. You are not the truth source, may not unlock tools, and may not mark gates passed.\n"
            "Use only current canonical planner families: macro, modeling_mesh, sculpt_region, inspect_only.\n"
            "Use only current canonical guided families: spatial_context, reference_context, primary_masses, secondary_parts, attachment_alignment, checkpoint_iterate, inspect_validate, finish, utility.\n"
            "Normalize draft aliases: mesh_edit -> modeling_mesh. material_finish is not a canonical family. macro_create_part is historical shorthand, not a current tool. mesh_shade_flat and macro_low_poly_* are future candidates only.\n"
            "For creature assembly cues, prefer canonical role labels such as body_core, head_mass, tail_mass, snout_mass, ear_pair, eye_pair, foreleg_pair, and hindleg_pair.\n"
            "Use anchor_role_candidates rather than scene-object names. If you were going to say anchor_object_candidates, convert that idea into canonical semantic role labels instead.\n"
            "Do not return raw Blender code, provider secrets, hidden/internal tools, passed/final-completion status, or a public router strategy tool.\n\n"
            "Return exactly one JSON object with only these keys:\n"
            "- subject\n"
            "- style\n"
            "- views\n"
            "- required_parts\n"
            "- mass_recipe\n"
            "- attachment_plan\n"
            "- contact_expectations\n"
            "- shape_profile_hints\n"
            "- silhouette_landmarks\n"
            "- part_order\n"
            "- must_seat_before_next_stage\n"
            "- non_goals\n"
            "- construction_strategy\n"
            "- router_handoff_hints\n"
            "- gate_proposals\n"
            "- visual_evidence_refs\n"
            "- verification_requirements\n"
        )

    if _uses_google_family_compare_contract(
        vision_contract_profile=vision_contract_profile,
        provider_name=provider_name,
        request=request,
    ):
        return (
            "You are a bounded vision assistant for Blender modeling.\n\n"
            "This request is a reference-guided checkpoint comparison for a Google-family vision contract.\n"
            "You are not the truth source. Use images only to compare the current checkpoint against the goal and references.\n"
            "Do not claim geometric correctness from images alone.\n\n"
            "Return exactly one JSON object with only these keys:\n"
            "- goal_summary: string\n"
            "- reference_match_summary: string or null\n"
            "- shape_mismatches: string[]\n"
            "- proportion_mismatches: string[]\n"
            "- correction_focus: string[]\n"
            "- next_corrections: string[]\n"
            "- findings: structured finding objects; set mark_id to a listed mark id or null\n\n"
            "Do not return visible_changes, likely_issues, recommended_checks, confidence, or captures_used.\n"
            "Do not echo the input payload. Do not wrap the result in markdown.\n"
            "Use shape_mismatches only for visible form/silhouette problems.\n"
            "Use proportion_mismatches only for visible size/ratio problems.\n"
            "Use correction_focus for the 1-3 highest-priority mismatch targets to fix next.\n"
            "Use next_corrections for 1-3 bounded next-step fixes that stay tightly aligned with those mismatches.\n"
            "When Set-of-Mark overlays are provided, key each shape/proportion finding to mark_id and do not invent marks.\n"
            "If the signal is weak, keep the arrays conservative but still return the required JSON shape.\n"
        )

    shared = (
        "You are a bounded vision assistant for Blender modeling.\n\n"
        "You are not the truth source. Use images only to interpret visible change and compare against the goal/reference.\n"
        "Do not claim geometric correctness from images alone. Recommend deterministic follow-up checks when correctness matters.\n\n"
        "Return exactly one JSON object with keys:\n"
        "- goal_summary: string\n"
        "- reference_match_summary: string or null\n"
        "- visible_changes: string[]\n"
        "- shape_mismatches: string[]\n"
        "- proportion_mismatches: string[]\n"
        "- correction_focus: string[]\n"
        '- likely_issues: [{"category": string, "summary": string, "severity": "high"|"medium"|"low"}]\n'
        "- next_corrections: string[]\n"
        '- recommended_checks: [{"tool_name": string, "reason": string, "priority": "high"|"normal"}]\n'
        "- confidence: number or null\n"
        "- captures_used: string[]\n"
    )
    if backend_kind in {"transformers_local", "mlx_local"}:
        return (
            shared
            + "\n"
            + "Do not explain the JSON. Do not echo the input payload. "
            + "Do not wrap the result in markdown unless unavoidable. "
            + "If there is a visible before/after difference, visible_changes must contain 1-3 short concrete visual items. "
            + "Leave visible_changes empty only when there is truly no visible change. "
            + "Do not use visible_changes for unchanged facts from truth_summary such as same dimensions, same center, or same volume. "
            + "Use shape_mismatches only for visible form/silhouette problems. "
            + "Use proportion_mismatches only for visible size/ratio relationship problems. "
            + "Use correction_focus for the 1-3 highest-priority mismatch targets to fix next. "
            + "Use next_corrections for 1-3 bounded next-step corrections only when they are visually justified. "
            + "Do not present next_corrections as proof that the fix is safe or correct; deterministic checks still decide correctness. "
            + "Leave likely_issues and recommended_checks empty unless there is a specific visible risk or a clearly valuable deterministic follow-up check. "
            + "If you do return recommended_checks, use only canonical MCP tool ids such as scene_measure_gap, scene_measure_overlap, scene_measure_alignment, scene_assert_contact, or scene_get_viewport. "
            + "For easy smoke or obvious progression cases, avoid filler likely_issues and avoid generic follow-up checks. "
            + "If signal is weak, still return the required JSON shape with conservative values.\n"
        )
    return shared


def _build_gemini_compare_payload_text(request: VisionRequest) -> str:
    image_lines = _image_roster_lines(request)
    truth_summary = request.truth_summary or {}
    truth_lines = []
    if isinstance(truth_summary, dict):
        for key, value in truth_summary.items():
            truth_lines.append(f"- {key}: {value}")

    parts = [
        "TASK:",
        "Compare the current checkpoint images against the active goal and the attached references.",
        "",
        f"GOAL: {request.goal}",
        f"TARGET_OBJECT: {request.target_object or 'none'}",
        f"PROMPT_HINT: {request.prompt_hint or 'none'}",
        "IMAGES:",
        *image_lines,
    ]
    if truth_lines:
        parts.extend(["TRUTH_SUMMARY:", *truth_lines])
    parts.extend(
        [
            "",
            "Return exactly one JSON object with only these keys:",
            "- goal_summary",
            "- reference_match_summary",
            "- shape_mismatches",
            "- proportion_mismatches",
            "- correction_focus",
            "- next_corrections",
            "Do not return visible_changes, likely_issues, recommended_checks, confidence, or captures_used.",
            "Do not repeat the input payload.",
            "Prefer concrete silhouette/proportion mismatches over generic praise.",
            "correction_focus should rank the most important fixes first.",
            "next_corrections should stay tightly aligned with the mismatches you listed.",
            "OUTPUT_TEMPLATE:",
            _gemini_compare_output_template(),
        ]
    )
    return "\n".join(parts)


def _build_reference_understanding_payload_text(request: VisionRequest) -> str:
    image_lines = _image_roster_lines(request)
    reference_ids = [str(item) for item in request.metadata.get("reference_ids") or []]
    reference_id_lines = [f"- {reference_id}" for reference_id in reference_ids]
    parts = [
        "TASK:",
        "Understand the attached references before any major build decision is made.",
        "",
        f"GOAL: {request.goal}",
        f"TARGET_OBJECT: {request.target_object or 'none'}",
        "REFERENCE_IMAGES:",
        *image_lines,
    ]
    if reference_id_lines:
        parts.extend(["REFERENCE_IDS:", *reference_id_lines])
    parts.extend(
        [
            "",
            "Return exactly one JSON object with only these keys:",
            "- subject",
            "- style",
            "- views",
            "- required_parts",
            "- non_goals",
            "- construction_strategy",
            "- router_handoff_hints",
            "- gate_proposals",
            "- visual_evidence_refs",
            "- verification_requirements",
            "",
            "Rules:",
            "- advisory only: do not claim passed/final-completion truth",
            "- do not unlock tools or invent a public router strategy tool",
            "- use current planner families only: macro, modeling_mesh, sculpt_region, inspect_only",
            "- use current guided families only: spatial_context, reference_context, primary_masses, secondary_parts, attachment_alignment, checkpoint_iterate, inspect_validate, finish, utility",
            "- normalize mesh_edit to modeling_mesh",
            "- do not use material_finish as a canonical family",
            "- treat macro_create_part, mesh_shade_flat, and macro_low_poly_* as historical/future ideas, not current tools",
            "- gate_proposals stay advisory and pending-oriented",
            "- verification_requirements should use canonical MCP tool ids only",
            "OUTPUT_TEMPLATE:",
            _reference_understanding_output_template(),
        ]
    )
    return "\n".join(parts)


def _build_reference_classification_payload_text(request: VisionRequest) -> str:
    image_lines = _image_roster_lines(request)
    reference_ids = [str(item) for item in request.metadata.get("reference_ids") or []]
    reference_id_lines = [f"- {reference_id}" for reference_id in reference_ids]
    parts = [
        "TASK:",
        "Classify the attached references into bounded style/build-strategy labels that can support Blender planning.",
        "",
        f"GOAL: {request.goal}",
        f"TARGET_OBJECT: {request.target_object or 'none'}",
        "REFERENCE_IMAGES:",
        *image_lines,
    ]
    if reference_id_lines:
        parts.extend(["REFERENCE_IDS:", *reference_id_lines])
    parts.extend(
        [
            "",
            "Return exactly one JSON object with only this key:",
            "- classification_scores",
            "",
            "Rules:",
            "- classification_scores must contain 1-5 bounded label/score pairs",
            "- sort from strongest to weakest",
            "- scores must stay between 0.0 and 1.0",
            "- labels should help Blender build-strategy choice, such as low_poly_faceted, creature_blockout, smooth_organic, hard_surface, architectural_mass, dental_surface, or organic_sculpt",
            "- advisory only: do not claim passed/final-completion truth",
            "- do not unlock tools, emit Blender code, or invent hidden/internal tools",
            "OUTPUT_TEMPLATE:",
            _reference_classification_output_template(),
        ]
    )
    return "\n".join(parts)


def build_vision_payload_text(
    request: VisionRequest,
    *,
    vision_contract_profile: VisionContractProfile | None = None,
    provider_name: str | None = None,
    model_capabilities: VisionModelCapabilities | None = None,
) -> str:
    """Serialize the bounded vision input payload."""

    if _is_reference_packet_compare_request(request):
        image_lines = _image_roster_lines(request)
        packet_id = str(request.metadata.get("packet_id") or "").strip() or "packet"
        packet_kind = str(request.metadata.get("packet_kind") or "").strip() or "view"
        packet_label = str(request.metadata.get("packet_label") or "").strip() or packet_id
        packet_phase = _reference_packet_compare_phase(request)
        packet_scope = str(request.metadata.get("packet_scope") or "").strip() or "none"
        packet_view = str(request.metadata.get("packet_view") or "").strip() or "none"
        reference_ids = [str(item) for item in request.metadata.get("packet_reference_ids") or []]
        capture_labels = [str(item) for item in request.metadata.get("packet_capture_labels") or []]
        support_evidence_summaries = [
            str(item) for item in request.metadata.get("support_evidence_summaries") or [] if str(item).strip()
        ]
        mark_overlay_lines = _mark_overlay_lines(request)
        truth_summary = request.truth_summary or {}
        truth_lines = []
        if isinstance(truth_summary, dict):
            for key, value in truth_summary.items():
                truth_lines.append(f"- {key}: {value}")
        parts = [
            "TASK:",
            "Interpret this staged compare packet only.",
            "",
            f"GOAL: {request.goal}",
            f"TARGET_OBJECT: {request.target_object or 'none'}",
            f"PACKET_ID: {packet_id}",
            f"PACKET_KIND: {packet_kind}",
            f"PACKET_LABEL: {packet_label}",
            f"COMPARE_PHASE: {packet_phase}",
            f"PACKET_VIEW: {packet_view}",
            f"PACKET_SCOPE: {packet_scope}",
            f"PROMPT_HINT: {request.prompt_hint or 'none'}",
            "IMAGES:",
            *image_lines,
        ]
        if reference_ids:
            parts.extend(["PACKET_REFERENCE_IDS:", *[f"- {item}" for item in reference_ids]])
        if capture_labels:
            parts.extend(["PACKET_CAPTURE_LABELS:", *[f"- {item}" for item in capture_labels]])
        if mark_overlay_lines:
            parts.extend(
                [
                    "MARK_OVERLAYS:",
                    *mark_overlay_lines,
                    "MARK_RULES:",
                    "- Key each shape/proportion finding to mark_id when the relevant object has a mark.",
                    "- Use only listed mark ids; do not invent marks.",
                    "- Magnitudes are proportional ratios versus a named anchor, never absolute measurements.",
                ]
            )
        if support_evidence_summaries:
            parts.extend(["SUPPORT_EVIDENCE:", *[f"- {item}" for item in support_evidence_summaries]])
        relation_triplets = _relation_triplet_lines_from_truth(request.truth_summary)
        if relation_triplets:
            parts.extend(["SCENE_RELATIONS:", *[f"- {item}" for item in relation_triplets]])
        if truth_lines:
            parts.extend(["TRUTH_SUMMARY:", *truth_lines])
        if packet_phase == "packet_ranking":
            extraction_visible_changes = [
                str(item) for item in request.metadata.get("extraction_visible_changes") or [] if str(item).strip()
            ]
            extraction_shape_mismatches = [
                str(item) for item in request.metadata.get("extraction_shape_mismatches") or [] if str(item).strip()
            ]
            extraction_proportion_mismatches = [
                str(item)
                for item in request.metadata.get("extraction_proportion_mismatches") or []
                if str(item).strip()
            ]
            extraction_correction_focus = [
                str(item) for item in request.metadata.get("extraction_correction_focus") or [] if str(item).strip()
            ]
            extraction_next_corrections = [
                str(item) for item in request.metadata.get("extraction_next_corrections") or [] if str(item).strip()
            ]
            extraction_status_reason = str(request.metadata.get("extraction_status_reason") or "").strip()
            extraction_goal_summary = str(request.metadata.get("extraction_goal_summary") or "").strip()
            extraction_reference_match = str(request.metadata.get("extraction_reference_match_summary") or "").strip()
            parts.extend(
                [
                    "EXTRACTION_EVIDENCE:",
                    f"- goal_summary: {extraction_goal_summary or 'none'}",
                    f"- reference_match_summary: {extraction_reference_match or 'none'}",
                    *[f"- visible_change: {item}" for item in extraction_visible_changes],
                    *[f"- shape_mismatch: {item}" for item in extraction_shape_mismatches],
                    *[f"- proportion_mismatch: {item}" for item in extraction_proportion_mismatches],
                    *[f"- suggested_focus: {item}" for item in extraction_correction_focus],
                    *[f"- suggested_next_correction: {item}" for item in extraction_next_corrections],
                    f"- extraction_status_reason: {extraction_status_reason or 'none'}",
                ]
            )
        parts.extend(
            [
                "",
                "Return exactly one JSON object with only these keys:",
                "- goal_summary",
                "- reference_match_summary",
                "- visible_changes",
                "- shape_mismatches",
                "- proportion_mismatches",
                "- correction_focus",
                "- likely_issues",
                "- next_corrections",
                "- recommended_checks",
                "- packet_guidance",
                "- confidence",
                "- captures_used",
                "",
                "Rules:",
                "- keep the packet bounded to 0-3 visible mismatches and 0-3 next corrections",
                "- packet_guidance.packet_status must be one of ready, clean, low_information, or blocked",
                "- packet_guidance.ranking_recommendation must be one of rank, skip_clean, skip_low_information, or skip_blocked",
                "- do not infer scene-wide claims from this packet alone",
                "- use the support-evidence summaries as advisory pre-chewed CV facts, not as scene-truth authority",
                "- use canonical MCP tool ids only for recommended_checks",
                "OUTPUT_TEMPLATE:",
                _packet_compare_output_template(request),
            ]
        )
        return "\n".join(parts)

    if _is_reference_classification_request(request):
        return _build_reference_classification_payload_text(request)

    if _is_reference_understanding_request(request):
        return _build_reference_understanding_payload_text(request)

    if _uses_google_family_compare_contract(
        vision_contract_profile=vision_contract_profile,
        provider_name=provider_name,
        request=request,
    ):
        return _build_gemini_compare_payload_text(request)

    payload = {
        "goal": request.goal,
        "target_object": request.target_object,
        "prompt_hint": request.prompt_hint,
        "truth_summary": request.truth_summary,
        "image_roster": [
            {"role": image.role, "label": image.label, "view_kind": image.view_kind} for image in request.images
        ],
        "mark_overlays": request.metadata.get("mark_overlays") if isinstance(request.metadata, dict) else None,
        "requested_json_keys": list(
            expected_json_keys(
                vision_contract_profile=vision_contract_profile,
                provider_name=provider_name,
                request=request,
                model_capabilities=model_capabilities,
            )
        ),
    }
    return json.dumps(payload, ensure_ascii=True, sort_keys=True, indent=2)


# Internal plumbing keys that carry no visual-interpretation value and should not
# be echoed to the external model (they leak bundle/session identifiers).
_INTERNAL_METADATA_KEYS = frozenset(
    {
        "bundle_id",
        "goal_id",
        "preset_names",
        "packet_id",
        "packet_capture_labels",
        "packet_reference_ids",
    }
)


def _sanitized_request_metadata(metadata: dict[str, object] | None) -> dict[str, object]:
    """Return request metadata with internal plumbing identifiers stripped."""

    if not isinstance(metadata, dict):
        return {}
    return {key: value for key, value in metadata.items() if key not in _INTERNAL_METADATA_KEYS}


def build_local_vision_payload_text(request: VisionRequest) -> str:
    """Return a shorter local-model-oriented payload to reduce echoing."""

    if _is_reference_classification_request(request):
        return _build_reference_classification_payload_text(request)

    if _is_reference_understanding_request(request):
        return _build_reference_understanding_payload_text(request)

    if _is_reference_packet_compare_request(request):
        return build_vision_payload_text(request)

    image_lines = _image_roster_lines(request)
    truth_summary = request.truth_summary or {}
    truth_lines = []
    if isinstance(truth_summary, dict):
        for key, value in truth_summary.items():
            truth_lines.append(f"- {key}: {value}")

    parts = [
        "TASK:",
        "Compare before/after images against the goal and any references.",
        "",
        f"GOAL: {request.goal}",
        f"TARGET_OBJECT: {request.target_object or 'none'}",
        f"PROMPT_HINT: {request.prompt_hint or 'none'}",
        "IMAGES:",
        *image_lines,
    ]
    if truth_lines:
        parts.extend(["TRUTH_SUMMARY:", *truth_lines])
    reference_guided_checkpoint = _is_reference_guided_checkpoint(request)
    parts.extend(
        [
            "",
            "Return exactly one JSON object with the required keys only.",
            "If you can provide only one useful sentence, put it in goal_summary.",
            "If the after image(s) visibly changed, also populate visible_changes with 1-3 short concrete visual observations.",
            "Do not use visible_changes for unchanged truth_summary facts such as same dimensions, same center, or same volume.",
            "Use shape_mismatches only for visible form/silhouette problems.",
            "Use proportion_mismatches only for visible size/ratio problems.",
            "Use correction_focus for the 1-3 highest-priority mismatch targets to fix next.",
            "Use next_corrections for 1-3 bounded next-step fixes only when they are visually justified.",
            "Do not present next_corrections as proof that the fix is safe or correct; deterministic checks still decide correctness.",
            "Leave likely_issues and recommended_checks empty unless you have a specific visual reason to add them.",
            "For easy smoke or obvious progression cases, avoid filler likely_issues and avoid generic follow-up checks.",
            "Do not repeat the input payload.",
            "Do not invent alternate top-level keys like comparison, summary, analysis, before, after, or reference.",
            "If uncertain, keep fields conservative but present.",
            "OUTPUT_TEMPLATE:",
            _local_output_template(request),
        ]
    )
    if reference_guided_checkpoint:
        parts.extend(
            [
                "Because this is a reference-guided checkpoint comparison:",
                "- populate reference_match_summary if the references meaningfully inform the comparison",
                "- prefer concrete silhouette/proportion mismatches over generic praise",
                "- correction_focus should rank the most important fixes first",
                "- next_corrections should stay tightly aligned with the mismatches you listed",
                "- if you recommend deterministic checks, use only canonical MCP tool ids rather than invented labels",
            ]
        )
    return "\n".join(parts)


def expected_json_keys(
    *,
    vision_contract_profile: VisionContractProfile | None = None,
    provider_name: str | None = None,
    request: VisionRequest | None = None,
    model_capabilities: VisionModelCapabilities | None = None,
) -> tuple[str, ...]:
    """Expose the canonical required JSON keys for tests and parse repair."""

    if _is_reference_classification_request(request):
        return _REFERENCE_CLASSIFICATION_EXPECTED_KEYS

    if _is_reference_understanding_request(request):
        return _REFERENCE_UNDERSTANDING_EXPECTED_KEYS

    if _is_reference_packet_compare_request(request):
        if _should_drop_findings(model_capabilities):
            return _strip_key(_PACKET_COMPARE_EXPECTED_KEYS, "findings")
        return _PACKET_COMPARE_EXPECTED_KEYS

    if _uses_google_family_compare_contract(
        vision_contract_profile=vision_contract_profile,
        provider_name=provider_name,
        request=request,
    ):
        return _GEMINI_COMPARE_EXPECTED_KEYS
    if _should_drop_findings(model_capabilities):
        return _strip_key(_EXPECTED_KEYS, "findings")
    return _EXPECTED_KEYS


def _strip_key(keys: tuple[str, ...], key: str) -> tuple[str, ...]:
    return tuple(item for item in keys if item != key)


def _should_drop_findings(model_capabilities: VisionModelCapabilities | None) -> bool:
    if model_capabilities is None:
        return False
    supported = set(model_capabilities.supported_parameters or [])
    if "structured_outputs" not in supported and "response_format" not in supported:
        return True
    max_completion_tokens = model_capabilities.max_completion_tokens
    return isinstance(max_completion_tokens, int) and max_completion_tokens < 1024


def _include_findings_for_capabilities(
    include_findings: bool,
    model_capabilities: VisionModelCapabilities | None,
) -> bool:
    return include_findings and not _should_drop_findings(model_capabilities)


def _maybe_strip_findings(schema: dict[str, object], include_findings: bool) -> dict[str, object]:
    """Remove the structured ``findings`` channel from a strict schema when a weak
    model should keep a leaner contract (keeps ``required`` and ``properties`` in
    sync for strict providers)."""

    if include_findings:
        return schema
    properties = schema.get("properties")
    if isinstance(properties, dict) and "findings" in properties:
        properties.pop("findings")
        required = schema.get("required")
        if isinstance(required, list):
            schema["required"] = [key for key in required if key != "findings"]
    return schema


def build_vision_response_json_schema(
    *,
    vision_contract_profile: VisionContractProfile | None = None,
    provider_name: str | None = None,
    request: VisionRequest | None = None,
    include_findings: bool = True,
    model_capabilities: VisionModelCapabilities | None = None,
) -> dict[str, object]:
    """Return a provider-agnostic JSON Schema for bounded vision responses.

    When ``include_findings`` is False (a model that does not reliably support
    structured outputs) the additive ``findings`` channel is dropped so the model
    keeps a leaner, easier-to-satisfy contract.
    """

    include_findings = _include_findings_for_capabilities(include_findings, model_capabilities)

    if _is_reference_classification_request(request):
        return {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "classification_scores": {
                    "type": "array",
                    "minItems": 1,
                    "maxItems": 5,
                    "items": {
                        "type": "object",
                        "additionalProperties": False,
                        "properties": {
                            "label": {"type": "string"},
                            "score": {"type": "number", "minimum": 0.0, "maximum": 1.0},
                        },
                        "required": ["label", "score"],
                    },
                }
            },
            "required": list(_REFERENCE_CLASSIFICATION_EXPECTED_KEYS),
        }

    if _is_reference_understanding_request(request):
        return {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "subject": {
                    "type": "object",
                    "additionalProperties": False,
                    "properties": {
                        "label": {"type": "string"},
                        "category": {
                            "type": "string",
                            "enum": [
                                "creature",
                                "hard_surface",
                                "architectural_mass",
                                "dental_surface",
                                "organic_form",
                                "unknown",
                            ],
                        },
                        "confidence": {"type": ["number", "null"]},
                        "uncertainty_notes": {"type": "array", "items": {"type": "string"}},
                    },
                    "required": ["label", "category", "confidence", "uncertainty_notes"],
                },
                "style": {
                    "type": "object",
                    "additionalProperties": False,
                    "properties": {
                        "style_label": {
                            "type": "string",
                            "enum": [
                                "low_poly_faceted",
                                "hard_surface",
                                "smooth_organic",
                                "architectural_mass",
                                "dental_surface",
                                "unknown",
                            ],
                        },
                        "confidence": {"type": ["number", "null"]},
                        "notes": {"type": "array", "items": {"type": "string"}},
                    },
                    "required": ["style_label", "confidence", "notes"],
                },
                "views": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "additionalProperties": False,
                        "properties": {
                            "view_id": {
                                "type": "string",
                                "enum": ["front", "side", "top", "back", "three_quarter", "detail", "unknown"],
                            },
                            "detected": {"type": "boolean"},
                            "confidence": {"type": ["number", "null"]},
                            "reference_ids": {"type": "array", "items": {"type": "string"}},
                            "key_features": {"type": "array", "items": {"type": "string"}},
                        },
                        "required": ["view_id", "detected", "confidence", "reference_ids", "key_features"],
                    },
                },
                "required_parts": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "additionalProperties": False,
                        "properties": {
                            "part_label": {"type": "string"},
                            "target_label": {"type": ["string", "null"]},
                            "construction_hint": {"type": ["string", "null"]},
                            "priority": {"type": "string", "enum": ["high", "normal"]},
                            "source_reference_ids": {"type": "array", "items": {"type": "string"}},
                        },
                        "required": [
                            "part_label",
                            "target_label",
                            "construction_hint",
                            "priority",
                            "source_reference_ids",
                        ],
                    },
                },
                "mass_recipe": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "additionalProperties": False,
                        "properties": {
                            "target_label": {"type": "string"},
                            "geometry_family": {"type": ["string", "null"]},
                            "construction_hint": {"type": ["string", "null"]},
                            "anchor_role_candidates": {"type": "array", "items": {"type": "string"}},
                            "support_surface_candidates": {"type": "array", "items": {"type": "string"}},
                            "contact_expectations": {"type": "array", "items": {"type": "string"}},
                            "source_reference_ids": {"type": "array", "items": {"type": "string"}},
                        },
                        "required": [
                            "target_label",
                            "geometry_family",
                            "construction_hint",
                            "anchor_role_candidates",
                            "support_surface_candidates",
                            "contact_expectations",
                            "source_reference_ids",
                        ],
                    },
                },
                "attachment_plan": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "additionalProperties": False,
                        "properties": {
                            "target_label": {"type": "string"},
                            "anchor_role_candidates": {"type": "array", "items": {"type": "string"}},
                            "required_relation": {
                                "type": "string",
                                "enum": [
                                    "segment_attachment",
                                    "seated_attachment",
                                    "embedded_attachment",
                                    "support_contact",
                                    "symmetry_pair",
                                    "unknown",
                                ],
                            },
                            "support_surface_candidates": {"type": "array", "items": {"type": "string"}},
                            "contact_expectations": {"type": "array", "items": {"type": "string"}},
                            "notes": {"type": "array", "items": {"type": "string"}},
                        },
                        "required": [
                            "target_label",
                            "anchor_role_candidates",
                            "required_relation",
                            "support_surface_candidates",
                            "contact_expectations",
                            "notes",
                        ],
                    },
                },
                "contact_expectations": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "additionalProperties": False,
                        "properties": {
                            "target_label": {"type": "string"},
                            "expected_contacts": {"type": "array", "items": {"type": "string"}},
                            "avoid_contacts": {"type": "array", "items": {"type": "string"}},
                            "notes": {"type": "array", "items": {"type": "string"}},
                        },
                        "required": ["target_label", "expected_contacts", "avoid_contacts", "notes"],
                    },
                },
                "shape_profile_hints": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "additionalProperties": False,
                        "properties": {
                            "target_label": {"type": "string"},
                            "summary": {"type": "string"},
                            "reference_id": {"type": ["string", "null"]},
                        },
                        "required": ["target_label", "summary", "reference_id"],
                    },
                },
                "silhouette_landmarks": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "additionalProperties": False,
                        "properties": {
                            "landmark_id": {"type": "string"},
                            "target_label": {"type": ["string", "null"]},
                            "view_id": {
                                "type": "string",
                                "enum": ["front", "side", "top", "back", "three_quarter", "detail", "unknown"],
                            },
                            "summary": {"type": "string"},
                        },
                        "required": ["landmark_id", "target_label", "view_id", "summary"],
                    },
                },
                "part_order": {"type": "array", "items": {"type": "string"}},
                "must_seat_before_next_stage": {"type": "array", "items": {"type": "string"}},
                "non_goals": {"type": "array", "items": {"type": "string"}},
                "construction_strategy": {
                    "type": "object",
                    "additionalProperties": False,
                    "properties": {
                        "construction_path": {
                            "type": "string",
                            "enum": [
                                "low_poly_facet",
                                "hard_surface",
                                "organic_sculpt",
                                "creature_blockout",
                                "dental_surface",
                                "architectural_mass",
                                "unknown",
                            ],
                        },
                        "primary_family": {
                            "type": "string",
                            "enum": ["macro", "modeling_mesh", "sculpt_region", "inspect_only"],
                        },
                        "allowed_families": {
                            "type": "array",
                            "items": {
                                "type": "string",
                                "enum": ["macro", "modeling_mesh", "sculpt_region", "inspect_only"],
                            },
                        },
                        "stage_sequence": {"type": "array", "items": {"type": "string"}},
                        "finish_policy": {
                            "type": "string",
                            "enum": ["preserve_facets", "inspect_first", "bounded_local_detail", "unknown"],
                        },
                    },
                    "required": [
                        "construction_path",
                        "primary_family",
                        "allowed_families",
                        "stage_sequence",
                        "finish_policy",
                    ],
                },
                "router_handoff_hints": {
                    "type": "object",
                    "additionalProperties": False,
                    "properties": {
                        "preferred_family": {
                            "type": "string",
                            "enum": ["macro", "modeling_mesh", "sculpt_region", "inspect_only"],
                        },
                        "allowed_guided_families": {
                            "type": "array",
                            "items": {
                                "type": "string",
                                "enum": [
                                    "spatial_context",
                                    "reference_context",
                                    "primary_masses",
                                    "secondary_parts",
                                    "attachment_alignment",
                                    "checkpoint_iterate",
                                    "inspect_validate",
                                    "finish",
                                    "utility",
                                ],
                            },
                        },
                        "sculpt_policy": {
                            "type": "string",
                            "enum": ["hidden", "local_detail_only", "allowed_or_primary"],
                        },
                    },
                    "required": ["preferred_family", "allowed_guided_families", "sculpt_policy"],
                },
                "gate_proposals": {"type": "array", "items": {"type": "object"}},
                "visual_evidence_refs": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "additionalProperties": False,
                        "properties": {
                            "evidence_id": {"type": "string"},
                            "source_class": {
                                "type": "string",
                                "enum": ["reference_image", "style_cue", "part_cue", "construction_hint", "gate_seed"],
                            },
                            "summary": {"type": "string"},
                            "reference_id": {"type": ["string", "null"]},
                        },
                        "required": ["evidence_id", "source_class", "summary", "reference_id"],
                    },
                },
                "verification_requirements": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "additionalProperties": False,
                        "properties": {
                            "tool_name": {"type": "string"},
                            "reason": {"type": "string"},
                            "priority": {"type": "string", "enum": ["high", "normal"]},
                        },
                        "required": ["tool_name", "reason", "priority"],
                    },
                },
            },
            "required": list(_REFERENCE_UNDERSTANDING_EXPECTED_KEYS),
        }

    if _is_reference_packet_compare_request(request):
        packet_schema: dict[str, object] = {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "goal_summary": {"type": "string"},
                "reference_match_summary": {"type": ["string", "null"]},
                "visible_changes": {"type": "array", "items": {"type": "string"}},
                "shape_mismatches": {"type": "array", "items": {"type": "string"}},
                "proportion_mismatches": {"type": "array", "items": {"type": "string"}},
                "correction_focus": {"type": "array", "items": {"type": "string"}},
                "likely_issues": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "additionalProperties": False,
                        "properties": {
                            "category": {"type": "string"},
                            "summary": {"type": "string"},
                            "severity": {"type": "string", "enum": ["high", "medium", "low"]},
                        },
                        "required": ["category", "summary", "severity"],
                    },
                },
                "next_corrections": {"type": "array", "items": {"type": "string"}},
                "recommended_checks": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "additionalProperties": False,
                        "properties": {
                            "tool_name": {"type": "string"},
                            "reason": {"type": "string"},
                            "priority": {"type": "string", "enum": ["high", "normal"]},
                        },
                        "required": ["tool_name", "reason", "priority"],
                    },
                },
                "findings": _FINDINGS_SCHEMA,
                "packet_guidance": {
                    "type": "object",
                    "additionalProperties": False,
                    "properties": {
                        "packet_status": {
                            "type": ["string", "null"],
                            "enum": ["ready", "clean", "low_information", "blocked", None],
                        },
                        "status_reason": {"type": ["string", "null"]},
                        "ranking_recommendation": {
                            "type": ["string", "null"],
                            "enum": ["rank", "skip_clean", "skip_low_information", "skip_blocked", None],
                        },
                    },
                    "required": ["packet_status", "status_reason", "ranking_recommendation"],
                },
                "confidence": {"type": ["number", "null"]},
                "captures_used": {"type": "array", "items": {"type": "string"}},
            },
            "required": list(
                expected_json_keys(
                    vision_contract_profile=vision_contract_profile,
                    provider_name=provider_name,
                    request=request,
                    model_capabilities=model_capabilities,
                )
            ),
        }
        return _maybe_strip_findings(packet_schema, include_findings)

    if _uses_google_family_compare_contract(
        vision_contract_profile=vision_contract_profile,
        provider_name=provider_name,
        request=request,
    ):
        return {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "goal_summary": {"type": "string"},
                "reference_match_summary": {"type": ["string", "null"]},
                "shape_mismatches": {"type": "array", "items": {"type": "string"}},
                "proportion_mismatches": {"type": "array", "items": {"type": "string"}},
                "correction_focus": {"type": "array", "items": {"type": "string"}},
                "next_corrections": {"type": "array", "items": {"type": "string"}},
                "findings": _FINDINGS_SCHEMA,
            },
            "required": list(_GEMINI_COMPARE_EXPECTED_KEYS),
        }

    default_schema: dict[str, object] = {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "goal_summary": {"type": "string"},
            "reference_match_summary": {"type": ["string", "null"]},
            "visible_changes": {"type": "array", "items": {"type": "string"}},
            "shape_mismatches": {"type": "array", "items": {"type": "string"}},
            "proportion_mismatches": {"type": "array", "items": {"type": "string"}},
            "correction_focus": {"type": "array", "items": {"type": "string"}},
            "likely_issues": {
                "type": "array",
                "items": {
                    "type": "object",
                    "additionalProperties": False,
                    "properties": {
                        "category": {"type": "string"},
                        "summary": {"type": "string"},
                        "severity": {"type": "string", "enum": ["high", "medium", "low"]},
                    },
                    "required": ["category", "summary", "severity"],
                },
            },
            "next_corrections": {"type": "array", "items": {"type": "string"}},
            "recommended_checks": {
                "type": "array",
                "items": {
                    "type": "object",
                    "additionalProperties": False,
                    "properties": {
                        "tool_name": {"type": "string"},
                        "reason": {"type": "string"},
                        "priority": {"type": "string", "enum": ["high", "normal"]},
                    },
                    "required": ["tool_name", "reason", "priority"],
                },
            },
            "findings": _FINDINGS_SCHEMA,
            "confidence": {"type": ["number", "null"]},
            "captures_used": {"type": "array", "items": {"type": "string"}},
        },
        "required": list(
            expected_json_keys(
                vision_contract_profile=vision_contract_profile,
                provider_name=provider_name,
                request=request,
                model_capabilities=model_capabilities,
            )
        ),
    }
    return _maybe_strip_findings(default_schema, include_findings)
