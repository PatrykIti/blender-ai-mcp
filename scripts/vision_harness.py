#!/usr/bin/env python3
"""Run bounded vision backends against a shared local bundle/input payload."""
# ruff: noqa: E402

from __future__ import annotations

import argparse
import asyncio
import copy
import json
import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from server.adapters.mcp.areas import reference_compare_packets as compare_packets_area
from server.adapters.mcp.areas.reference_silhouette import build_compare_support_evidence
from server.adapters.mcp.contracts.reference import (
    ReferenceComparePacketContract,
    ReferenceImageRecordContract,
    ReferencePartSegmentationContract,
    ReferenceRuntimeCapabilityUsageContract,
    ReferenceRuntimeEvidenceContract,
)
from server.adapters.mcp.contracts.vision import (
    VisionCaptureBundleContract,
    VisionCaptureImageContract,
)
from server.adapters.mcp.vision import (
    ResolvedVisionGoldenScenario,
    VisionImageInput,
    VisionRequest,
    VisionRuntimeConfig,
    build_advisory_reliability_scorecard,
    build_reference_capture_images,
    build_vision_request_from_capture_bundle,
    build_vision_runtime_config,
    create_vision_backend,
    evaluate_vision_result,
    load_golden_scenario,
)
from server.infrastructure.config import Config


@dataclass(frozen=True)
class HarnessConfig:
    backend: str
    config: Config


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _resolve_local_path(base_dir: Path, value: str | None) -> str | None:
    if value is None:
        return None
    path = Path(value)
    if path.is_absolute():
        return str(path)
    return str((base_dir / path).resolve())


def _resolve_bundle_paths(bundle_data: dict[str, Any], source_path: Path) -> dict[str, Any]:
    resolved = copy.deepcopy(bundle_data)
    base_dir = source_path.parent
    for key in ("captures_before", "captures_after"):
        for item in resolved.get(key, []):
            if isinstance(item, dict):
                item["image_path"] = _resolve_local_path(base_dir, item.get("image_path"))
    return resolved


def _resolve_reference_paths(references_data: dict[str, Any], source_path: Path) -> dict[str, Any]:
    resolved = copy.deepcopy(references_data)
    base_dir = source_path.parent
    for item in resolved.get("references", []):
        if not isinstance(item, dict):
            continue
        for key in ("original_path", "stored_path", "host_visible_path"):
            item[key] = _resolve_local_path(base_dir, item.get(key))
    return resolved


def _capture_image(
    path: str,
    *,
    label: str,
    view_kind: Literal["wide", "focus", "overlay", "reference"],
) -> VisionCaptureImageContract:
    media_type = "image/png" if path.lower().endswith(".png") else "image/jpeg"
    return VisionCaptureImageContract(
        label=label,
        image_path=path,
        media_type=media_type,
        view_kind=view_kind,
    )


def _resolve_golden(args: Any) -> ResolvedVisionGoldenScenario | None:
    if not args.golden_json:
        return None
    return load_golden_scenario(args.golden_json)


def _effective_goal(args: Any, golden: ResolvedVisionGoldenScenario | None) -> str:
    if args.goal:
        return str(args.goal)
    if golden is not None:
        return golden.scenario.goal
    raise ValueError("goal is required when no golden scenario is provided")


def _effective_target_object(args: Any, golden: ResolvedVisionGoldenScenario | None) -> str | None:
    if args.target_object is not None:
        return args.target_object
    if golden is not None:
        return golden.scenario.target_object
    return None


def _effective_prompt_hint(args: Any, golden: ResolvedVisionGoldenScenario | None) -> str | None:
    if args.prompt_hint is not None:
        return args.prompt_hint
    if golden is not None:
        return golden.scenario.prompt_hint
    return None


def _effective_bundle_json(args: Any, golden: ResolvedVisionGoldenScenario | None) -> str | None:
    if args.bundle_json is not None:
        return args.bundle_json
    if golden is not None:
        return str(golden.bundle_path)
    return None


def _effective_references_json(args: Any, golden: ResolvedVisionGoldenScenario | None) -> str | None:
    if args.references_json is not None:
        return args.references_json
    if golden is not None and golden.references_path is not None:
        return str(golden.references_path)
    return None


