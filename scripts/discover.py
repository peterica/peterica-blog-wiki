"""블로그의 전체 게시글 URL을 수집한다.

전략 (config.yaml blog.platform 기반):
1. sitemap.xml 우선 파싱
2. 실패 시 archive 페이지 순회 폴백

사용법:
    python scripts/discover.py
    python scripts/discover.py --incremental
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path
from xml.etree import ElementTree as ET

from selectolax.parser import HTMLParser

from _common import (
    ROOT, DATA_DIR, cfg, ensure_dirs, extract_post_id,
    fetch, get_logger, http_client, RateLimiter,
)

log = get_logger("discover")


def _parse_sitemap(xml_text: str) -> list[str]:
    """sitemap.xml 에서 포스트 URL만 추출."""
    urls: list[str] = []
    try:
        root = ET.fromstring(xml_text)
    except ET.ParseError:
        return []
    ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    for loc in root.findall(".//sm:url/sm:loc", ns):
        if loc.text and extract_post_id(loc.text):
            urls.append(loc.text.strip())
    return urls


def _parse_archive_page(html: str) -> list[str]:
    blog_base = cfg("blog.url")
    tree = HTMLParser(html)
    found: set[str] = set()
    for a in tree.css("a[href]"):
        href = a.attributes.get("href", "")
        if not href:
            continue
        if href.startswith("/"):
            candidate = blog_base + href.split("?")[0].split("#")[0]
        elif href.startswith(blog_base):
            candidate = href.split("?")[0].split("#")[0]
        else:
            continue
        if extract_post_id(candidate):
            found.add(candidate)
    return sorted(found)


def discover_via_sitemap(limiter: RateLimiter) -> list[str]:
    blog_base = cfg("blog.url")
    sitemap_url = f"{blog_base}/sitemap.xml"
    with http_client() as client:
        try:
            resp = fetch(client, sitemap_url, limiter)
        except Exception as exc:
            log.warning("sitemap fetch failed: %s", exc)
            return []
        return _parse_sitemap(resp.text)


def discover_via_archive(limiter: RateLimiter, max_pages: int = 200) -> list[str]:
    blog_base = cfg("blog.url")
    collected: set[str] = set()
    empty_streak = 0
    with http_client() as client:
        for page in range(1, max_pages + 1):
            url = f"{blog_base}/?page={page}"
            try:
                resp = fetch(client, url, limiter)
            except Exception as exc:
                log.warning("archive page %d failed: %s", page, exc)
                empty_streak += 1
                if empty_streak >= 3:
                    break
                continue
            page_urls = _parse_archive_page(resp.text)
            new = [u for u in page_urls if u not in collected]
            if not new:
                empty_streak += 1
                if empty_streak >= 3:
                    log.info("archive exhausted at page %d", page)
                    break
            else:
                empty_streak = 0
                collected.update(new)
                log.info("page %d: +%d (total %d)", page, len(new), len(collected))
    return sorted(collected, key=lambda u: int(extract_post_id(u) or 0))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", default="data/urls.txt")
    parser.add_argument("--incremental", action="store_true")
    parser.add_argument("--max-pages", type=int, default=200)
    args = parser.parse_args()

    ensure_dirs()
    out_path = (ROOT / args.out) if not Path(args.out).is_absolute() else Path(args.out)
    limiter = RateLimiter()

    log.info("[1/2] sitemap 시도")
    urls = discover_via_sitemap(limiter)
    if len(urls) < 100:
        log.info("sitemap 결과 부족(%d) -> archive 폴백", len(urls))
        urls = discover_via_archive(limiter, args.max_pages)

    if not urls:
        log.error("URL 수집 실패")
        return 2

    urls = sorted(set(urls), key=lambda u: int(extract_post_id(u) or 0))

    existing: set[str] = set()
    if args.incremental and out_path.exists():
        existing = {l.strip() for l in out_path.read_text(encoding="utf-8").splitlines() if l.strip()}
    new_urls = [u for u in urls if u not in existing]
    final = sorted(existing | set(urls), key=lambda u: int(extract_post_id(u) or 0))

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(final) + "\n", encoding="utf-8")
    log.info("총 %d건 저장 (신규 %d) -> %s", len(final), len(new_urls), out_path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
