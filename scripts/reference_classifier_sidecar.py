#!/usr/bin/env python3
"""Run a local SigLIP2-based reference-classifier sidecar for blender-ai-mcp."""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from collections.abc import Sequence
from dataclasses import dataclass
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any

DEFAULT_LABEL_SPACE: tuple[tuple[str, str], ...] = (
    ("low_poly_faceted", "a low-poly faceted animal reference"),
    ("creature_blockout", "a generic creature blockout reference"),
    ("smooth_organic", "a smooth organic creature sculpt reference"),
    ("hard_surface", "a hard-surface product or prop reference"),
    ("architectural_mass", "an architectural facade or massing reference"),
    ("dental_surface", "a dental crown or dental surface reference"),
)


def _resolve_device_name(requested: str) -> str:
    normalized = str(requested or "auto").strip().lower()
    if normalized != "auto":
        return normalized

    try:
        import torch
    except Exception:
        return "cpu"

    if getattr(torch.backends, "mps", None) is not None and torch.backends.mps.is_available():
        return "mps"
    if torch.cuda.is_available():
        return "cuda:0"
    return "cpu"


def _build_classifier_pipeline(*, model_name: str, device_name: str):
    try:
        from transformers import pipeline
    except Exception as exc:  # pragma: no cover - exercised as operator dependency failure
        raise RuntimeError(
            "reference_classifier_sidecar requires the optional vision runtime dependencies. "
            "Install them with `poetry install --with vision`."
        ) from exc

    return pipeline(
        task="zero-shot-image-classification",
        model=model_name,
        device=device_name,
    )


def _iter_reference_image_paths(payload: dict[str, Any]) -> list[str]:
    references = payload.get("references")
    if not isinstance(references, list):
        return []

    image_paths: list[str] = []
    for item in references:
        if not isinstance(item, dict):
            continue
        for key in ("image_path", "stored_path", "host_visible_path", "original_path"):
            value = str(item.get(key) or "").strip()
            if value:
                image_paths.append(value)
                break
    return image_paths


def _aggregate_label_scores(
    results: Sequence[Sequence[dict[str, Any]]],
    *,
    label_space: Sequence[tuple[str, str]],
    top_k: int,
) -> list[dict[str, Any]]:
    prompt_to_label = {prompt: label for label, prompt in label_space}
    aggregated: dict[str, list[float]] = defaultdict(list)

    for image_result in results:
        for item in image_result:
            label_prompt = str(item.get("label") or "").strip()
            score = item.get("score")
            canonical_label = prompt_to_label.get(label_prompt)
            if canonical_label is None or not isinstance(score, (int, float)):
                continue
            aggregated[canonical_label].append(float(score))

    ranked_entries = [(label, round(sum(values) / len(values), 4)) for label, values in aggregated.items() if values]
    ranked_entries.sort(key=lambda item: item[1], reverse=True)
    return [
        {
            "label": label,
            "score": score,
        }
        for label, score in ranked_entries[:top_k]
    ]


@dataclass
class ReferenceClassifierService:
    model_name: str
    device_name: str
    top_k: int
    label_space: tuple[tuple[str, str], ...] = DEFAULT_LABEL_SPACE
    _pipeline: Any | None = None

    @property
    def labels(self) -> list[str]:
        return [label for label, _prompt in self.label_space]

    @property
    def candidate_prompts(self) -> list[str]:
        return [prompt for _label, prompt in self.label_space]

    def _ensure_pipeline(self):
        if self._pipeline is None:
            self._pipeline = _build_classifier_pipeline(
                model_name=self.model_name,
                device_name=self.device_name,
            )
        return self._pipeline

    def warmup(self) -> None:
        """Load the zero-shot pipeline before the first live RU request."""

        self._ensure_pipeline()

    def classify_payload(self, payload: dict[str, Any]) -> dict[str, Any]:
        image_paths = _iter_reference_image_paths(payload)
        if not image_paths:
            raise ValueError("Payload did not include any reference image paths.")

        try:
            from PIL import Image
        except Exception as exc:  # pragma: no cover - exercised as operator dependency failure
            raise RuntimeError(
                "reference_classifier_sidecar requires Pillow. Install repo dependencies before running it."
            ) from exc

        classifier = self._ensure_pipeline()
        per_image_results: list[Sequence[dict[str, Any]]] = []
        for image_path in image_paths:
            with Image.open(image_path) as image:
                result = classifier(image, candidate_labels=self.candidate_prompts)
            if isinstance(result, dict):
                per_image_results.append([result])
            elif isinstance(result, list):
                per_image_results.append(result)
            else:
                raise RuntimeError("Classifier returned an unsupported result shape.")

        return {
            "classification_scores": _aggregate_label_scores(
                per_image_results,
                label_space=self.label_space,
                top_k=self.top_k,
            ),
            "model_name": self.model_name,
            "device_name": self.device_name,
            "label_space": self.labels,
        }


class ReferenceClassifierRequestHandler(BaseHTTPRequestHandler):
    service: ReferenceClassifierService | None = None

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
                "model_name": service.model_name,
                "device_name": service.device_name,
                "label_space": service.labels,
                "top_k": service.top_k,
            },
        )

    def do_POST(self) -> None:  # noqa: N802
        if self.path != "/classify":
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
            response_payload = service.classify_payload(payload)
        except Exception as exc:
            self._write_json(
                status=HTTPStatus.BAD_REQUEST,
                payload={"error": str(exc)},
            )
            return

        self._write_json(status=HTTPStatus.OK, payload=response_payload)

    def log_message(self, format: str, *args: object) -> None:  # noqa: A003
        return


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=9200)
    parser.add_argument("--model", default="google/siglip2-base-patch16-224")
    parser.add_argument("--device", default="auto")
    parser.add_argument("--top-k", type=int, default=5)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    service = ReferenceClassifierService(
        model_name=args.model,
        device_name=_resolve_device_name(args.device),
        top_k=args.top_k,
    )
    service.warmup()
    ReferenceClassifierRequestHandler.service = service
    server = ThreadingHTTPServer((args.host, args.port), ReferenceClassifierRequestHandler)
    print(
        json.dumps(
            {
                "status": "starting",
                "host": args.host,
                "port": args.port,
                "model_name": service.model_name,
                "device_name": service.device_name,
                "label_space": service.labels,
                "top_k": service.top_k,
                "classify_endpoint": f"http://{args.host}:{args.port}/classify",
                "health_endpoint": f"http://{args.host}:{args.port}/health",
            },
            ensure_ascii=False,
        )
    )
    server.serve_forever()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
