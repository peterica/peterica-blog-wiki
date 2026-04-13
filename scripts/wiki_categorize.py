"""카테고리 -> MOC 매핑. wiki 파이프라인 Step 1.

매핑 테이블은 config.yaml의 wiki.moc_map에서 읽는다.

사용법:
    python scripts/wiki_categorize.py
    python scripts/wiki_categorize.py --dry-run
"""
from __future__ import annotations

import argparse
from pathlib import Path

from _common import ROOT, DATA_DIR, cfg, get_logger, read_jsonl, write_jsonl

log = get_logger("wiki_categorize")


def categorize(posts: list[dict]) -> list[dict]:
    moc_map = cfg("wiki.moc_map", {})
    fallback = cfg("wiki.fallback_moc", "Life")
    unmapped: dict[str, int] = {}
    for p in posts:
        cat = p.get("category", "")
        moc = moc_map.get(cat)
        if moc is None:
            unmapped[cat] = unmapped.get(cat, 0) + 1
            moc = fallback
        p["moc"] = moc
    if unmapped:
        log.warning("매핑 안 된 카테고리 -> %s 폴백: %s", fallback, unmapped)
    return posts


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--in", dest="inp", default=str(DATA_DIR / "posts.jsonl"))
    parser.add_argument("--out", default=str(DATA_DIR / "posts_wiki.jsonl"))
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    posts = list(read_jsonl(Path(args.inp)))
    log.info("입력: %d건, 카테고리 %d종", len(posts), len({p.get("category", "") for p in posts}))

    posts = categorize(posts)

    dist: dict[str, int] = {}
    for p in posts:
        dist[p["moc"]] = dist.get(p["moc"], 0) + 1
    log.info("MOC 분포 (%d종):", len(dist))
    for moc, cnt in sorted(dist.items(), key=lambda x: -x[1]):
        log.info("  %4d  %s", cnt, moc)

    if args.dry_run:
        log.info("--dry-run: 파일 미생성")
        return

    write_jsonl(Path(args.out), posts)
    log.info("출력: %s (%d건)", args.out, len(posts))


if __name__ == "__main__":
    main()