def _reference_records_from_inputs(
    *,
    args: Any,
    golden: ResolvedVisionGoldenScenario | None,
    goal: str,
) -> tuple[ReferenceImageRecordContract, ...]:
    references_json = _effective_references_json(args, golden)
    if references_json:
        raw_reference_items = _resolve_reference_paths(_read_json(Path(references_json)), Path(references_json)).get(
            "references", []
        )
    else:
        raw_reference_items = [
            {
                "reference_id": f"cli_ref_{index}",
                "goal": goal,
                "label": f"reference_{index}",
                "target_object": getattr(args, "target_object", None),
                "target_view": getattr(args, "target_view", None),
                "media_type": "image/png" if str(path).lower().endswith(".png") else "image/jpeg",
                "source_kind": "local_path",
                "original_path": str(Path(path).resolve()),
                "stored_path": str(Path(path).resolve()),
                "host_visible_path": str(Path(path).resolve()),
                "added_at": "2026-05-06T00:00:00Z",
            }
            for index, path in enumerate(args.reference or [], start=1)
        ]
    return tuple(ReferenceImageRecordContract.model_validate(item) for item in raw_reference_items)


def _localized_support_captures_from_inputs(
    *,
    args: Any,
    golden: ResolvedVisionGoldenScenario | None,
) -> tuple[VisionCaptureImageContract, ...]:
    bundle_json = _effective_bundle_json(args, golden)
    if bundle_json:
        bundle_path = Path(bundle_json)
        bundle_data = _resolve_bundle_paths(_read_json(bundle_path), bundle_path)
        bundle = VisionCaptureBundleContract.model_validate(bundle_data)
        return tuple(bundle.captures_after)

    return tuple(
        _capture_image(
            path,
            label=f"after_{index}",
            view_kind="focus",
        )
        for index, path in enumerate(args.after or [], start=1)
    )


def _localized_support_packet(
    *,
    args: Any,
    reference_records: tuple[ReferenceImageRecordContract, ...],
    captures: tuple[VisionCaptureImageContract, ...],
) -> ReferenceComparePacketContract:
    query_label = str(args.localized_support_query_label).strip()
    target_view = getattr(args, "target_view", None)
    target_object = getattr(args, "target_object", None)
    return ReferenceComparePacketContract(
        packet_id="harness:localized_support",
        packet_kind="scope",
        packet_label=query_label,
        target_view=target_view,
        scope_label=query_label,
        target_objects=[target_object] if target_object else [],
        reference_ids=[record.reference_id for record in reference_records],
        capture_labels=[capture.label for capture in captures],
        compare_question="Localized support harness packet.",
        localized_support_reason=getattr(args, "localized_support_reason", "mask_needed"),
    )


def _disabled_localized_support_result() -> ReferencePartSegmentationContract:
    return ReferencePartSegmentationContract(
        status="disabled",
        provider_name=None,
        advisory_only=True,
        parts=[],
        notes=[
            "Optional localized support remains disabled by default.",
            "The harness did not invoke any compare-time optional adapter.",
        ],
    )


def _localized_support_runtime_evidence(
    *,
    packet: ReferenceComparePacketContract,
    localization_config: Any,
    segmentation_config: Any,
    localization_candidates_count: int,
    part_segmentation: ReferencePartSegmentationContract,
) -> ReferenceRuntimeEvidenceContract:
    localization_configured = localization_config is not None and bool(getattr(localization_config, "enabled", False))
    segmentation_configured = segmentation_config is not None and bool(getattr(segmentation_config, "enabled", False))
    localization_invoked = localization_config is not None
    segmentation_invoked = segmentation_config is not None
    return ReferenceRuntimeEvidenceContract(
        checkpoint_id=packet.packet_id,
        packet_ids=[packet.packet_id],
        capabilities=[
            ReferenceRuntimeCapabilityUsageContract(
                capability="classifier",
                status="not_configured",
                configured=False,
                considered=False,
                invoked=False,
                notes=["Localized-support harness does not run the reference-understanding classifier."],
            ),
            ReferenceRuntimeCapabilityUsageContract(
                capability="vision",
                status="not_configured",
                configured=False,
                considered=False,
                invoked=False,
                notes=["Localized-support harness calls sidecars directly, not the main vision assistant."],
            ),
            ReferenceRuntimeCapabilityUsageContract(
                capability="localization",
                status=(
                    "used"
                    if localization_candidates_count
                    else ("unavailable" if localization_invoked else "not_configured")
                ),
                configured=localization_configured,
                considered=True,
                invoked=localization_invoked,
                provider_name=getattr(localization_config, "provider_name", None),
                packet_ids=[packet.packet_id],
            ),
            ReferenceRuntimeCapabilityUsageContract(
                capability="segmentation",
                status=(
                    "used"
                    if part_segmentation.status == "available"
                    else ("unavailable" if segmentation_invoked else "not_configured")
                ),
                configured=segmentation_configured,
                considered=True,
                invoked=segmentation_invoked,
                provider_name=getattr(segmentation_config, "provider_name", None),
                packet_ids=[packet.packet_id],
                notes=list(part_segmentation.notes or [])[:4],
            ),
        ],
        notes=["Harness runtime evidence is bounded and advisory-only."],
    )


