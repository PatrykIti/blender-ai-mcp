#!/usr/bin/env python3
"""
Translate documents under a directory to English using the OpenAI API.

Goals:
- 1:1 translation (no summarization, no omission)
- Preserve formatting (Markdown/YAML), code blocks, identifiers, paths, etc.
- Update in-document anchor links/TOC when headings are translated (model instructed)

Usage (dry-run):
  python3 scripts/translate_docs.py --root _docs --dry-run

Usage (write translations to a parallel tree):
  export OPENAI_API_KEY="..."
  python3 scripts/translate_docs.py --root _docs --output-root _docs_en

Usage (overwrite in place):
  export OPENAI_API_KEY="..."
  python3 scripts/translate_docs.py --root _docs --in-place
"""

from __future__ import annotations

import argparse
import json
import os
import re
import socket
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Optional


POLISH_CHARS_RE = re.compile(r"[ąćęłńóśżźĄĆĘŁŃÓŚŻŹ]")
POLISH_WORD_RE = re.compile(
    r"\b("
    r"krok|kroki|spis|treści|tresc|przegląd|przeglad|"
    r"założenia|zalozenia|"
    r"najczęstsze|najczestsze|"
    r"użyj|uzyj|"
    r"wartość|wartosc|wartości|wartosci|"
    r"parametr|parametry|"
    r"stół|stol|stołu|stolu|"
    r"ławka|lawka|ławki|lawki|"
    r"nogi|nogami|"
    r"dlaczego|ponieważ|poniewaz|"
    r"wymóg|wymog"
    r")\b",
    re.IGNORECASE,
)


SYSTEM_PROMPT = """You are a professional technical translator.

Translate the provided document into English.

Hard requirements:
- Translate 1:1 (do NOT summarize, do NOT omit, do NOT add new content).
- Preserve the original structure and formatting exactly:
  - Keep headings, lists, tables, indentation, and whitespace structure.
  - Preserve fenced code blocks (``` ... ```), inline code (`...`), file paths, identifiers, CLI commands, and config keys.
  - Do not “fix” code samples; keep them syntactically valid and unchanged except for natural-language comments/strings when applicable.
- If you translate headings that are referenced by in-document links/anchors or a Table of Contents, update those links so they still point to the correct headings.

Output only the translated document. No extra commentary."""


@dataclass(frozen=True)
class OpenAIConfig:
    api_key: str
    model: str
    api: str
    endpoint: str
    temperature: float = 0.0
    timeout_s: float = 120.0
    max_output_tokens: int = 16384


def default_endpoint(api: str) -> str:
    if api == "responses":
        return "https://api.openai.com/v1/responses"
    if api == "chat":
        return "https://api.openai.com/v1/chat/completions"
    raise ValueError(f"Unknown api: {api}")


def iter_candidate_files(root: Path, exts: set[str]) -> Iterable[Path]:
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        if path.suffix.lower() not in exts:
            continue
        yield path


def looks_non_english(text: str) -> bool:
    return bool(POLISH_CHARS_RE.search(text) or POLISH_WORD_RE.search(text))


def load_env_file(path: Path) -> dict[str, str]:
    """
    Minimal .env parser:
    - KEY=VALUE (VALUE may be quoted)
    - ignores empty lines and comments (# ...)
    """
    env: dict[str, str] = {}
    if not path.exists():
        return env

    for raw_line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip("'").strip('"')
        if key:
            env[key] = value
    return env


def unwrap_full_document_code_fence(text: str) -> str:
    stripped = text.strip("\n")
    if not stripped.startswith("```"):
        return text
    lines = stripped.splitlines()
    if len(lines) < 3:
        return text
    if not lines[-1].startswith("```"):
        return text
    # unwrap only if the entire output is fenced (common model failure mode)
    return "\n".join(lines[1:-1]) + "\n"


def _extract_openai_error_code(error_detail: str) -> Optional[str]:
    try:
        parsed = json.loads(error_detail)
    except json.JSONDecodeError:
        return None
    err = parsed.get("error")
    if not isinstance(err, dict):
        return None
    code = err.get("code")
    if isinstance(code, str) and code:
        return code
    typ = err.get("type")
    if isinstance(typ, str) and typ:
        return typ
    return None


