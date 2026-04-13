"""MOC (Map of Content) 페이지 자동 생성. wiki 파이프라인 Step 2.

사용법:
    python scripts/wiki_moc.py
    python scripts/wiki_moc.py --in data/posts_wiki.jsonl --out-dir wiki/moc
"""
from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path

from _common import ROOT, DATA_DIR, cfg, get_logger, wiki_dir

log = get_logger("wiki_moc")


def load_posts(path: Path) -> list[dict]:
    posts = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                posts.append(json.loads(line))
    return posts


def posts_by_year(posts: list[dict]) -> dict[str, list[dict]]:
    by_year: dict[str, list[dict]] = defaultdict(list)
    for p in posts:
        year = p.get("published_at", "")[:4] or "unknown"
        by_year[year].append(p)
    return dict(sorted(by_year.items(), reverse=True))


def top_tags(posts: list[dict], n: int = 15) -> list[tuple[str, int]]:
    tag_count: dict[str, int] = defaultdict(int)
    for p in posts:
        for t in p.get("tags", []):
            tag_count[t] += 1
    return sorted(tag_count.items(), key=lambda x: -x[1])[:n]


def generate_moc(moc_name: str, posts: list[dict]) -> str:
    icons = cfg("wiki.moc_icons", {})
    icon = icons.get(moc_name, "")
    by_year = posts_by_year(posts)
    tags = top_tags(posts)

    lines = [
        "---",
        "type: moc",
        f'title: "{moc_name}"',
        f'icon: "{icon}"',
        f"tags: [moc, {moc_name.lower()}]",
        f"post_count: {len(posts)}",
        "---",
        "",
        f"# {icon} {moc_name}",
        "",
        f"> {len(posts)}개 포스트",
        "",
        "## 주요 태그",
        "",
        " / ".join(f"`{t}` ({c})" for t, c in tags),
        "",
        "## 개념 지도",
        "",
        "_(concept 생성 후 자동 채워짐)_",
        "",
        "## 포스트",
        "",
    ]

    for year, year_posts in by_year.items():
        lines.append(f"### {year} ({len(year_posts)})")
        lines.append("")
        for p in sorted(year_posts, key=lambda p: p.get("published_at", ""), reverse=True):
            date = p.get("published_at", "")
            summary = p.get("summary", "")[:50]
            if len(p.get("summary", "")) > 50:
                summary += "..."
            lines.append(f"- {date} / **{p.get('title', '')}** -- {summary}")
        lines.append("")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--in", dest="inp", default=str(DATA_DIR / "posts_wiki.jsonl"))
    parser.add_argument("--out-dir", dest="out_dir", default=str(wiki_dir() / "moc"))
    args = parser.parse_args()

    posts = load_posts(Path(args.inp))
    groups: dict[str, list[dict]] = defaultdict(list)
    for p in posts:
        groups[p["moc"]].append(p)

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    for moc_name, moc_posts in sorted(groups.items()):
        content = generate_moc(moc_name, moc_posts)
        out_path = out_dir / f"MOC-{moc_name}.md"
        out_path.write_text(content, encoding="utf-8")
        log.info("  %s: %d posts", out_path.name, len(moc_posts))

    log.info("MOC 생성 완료: %d개", len(groups))


if __name__ == "__main__":
    main()