def _build_request_from_args(args: Any, golden: ResolvedVisionGoldenScenario | None = None) -> VisionRequest:
    goal = _effective_goal(args, golden)
    target_object = _effective_target_object(args, golden)
    prompt_hint = _effective_prompt_hint(args, golden)
    bundle_json = _effective_bundle_json(args, golden)
    references_json = _effective_references_json(args, golden)
    request_mode = getattr(args, "mode", None)

    if bundle_json:
        bundle_path = Path(bundle_json)
        bundle_data = _resolve_bundle_paths(_read_json(bundle_path), bundle_path)
        bundle = VisionCaptureBundleContract.model_validate(bundle_data)
        if references_json:
            raw_reference_items = _resolve_reference_paths(
                _read_json(Path(references_json)), Path(references_json)
            ).get("references", [])
        else:
            raw_reference_items = [
                {
                    "reference_id": f"cli_ref_{index}",
                    "goal": goal,
                    "label": f"reference_{index}",
                    "media_type": "image/png" if str(path).lower().endswith(".png") else "image/jpeg",
                    "source_kind": "local_path",
                    "original_path": str(Path(path).resolve()),
                    "stored_path": str(Path(path).resolve()),
                    "host_visible_path": str(Path(path).resolve()),
                    "added_at": "2026-05-06T00:00:00Z",
                }
                for index, path in enumerate(args.reference or [], start=1)
            ]

        reference_records = tuple(ReferenceImageRecordContract.model_validate(item) for item in raw_reference_items)
        if request_mode == "reference-understanding":
            return VisionRequest(
                goal=goal,
                images=tuple(
                    VisionImageInput(
                        path=image.image_path,
                        role="reference",
                        label=image.label,
                        media_type=image.media_type,
                    )
                    for image in build_reference_capture_images(reference_records)
                ),
                target_object=target_object,
                prompt_hint="reference_understanding",
                metadata={
                    "mode": "reference_understanding",
                    "reference_ids": [record.reference_id for record in reference_records],
                    "source": "vision_harness",
                },
            )
        request = build_vision_request_from_capture_bundle(
            bundle,
            goal=goal,
            reference_images=build_reference_capture_images(reference_records),
            prompt_hint=prompt_hint,
        )
        if getattr(args, "fixture_only", None) == "reference-understanding":
            return VisionRequest(
                goal=request.goal,
                images=tuple(image for image in request.images if image.role == "reference"),
                target_object=request.target_object,
                prompt_hint="reference_understanding",
                truth_summary=request.truth_summary,
                metadata={
                    **request.metadata,
                    "mode": "reference_understanding",
                    "reference_ids": [record.reference_id for record in reference_records],
                },
            )
        return request

    before = [
        _capture_image(path, label=f"before_{index}", view_kind="wide")
        for index, path in enumerate(args.before or [], start=1)
    ]
    after = [
        _capture_image(path, label=f"after_{index}", view_kind="wide")
        for index, path in enumerate(args.after or [], start=1)
    ]
    reference_images = [
        VisionImageInput(
            path=path,
            role="reference",
            label=f"reference_{index}",
            media_type="image/png" if path.lower().endswith(".png") else "image/jpeg",
        )
        for index, path in enumerate(args.reference or [], start=1)
    ]
    images = tuple(
        [
            *[
                VisionImageInput(path=item.image_path, role="before", label=item.label, media_type=item.media_type)
                for item in before
            ],
            *[
                VisionImageInput(path=item.image_path, role="after", label=item.label, media_type=item.media_type)
                for item in after
            ],
            *reference_images,
        ]
    )
    request = VisionRequest(
        goal=goal,
        images=images,
        target_object=target_object,
        prompt_hint=prompt_hint,
        truth_summary=_read_json(Path(args.truth_json)) if args.truth_json else None,
        metadata={"source": "vision_harness"},
    )
    if request_mode == "reference-understanding":
        return VisionRequest(
            goal=request.goal,
            images=tuple(image for image in request.images if image.role == "reference"),
            target_object=request.target_object,
            prompt_hint="reference_understanding",
            truth_summary=request.truth_summary,
            metadata={
                **request.metadata,
                "mode": "reference_understanding",
                "reference_ids": [
                    f"fixture_ref_{index}"
                    for index, image in enumerate(request.images, start=1)
                    if image.role == "reference"
                ],
            },
        )
    if getattr(args, "fixture_only", None) == "reference-understanding":
        return VisionRequest(
            goal=request.goal,
            images=tuple(image for image in request.images if image.role == "reference"),
            target_object=request.target_object,
            prompt_hint="reference_understanding",
            truth_summary=request.truth_summary,
            metadata={
                **request.metadata,
                "mode": "reference_understanding",
                "reference_ids": [
                    f"fixture_ref_{index}"
                    for index, image in enumerate(request.images, start=1)
                    if image.role == "reference"
                ],
            },
        )
    return request


