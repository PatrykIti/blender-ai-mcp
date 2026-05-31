"""Tests for bounded vision prompt builders."""

from __future__ import annotations

import json
from dataclasses import replace

import pytest
from server.adapters.mcp.vision.backend import VisionImageInput, VisionRequest
from server.adapters.mcp.vision.config import VisionModelCapabilities
from server.adapters.mcp.vision.prompting import (
    build_local_vision_payload_text,
    build_vision_payload_text,
    build_vision_response_json_schema,
    build_vision_system_prompt,
    expected_json_keys,
    format_image_caption,
    format_image_roster_line,
    serialize_relation_triplets,
)


def _assert_strict_required_matches_properties(schema: dict) -> None:
    if schema.get("type") != "object":
        return
    properties = schema.get("properties")
    if isinstance(properties, dict):
        assert schema.get("additionalProperties") is False
        assert set(schema.get("required") or []) == set(properties)
        for nested in properties.values():
            if isinstance(nested, dict):
                _assert_strict_required_matches_properties(nested)
                items = nested.get("items")
                if isinstance(items, dict):
                    _assert_strict_required_matches_properties(items)


def _request() -> VisionRequest:
    return VisionRequest(
        goal="rounded housing",
        target_object="Housing",
        images=(
            VisionImageInput(path="/tmp/before.png", role="before", label="before_1"),
            VisionImageInput(path="/tmp/after.png", role="after", label="after_1"),
            VisionImageInput(path="/tmp/ref.png", role="reference", label="ref_1"),
        ),
        prompt_hint="Return JSON only.",
        truth_summary={"dimensions": [1.0, 2.0, 3.0]},
    )


def _reference_understanding_request() -> VisionRequest:
    return VisionRequest(
        goal="create a low-poly squirrel matching front and side references",
        images=(
            VisionImageInput(path="/tmp/ref_front.png", role="reference", label="ref_front"),
            VisionImageInput(path="/tmp/ref_side.png", role="reference", label="ref_side"),
        ),
        metadata={
            "mode": "reference_understanding",
            "reference_ids": ["ref_front", "ref_side"],
        },
    )


def _reference_classification_request() -> VisionRequest:
    return VisionRequest(
        goal="classify the attached low-poly squirrel reference for bounded Blender planning",
        images=(VisionImageInput(path="/tmp/ref_front.png", role="reference", label="ref_front"),),
        metadata={
            "mode": "reference_classification",
            "reference_ids": ["ref_front"],
        },
    )


def _packet_compare_request() -> VisionRequest:
    return VisionRequest(
        goal="low poly squirrel",
        target_object="Squirrel",
        images=(
            VisionImageInput(path="/tmp/front.png", role="after", label="target_front_after"),
            VisionImageInput(path="/tmp/ref_front.png", role="reference", label="ref_front"),
        ),
        prompt_hint="comparison_mode=stage_checkpoint_vs_reference | compare_phase=packet_extraction",
        metadata={
            "mode": "reference_compare_packet",
            "packet_id": "packet:front:1234abcd",
            "packet_kind": "view",
            "packet_label": "front packet",
            "packet_view": "front",
            "packet_scope": "Squirrel",
            "packet_reference_ids": ["ref_front"],
            "packet_capture_labels": ["target_front_after"],
            "support_evidence_summaries": [
                "Silhouette overlap is 0.52 (high).",
                "Action hint: Upper silhouette band is narrower than the reference.",
            ],
        },
        truth_summary={"summary": {"pair_count": 0}},
    )


