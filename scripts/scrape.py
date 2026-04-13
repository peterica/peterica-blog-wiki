"""단일 shard를 스크래핑하여 raw JSONL을 생성한다.

CSS 셀렉터는 config.yaml에서 읽으며, 다중 셀렉터 폴백을 지원한다.

사용법:
    python scripts/scrape.py --in data/shards/0001.txt --out data/shards/0001.raw.jsonl
    python scripts/scrape.py --in data/shards/0001.txt --out data/shards/0001.raw.jsonl --incremental
"""
from __future__ import annotations

import argparse
import sys
from datetime import datetime
from pathlib import Path

from selectolax.parser import HTMLParser

from _common import (
    ROOT, cfg, ensure_dirs, extract_post_id, fetch, get_logger,
    http_client, RateLimiter, read_jsonl, sha256_hex, write_jsonl,
)

log = get_logger("scrape")


def _first_text(tree: HTMLParser, selectors: list[str], attr: str | None = None) -> str | None:
    for sel in selectors:
        node = tree.css_first(sel)
        if not node:
            continue
        if attr:
            val = node.attributes.get(attr)
        elif sel.startswith("meta"):
            val = node.attributes.get("content")
        elif "time" in sel:
            val = node.attributes.get("datetime") or node.text(strip=True)
        else:
            val = node.text(strip=True)
        if val:
            return val
    return None


def _extract_body(tree: HTMLParser) -> str:
    selectors = cfg("scrape.selectors.body", ["article", "#content"])
    for sel in selectors:
        node = tree.css_first(sel)
        if node:
            text = node.text(separator="\n", strip=True)
            if len(text) >= 50:
                return text
    body = tree.css_first("body")
    return body.text(separator="\n", strip=True) if body else ""


def _normalize_date(raw: str | None) -> str | None:
    if not raw:
        return None
    raw = raw.strip()
    for fmt in ("%Y-%m-%dT%H:%M:%S%z", "%Y-%m-%dT%H:%M:%S",
                "%Y-%m-%d %H:%M:%S", "%Y-%m-%d", "%Y.%m.%d", "%Y.%m.%d %H:%M"):
        try:
            dt = datetime.strptime(raw[:len(raw)], fmt)
            return dt.date().isoformat()
        except ValueError:
            continue
    if len(raw) >= 10 and raw[4] == "-" and raw[7] == "-":
        return raw[:10]
    return None


def parse_post(url: str, html: str) -> dict | None:
    post_id = extract_post_id(url)
    if not post_id:
        return None
    tree = HTMLParser(html)
    title_sels = cfg("scrape.selectors.title", ["h1"])
    date_sels = cfg("scrape.selectors.date", ["time[datetime]"])
    cat_sels = cfg("scrape.selectors.category", [".category"])

    title = _first_text(tree, title_sels) or ""
    date_raw = _first_text(tree, date_sels)
    published_at = _normalize_date(date_raw)
    body = _extract_body(tree)
    category_raw = _first_text(tree, cat_sels)
    word_count = len(body.split())

    if not title or word_count < 10:
        return None

    return {
        "id": post_id,
        "title": title.strip(),
        "url": url,
        "published_at": published_at,
        "category_raw": category_raw,
        "content_text": body,
        "word_count": word_count,
        "source_hash": sha256_hex(body),
        "scraped_at": datetime.utcnow().isoformat(timespec="seconds") + "Z",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--in", dest="inp", required=True, help="shard .txt 경로")
    parser.add_argument("--out", dest="out", required=True, help="raw.jsonl 출력 경로")
    parser.add_argument("--incremental", action="store_true")
    args = parser.parse_args()

    ensure_dirs()
    inp = (ROOT / args.inp) if not Path(args.inp).is_absolute() else Path(args.inp)
    out = (ROOT / args.out) if not Path(args.out).is_absolute() else Path(args.out)

    if not inp.exists():
        log.error("shard 파일 없음: %s", inp)
        return 2

    urls = [u.strip() for u in inp.read_text(encoding="utf-8").splitlines() if u.strip()]
    existing: dict[str, dict] = {}
    if args.incremental:
        for rec in read_jsonl(out):
            existing[rec["id"]] = rec

    limiter = RateLimiter()
    out_records: list[dict] = []
    fail_count = 0

    with http_client() as client:
        for url in urls:
            post_id = extract_post_id(url)
            if not post_id:
                fail_count += 1
                continue
            try:
                resp = fetch(client, url, limiter)
            except Exception as exc:
                log.warning("fetch fail %s: %s", url, exc)
                fail_count += 1
                continue
            rec = parse_post(url, resp.text)
            if rec is None:
                fail_count += 1
                log.warning("parse fail %s", url)
                continue
            prev = existing.get(post_id)
            if prev and prev.get("source_hash") == rec["source_hash"]:
                out_records.append(prev)
            else:
                out_records.append(rec)

    n = write_jsonl(out, out_records)
    log.info("shard %s: ok=%d fail=%d -> %s", inp.stem, n, fail_count, out)
    return 0 if fail_count / max(len(urls), 1) < 0.05 else 1


if __name__ == "__main__":
    sys.exit(main())