def _config_for_backend(args: Any, backend: str, *, vision_enabled: bool = True) -> Config:
    payload: dict[str, Any] = {
        "BLENDER_RPC_HOST": "127.0.0.1",
        "BLENDER_RPC_PORT": 8765,
        "ROUTER_ENABLED": True,
        "ROUTER_LOG_DECISIONS": True,
        "OTEL_ENABLED": False,
        "OTEL_EXPORTER": "none",
        "OTEL_SERVICE_NAME": "blender-ai-mcp",
        "MCP_SURFACE_PROFILE": "llm-guided",
        "MCP_DEFAULT_CONTRACT_LINE": None,
        "MCP_LIST_PAGE_SIZE": 100,
        "MCP_TOOL_TIMEOUT_SECONDS": 30.0,
        "MCP_TASK_TIMEOUT_SECONDS": 300.0,
        "RPC_TIMEOUT_SECONDS": 30.0,
        "ADDON_EXECUTION_TIMEOUT_SECONDS": 30.0,
        "VISION_ENABLED": vision_enabled,
        "VISION_PROVIDER": backend,
        "VISION_ALLOW_ON_GUIDED": True,
        "VISION_MAX_IMAGES": args.max_images,
        "VISION_MAX_TOKENS": args.max_tokens,
        "VISION_TIMEOUT_SECONDS": args.timeout_seconds,
        "VISION_LOCAL_MODEL_ID": args.transformers_model if backend == "transformers_local" else None,
        "VISION_LOCAL_MODEL_PATH": None,
        "VISION_LOCAL_DEVICE": args.local_device,
        "VISION_LOCAL_DTYPE": args.local_dtype,
        "VISION_MLX_MODEL_ID": args.mlx_model if backend == "mlx_local" else None,
        "VISION_MLX_MODEL_PATH": None,
        "VISION_EXTERNAL_BASE_URL": args.external_base_url if backend == "openai_compatible_external" else None,
        "VISION_EXTERNAL_MODEL": args.external_model if backend == "openai_compatible_external" else None,
        "VISION_EXTERNAL_API_KEY": args.external_api_key if backend == "openai_compatible_external" else None,
        "VISION_EXTERNAL_API_KEY_ENV": args.external_api_key_env if backend == "openai_compatible_external" else None,
        "VISION_EXTERNAL_PROVIDER": args.external_provider if backend == "openai_compatible_external" else "generic",
        "VISION_EXTERNAL_CONTRACT_PROFILE": (
            args.external_contract_profile if backend == "openai_compatible_external" else None
        ),
        "VISION_OPENROUTER_BASE_URL": args.openrouter_base_url if backend == "openai_compatible_external" else None,
        "VISION_OPENROUTER_MODEL": args.openrouter_model if backend == "openai_compatible_external" else None,
        "VISION_OPENROUTER_API_KEY": args.openrouter_api_key if backend == "openai_compatible_external" else None,
        "VISION_OPENROUTER_API_KEY_ENV": args.openrouter_api_key_env
        if backend == "openai_compatible_external"
        else None,
        "VISION_OPENROUTER_SITE_URL": args.openrouter_site_url if backend == "openai_compatible_external" else None,
        "VISION_OPENROUTER_SITE_NAME": args.openrouter_site_name if backend == "openai_compatible_external" else None,
        "VISION_GEMINI_BASE_URL": args.gemini_base_url if backend == "openai_compatible_external" else None,
        "VISION_GEMINI_MODEL": args.gemini_model if backend == "openai_compatible_external" else None,
        "VISION_GEMINI_API_KEY": args.gemini_api_key if backend == "openai_compatible_external" else None,
        "VISION_GEMINI_API_KEY_ENV": args.gemini_api_key_env if backend == "openai_compatible_external" else None,
        "VISION_SEGMENTATION_ENABLED": os.getenv("VISION_SEGMENTATION_ENABLED", "false").lower()
        in {"true", "1", "yes"},
        "VISION_SEGMENTATION_PROVIDER": os.getenv("VISION_SEGMENTATION_PROVIDER", "generic_sidecar"),
        "VISION_SEGMENTATION_ENDPOINT": os.getenv("VISION_SEGMENTATION_ENDPOINT") or None,
        "VISION_SEGMENTATION_MODEL": os.getenv("VISION_SEGMENTATION_MODEL") or None,
        "VISION_SEGMENTATION_API_KEY": os.getenv("VISION_SEGMENTATION_API_KEY") or None,
        "VISION_SEGMENTATION_API_KEY_ENV": os.getenv("VISION_SEGMENTATION_API_KEY_ENV") or None,
        "VISION_SEGMENTATION_TIMEOUT_SECONDS": float(os.getenv("VISION_SEGMENTATION_TIMEOUT_SECONDS", 15.0)),
        "VISION_SEGMENTATION_MAX_PARTS": int(os.getenv("VISION_SEGMENTATION_MAX_PARTS", 16)),
        "VISION_LOCALIZATION_ENABLED": os.getenv("VISION_LOCALIZATION_ENABLED", "false").lower()
        in {"true", "1", "yes"},
        "VISION_LOCALIZATION_PROVIDER": os.getenv("VISION_LOCALIZATION_PROVIDER", "generic_sidecar"),
        "VISION_LOCALIZATION_ENDPOINT": os.getenv("VISION_LOCALIZATION_ENDPOINT") or None,
        "VISION_LOCALIZATION_MODEL": os.getenv("VISION_LOCALIZATION_MODEL") or None,
        "VISION_LOCALIZATION_API_KEY": os.getenv("VISION_LOCALIZATION_API_KEY") or None,
        "VISION_LOCALIZATION_API_KEY_ENV": os.getenv("VISION_LOCALIZATION_API_KEY_ENV") or None,
        "VISION_LOCALIZATION_TIMEOUT_SECONDS": float(os.getenv("VISION_LOCALIZATION_TIMEOUT_SECONDS", 15.0)),
        "VISION_LOCALIZATION_MAX_CANDIDATES": int(os.getenv("VISION_LOCALIZATION_MAX_CANDIDATES", 8)),
    }
    return Config(**payload)