def _packet_ranking_request() -> VisionRequest:
    return VisionRequest(
        goal="low poly squirrel",
        target_object="Squirrel",
        images=(
            VisionImageInput(path="/tmp/front.png", role="after", label="target_front_after"),
            VisionImageInput(path="/tmp/ref_front.png", role="reference", label="ref_front"),
        ),
        prompt_hint="comparison_mode=stage_checkpoint_vs_reference | compare_phase=packet_ranking",
        metadata={
            "mode": "reference_compare_packet",
            "packet_id": "packet:front:1234abcd",
            "packet_kind": "view",
            "packet_label": "front packet",
            "packet_view": "front",
            "packet_scope": "Squirrel",
            "packet_reference_ids": ["ref_front"],
            "packet_capture_labels": ["target_front_after"],
            "compare_phase": "packet_ranking",
            "support_evidence_summaries": [
                "Silhouette overlap is 0.52 (high).",
                "Action hint: Upper silhouette band is narrower than the reference.",
            ],
            "extraction_goal_summary": "Front packet still shows a round head silhouette.",
            "extraction_reference_match_summary": "The packet has enough signal for one more bounded correction step.",
            "extraction_visible_changes": ["Front silhouette is readable."],
            "extraction_shape_mismatches": ["Head silhouette is still too spherical."],
            "extraction_proportion_mismatches": ["Head still reads slightly too large."],
            "extraction_correction_focus": ["Head silhouette"],
            "extraction_next_corrections": ["Flatten the head silhouette slightly."],
            "extraction_status_reason": None,
        },
        truth_summary={"summary": {"pair_count": 0}},
    )


def _checkpoint_compare_request() -> VisionRequest:
    return VisionRequest(
        goal="low poly squirrel",
        target_object="Squirrel",
        images=(
            VisionImageInput(path="/tmp/front.png", role="after", label="target_front_after"),
            VisionImageInput(path="/tmp/ref_front.png", role="reference", label="ref_front"),
        ),
        prompt_hint="comparison_mode=stage_checkpoint_vs_reference",
    )


def test_local_prompt_payload_is_more_compact_and_task_focused():
    text = build_local_vision_payload_text(_request())

    assert "TASK:" in text
    assert "IMAGES:" in text
    assert "- before: before_1" in text
    assert "OUTPUT_TEMPLATE:" in text
    assert '"goal_summary"' in text
    assert '"shape_mismatches"' in text
    assert '"proportion_mismatches"' in text
    assert '"correction_focus"' in text
    assert '"next_corrections"' in text
    assert "If you can provide only one useful sentence, put it in goal_summary." in text
    assert "also populate visible_changes with 1-3 short concrete visual observations" in text
    assert "Leave likely_issues and recommended_checks empty unless you have a specific visual reason" in text
    assert "Do not use visible_changes for unchanged truth_summary facts" in text
    assert "Use shape_mismatches only for visible form/silhouette problems." in text
    assert "Use correction_focus for the 1-3 highest-priority mismatch targets to fix next." in text
    assert "Use next_corrections for 1-3 bounded next-step fixes only when they are visually justified." in text
    assert "avoid filler likely_issues and avoid generic follow-up checks" in text
    assert "Do not invent alternate top-level keys like comparison" in text
    assert "Do not repeat the input payload." in text
    assert '"goal"' not in text


def test_generic_payload_builder_uses_curated_json_payload_without_metadata():
    text = build_vision_payload_text(_request())

    assert '"goal": "rounded housing"' in text
    assert '"prompt_hint": "Return JSON only."' in text
    assert '"image_roster"' in text
    assert '"requested_json_keys"' in text
    assert '"metadata"' not in text


def test_system_prompt_is_stricter_for_local_backends():
    local_prompt = build_vision_system_prompt(backend_kind="mlx_local")
    external_prompt = build_vision_system_prompt(backend_kind="openai_compatible_external")

    assert "Do not echo the input payload" in local_prompt
    assert "visible_changes must contain 1-3 short concrete visual items" in local_prompt
    assert "same dimensions, same center, or same volume" in local_prompt
    assert "shape_mismatches" in local_prompt
    assert "correction_focus" in local_prompt
    assert "next_corrections" in local_prompt
    assert "Do not echo the input payload" not in external_prompt


