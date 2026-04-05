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

from server.adapters.mcp.contracts.reference import ReferenceImageRecordContract
from server.adapters.mcp.contracts.vision import (
    VisionCaptureBundleContract,
    VisionCaptureImageContract,
)
from server.adapters.mcp.vision import (
    ResolvedVisionGoldenScenario,
    VisionImageInput,
    VisionRequest,
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


def _build_request_from_args(args: Any, golden: ResolvedVisionGoldenScenario | None = None) -> VisionRequest:
    goal = _effective_goal(args, golden)
    target_object = _effective_target_object(args, golden)
    prompt_hint = _effective_prompt_hint(args, golden)
    bundle_json = _effective_bundle_json(args, golden)
    references_json = _effective_references_json(args, golden)

    if bundle_json:
        bundle_path = Path(bundle_json)
        bundle_data = _resolve_bundle_paths(_read_json(bundle_path), bundle_path)
        bundle = VisionCaptureBundleContract.model_validate(bundle_data)
        reference_records = tuple(
            ReferenceImageRecordContract.model_validate(item)
            for item in (
                _resolve_reference_paths(_read_json(Path(references_json)), Path(references_json)).get("references", [])
                if references_json
                else []
            )
        )
        return build_vision_request_from_capture_bundle(
            bundle,
            goal=goal,
            reference_images=build_reference_capture_images(reference_records),
            prompt_hint=prompt_hint,
        )

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
    return VisionRequest(
        goal=goal,
        images=images,
        target_object=target_object,
        prompt_hint=prompt_hint,
        truth_summary=_read_json(Path(args.truth_json)) if args.truth_json else None,
        metadata={"source": "vision_harness"},
    )


def _config_for_backend(args: Any, backend: str) -> Config:
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
        "VISION_ENABLED": True,
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
    }
    return Config(**payload)


def _backend_list(args: Any) -> list[str]:
    if args.backend == "all":
        return ["mlx_local", "transformers_local", "openai_compatible_external"]
    return [args.backend]


async def _run_backend(
    args: Any,
    backend_name: str,
    request: VisionRequest,
    golden: ResolvedVisionGoldenScenario | None = None,
) -> dict[str, Any]:
    runtime = build_vision_runtime_config(_config_for_backend(args, backend_name))
    backend = create_vision_backend(runtime)
    result = await backend.analyze(request)
    entry = {
        "backend": backend_name,
        "model_name": runtime.active_model_name,
        "vision_contract_profile": runtime.active_vision_contract_profile,
        "status": "success",
        "result": result,
    }
    diagnostics = getattr(backend, "last_output_diagnostics", None)
    if diagnostics is not None:
        entry["diagnostics"] = diagnostics
    if golden is not None:
        entry["evaluation"] = evaluate_vision_result(entry, golden).model_dump(mode="json")
    return entry


async def _run(args: Any) -> list[dict[str, Any]]:
    golden = _resolve_golden(args)
    request = _build_request_from_args(args, golden=golden)
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
    parser.add_argument("--before", action="append")
    parser.add_argument("--after", action="append")
    parser.add_argument("--reference", action="append")
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
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.golden_json is None and args.goal is None:
        parser.error("Provide --goal or --golden-json")

    if args.golden_json is None and args.bundle_json is None and not any([args.before, args.after, args.reference]):
        parser.error("Provide --bundle-json or at least one of --before/--after/--reference")

    results = asyncio.run(_run(args))
    print(json.dumps(results, ensure_ascii=False, indent=2))

    return 0 if all(item.get("status") == "success" for item in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