def _parse_chat_completion_text(parsed: dict) -> str:
    return parsed["choices"][0]["message"]["content"]


def _parse_responses_text(parsed: dict) -> str:
    # New Responses API (preferred): output[].content[].text
    texts: list[str] = []
    output = parsed.get("output")
    if isinstance(output, list):
        for item in output:
            if not isinstance(item, dict):
                continue
            content = item.get("content")
            if not isinstance(content, list):
                continue
            for c in content:
                if isinstance(c, dict):
                    t = c.get("text")
                    if isinstance(t, str):
                        texts.append(t)
                elif isinstance(c, str):
                    texts.append(c)

    if texts:
        return "".join(texts)

    # Some variants expose a convenience field
    output_text = parsed.get("output_text")
    if isinstance(output_text, str) and output_text:
        return output_text

    # Fallback if the endpoint returned chat-completions shape
    if "choices" in parsed:
        return _parse_chat_completion_text(parsed)

    raise KeyError("No assistant text found in OpenAI Responses payload")


def openai_translate(cfg: OpenAIConfig, source_text: str, *, max_retries: int = 3) -> str:
    if cfg.api == "responses":
        payload = {
            "model": cfg.model,
            "max_output_tokens": cfg.max_output_tokens,
            "input": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": source_text},
            ],
        }
    elif cfg.api == "chat":
        payload = {
            "model": cfg.model,
            "temperature": cfg.temperature,
            "max_tokens": cfg.max_output_tokens,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": source_text},
            ],
        }
    else:
        raise ValueError(f"Unsupported api: {cfg.api}")

    data = json.dumps(payload).encode("utf-8")
    headers = {
        "Authorization": f"Bearer {cfg.api_key}",
        "Content-Type": "application/json",
    }

    retryable_statuses = {429, 500, 502, 503, 504}
    attempt = 0
    while True:
        attempt += 1
        req = urllib.request.Request(cfg.endpoint, data=data, method="POST", headers=headers)
        try:
            with urllib.request.urlopen(req, timeout=cfg.timeout_s) as resp:
                body = resp.read().decode("utf-8")
            break
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="ignore")
            # Non-retryable: project/account has no quota.
            if _extract_openai_error_code(detail) == "insufficient_quota":
                raise RuntimeError(f"OpenAI HTTPError {exc.code}: {detail}") from exc
            if exc.code in retryable_statuses and attempt <= max_retries:
                time.sleep(min(10.0, 0.8 * (2 ** (attempt - 1))))
                continue
            raise RuntimeError(f"OpenAI HTTPError {exc.code}: {detail}") from exc
        except urllib.error.URLError as exc:
            if attempt <= max_retries:
                time.sleep(min(10.0, 0.8 * (2 ** (attempt - 1))))
                continue
            raise RuntimeError(f"OpenAI URLError: {exc}") from exc
        except socket.timeout as exc:
            if attempt <= max_retries:
                time.sleep(min(10.0, 0.8 * (2 ** (attempt - 1))))
                continue
            raise RuntimeError(f"OpenAI socket timeout after {cfg.timeout_s}s") from exc

    parsed = json.loads(body)
    try:
        if cfg.api == "responses":
            content = _parse_responses_text(parsed)
        else:
            content = _parse_chat_completion_text(parsed)
    except (KeyError, IndexError, TypeError) as exc:
        raise RuntimeError(f"Unexpected OpenAI response shape: {parsed}") from exc

    if cfg.api == "chat":
        finish_reason = parsed.get("choices", [{}])[0].get("finish_reason")
        if finish_reason == "length":
            raise RuntimeError(
                "OpenAI output was truncated (finish_reason='length'). "
                "Re-run with a higher --max-output-tokens or a larger model."
            )
    else:
        status = parsed.get("status")
        incomplete = parsed.get("incomplete_details")
        if status == "incomplete" or (isinstance(incomplete, dict) and incomplete.get("reason") == "max_output_tokens"):
            raise RuntimeError(
                "OpenAI output was truncated (Responses API). "
                "Re-run with a higher --max-output-tokens or a larger model."
            )

    content = unwrap_full_document_code_fence(content)
    if not content.endswith("\n"):
        content += "\n"
    return content


