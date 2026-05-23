#!/usr/bin/env python3
"""Run a local compare-time localization sidecar for blender-ai-mcp."""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from vision_sidecar_common import (  # noqa: E402
    clamp_box_to_image,
    humanize_query_label,
    iter_payload_images,
    resolve_device_name,
    resolve_model_alias,
    write_temp_image,
)

DEFAULT_LOCALIZATION_MODEL = "google/owlv2-base-patch16-ensemble"
LOCALIZATION_MODEL_ALIASES = {
    "grounding-sidecar-v1": DEFAULT_LOCALIZATION_MODEL,
}


def _build_localization_pipeline(*, model_name: str, device_name: str):
    try:
        from transformers import pipeline
    except Exception as exc:  # pragma: no cover - exercised as operator dependency failure
        raise RuntimeError(
            "localization_sidecar requires the optional vision runtime dependencies. "
            "Install them with `poetry install --with vision`."
        ) from exc

    return pipeline(
        task="zero-shot-object-detection",
        model=model_name,
        device=device_name,
    )


def _normalize_box(payload: Any) -> tuple[float, float, float, float] | None:
    if isinstance(payload, dict):
        keys = ("xmin", "ymin", "xmax", "ymax")
        if all(isinstance(payload.get(key), (int, float)) for key in keys):
            return (
                float(payload["xmin"]),
                float(payload["ymin"]),
                float(payload["xmax"]),
                float(payload["ymax"]),
            )
        alt_keys = ("x1", "y1", "x2", "y2")
        if all(isinstance(payload.get(key), (int, float)) for key in alt_keys):
            return (
                float(payload["x1"]),
                float(payload["y1"]),
                float(payload["x2"]),
                float(payload["y2"]),
            )
    if isinstance(payload, list) and len(payload) == 4 and all(isinstance(item, (int, float)) for item in payload):
        return float(payload[0]), float(payload[1]), float(payload[2]), float(payload[3])
    return None


def _run_localization_pipeline(
    detector: Any,
    *,
    image: Any,
    query_labels: list[str],
    threshold: float,
) -> list[dict[str, Any]]:
    prompt_lookup = {humanize_query_label(label).lower(): label for label in query_labels}
    detections = detector(
        image,
        candidate_labels=[humanize_query_label(label) for label in query_labels],
        threshold=threshold,
    )
    if isinstance(detections, dict):
        detections = [detections]
    if not isinstance(detections, list):
        raise RuntimeError("Localization detector returned an unsupported result shape.")

    normalized: list[dict[str, Any]] = []
    for item in detections:
        if not isinstance(item, dict):
            continue
        raw_label = str(item.get("label") or item.get("text") or "").strip()
        query_label = prompt_lookup.get(raw_label.lower())
        box_xyxy = _normalize_box(item.get("box"))
        confidence = item.get("score") or item.get("confidence")
        if query_label is None or box_xyxy is None or not isinstance(confidence, (int, float)):
            continue
        normalized.append(
            {
                "query_label": query_label,
                "box_xyxy": box_xyxy,
                "confidence": float(confidence),
            }
        )
    return normalized


def _iter_query_labels(payload: dict[str, Any]) -> list[str]:
    raw_labels = payload.get("query_labels")
    if not isinstance(raw_labels, list):
        return []
    labels: list[str] = []
    for item in raw_labels:
        value = str(item or "").strip()
        if value:
            labels.append(value)
    return labels