def _backend_list(args: Any) -> list[str]:
    if args.backend == "all":
        return ["mlx_local", "transformers_local", "openai_compatible_external"]
    return [args.backend]


def _attach_reliability_scorecard_if_requested(
    args: Any,
    entry: dict[str, Any],
    *,
    request: VisionRequest | None,
) -> None:
    if not getattr(args, "emit_reliability_scorecard", False):
        return
    entry["reliability_scorecard"] = build_advisory_reliability_scorecard(
        entry=entry,
        request=request,
    ).model_dump(mode="json")


def _post_request_runtime_config(backend: Any, fallback: VisionRuntimeConfig) -> VisionRuntimeConfig:
    backend_runtime = getattr(backend, "runtime_config", None)
    return backend_runtime if isinstance(backend_runtime, VisionRuntimeConfig) else fallback


async def _run_backend(
    args: Any,
    backend_name: str,
    request: VisionRequest,
    golden: ResolvedVisionGoldenScenario | None = None,
) -> dict[str, Any]:
    runtime = build_vision_runtime_config(_config_for_backend(args, backend_name))
    backend = create_vision_backend(runtime)
    result = await backend.analyze(request)
    runtime = _post_request_runtime_config(backend, runtime)
    entry = {
        "backend": backend_name,
        "model_name": runtime.active_model_name,
        "vision_contract_profile": runtime.active_vision_contract_profile,
        "status": "success",
        "result": result,
    }
    if (
        runtime.openai_compatible_external is not None
        and runtime.openai_compatible_external.model_capabilities is not None
    ):
        capabilities = runtime.openai_compatible_external.model_capabilities
        capability_summary: dict[str, Any] = {
            "model_id": capabilities.model_id,
            "capability_source": capabilities.capability_source,
            "context_length": capabilities.context_length,
            "max_completion_tokens": capabilities.max_completion_tokens,
            "input_modalities": list(capabilities.input_modalities),
            "output_modalities": list(capabilities.output_modalities),
            "supported_parameters": list(capabilities.supported_parameters),
        }
        request_policy = getattr(backend, "last_request_policy_summary", None)
        if isinstance(request_policy, dict):
            if isinstance(request_policy.get("requested_max_tokens"), int):
                capability_summary["requested_max_tokens"] = request_policy["requested_max_tokens"]
            if isinstance(request_policy.get("response_format_type"), str):
                capability_summary["request_mode"] = request_policy["response_format_type"]
            if isinstance(request_policy.get("plugins"), list):
                capability_summary["response_healing_enabled"] = "response-healing" in request_policy["plugins"]
        entry["capability_summary"] = capability_summary
    diagnostics = getattr(backend, "last_output_diagnostics", None)
    if diagnostics is not None:
        entry["diagnostics"] = diagnostics
    if golden is not None:
        entry["evaluation"] = evaluate_vision_result(entry, golden).model_dump(mode="json")
    _attach_reliability_scorecard_if_requested(args, entry, request=request)
    return entry