def test_local_prompt_adds_reference_guided_checkpoint_guidance_when_requested():
    request = VisionRequest(
        goal="low poly squirrel",
        target_object="Squirrel",
        images=(
            VisionImageInput(path="/tmp/front.png", role="after", label="target_front_after"),
            VisionImageInput(path="/tmp/ref_front.png", role="reference", label="ref_front"),
        ),
        prompt_hint="comparison_mode=stage_checkpoint_vs_reference",
    )

    local_prompt = build_local_vision_payload_text(request)

    assert "Because this is a reference-guided checkpoint comparison:" in local_prompt
    assert "correction_focus should rank the most important fixes first" in local_prompt


@pytest.mark.parametrize(
    ("vision_request", "kwargs"),
    [
        (_request(), {}),
        (
            _checkpoint_compare_request(),
            {"vision_contract_profile": "google_family_compare", "provider_name": "openrouter"},
        ),
        (_packet_compare_request(), {}),
        (_reference_understanding_request(), {}),
        (_reference_classification_request(), {}),
    ],
)
def test_expected_json_keys_match_schema_properties_for_repairable_contracts(vision_request, kwargs):
    schema = build_vision_response_json_schema(request=vision_request, **kwargs)

    assert tuple(schema["properties"]) == expected_json_keys(request=vision_request, **kwargs)


def test_capability_limited_schema_drops_structured_findings():
    capabilities = VisionModelCapabilities(
        model_id="weak-json-model",
        capability_source="fallback_registry",
        max_completion_tokens=900,
        input_modalities=["text", "image"],
        output_modalities=["text"],
        supported_parameters=["max_tokens"],
    )

    schema = build_vision_response_json_schema(request=_packet_compare_request(), model_capabilities=capabilities)

    assert "findings" not in schema["properties"]
    assert "findings" not in schema["required"]
    assert "findings" not in expected_json_keys(
        request=_packet_compare_request(),
        model_capabilities=capabilities,
    )


def test_generic_payload_requested_keys_follow_capability_limited_schema():
    capabilities = VisionModelCapabilities(
        model_id="weak-json-model",
        capability_source="fallback_registry",
        max_completion_tokens=900,
        input_modalities=["text", "image"],
        output_modalities=["text"],
        supported_parameters=["max_tokens"],
    )

    payload = json.loads(build_vision_payload_text(_request(), model_capabilities=capabilities))
    schema = build_vision_response_json_schema(request=_request(), model_capabilities=capabilities)

    assert "findings" not in payload["requested_json_keys"]
    assert "findings" not in schema["properties"]
    assert tuple(payload["requested_json_keys"]) == tuple(schema["properties"])


def test_packet_compare_request_uses_packet_specific_prompt_payload_and_schema():
    request = _packet_compare_request()

    system_prompt = build_vision_system_prompt(backend_kind="mlx_local", request=request)
    payload_text = build_vision_payload_text(request)
    schema = build_vision_response_json_schema(request=request)

    assert "bounded packet-compare vision assistant" in system_prompt
    assert "packet_guidance" in system_prompt
    assert "PACKET_ID: packet:front:1234abcd" in payload_text
    assert "PACKET_LABEL: front packet" in payload_text
    assert "SUPPORT_EVIDENCE:" in payload_text
    assert '"packet_guidance"' in payload_text
    assert set(schema["properties"]) == {
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
    }
    assert set(schema["properties"]["findings"]["items"]["properties"]) == {
        "finding",
        "view_id",
        "target_label",
        "axis",
        "direction",
        "magnitude_ratio",
        "reference_id",
        "confidence",
    }
    assert set(schema["properties"]["packet_guidance"]["properties"]) == {
        "packet_status",
        "status_reason",
        "ranking_recommendation",
    }
    _assert_strict_required_matches_properties(schema)


