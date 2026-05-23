#!/usr/bin/env python3
"""Run a local compare-time segmentation sidecar for blender-ai-mcp."""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any

import numpy as np

from scripts.vision_sidecar_common import (
    PayloadImageRef,
    clamp_box_to_image,
    iter_payload_images,
    mask_bbox,
    resolve_device_name,
    resolve_model_alias,
    write_mask_image,
    write_temp_image,
)

DEFAULT_SEGMENTATION_MODEL = "facebook/sam-vit-base"
SEGMENTATION_MODEL_ALIASES = {
    "sam-sidecar-v1": DEFAULT_SEGMENTATION_MODEL,
}


@dataclass(frozen=True)
class SegmentationPrompt:
    part_label: str
    box_xyxy: tuple[int, int, int, int]
    reference_id: str | None = None
    capture_label: str | None = None
    target_view: str | None = None


@dataclass
class SegmentationPrediction:
    mask: np.ndarray
    confidence: float | None


@dataclass
class SegmentationRuntime:
    model: Any
    processor: Any
    torch_module: Any
    device_name: str


def _build_segmentation_runtime(*, model_name: str, device_name: str) -> SegmentationRuntime:
    try:
        import torch
        from transformers import SamModel, SamProcessor
    except Exception as exc:  # pragma: no cover - exercised as operator dependency failure
        raise RuntimeError(
            "segmentation_sidecar requires the optional vision runtime dependencies. "
            "Install them with `poetry install --with vision`."
        ) from exc

    model = SamModel.from_pretrained(model_name)
    processor = SamProcessor.from_pretrained(model_name)
    model.to(device_name)
    model.eval()
    return SegmentationRuntime(
        model=model,
        processor=processor,
        torch_module=torch,
        device_name=device_name,
    )


def _predict_segmentation(
    runtime: SegmentationRuntime,
    *,
    image: Any,
    prompts: list[SegmentationPrompt],
) -> list[SegmentationPrediction]:
    prompt_boxes = [list(prompt.box_xyxy) for prompt in prompts]
    inputs = runtime.processor(images=image, input_boxes=[prompt_boxes], return_tensors="pt")
    moved_inputs = {
        key: value.to(runtime.device_name) if hasattr(value, "to") else value for key, value in inputs.items()
    }

    with runtime.torch_module.inference_mode():
        outputs = runtime.model(**moved_inputs, multimask_output=False)

    masks = runtime.processor.image_processor.post_process_masks(
        outputs.pred_masks.detach().cpu(),
        moved_inputs["original_sizes"].detach().cpu(),
        moved_inputs["reshaped_input_sizes"].detach().cpu(),
        binarize=True,
    )
    raw_masks = masks[0]
    iou_scores = outputs.iou_scores.detach().cpu().reshape(-1).tolist()

    predictions: list[SegmentationPrediction] = []
    for index, prompt in enumerate(prompts):
        mask = raw_masks[index]
        mask_array = mask.numpy() if hasattr(mask, "numpy") else np.asarray(mask)
        predictions.append(
            SegmentationPrediction(
                mask=mask_array.astype(bool),
                confidence=float(iou_scores[index]) if index < len(iou_scores) else None,
            )
        )
    return predictions


def _resolve_seed_prompts(
    payload: dict[str, Any],
    image_ref: PayloadImageRef,
    *,
    width: int,
    height: int,
    allow_fallback: bool,
) -> list[SegmentationPrompt]:
    raw_seeds = payload.get("seed_boxes")
    prompts: list[SegmentationPrompt] = []
    if isinstance(raw_seeds, list):
        for item in raw_seeds:
            if not isinstance(item, dict):
                continue
            seed_capture_label = str(item.get("capture_label") or "").strip() or None
            seed_reference_id = str(item.get("reference_id") or "").strip() or None
            if seed_capture_label is not None and seed_capture_label != image_ref.capture_label:
                continue
            if seed_reference_id is not None and seed_reference_id != image_ref.reference_id:
                continue
            box_xyxy = item.get("box_xyxy")
            if not (
                isinstance(box_xyxy, list)
                and len(box_xyxy) == 4
                and all(isinstance(value, (int, float)) for value in box_xyxy)
            ):
                continue
            prompts.append(
                SegmentationPrompt(
                    part_label=str(item.get("query_label") or item.get("part_label") or "focus_region").strip(),
                    box_xyxy=clamp_box_to_image(
                        (float(box_xyxy[0]), float(box_xyxy[1]), float(box_xyxy[2]), float(box_xyxy[3])),
                        width=width,
                        height=height,
                    ),
                    reference_id=image_ref.reference_id,
                    capture_label=image_ref.capture_label,
                    target_view=image_ref.target_view,
                )
            )
    if prompts or not allow_fallback:
        return prompts

    packet = payload.get("packet")
    packet_label = (
        str(packet.get("scope_label") or packet.get("packet_label") or "").strip() if isinstance(packet, dict) else ""
    )
    target_objects = packet.get("target_objects") if isinstance(packet, dict) else None
    fallback_label = packet_label or (
        str(target_objects[0]).strip() if isinstance(target_objects, list) and target_objects else "focus_region"
    )
    return [
        SegmentationPrompt(
            part_label=fallback_label,
            box_xyxy=(0, 0, width, height),
            reference_id=image_ref.reference_id,
            capture_label=image_ref.capture_label,
            target_view=image_ref.target_view,
        )
    ]