def ensure_parent_dir(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def estimate_tokens(text: str, token_per_char: float) -> int:
    # Rough heuristic: ~4 chars per token for many Latin texts.
    return int(len(text) * token_per_char)


def estimate_total_tokens(source_text: str, *, token_per_char: float, max_output_tokens: int) -> int:
    """
    Heuristic for TPM throttling.
    - input tokens ~= chars * factor
    - output tokens ~= ~1.3x input tokens (translation can expand a bit), capped by max_output_tokens
    """
    input_tokens = estimate_tokens(source_text, token_per_char)
    output_tokens = min(max_output_tokens, int(input_tokens * 1.3) + 256)
    return input_tokens + output_tokens


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Translate _docs to English via OpenAI API")
    parser.add_argument("--root", type=Path, default=Path("_docs"))
    parser.add_argument("--output-root", type=Path, default=Path("_docs_en"))
    parser.add_argument("--in-place", action="store_true", help="Overwrite files under --root")
    parser.add_argument("--all", action="store_true", help="Translate all matching files, even if they look English")
    parser.add_argument(
        "--ext",
        action="append",
        default=[".md", ".yaml", ".yml"],
        help="File extension to include (repeatable)",
    )
    parser.add_argument("--model", default=None, help="OpenAI model (overrides OPENAI_MODEL/.env)")
    parser.add_argument(
        "--api",
        choices=["responses", "chat"],
        default=None,
        help="OpenAI API style: responses (recommended) or chat (legacy)",
    )
    parser.add_argument(
        "--endpoint",
        default=None,
        help="Override the OpenAI endpoint URL (advanced)",
    )
    parser.add_argument(
        "--max-output-tokens",
        type=int,
        default=None,
        help="max_tokens for the completion (larger docs may need more)",
    )
    parser.add_argument(
        "--timeout-s",
        type=float,
        default=None,
        help="HTTP timeout per request (seconds). Can also be set via OPENAI_TIMEOUT_S.",
    )
    parser.add_argument("--env-file", type=Path, default=Path(".env"), help="Optional .env file to read OPENAI_* from")
    parser.add_argument("--dry-run", action="store_true", help="List candidate files and exit")
    parser.add_argument(
        "--skip-existing",
        action="store_true",
        help="When using --output-root, skip files that already exist (useful for resume)",
    )
    parser.add_argument("--max-files", type=int, default=0, help="Limit number of files (0 = no limit)")
    parser.add_argument("--sleep-s", type=float, default=0.0, help="Sleep between requests (rate limiting)")
    parser.add_argument(
        "--tpm-limit",
        type=int,
        default=0,
        help="Approximate tokens-per-minute limit (0 = disabled). Uses a heuristic estimate.",
    )
    parser.add_argument(
        "--token-per-char",
        type=float,
        default=0.25,
        help="Token estimation factor (tokens ~= chars * factor). Default 0.25 (~4 chars/token).",
    )

    args = parser.parse_args(argv)

    exts = {e.lower() if e.startswith(".") else f".{e.lower()}" for e in args.ext}

    root: Path = args.root
    if not root.exists():
        raise SystemExit(f"Root directory does not exist: {root}")

    all_files = sorted(iter_candidate_files(root, exts))
    needs_translation: dict[Path, bool] = {}
    for path in all_files:
        text = path.read_text(encoding="utf-8", errors="ignore")
        needs_translation[path] = bool(args.all or looks_non_english(text))

    translate_files = [p for p in all_files if needs_translation[p]]
    if args.max_files and len(translate_files) > args.max_files:
        # Limit translation requests; still mirror/copy the rest when using --output-root.
        limited_set = set(translate_files[: args.max_files])
        for p in translate_files[args.max_files :]:
            needs_translation[p] = False
        translate_files = [p for p in all_files if needs_translation[p]]

    if args.dry_run:
        for path in translate_files:
            print(path.as_posix())
        print(f"Translate: {len(translate_files)} / Total: {len(all_files)}")
        return 0

    env_fallback = load_env_file(args.env_file)
    api_key = os.environ.get("OPENAI_API_KEY", "").strip() or env_fallback.get("OPENAI_API_KEY", "").strip()
    if not api_key:
        raise SystemExit("Missing OPENAI_API_KEY env var")

    api = os.environ.get("OPENAI_API", "").strip() or env_fallback.get("OPENAI_API", "").strip() or "responses"
    endpoint = (
        os.environ.get("OPENAI_ENDPOINT", "").strip()
        or env_fallback.get("OPENAI_ENDPOINT", "").strip()
        or default_endpoint(api)
    )
    model = os.environ.get("OPENAI_MODEL", "").strip() or env_fallback.get("OPENAI_MODEL", "").strip() or "gpt-4.1-mini"
    max_output_tokens = int(os.environ.get("OPENAI_MAX_TOKENS", "").strip() or env_fallback.get("OPENAI_MAX_TOKENS", "").strip() or "16384")
    timeout_s = float(os.environ.get("OPENAI_TIMEOUT_S", "").strip() or env_fallback.get("OPENAI_TIMEOUT_S", "").strip() or "120")

    # CLI overrides (highest priority)
    if args.api:
        api = args.api
        if not (args.endpoint or os.environ.get("OPENAI_ENDPOINT") or env_fallback.get("OPENAI_ENDPOINT")):
            endpoint = default_endpoint(api)
    if args.endpoint:
        endpoint = args.endpoint
    if args.model:
        model = args.model
    if args.max_output_tokens is not None:
        max_output_tokens = args.max_output_tokens
    if args.timeout_s is not None:
        timeout_s = args.timeout_s

    cfg = OpenAIConfig(
        api_key=api_key,
        model=model,
        api=api,
        endpoint=endpoint,
        max_output_tokens=max_output_tokens,
        timeout_s=timeout_s,
    )

    processed = 0
    translated_count = 0
    window_start = time.time()
    window_tokens_est = 0
    for src_path in all_files:
        processed += 1
        if args.in_place:
            dst_path = src_path
        else:
            rel = src_path.relative_to(root)
            dst_path = args.output_root / rel
            ensure_parent_dir(dst_path)
            if args.skip_existing and dst_path.exists():
                print(f"[{processed}/{len(all_files)}] skipped    -> {dst_path.as_posix()}")
                continue

        source = src_path.read_text(encoding="utf-8", errors="ignore")
        if needs_translation[src_path]:
            if args.tpm_limit > 0:
                est = estimate_total_tokens(
                    source,
                    token_per_char=args.token_per_char,
                    max_output_tokens=cfg.max_output_tokens,
                )
                now = time.time()
                if now - window_start >= 60.0:
                    window_start = now
                    window_tokens_est = 0
                if window_tokens_est + est > args.tpm_limit:
                    sleep_for = max(0.0, 60.0 - (now - window_start)) + 0.25
                    time.sleep(sleep_for)
                    window_start = time.time()
                    window_tokens_est = 0
                window_tokens_est += est

            try:
                translated = openai_translate(cfg, source)
            except Exception as exc:
                print(f"[{processed}/{len(all_files)}] ERROR translating {src_path.as_posix()}: {exc}")
                raise
            dst_path.write_text(translated, encoding="utf-8")
            translated_count += 1
            print(f"[{processed}/{len(all_files)}] translated -> {dst_path.as_posix()}")
            if args.sleep_s > 0:
                time.sleep(args.sleep_s)
        else:
            if not args.in_place:
                dst_path.write_text(source if source.endswith("\n") else (source + "\n"), encoding="utf-8")
            print(f"[{processed}/{len(all_files)}] copied     -> {dst_path.as_posix()}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
