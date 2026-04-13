"""Concept/Entity 페이지 LLM 생성. wiki 파이프라인 Step 4.

LLM provider는 config.yaml의 llm 섹션에서 설정.
포스트 전문이 아닌 요약+태그+키워드만 전달하여 토큰 84% 절감.

사용법:
    python scripts/wiki_generate.py
    python scripts/wiki_generate.py --moc DevOps
    python scripts/wiki_generate.py --dry-run
"""
from __future__ import annotations

import argparse
import json
import re
import time
from collections import defaultdict
from pathlib import Path

import httpx

from _common import ROOT, DATA_DIR, cfg, get_logger, wiki_dir

log = get_logger("wiki_generate")


def load_posts_by_moc(jsonl_path: Path) -> dict[str, list[dict]]:
    groups: dict[str, list[dict]] = defaultdict(list)
    with jsonl_path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rec = json.loads(line)
                groups[rec.get("moc", "unknown")].append(rec)
    return dict(groups)


def post_metadata_block(posts: list[dict]) -> str:
    lines = []
    for p in posts:
        pid = p.get("id", "")
        title = p.get("title", "")
        summary = p.get("summary", "")
        tags = ", ".join(p.get("tags", [])[:5])
        keywords = ", ".join(p.get("keywords", [])[:5])
        lines.append(f"[{pid}] {title}\n  요약: {summary}\n  태그: {tags}\n  키워드: {keywords}")
    return "\n\n".join(lines)


def build_concept_prompt(moc_name: str, posts: list[dict]) -> str:
    metadata = post_metadata_block(posts)
    return f"""당신은 개발자의 블로그 포스트를 분석하여 지식 위키의 "개념 페이지"를 생성하는 전문가입니다.

아래는 [{moc_name}] 카테고리에 속한 {len(posts)}개 포스트의 요약/태그/키워드입니다.

{metadata}

## 지시사항

1. 위 포스트들에서 **공통 주제/패턴**을 식별하여 3~8개의 "개념(concept)"을 추출하세요.
2. 각 개념에 대해 아래 JSON 배열 형식으로 출력하세요.

```json
[
  {{
    "slug": "kebab-case-영문-이름",
    "title": "한국어 개념 제목",
    "definition": "한 줄 정의 (1~2문장)",
    "content": "핵심 내용 설명 (3~5문장, 마크다운 가능)",
    "experience": "블로그 저자가 이 주제에서 경험한 것 요약 (2~3문장)",
    "related_posts": ["포스트ID1", "포스트ID2"],
    "related_concepts": ["관련-개념-slug1"],
    "confidence": "high|medium|low"
  }}
]
```

규칙:
- slug는 영문 kebab-case
- related_posts는 위 포스트 목록의 [ID] 값
- confidence: 관련 포스트 5개 이상이면 high, 3~4개면 medium, 1~2개면 low
- 한국어로 작성
- JSON만 출력, 다른 텍스트 없이
/no_think"""


def build_entity_prompt(moc_name: str, posts: list[dict]) -> str:
    tech_count: dict[str, int] = defaultdict(int)
    for p in posts:
        for t in p.get("tags", []):
            tech_count[t] += 1
        for k in p.get("keywords", []):
            tech_count[k] += 1

    frequent = sorted(
        [(t, c) for t, c in tech_count.items() if c >= 3],
        key=lambda x: -x[1]
    )[:20]

    if not frequent:
        return ""

    freq_str = "\n".join(f"- {t} ({c}회)" for t, c in frequent)
    metadata = post_metadata_block(posts[:30])

    return f"""당신은 개발자의 블로그에서 자주 언급되는 기술/도구를 "엔티티 페이지"로 정리하는 전문가입니다.

카테고리: [{moc_name}]
자주 등장하는 기술/도구:
{freq_str}

관련 포스트 (상위 30건):
{metadata}

## 지시사항

위 기술/도구 중 **독립 페이지로 만들 가치가 있는 것**을 3~6개 선정하여 JSON 배열로 출력하세요.

```json
[
  {{
    "slug": "기술명-영문-kebab",
    "title": "기술명",
    "category": "tool|framework|platform|language",
    "definition": "한 줄 정의",
    "usage_context": "블로그 저자가 이 기술을 어떤 맥락에서 사용했는지 (2~3문장)",
    "related_posts": ["포스트ID1", "포스트ID2"],
    "related_concepts": ["관련-개념-slug"],
    "confidence": "high|medium|low"
  }}
]
```

규칙:
- 너무 일반적인 것(예: devops, programming) 제외
- 구체적 기술/도구만 (예: Docker, Jenkins, Terraform)
- 한국어로 작성
- JSON만 출력
/no_think"""


def call_llm(prompt: str) -> str:
    """config 기반 LLM 호출."""
    provider = cfg("llm.provider", "ollama")

    if provider == "ollama":
        url = cfg("llm.ollama_url", "http://localhost:11434/api/generate")
        model = cfg("llm.model", "qwen3:8b")
        timeout = cfg("llm.ollama_timeout", 300)
        resp = httpx.post(
            url,
            json={"model": model, "prompt": prompt, "stream": False},
            timeout=float(timeout),
        )
        resp.raise_for_status()
        return resp.json().get("response", "")
    elif provider == "openai":
        import os
        api_key = os.environ.get("OPENAI_API_KEY", cfg("llm.openai_api_key", ""))
        model = cfg("llm.openai_model", cfg("llm.model"))
        resp = httpx.post(
            "https://api.openai.com/v1/chat/completions",
            headers={"Authorization": f"Bearer {api_key}"},
            json={"model": model, "messages": [{"role": "user", "content": prompt}], "temperature": 0.3},
            timeout=120.0,
        )
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"]
    else:
        raise ValueError(f"Unknown provider: {provider}")


