"""raw.jsonl 의 본문을 LLM에 위임해 요약/태그/카테고리/키워드를 생성한다.

LLM provider는 config.yaml의 llm.provider로 선택:
  - ollama: 로컬 Ollama API (무료)
  - openai: OpenAI API
  - anthropic: Anthropic API

사용법:
    python scripts/summarize.py --in data/shards/0001.raw.jsonl --out data/shards/0001.jsonl
    python scripts/summarize.py ... --dry-run        # LLM 호출 없이 프롬프트만 출력
    python scripts/summarize.py ... --incremental    # 기존 결과의 source_hash와 같으면 스킵
    python scripts/summarize.py ... --limit 10       # 상위 N건만 (PoC용)
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path

import httpx

from _common import ROOT, cfg, ensure_dirs, get_logger, read_jsonl, write_jsonl

log = get_logger("summarize")

PROMPT_TEMPLATE = """당신은 한국어 블로그 요약/분류 전문가입니다.
아래 블로그 본문을 읽고 **단일 JSON 객체**만 출력하세요. 설명/주석/코드블록 금지.

JSON 스키마:
{{
  "summary": "본문을 2~4문장, 150~400자 한국어로 요약. 환각 금지. 본문 핵심 키워드 2개 이상 포함.",
  "tags": ["kebab-case", "3~7개", "중복금지"],
  "category": "한 단어 카테고리. 본문 주제에 가장 가까운 것 선택 (예: DevOps, Cloud, Kubernetes, Database, Java, Kotlin, Spring, Web, LLM, Docker, Linux, Security, Programming, Go, Flutter, Life, Tools, Networking 등). AI/머신러닝 관련일 때만 LLM 사용.",
  "keywords": ["본문 고빈도 키워드 최대 5개"]
}}

제약:
- 요약 언어: 한국어 only
- tags: kebab-case 소문자, 3~7개
- category: LLM이 새로 분류 (원본 카테고리 무시)