@dataclass
class LocalizationService:
    requested_model_name: str
    device_name: str
    max_candidates: int
    threshold: float
    _pipeline: Any | None = None

    @property
    def resolved_model_name(self) -> str:
        return resolve_model_alias(self.requested_model_name, LOCALIZATION_MODEL_ALIASES)

    def _ensure_pipeline(self):
        if self._pipeline is None:
            self._pipeline = _build_localization_pipeline(
                model_name=self.resolved_model_name,
                device_name=self.device_name,
            )
        return self._pipeline

    def warmup(self) -> None:
        self._ensure_pipeline()

    def localize_payload(self, payload: dict[str, Any]) -> dict[str, Any]:
        images = iter_payload_images(payload)
        query_labels = _iter_query_labels(payload)
        if not images:
            raise ValueError("Payload did not include any capture or reference image paths.")
        if not query_labels:
            raise ValueError("Payload did not include any query_labels.")

        try:
            from PIL import Image
        except Exception as exc:  # pragma: no cover - exercised as operator dependency failure
            raise RuntimeError(
                "localization_sidecar requires Pillow. Install repo dependencies before running it."
            ) from exc

        detector = self._ensure_pipeline()
        best_by_query_label: dict[str, dict[str, Any]] = {}

        for image_ref in images:
            with Image.open(image_ref.image_path).convert("RGB") as image:
                detections = _run_localization_pipeline(
                    detector,
                    image=image,
                    query_labels=query_labels,
                    threshold=self.threshold,
                )
                for item in detections:
                    box_xyxy = clamp_box_to_image(
                        item["box_xyxy"],
                        width=image.width,
                        height=image.height,
                    )
                    crop_path = write_temp_image(
                        image.crop(box_xyxy),
                        prefix="localization_crop_",
                        suffix=".png",
                    )
                    query_label = item["query_label"]
                    candidate = {
                        "query_label": query_label,
                        "reference_id": image_ref.reference_id,
                        "capture_label": image_ref.capture_label,
                        "target_view": image_ref.target_view,
                        "confidence": item["confidence"],
                        "box_xyxy": list(box_xyxy),
                        "crop_path": crop_path,
                    }
                    existing = best_by_query_label.get(query_label)
                    if existing is None or float(candidate["confidence"]) > float(existing["confidence"]):
                        best_by_query_label[query_label] = candidate

        ranked_candidates = sorted(
            best_by_query_label.values(),
            key=lambda item: float(item["confidence"]),
            reverse=True,
        )[: self.max_candidates]
        return {
            "candidates": ranked_candidates,
            "requested_model_name": self.requested_model_name,
            "resolved_model_name": self.resolved_model_name,
            "device_name": self.device_name,
            "threshold": self.threshold,
        }


class LocalizationRequestHandler(BaseHTTPRequestHandler):
    service: LocalizationService | None = None

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
                "pipeline_loaded": service._pipeline is not None,
                "requested_model_name": service.requested_model_name,
                "resolved_model_name": service.resolved_model_name,
                "device_name": service.device_name,
                "max_candidates": service.max_candidates,
                "threshold": service.threshold,
            },
        )

    def do_POST(self) -> None:  # noqa: N802
        if self.path != "/localize":
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
            response_payload = service.localize_payload(payload)
        except Exception as exc:
            self._write_json(status=HTTPStatus.BAD_REQUEST, payload={"error": str(exc)})
            return

        self._write_json(status=HTTPStatus.OK, payload=response_payload)

    def log_message(self, format: str, *args: object) -> None:  # noqa: A003
        return


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=9300)
    parser.add_argument("--model", default="grounding-sidecar-v1")
    parser.add_argument("--device", default="auto")
    parser.add_argument("--max-candidates", type=int, default=8)
    parser.add_argument("--threshold", type=float, default=0.1)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    service = LocalizationService(
        requested_model_name=args.model,
        device_name=resolve_device_name(args.device),
        max_candidates=args.max_candidates,
        threshold=args.threshold,
    )
    service.warmup()
    LocalizationRequestHandler.service = service
    server = ThreadingHTTPServer((args.host, args.port), LocalizationRequestHandler)
    print(
        json.dumps(
            {
                "status": "starting",
                "host": args.host,
                "port": args.port,
                "requested_model_name": service.requested_model_name,
                "resolved_model_name": service.resolved_model_name,
                "device_name": service.device_name,
                "max_candidates": service.max_candidates,
                "threshold": service.threshold,
                "localize_endpoint": f"http://{args.host}:{args.port}/localize",
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
