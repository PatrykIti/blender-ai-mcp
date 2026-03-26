#!/usr/bin/env python3
"""Run bounded vision backends against a shared local bundle/input payload."""

from __future__ import annotations

import argparse
import asyncio
import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from server.adapters.mcp.contracts.reference import ReferenceImageRecordContract
from server.adapters.mcp.contracts.vision import (
    VisionCaptureBundleContract,
    VisionCaptureImageContract,
)
from server.adapters.mcp.vision import (
    VisionImageInput,
    VisionRequest,
    build_reference_capture_images,
    build_vision_request_from_capture_bundle,
    create_vision_backend,
    build_vision_runtime_config,
)
from server.infrastructure.config import Config


@dataclass(frozen=True)
class HarnessConfig:
    backend: str
    config: Config


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _capture_image(path: str, *, label: str, view_kind: str) -> VisionCaptureImageContract:
    media_type = "image/png" if path.lower().endswith(".png") else "image/jpeg"
    return VisionCaptureImageContract(
        label=label,
        image_path=path,
        media_type=media_type,
        view_kind=view_kind,
    )


def _build_request_from_args(args: argparse.Namespace) -> VisionRequest:
    if args.bundle_json:
        bundle_data = _read_json(Path(args.bundle_json))
        bundle = VisionCaptureBundleContract.model_validate(bundle_data)
        references = tuple(
            ReferenceImageRecordContract.model_validate(item)
            for item in (_read_json(Path(args.references_json)).get("references", []) if args.references_json else [])
        )
        return build_vision_request_from_capture_bundle(
            bundle,
            goal=args.goal,
            reference_images=build_reference_capture_images(references),
            prompt_hint=args.prompt_hint,
        )

    before = [
        _capture_image(path, label=f"before_{index}", view_kind="wide")
        for index, path in enumerate(args.before or [], start=1)
    ]
    after = [
        _capture_image(path, label=f"after_{index}", view_kind="wide")
        for index, path in enumerate(args.after or [], start=1)
    ]
    references = [
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
            *references,
        ]
    )
    return VisionRequest(
        goal=args.goal,
        images=images,
        target_object=args.target_object,
        prompt_hint=args.prompt_hint,
        truth_summary=_read_json(Path(args.truth_json)) if args.truth_json else None,
        metadata={"source": "vision_harness"},
    )


def _config_for_backend(args: argparse.Namespace, backend: str) -> Config:
    payload = {
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
    }
    return Config(**payload)


def _backend_list(args: argparse.Namespace) -> list[str]:
    if args.backend == "all":
        return ["mlx_local", "transformers_local", "openai_compatible_external"]
    return [args.backend]


async def _run_backend(args: argparse.Namespace, backend_name: str, request: VisionRequest) -> dict[str, Any]:
    runtime = build_vision_runtime_config(_config_for_backend(args, backend_name))
    backend = create_vision_backend(runtime)
    result = await backend.analyze(request)
    return {
        "backend": backend_name,
        "model_name": runtime.active_model_name,
        "status": "success",
        "result": result,
    }


async def _run(args: argparse.Namespace) -> list[dict[str, Any]]:
    request = _build_request_from_args(args)
    results: list[dict[str, Any]] = []
    for backend_name in _backend_list(args):
        try:
            results.append(await _run_backend(args, backend_name, request))
        except Exception as exc:
            results.append(
                {
                    "backend": backend_name,
                    "status": "error",
                    "error": str(exc),
                }
            )
    return results


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--backend", choices=["mlx_local", "transformers_local", "openai_compatible_external", "all"], default="all")
    parser.add_argument("--goal", required=True)
    parser.add_argument("--target-object")
    parser.add_argument("--prompt-hint")
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
    parser.add_argument("--mlx-model", default=os.getenv("VISION_MLX_MODEL_ID"))
    parser.add_argument("--external-base-url", default=os.getenv("VISION_EXTERNAL_BASE_URL"))
    parser.add_argument("--external-model", default=os.getenv("VISION_EXTERNAL_MODEL"))
    parser.add_argument("--external-api-key", default=os.getenv("VISION_EXTERNAL_API_KEY"))
    parser.add_argument("--external-api-key-env", default=os.getenv("VISION_EXTERNAL_API_KEY_ENV"))
    parser.add_argument("--local-device", default=os.getenv("VISION_LOCAL_DEVICE", "cpu"))
    parser.add_argument("--local-dtype", default=os.getenv("VISION_LOCAL_DTYPE", "auto"))
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.bundle_json is None and not any([args.before, args.after, args.reference]):
        parser.error("Provide --bundle-json or at least one of --before/--after/--reference")

    results = asyncio.run(_run(args))
    print(json.dumps(results, ensure_ascii=False, indent=2))

    return 0 if all(item.get("status") == "success" for item in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