def test_packet_compare_prompt_includes_mark_overlay_legend():
    request = _packet_compare_request()
    request = replace(
        request,
        metadata={
            **request.metadata,
            "mark_overlays": [
                {
                    "label": "target_front_after_overlay",
                    "marks": [
                        {"mark_id": 1, "object_name": "Body", "status": "placed"},
                        {"mark_id": 2, "object_name": "Head", "status": "placed"},
                    ],
                }
            ],
        },
    )

    payload_text = build_vision_payload_text(request)

    assert "MARK_OVERLAYS:" in payload_text
    assert "- target_front_after_overlay: mark 1 -> Body (placed)" in payload_text
    assert "- target_front_after_overlay: mark 2 -> Head (placed)" in payload_text


def test_packet_compare_prompt_omits_unplaced_overlay_marks_from_legend():
    request = _packet_compare_request()
    request = replace(
        request,
        metadata={
            **request.metadata,
            "mark_overlays": [
                {
                    "label": "target_front_after_overlay",
                    "marks": [
                        {"mark_id": 1, "object_name": "Body", "status": "unmarked"},
                        {"mark_id": 2, "object_name": "Head", "status": "placed"},
                    ],
                }
            ],
        },
    )

    payload_text = build_vision_payload_text(request)

    assert "MARK_OVERLAYS:" in payload_text
    assert "mark 1 -> Body" not in payload_text
    assert "- target_front_after_overlay: mark 2 -> Head (placed)" in payload_text


def test_packet_ranking_request_uses_ranking_specific_prompt_payload():
    request = _packet_ranking_request()

    system_prompt = build_vision_system_prompt(backend_kind="mlx_local", request=request)
    payload_text = build_vision_payload_text(request)

    assert "bounded packet-ranking vision assistant" in system_prompt
    assert "second staged compare phase" in system_prompt
    assert "COMPARE_PHASE: packet_ranking" in payload_text
    assert "SUPPORT_EVIDENCE:" in payload_text
    assert "EXTRACTION_EVIDENCE:" in payload_text
    assert "- shape_mismatch: Head silhouette is still too spherical." in payload_text
    assert "- suggested_next_correction: Flatten the head silhouette slightly." in payload_text


def test_google_family_compare_profile_uses_narrow_contract_even_on_openrouter():
    request = VisionRequest(
        goal="low poly squirrel",
        target_object="Squirrel",
        images=(
            VisionImageInput(path="/tmp/front.png", role="after", label="target_front_after"),
            VisionImageInput(path="/tmp/ref_front.png", role="reference", label="ref_front"),
        ),
        prompt_hint="comparison_mode=stage_checkpoint_vs_reference",
    )

    system_prompt = build_vision_system_prompt(
        backend_kind="openai_compatible_external",
        vision_contract_profile="google_family_compare",
        provider_name="openrouter",
        request=request,
    )
    payload_text = build_vision_payload_text(
        request,
        vision_contract_profile="google_family_compare",
        provider_name="openrouter",
    )
    schema = build_vision_response_json_schema(
        vision_contract_profile="google_family_compare",
        provider_name="openrouter",
        request=request,
    )

    assert "Return exactly one JSON object with only these keys:" in system_prompt
    assert (
        "Do not return visible_changes, likely_issues, recommended_checks, confidence, or captures_used."
        in system_prompt
    )
    assert '"visible_changes"' not in payload_text
    assert '"shape_mismatches"' in payload_text
    assert '"next_corrections"' in payload_text
    assert set(schema["properties"]) == {
        "goal_summary",
        "reference_match_summary",
        "shape_mismatches",
        "proportion_mismatches",
        "correction_focus",
        "next_corrections",
    }
    _assert_strict_required_matches_properties(schema)


def test_google_family_compare_profile_keeps_full_contract_for_non_checkpoint_requests():
    request = VisionRequest(
        goal="rounded housing",
        target_object="Housing",
        images=(VisionImageInput(path="/tmp/after.png", role="after", label="after_1"),),
        prompt_hint="Return JSON only.",
    )

    system_prompt = build_vision_system_prompt(
        backend_kind="openai_compatible_external",
        vision_contract_profile="google_family_compare",
        provider_name="openrouter",
        request=request,
    )
    payload_text = build_vision_payload_text(
        request,
        vision_contract_profile="google_family_compare",
        provider_name="openrouter",
    )
    schema = build_vision_response_json_schema(
        vision_contract_profile="google_family_compare",
        provider_name="openrouter",
        request=request,
    )

    assert "visible_changes" in system_prompt
    assert '"goal": "rounded housing"' in payload_text
    assert "visible_changes" in schema["properties"]
    _assert_strict_required_matches_properties(schema)


