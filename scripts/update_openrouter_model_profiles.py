#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2024-2026 Patryk Ciechański
# SPDX-License-Identifier: Apache-2.0

"""Generate candidate OpenRouter model-capability profiles from the model catalog.

This script is intentionally a candidate generator. Its output should be
reviewed before entries are promoted into runtime fallback modules such as
`server/adapters/mcp/vision/model_profiles/openrouter_openai.py`.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.request
from datetime import date
from pathlib import Path
from typing import Any

DEFAULT_MODELS_URL = "https://openrouter.ai/api/v1/models"
DEFAULT_OUTPUT = Path("server/adapters/mcp/vision/model_profiles/openrouter_candidates.py")
REVIEW_NOTE = "Generated candidate from OpenRouter catalog; review before runtime fallback promotion."


def _fetch_catalog(url: str) -> dict[str, Any]:
    with urllib.request.urlopen(url, timeout=30) as response:  # noqa: S310 - operator-invoked trusted catalog URL
        return json.loads(response.read().decode("utf-8"))


def _load_catalog(*, catalog_json: Path | None, url: str) -> dict[str, Any]:
    if catalog_json is not None:
        return json.loads(catalog_json.read_text(encoding="utf-8"))
    return _fetch_catalog(url)


def _model_provider(model_id: str) -> str:
    return model_id.split("/", 1)[0].strip().lower()


def _family_name(model_id: str) -> str:
    provider = _model_provider(model_id)
    remainder = model_id.split("/", 1)[1] if "/" in model_id else model_id
    cleaned = re.sub(r"[^a-z0-9]+", "_", remainder.lower()).strip("_")
    if provider == "openai" and cleaned.startswith("gpt_"):
        parts = cleaned.split("_")
        return "_".join(["openai", *parts[:3]]).strip("_")
    return f"{provider}_{cleaned.split('_')[0]}".strip("_")


def _modalities(model: dict[str, Any], field: str) -> tuple[str, ...]:
    raw_architecture = model.get("architecture")
    architecture = raw_architecture if isinstance(raw_architecture, dict) else {}
    values = architecture.get(field)
    if not isinstance(values, list):
        return ()
    return tuple(sorted({str(value).strip().lower() for value in values if str(value).strip()}))


def _supported_parameters(model: dict[str, Any]) -> tuple[str, ...]:
    values = model.get("supported_parameters")
    if not isinstance(values, list):
        return ()
    return tuple(sorted({str(value).strip() for value in values if str(value).strip()}))


def _top_provider_max_completion_tokens(model: dict[str, Any]) -> int | None:
    raw_top_provider = model.get("top_provider")
    top_provider = raw_top_provider if isinstance(raw_top_provider, dict) else {}
    raw_value = top_provider.get("max_completion_tokens")
    return int(raw_value) if isinstance(raw_value, int) and raw_value > 0 else None


def _context_length(model: dict[str, Any]) -> int | None:
    raw_value = model.get("context_length")
    return int(raw_value) if isinstance(raw_value, int) and raw_value > 0 else None


def _is_vision_compare_candidate(model: dict[str, Any]) -> bool:
    return "image" in _modalities(model, "input_modalities") and "text" in _modalities(model, "output_modalities")


def _is_openai_gpt(model: dict[str, Any]) -> bool:
    return str(model.get("id") or "").lower().startswith("openai/gpt-")


def _preferred_contract_profile(model: dict[str, Any]) -> str | None:
    provider = _model_provider(str(model.get("id") or ""))
    if provider in {"openai", "anthropic", "google"}:
        return "google_family_compare"
    return None


def _preferred_stage_max_tokens(max_completion_tokens: int | None) -> int | None:
    if max_completion_tokens is None:
        return None
    return min(max_completion_tokens, 4096)


def _profile_entry(model: dict[str, Any], *, reviewed_on: str) -> dict[str, Any]:
    model_id = str(model.get("id") or "").strip()
    max_completion_tokens = _top_provider_max_completion_tokens(model)
    return {
        "model_id": model_id,
        "provider": "openrouter",
        "family": _family_name(model_id),
        "context_length": _context_length(model),
        "max_completion_tokens": max_completion_tokens,
        "input_modalities": _modalities(model, "input_modalities"),
        "output_modalities": _modalities(model, "output_modalities"),
        "supported_parameters": _supported_parameters(model),
        "preferred_contract_profile": _preferred_contract_profile(model),
        "preferred_stage_max_tokens": _preferred_stage_max_tokens(max_completion_tokens),
        "docs_url": f"https://openrouter.ai/{model_id}",
        "last_reviewed": reviewed_on,
        "notes": REVIEW_NOTE,
    }


def select_candidate_profiles(
    catalog: dict[str, Any],
    *,
    top_n: int,
    include_all_openai_gpt: bool,
    vision_only: bool,
    reviewed_on: str,
) -> list[dict[str, Any]]:
    models = catalog.get("data")
    if not isinstance(models, list):
        raise ValueError("OpenRouter catalog JSON must contain a list under `data`.")

    selected: list[dict[str, Any]] = []
    seen_ids: set[str] = set()

    for model in models:
        if not isinstance(model, dict):
            continue
        model_id = str(model.get("id") or "").strip()
        if not model_id:
            continue
        if vision_only and not _is_vision_compare_candidate(model):
            continue
        if len(selected) < top_n:
            selected.append(model)
            seen_ids.add(model_id)
            continue
        if include_all_openai_gpt and _is_openai_gpt(model) and model_id not in seen_ids:
            selected.append(model)
            seen_ids.add(model_id)

    return [_profile_entry(model, reviewed_on=reviewed_on) for model in selected]


def render_python_module(profiles: list[dict[str, Any]]) -> str:
    lines = [
        "# SPDX-FileCopyrightText: 2024-2026 Patryk Ciechański",
        "# SPDX-License-Identifier: Apache-2.0",
        "",
        '"""Generated candidate OpenRouter model profiles. Review before runtime use."""',
        "",
        "from __future__ import annotations",
        "",
        "from .types import ModelCapabilityProfile",
        "",
        "GENERATED_OPENROUTER_CANDIDATE_PROFILES: tuple[ModelCapabilityProfile, ...] = (",
    ]
    for profile in profiles:
        lines.extend(
            [
                "    ModelCapabilityProfile(",
                f"        model_id={profile['model_id']!r},",
                "        provider='openrouter',",
                f"        family={profile['family']!r},",
                f"        context_length={profile['context_length']!r},",
                f"        max_completion_tokens={profile['max_completion_tokens']!r},",
                f"        input_modalities={profile['input_modalities']!r},",
                f"        output_modalities={profile['output_modalities']!r},",
                f"        supported_parameters={profile['supported_parameters']!r},",
                f"        preferred_contract_profile={profile['preferred_contract_profile']!r},",
                f"        preferred_stage_max_tokens={profile['preferred_stage_max_tokens']!r},",
                f"        docs_url={profile['docs_url']!r},",
                f"        last_reviewed={profile['last_reviewed']!r},",
                f"        notes={profile['notes']!r},",
                "    ),",
            ]
        )
    lines.append(")")
    lines.append("")
    return "\n".join(lines)


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--catalog-json", type=Path, help="Read an existing OpenRouter model catalog JSON file.")
    parser.add_argument("--url", default=DEFAULT_MODELS_URL, help="OpenRouter models API URL.")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT, help="Output Python candidate module path.")
    parser.add_argument("--top-n", type=int, default=100, help="Number of catalog-order vision models to include.")
    parser.add_argument("--reviewed-on", default=date.today().isoformat(), help="Review date written into profiles.")
    parser.add_argument("--all-modalities", action="store_true", help="Include non-image models too.")
    parser.add_argument(
        "--no-include-all-openai-gpt",
        action="store_true",
        help="Do not force-include all openai/gpt-* models beyond --top-n.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_arg_parser().parse_args(argv)
    catalog = _load_catalog(catalog_json=args.catalog_json, url=args.url)
    profiles = select_candidate_profiles(
        catalog,
        top_n=args.top_n,
        include_all_openai_gpt=not args.no_include_all_openai_gpt,
        vision_only=not args.all_modalities,
        reviewed_on=args.reviewed_on,
    )
    rendered = render_python_module(profiles)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(rendered, encoding="utf-8")
    print(f"Wrote {len(profiles)} OpenRouter candidate profiles to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
