# Translating `_docs/` to English

This repository contains a large set of Markdown/YAML documentation files under `_docs/`.
If you want an **exact, 1:1 translation to English** (no summarization, no omissions), use the provided script:

`scripts/translate_docs.py`

The script uses the OpenAI API, so you need an API key and network access.

---

## Quick start

1) **List files that look non‑English (Polish heuristic):**

```bash
python3 scripts/translate_docs.py --root _docs --dry-run
```

2) **Translate into a parallel directory (recommended first):**

```bash
export OPENAI_API_KEY="..."
export OPENAI_MODEL="gpt-4.1-mini"   # optional

python3 scripts/translate_docs.py --root _docs --output-root _docs_en
```

If your key is stored in a `.env` file instead of exported env vars:

```bash
python3 scripts/translate_docs.py --root _docs --output-root _docs_en --env-file .env
```

If you want to use a specific model (e.g. `gpt-5-mini`) without editing your `.env`:

```bash
python3 scripts/translate_docs.py --root _docs --output-root _docs_en --env-file .env --model gpt-5-mini --api responses
```

3) **Review changes and replace if desired:**

- Compare `_docs/` vs `_docs_en/`
- Once satisfied, move/replace the translated files into `_docs/`

---

## In-place translation

If you want to overwrite files under `_docs/` directly:

```bash
export OPENAI_API_KEY="..."
python3 scripts/translate_docs.py --root _docs --in-place
```

---

## Options

- `--ext .md --ext .yaml --ext .yml` — control which extensions are included (default: `.md`, `.yaml`, `.yml`)
- `--all` — translate all matching files, even if they already look English *(not recommended, can introduce unnecessary diffs)*
- `--max-files 10` — limit scope for incremental runs
- `--max-output-tokens 16384` — increase if you hit truncated output
- `--tpm-limit 200000` — approximate throttle (tokens/min) using a heuristic estimate
- `--sleep-s 0.5` — rate limiting

---

## Validation (optional)

After translation, a quick check for Polish diacritics:

```bash
rg -n "[ąćęłńóśżź]" _docs
```