def test_reference_understanding_prompt_and_schema_use_internal_contract():
    request = _reference_understanding_request()

    system_prompt = build_vision_system_prompt(backend_kind="openai_compatible_external", request=request)
    payload_text = build_vision_payload_text(request)
    schema = build_vision_response_json_schema(request=request)

    assert "bounded reference-understanding assistant" in system_prompt
    assert "mesh_edit -> modeling_mesh" in system_prompt
    assert "Return exactly one JSON object with only these keys:" in payload_text
    assert "- views" in payload_text
    assert '"mass_recipe"' in payload_text
    assert '"attachment_plan"' in payload_text
    assert '"part_order"' in payload_text
    assert "- construction_strategy" in payload_text
    assert "- router_handoff_hints" in payload_text
    assert set(schema["properties"]) == {
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
    }
    assert "- classification_scores" not in payload_text
    assert "- segmentation_artifacts" not in payload_text
    _assert_strict_required_matches_properties(schema)


def test_reference_classification_prompt_and_schema_use_bounded_contract():
    request = _reference_classification_request()

    system_prompt = build_vision_system_prompt(backend_kind="openai_compatible_external", request=request)
    payload_text = build_vision_payload_text(request)
    schema = build_vision_response_json_schema(request=request)

    assert "bounded reference-classification assistant" in system_prompt
    assert "classification_scores must be an array of 1-5 objects" in system_prompt
    assert "Return exactly one JSON object with only this key:" in payload_text
    assert "- classification_scores" in payload_text
    assert set(schema["properties"]) == {"classification_scores"}
    assert schema["properties"]["classification_scores"]["maxItems"] == 5
    _assert_strict_required_matches_properties(schema)


def test_format_image_caption_is_symbolic_and_derives_view_stage():
    caption = format_image_caption(VisionImageInput(path="/tmp/f.png", role="after", label="target_front_after"))
    assert caption == "[image: target_front_after | role=after | view=front]"
    # Symbolic only: no coordinates, absolute metrics, or chain-of-thought tokens.
    for forbidden in ("xyxy", "bbox", "px", "mm", "cm", "because", "let's", "step "):
        assert forbidden not in caption.lower()


def test_format_image_caption_omits_underivable_tokens():
    caption = format_image_caption(VisionImageInput(path="/tmp/r.png", role="reference", label="ref_front"))
    # 'ref_front' yields a view token but no stage token; the stage token is omitted.
    assert caption == "[image: ref_front | role=reference | view=front]"

    bare = format_image_caption(VisionImageInput(path="/tmp/x.png", role="before"))
    assert bare == "[image: before | role=before]"


def test_format_image_caption_prefers_explicit_view_kind_for_grid():
    caption = format_image_caption(
        VisionImageInput(path="/tmp/grid.jpg", role="after", label="view_grid_after", view_kind="grid")
    )

    assert caption == "[image: view_grid_after | role=after | view=grid]"


def test_format_image_caption_marks_auxiliary_channels_as_advisory():
    depth = format_image_caption(
        VisionImageInput(path="/tmp/depth.png", role="after", label="target_front_after_depth", view_kind="depth")
    )
    normal = format_image_caption(
        VisionImageInput(path="/tmp/normal.png", role="after", label="target_front_after_normal", view_kind="normal")
    )
    object_id = format_image_caption(
        VisionImageInput(
            path="/tmp/object_id.png",
            role="after",
            label="target_front_after_object_id",
            view_kind="object_id",
        )
    )

    assert depth == (
        "[image: target_front_after_depth | role=after | view=depth | channel=relative_depth | "
        "advisory=geometric_enrichment_not_truth_source]"
    )
    assert "channel=surface_normal" in normal
    assert "channel=object_id_mask" in object_id
    assert "advisory=geometric_enrichment_not_truth_source" in normal
    assert "advisory=geometric_enrichment_not_truth_source" in object_id


