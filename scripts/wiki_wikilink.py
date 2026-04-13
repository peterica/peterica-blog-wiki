"""포스트 md에 위키링크(MOC, 태그) 삽입. wiki 파이프라인 Step 3.

사용법:
    python scripts/wiki_wikilink.py
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from _common import ROOT, DATA_DIR, get_logger, wiki_dir

log = get_logger("wiki_wikilink")

WIKILINK_MARKER = "<!-- wiki-links -->"


def load_moc_map(wiki_jsonl: Path) -> dict[str, str]:
    mapping = {}
    with wiki_jsonl.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rec = json.loads(line)
                mapping[str(rec["id"])] = rec.get("moc", "")
    return mapping


def inject_wikilinks(md_path: Path, moc: str, tags: list[str]) -> bool:
    content = md_path.read_text(encoding="utf-8")
    if WIKILINK_MARKER in content:
        return False

    links = [
        "",
        WIKILINK_MARKER,
        "",
        "---",
        "",
        f"**분류**: [[MOC-{moc}]]",
    ]
    if tags:
        tag_str = " ".join(f"#{t}" for t in tags[:10])
        links.append(f"**태그**: {tag_str}")
    links.append("")

    content = content.rstrip() + "\n" + "\n".join(links)
    md_path.write_text(content, encoding="utf-8")
    return True


def extract_id_from_filename(filename: str) -> str:
    match = re.match(r"^0*(\d+)-", filename)
    return match.group(1) if match else ""


def extract_tags_from_frontmatter(md_path: Path) -> list[str]:
    content = md_path.read_text(encoding="utf-8")
    if not content.startswith("---"):
        return []
    end = content.find("---", 3)
    if end < 0:
        return []
    fm = content[3:end]
    match = re.search(r'tags:\s*\[([^\]]*)\]', fm)
    if match:
        raw = match.group(1)
        return [t.strip().strip('"').strip("'") for t in raw.split(",") if t.strip()]
    return []


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--posts-dir", default=str(wiki_dir() / "posts"))
    parser.add_argument("--wiki-jsonl", default=str(DATA_DIR / "posts_wiki.jsonl"))
    args = parser.parse_args()

    posts_dir = Path(args.posts_dir)
    moc_map = load_moc_map(Path(args.wiki_jsonl))
    log.info("MOC 매핑 로드: %d건", len(moc_map))

    updated = skipped = no_moc = 0
    for md_path in sorted(posts_dir.rglob("*.md")):
        post_id = extract_id_from_filename(md_path.name)
        if not post_id:
            continue
        moc = moc_map.get(post_id)
        if not moc:
            no_moc += 1
            continue
        tags = extract_tags_from_frontmatter(md_path)
        if inject_wikilinks(md_path, moc, tags):
            updated += 1
        else:
            skipped += 1

    log.info("완료: %d 업데이트, %d skip, %d MOC 미매핑", updated, skipped, no_moc)


if __name__ == "__main__":
    main()