async def _run_localized_support_harness(
    args: Any,
    *,
    golden: ResolvedVisionGoldenScenario | None = None,
) -> list[dict[str, Any]]:
    goal = _effective_goal(args, golden)
    reference_records = _reference_records_from_inputs(args=args, golden=golden, goal=goal)
    captures = _localized_support_captures_from_inputs(args=args, golden=golden)
    packet = _localized_support_packet(args=args, reference_records=reference_records, captures=captures)

    if args.fixture_only == "localized-support":
        return [
            {
                "backend": "fixture_only",
                "status": "fixture_only",
                "fixture_only_mode": "localized-support",
                "result": {
                    "goal": goal,
                    "target_object": getattr(args, "target_object", None),
                    "target_view": getattr(args, "target_view", None),
                    "localized_support_reason": packet.localized_support_reason,
                    "query_labels": compare_packets_area._query_labels_for_packet(packet),
                    "capture_count": len(captures),
                    "reference_count": len(reference_records),
                    "packet": packet.model_dump(mode="json", exclude_none=True),
                },
            }
        ]

    backend_name = "mlx_local" if args.backend == "all" else args.backend
    runtime = build_vision_runtime_config(_config_for_backend(args, backend_name, vision_enabled=False))
    localization_config = runtime.active_localization_config
    segmentation_config = runtime.active_segmentation_sidecar
    part_segmentation: ReferencePartSegmentationContract | None

    if localization_config is None and segmentation_config is None:
        part_segmentation = _disabled_localized_support_result()
        support_evidence = build_compare_support_evidence(None, part_segmentation=part_segmentation)
        localization_candidates_count = 0
        query_labels = compare_packets_area._query_labels_for_packet(packet)
    else:
        (
            localization_candidates,
            localization_projection,
        ) = await compare_packets_area.collect_compare_time_localization_support(
            config=localization_config,
            goal=goal,
            packet=packet,
            reference_records=reference_records,
            captures=captures,
        )
        segmentation_projection = await compare_packets_area.collect_compare_time_segmentation_support(
            config=segmentation_config,
            goal=goal,
            packet_id=packet.packet_id,
            packet_label=packet.packet_label,
            target_view=packet.target_view,
            scope_label=packet.scope_label,
            target_objects=packet.target_objects,
            reference_records=reference_records,
            captures=captures,
            localization_candidates=localization_candidates,
        )
        part_segmentation = compare_packets_area.merge_compare_time_part_segmentation(
            localization_projection,
            segmentation_projection,
        )
        if part_segmentation is None:
            part_segmentation = _disabled_localized_support_result()
        support_evidence = build_compare_support_evidence(None, part_segmentation=part_segmentation)
        localization_candidates_count = len(localization_candidates)
        query_labels = compare_packets_area._query_labels_for_packet(packet)
    runtime_evidence = _localized_support_runtime_evidence(
        packet=packet,
        localization_config=localization_config,
        segmentation_config=segmentation_config,
        localization_candidates_count=localization_candidates_count,
        part_segmentation=part_segmentation,
    )

    return [
        {
            "backend": backend_name,
            "status": "success",
            "localized_optional_mode": "packet_support",
            "result": {
                "goal": goal,
                "target_object": getattr(args, "target_object", None),
                "target_view": getattr(args, "target_view", None),
                "localized_support_reason": packet.localized_support_reason,
                "query_labels": query_labels,
                "localization_candidate_count": localization_candidates_count,
                "part_segmentation": part_segmentation.model_dump(mode="json", exclude_none=True),
                "runtime_evidence": runtime_evidence.model_dump(mode="json", exclude_none=True),
                "support_evidence": [item.model_dump(mode="json", exclude_none=True) for item in support_evidence],
            },
        }
    ]