def test_roster_line_keeps_lean_baseline_format():
    # The roster stays lean (`- role: label`); the richer bracketed identity is
    # interleaved before each image in the external payload, not in the roster,
    # because small local (MLX) models are sensitive to verbose roster wording.
    image = VisionImageInput(path="/tmp/f.png", role="after", label="target_side_after")
    assert format_image_roster_line(image) == "- after: target_side_after"


def test_packet_compare_roster_uses_lean_baseline_format():
    request = VisionRequest(
        goal="low poly squirrel",
        target_object="Squirrel",
        images=(
            VisionImageInput(path="/tmp/front.png", role="after", label="target_front_after"),
            VisionImageInput(path="/tmp/ref.png", role="reference", label="ref_front"),
        ),
        metadata={"mode": "reference_compare_packet", "packet_id": "p1"},
    )
    text = build_vision_payload_text(request)
    assert "- after: target_front_after" in text
    assert "- reference: ref_front" in text


def test_serialize_relation_triplets_emits_symbolic_relations_not_coordinates():
    pairs = [
        {"from_object": "Head", "to_object": "Body", "contact_passed": True},
        {"from_object": "Tail", "to_object": "Body", "gap_relation": "separated"},
        {"from_object": "EarL", "to_object": "EarR", "relation_kinds": ["symmetry"]},
        {"from_object": "", "to_object": "Body", "relation_kinds": ["contact"]},  # dropped: no subject
        {"from_object": "Leg", "to_object": "Body"},  # dropped: no derivable relation
    ]
    triplets = serialize_relation_triplets(pairs)
    assert triplets == ["Head contact Body", "Tail separated Body", "EarL symmetry EarR"]
    # No coordinate tokens anywhere.
    blob = " ".join(triplets).lower()
    for forbidden in ("xyz", "(", "[", "0.", "x=", "coord"):
        assert forbidden not in blob


def test_serialize_relation_triplets_caps_per_subject():
    pairs = [{"from_object": "Body", "to_object": f"Part{i}", "relation_kinds": ["contact"]} for i in range(10)]
    triplets = serialize_relation_triplets(pairs, max_per_object=3)
    assert len(triplets) == 3
    assert all(t.startswith("Body contact ") for t in triplets)


def test_packet_compare_prompt_includes_scene_relations_when_present():
    request = VisionRequest(
        goal="low poly squirrel",
        target_object="Squirrel",
        images=(
            VisionImageInput(path="/tmp/front.png", role="after", label="target_front_after"),
            VisionImageInput(path="/tmp/ref.png", role="reference", label="ref_front"),
        ),
        metadata={"mode": "reference_compare_packet", "packet_id": "p1"},
        truth_summary={
            "relation_graph": {
                "pairs": [
                    {"from_object": "Head", "to_object": "Body", "contact_passed": True},
                    {"from_object": "Tail", "to_object": "Body", "gap_relation": "separated"},
                ]
            }
        },
    )
    text = build_vision_payload_text(request)
    assert "SCENE_RELATIONS:" in text
    assert "- Head contact Body" in text
    assert "- Tail separated Body" in text


def test_packet_compare_prompt_omits_scene_relations_when_absent():
    request = VisionRequest(
        goal="low poly squirrel",
        target_object="Squirrel",
        images=(VisionImageInput(path="/tmp/front.png", role="after", label="target_front_after"),),
        metadata={"mode": "reference_compare_packet", "packet_id": "p1"},
        truth_summary={"summary": {"pair_count": 0}},
    )
    assert "SCENE_RELATIONS:" not in build_vision_payload_text(request)