제목: {title}
URL: {url}
본문:
{body}
"""

JSON_BLOCK_RE = re.compile(r"\{[\s\S]*\}")


def build_prompt(rec: dict) -> str:
    max_chars = cfg("llm.max_body_chars", 6000)
    body = rec.get("content_text", "")
    if len(body) > max_chars:
        body = body[:max_chars] + "\n...(이하 생략)"
    return PROMPT_TEMPLATE.format(
        title=rec.get("title", ""),
        url=rec.get("url", ""),
        body=body,
    )


def call_llm(prompt: str) -> str:
    """config.yaml의 llm.provider에 따라 LLM을 호출한다."""
    provider = cfg("llm.provider", "ollama")

    if provider == "ollama":
        return _call_ollama(prompt)
    elif provider == "openai":
        return _call_openai(prompt)
    elif provider == "anthropic":
        return _call_anthropic(prompt)
    else:
        raise ValueError(f"Unknown LLM provider: {provider}")


def _call_ollama(prompt: str) -> str:
    url = cfg("llm.ollama_url", "http://localhost:11434/api/generate")
    model = cfg("llm.model", "qwen3:8b")
    timeout = cfg("llm.ollama_timeout", 300)
    # /no_think 접미사로 thinking 비활성화 (qwen3 등)
    prompt_with_flag = prompt + "\n/no_think"
    resp = httpx.post(
        url,
        json={"model": model, "prompt": prompt_with_flag, "stream": False},
        timeout=float(timeout),
    )
    resp.raise_for_status()
    return resp.json().get("response", "")


def _call_openai(prompt: str) -> str:
    api_key = os.environ.get("OPENAI_API_KEY", cfg("llm.openai_api_key", ""))
    model = cfg("llm.openai_model", cfg("llm.model", "gpt-4o-mini"))
    resp = httpx.post(
        "https://api.openai.com/v1/chat/completions",
        headers={"Authorization": f"Bearer {api_key}"},
        json={
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.3,
        },
        timeout=120.0,
    )
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"]


def _call_anthropic(prompt: str) -> str:
    api_key = os.environ.get("ANTHROPIC_API_KEY", cfg("llm.anthropic_api_key", ""))
    model = cfg("llm.anthropic_model", cfg("llm.model", "claude-sonnet-4-20250514"))
    resp = httpx.post(
        "https://api.anthropic.com/v1/messages",
        headers={
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
        },
        json={
            "model": model,
            "max_tokens": 1024,
            "messages": [{"role": "user", "content": prompt}],
        },
        timeout=120.0,
    )
    resp.raise_for_status()
    return resp.json()["content"][0]["text"]


def extract_json(text: str) -> dict:
    m = JSON_BLOCK_RE.search(text)
    if not m:
        raise ValueError(f"JSON block not found in: {text[:200]}")
    return json.loads(m.group(0))


def validate_llm_output(obj: dict) -> tuple[bool, str]:
    required = ["summary", "tags", "category", "keywords"]
    for key in required:
        if key not in obj:
            return False, f"missing:{key}"
    summary = obj.get("summary", "")
    if not isinstance(summary, str) or not (50 <= len(summary) <= 600):
        return False, "summary_length"
    tags = obj.get("tags", [])
    if not isinstance(tags, list) or not (3 <= len(tags) <= 7):
        return False, "tags_count"
    return True, "ok"


def merge_record(raw: dict, llm: dict) -> dict:
    provider = cfg("llm.provider", "ollama")
    model = cfg("llm.model", "unknown")
    return {
        "id": raw["id"],
        "title": raw["title"],
        "url": raw["url"],
        "published_at": raw.get("published_at"),
        "category": llm.get("category") or "uncategorized",
        "tags": llm.get("tags") or [],
        "summary": llm.get("summary") or "",
        "keywords": llm.get("keywords") or [],
        "word_count": raw.get("word_count"),
        "source_hash": raw.get("source_hash"),
        "generated_at": datetime.utcnow().isoformat(timespec="seconds") + "Z",
        "model": f"{provider}/{model}",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--in", dest="inp", required=True)
    parser.add_argument("--out", dest="out", required=True)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--incremental", action="store_true")
    parser.add_argument("--limit", type=int, default=0)
    args = parser.parse_args()

    ensure_dirs()
    inp = (ROOT / args.inp) if not Path(args.inp).is_absolute() else Path(args.inp)
    out = (ROOT / args.out) if not Path(args.out).is_absolute() else Path(args.out)

    if not inp.exists():
        log.error("입력 없음: %s", inp)
        return 2

    existing: dict[str, dict] = {}
    if args.incremental:
        for rec in read_jsonl(out):
            existing[rec["id"]] = rec

    results: list[dict] = []
    ok = fail = processed = 0
    for raw in read_jsonl(inp):
        if args.limit and processed >= args.limit:
            break
        processed += 1
        prev = existing.get(raw["id"])
        if prev and prev.get("source_hash") == raw.get("source_hash"):
            results.append(prev)
            ok += 1
            continue

        prompt = build_prompt(raw)
        if args.dry_run:
            print(f"--- PROMPT for {raw['id']} ---")
            print(prompt[:500])
            print()
            continue

        try:
            log.info("summarize id=%s (%s)", raw["id"], raw.get("title", "")[:40])
            resp = call_llm(prompt)
            llm_obj = extract_json(resp)
            valid, reason = validate_llm_output(llm_obj)
            if not valid:
                log.warning("selfcheck fail id=%s reason=%s", raw["id"], reason)
                fail += 1
                continue
            rec = merge_record(raw, llm_obj)
            results.append(rec)
            ok += 1
        except Exception as exc:
            log.warning("summarize fail id=%s: %s", raw.get("id"), exc)
            fail += 1

    if not args.dry_run:
        n = write_jsonl(out, results)
        log.info("ok=%d fail=%d written=%d -> %s", ok, fail, n, out)
    return 0 if fail == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