async def _run(args: Any) -> list[dict[str, Any]]:
    golden = _resolve_golden(args)
    if args.mode == "localized-support":
        return await _run_localized_support_harness(args, golden=golden)
    request = _build_request_from_args(args, golden=golden)
    if args.fixture_only:
        fixture_entry = {
            "backend": "fixture_only",
            "model_name": None,
            "vision_contract_profile": None,
            "status": "fixture_only",
            "fixture_only_mode": args.fixture_only,
            "result": {
                "goal": request.goal,
                "target_object": request.target_object,
                "image_count": len(request.images),
                "image_roles": [image.role for image in request.images],
                "metadata": request.metadata,
            },
        }
        _attach_reliability_scorecard_if_requested(args, fixture_entry, request=request)
        return [
            {
                **fixture_entry,
            }
        ]
    results: list[dict[str, Any]] = []
    for backend_name in _backend_list(args):
        try:
            results.append(await _run_backend(args, backend_name, request, golden=golden))
        except Exception as exc:
            entry: dict[str, Any] = {
                "backend": backend_name,
                "model_name": None,
                "vision_contract_profile": None,
                "status": "error",
                "error": str(exc),
            }
            if golden is not None:
                entry["evaluation"] = evaluate_vision_result(entry, golden).model_dump(mode="json")
            _attach_reliability_scorecard_if_requested(args, entry, request=request)
            results.append(entry)
    return results


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--backend", choices=["mlx_local", "transformers_local", "openai_compatible_external", "all"], default="all"
    )
    parser.add_argument("--goal")
    parser.add_argument("--target-object")
    parser.add_argument("--prompt-hint")
    parser.add_argument("--golden-json")
    parser.add_argument("--bundle-json")
    parser.add_argument("--references-json")
    parser.add_argument("--truth-json")
    parser.add_argument(
        "--mode", choices=["compare", "reference-understanding", "localized-support"], default="compare"
    )
    parser.add_argument("--before", action="append")
    parser.add_argument("--after", action="append")
    parser.add_argument("--reference", action="append")
    parser.add_argument("--target-view")
    parser.add_argument(
        "--localized-support-reason",
        choices=[
            "part_missing_ambiguity",
            "anchor_ambiguity",
            "attachment_gap",
            "seam_unclear",
            "mask_needed",
        ],
        default="mask_needed",
    )
    parser.add_argument("--localized-support-query-label")
    parser.add_argument("--max-images", type=int, default=8)
    parser.add_argument("--max-tokens", type=int, default=400)
    parser.add_argument("--timeout-seconds", type=float, default=60.0)
    parser.add_argument("--transformers-model", default=os.getenv("VISION_LOCAL_MODEL_ID"))
    parser.add_argument(
        "--mlx-model", default=os.getenv("VISION_MLX_MODEL_ID") or "mlx-community/Qwen3-VL-2B-Instruct-4bit"
    )
    parser.add_argument("--external-base-url", default=os.getenv("VISION_EXTERNAL_BASE_URL"))
    parser.add_argument("--external-model", default=os.getenv("VISION_EXTERNAL_MODEL"))
    parser.add_argument("--external-api-key", default=os.getenv("VISION_EXTERNAL_API_KEY"))
    parser.add_argument("--external-api-key-env", default=os.getenv("VISION_EXTERNAL_API_KEY_ENV"))
    parser.add_argument(
        "--external-provider",
        choices=["generic", "openrouter", "google_ai_studio"],
        default=os.getenv("VISION_EXTERNAL_PROVIDER", "generic"),
    )
    parser.add_argument(
        "--external-contract-profile",
        choices=["generic_full", "google_family_compare"],
        default=os.getenv("VISION_EXTERNAL_CONTRACT_PROFILE"),
    )
    parser.add_argument("--openrouter-base-url", default=os.getenv("VISION_OPENROUTER_BASE_URL"))
    parser.add_argument("--openrouter-model", default=os.getenv("VISION_OPENROUTER_MODEL"))
    parser.add_argument("--openrouter-api-key", default=os.getenv("VISION_OPENROUTER_API_KEY"))
    parser.add_argument("--openrouter-api-key-env", default=os.getenv("VISION_OPENROUTER_API_KEY_ENV"))
    parser.add_argument("--openrouter-site-url", default=os.getenv("VISION_OPENROUTER_SITE_URL"))
    parser.add_argument("--openrouter-site-name", default=os.getenv("VISION_OPENROUTER_SITE_NAME"))
    parser.add_argument("--gemini-base-url", default=os.getenv("VISION_GEMINI_BASE_URL"))
    parser.add_argument("--gemini-model", default=os.getenv("VISION_GEMINI_MODEL"))
    parser.add_argument("--gemini-api-key", default=os.getenv("VISION_GEMINI_API_KEY"))
    parser.add_argument("--gemini-api-key-env", default=os.getenv("VISION_GEMINI_API_KEY_ENV"))
    parser.add_argument("--local-device", default=os.getenv("VISION_LOCAL_DEVICE", "cpu"))
    parser.add_argument("--local-dtype", default=os.getenv("VISION_LOCAL_DTYPE", "auto"))
    parser.add_argument("--fixture-only", choices=["reference-understanding", "localized-support"])
    parser.add_argument(
        "--emit-reliability-scorecard",
        action="store_true",
        help="Attach default-off advisory per-axis reliability telemetry to harness results.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.golden_json is None and args.goal is None:
        parser.error("Provide --goal or --golden-json")

    if args.mode == "reference-understanding":
        if args.bundle_json is None and not args.reference:
            parser.error("Provide --reference or --bundle-json when --mode=reference-understanding")
        if args.bundle_json is not None and args.references_json is None and not args.reference:
            parser.error(
                "Provide --references-json or --reference when --mode=reference-understanding uses --bundle-json"
            )
    elif args.mode == "localized-support":
        if not args.localized_support_query_label:
            parser.error("Provide --localized-support-query-label when --mode=localized-support")
        if args.bundle_json is None and not args.after:
            parser.error("Provide --after or --bundle-json when --mode=localized-support")
        if args.bundle_json is None and args.references_json is None and not args.reference:
            parser.error("Provide --reference or --references-json when --mode=localized-support")
        if args.bundle_json is not None and args.references_json is None and not args.reference:
            parser.error("Provide --references-json or --reference when --mode=localized-support uses --bundle-json")
    elif args.golden_json is None and args.bundle_json is None and not any([args.before, args.after, args.reference]):
        parser.error("Provide --bundle-json or at least one of --before/--after/--reference")

    results = asyncio.run(_run(args))
    print(json.dumps(results, ensure_ascii=False, indent=2))

    return 0 if all(item.get("status") in {"success", "fixture_only"} for item in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