def extract_json_array(text: str) -> list[dict]:
    m = re.search(r"```(?:json)?\s*(\[[\s\S]*?\])\s*```", text)
    if m:
        return json.loads(m.group(1))
    m = re.search(r"\[[\s\S]*\]", text)
    if m:
        return json.loads(m.group(0))
    raise ValueError(f"JSON array not found in: {text[:300]}")


def write_concept_page(concept: dict, moc_name: str, out_dir: Path) -> Path:
    slug = concept["slug"]
    path = out_dir / f"{slug}.md"
    posts_refs = "\n".join(f"- [[{pid}]]" for pid in concept.get("related_posts", []))
    related = "\n".join(f"- [[{r}]]" for r in concept.get("related_concepts", []))

    content = f"""---
type: concept
title: "{concept['title']}"
parent: "[[MOC-{moc_name}]]"
related: [{', '.join(f'"[[{r}]]"' for r in concept.get("related_concepts", []))}]
tags: [{moc_name.lower()}, concept]
confidence: {concept.get('confidence', 'medium')}
post_count: {len(concept.get('related_posts', []))}
---

# {concept['title']}

## 한 줄 정의
> {concept.get('definition', '')}

## 핵심 개념
{concept.get('content', '')}

## 내가 경험한 것
{concept.get('experience', '')}

## 관련 포스트
{posts_refs}

## 관련 개념
{related}
"""
    path.write_text(content, encoding="utf-8")
    return path


def write_entity_page(entity: dict, moc_name: str, out_dir: Path) -> Path:
    slug = entity["slug"]
    path = out_dir / f"{slug}.md"
    posts_refs = "\n".join(f"- [[{pid}]]" for pid in entity.get("related_posts", []))
    related = "\n".join(f"- [[{r}]]" for r in entity.get("related_concepts", []))

    content = f"""---
type: entity
title: "{entity['title']}"
parent: "[[MOC-{moc_name}]]"
category: {entity.get('category', 'tool')}
related: [{', '.join(f'"[[{r}]]"' for r in entity.get("related_concepts", []))}]
tags: [{moc_name.lower()}, entity]
confidence: {entity.get('confidence', 'medium')}
post_count: {len(entity.get('related_posts', []))}
---

# {entity['title']}

## 한 줄 정의
> {entity.get('definition', '')}

## 내가 사용한 맥락
{entity.get('usage_context', '')}

## 관련 포스트
{posts_refs}

## 관련 개념
{related}
"""
    path.write_text(content, encoding="utf-8")
    return path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--in", dest="inp", default=str(DATA_DIR / "posts_wiki.jsonl"))
    parser.add_argument("--moc", help="단일 MOC만 처리")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    concepts_dir = wiki_dir() / "concepts"
    entities_dir = wiki_dir() / "entities"
    concepts_dir.mkdir(parents=True, exist_ok=True)
    entities_dir.mkdir(parents=True, exist_ok=True)

    max_batch = cfg("batch.max_posts_per_batch", 60)
    groups = load_posts_by_moc(Path(args.inp))
    if args.moc:
        if args.moc not in groups:
            log.error("MOC '%s' 없음. 가능: %s", args.moc, list(groups.keys()))
            return
        groups = {args.moc: groups[args.moc]}

    log.info("대상 MOC %d개, 총 %d 포스트", len(groups), sum(len(v) for v in groups.values()))

    total_concepts = total_entities = 0
    errors = []

    for moc_name, posts in sorted(groups.items()):
        log.info("=== MOC: %s (%d posts) ===", moc_name, len(posts))

        # Concept 생성 (배치 분할)
        batches = [posts[i:i + max_batch] for i in range(0, len(posts), max_batch)]
        for bi, batch in enumerate(batches):
            prompt = build_concept_prompt(moc_name, batch)
            if args.dry_run:
                log.info("Concept prompt batch %d (%d chars)", bi, len(prompt))
                continue
            try:
                log.info("  Concept batch %d/%d (%d posts)...", bi + 1, len(batches), len(batch))
                t0 = time.time()
                response = call_llm(prompt)
                concepts = extract_json_array(response)
                log.info("  %d concepts (%.1fs)", len(concepts), time.time() - t0)
                for c in concepts:
                    if not c.get("slug"):
                        continue
                    write_concept_page(c, moc_name, concepts_dir)
                    total_concepts += 1
            except Exception as e:
                log.error("  Concept batch %d failed: %s", bi + 1, e)
                errors.append(f"concept/{moc_name}/batch{bi + 1}: {e}")

        # Entity 생성
        entity_prompt = build_entity_prompt(moc_name, posts)
        if not entity_prompt:
            continue
        if args.dry_run:
            continue
        try:
            log.info("  Entity 생성 중...")
            t0 = time.time()
            response = call_llm(entity_prompt)
            entities = extract_json_array(response)
            log.info("  %d entities (%.1fs)", len(entities), time.time() - t0)
            for e in entities:
                write_entity_page(e, moc_name, entities_dir)
                total_entities += 1
        except Exception as e:
            log.error("  Entity failed: %s", e)
            errors.append(f"entity/{moc_name}: {e}")

    log.info("완료: Concepts=%d, Entities=%d, Errors=%d", total_concepts, total_entities, len(errors))


if __name__ == "__main__":
    main()