@dataclass
class SegmentationService:
    requested_model_name: str
    device_name: str
    max_parts: int
    _runtime: SegmentationRuntime | None = None

    @property
    def resolved_model_name(self) -> str:
        return resolve_model_alias(self.requested_model_name, SEGMENTATION_MODEL_ALIASES)

    def _ensure_runtime(self) -> SegmentationRuntime:
        if self._runtime is None:
            self._runtime = _build_segmentation_runtime(
                model_name=self.resolved_model_name,
                device_name=self.device_name,
            )
        return self._runtime

    def warmup(self) -> None:
        self._ensure_runtime()

    def segment_payload(self, payload: dict[str, Any]) -> dict[str, Any]:
        images = iter_payload_images(payload)
        if not images:
            raise ValueError("Payload did not include any capture or reference image paths.")

        try:
            from PIL import Image
        except Exception as exc:  # pragma: no cover - exercised as operator dependency failure
            raise RuntimeError(
                "segmentation_sidecar requires Pillow. Install repo dependencies before running it."
            ) from exc

        runtime = self._ensure_runtime()
        parts: list[dict[str, Any]] = []
        for index, image_ref in enumerate(images):
            with Image.open(image_ref.image_path).convert("RGB") as image:
                prompts = _resolve_seed_prompts(
                    payload,
                    image_ref,
                    width=image.width,
                    height=image.height,
                    allow_fallback=index == 0,
                )
                if not prompts:
                    continue
                predictions = _predict_segmentation(
                    runtime,
                    image=image,
                    prompts=prompts,
                )
                for prompt, prediction in zip(prompts, predictions):
                    derived_box = mask_bbox(prediction.mask) or prompt.box_xyxy
                    bounded_box = clamp_box_to_image(
                        (
                            float(derived_box[0]),
                            float(derived_box[1]),
                            float(derived_box[2]),
                            float(derived_box[3]),
                        ),
                        width=image.width,
                        height=image.height,
                    )
                    parts.append(
                        {
                            "part_label": prompt.part_label,
                            "mask_path": write_mask_image(
                                prediction.mask.astype(np.uint8), prefix="segmentation_mask_"
                            ),
                            "crop_path": write_temp_image(
                                image.crop(bounded_box),
                                prefix="segmentation_crop_",
                                suffix=".png",
                            ),
                            "confidence": prediction.confidence,
                            "landmarks": [],
                        }
                    )
                    if len(parts) >= self.max_parts:
                        break
            if len(parts) >= self.max_parts:
                break

        return {
            "parts": parts[: self.max_parts],
            "requested_model_name": self.requested_model_name,
            "resolved_model_name": self.resolved_model_name,
            "device_name": self.device_name,
        }


class SegmentationRequestHandler(BaseHTTPRequestHandler):
    service: SegmentationService | None = None

    def _write_json(self, *, status: HTTPStatus, payload: dict[str, Any]) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status.value)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:  # noqa: N802
        if self.path != "/health":
            self._write_json(status=HTTPStatus.NOT_FOUND, payload={"error": "Not found"})
            return

        service = self.service
        assert service is not None
        self._write_json(
            status=HTTPStatus.OK,
            payload={
                "status": "ok",
                "runtime_loaded": service._runtime is not None,
                "requested_model_name": service.requested_model_name,
                "resolved_model_name": service.resolved_model_name,
                "device_name": service.device_name,
                "max_parts": service.max_parts,
            },
        )

    def do_POST(self) -> None:  # noqa: N802
        if self.path != "/segment":
            self._write_json(status=HTTPStatus.NOT_FOUND, payload={"error": "Not found"})
            return

        service = self.service
        assert service is not None
        try:
            content_length = int(self.headers.get("Content-Length", "0") or "0")
            raw_body = self.rfile.read(content_length)
            payload = json.loads(raw_body.decode("utf-8"))
            if not isinstance(payload, dict):
                raise ValueError("Request body must decode to a JSON object.")
            response_payload = service.segment_payload(payload)
        except Exception as exc:
            self._write_json(status=HTTPStatus.BAD_REQUEST, payload={"error": str(exc)})
            return

        self._write_json(status=HTTPStatus.OK, payload=response_payload)

    def log_message(self, format: str, *args: object) -> None:  # noqa: A003
        return


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=9100)
    parser.add_argument("--model", default="sam-sidecar-v1")
    parser.add_argument("--device", default="auto")
    parser.add_argument("--max-parts", type=int, default=16)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    service = SegmentationService(
        requested_model_name=args.model,
        device_name=resolve_device_name(args.device),
        max_parts=args.max_parts,
    )
    service.warmup()
    SegmentationRequestHandler.service = service
    server = ThreadingHTTPServer((args.host, args.port), SegmentationRequestHandler)
    print(
        json.dumps(
            {
                "status": "starting",
                "host": args.host,
                "port": args.port,
                "requested_model_name": service.requested_model_name,
                "resolved_model_name": service.resolved_model_name,
                "device_name": service.device_name,
                "max_parts": service.max_parts,
                "segment_endpoint": f"http://{args.host}:{args.port}/segment",
                "health_endpoint": f"http://{args.host}:{args.port}/health",
            },
            ensure_ascii=False,
        ),
        flush=True,
    )
    server.serve_forever()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
