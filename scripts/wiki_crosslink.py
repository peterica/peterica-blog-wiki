"""크로스링크 보강 + _index.md 생성. wiki 파이프라인 Step 5.

사용법:
    python scripts/wiki_crosslink.py
"""
from __future__ import annotations

import argparse
import re
from pathlib import Path

import yaml

from _common import ROOT, get_logger, wiki_dir as _wiki_dir

log = get_logger("wiki_crosslink")


def parse_frontmatter(content: str) -> dict:
    if not content.startswith("---"):
        return {}
    end = content.find("---", 3)
    if end < 0:
        return {}
    try:
        return yaml.safe_load(content[3:end]) or {}
    except yaml.YAMLError:
        return {}


def collect_pages(wd: Path) -> dict[str, dict]:
    pages = {}
    for md in wd.rglob("*.md"):
        rel = md.relative_to(wd)
        if str(rel).startswith(".obsidian"):
            continue
        content = md.read_text(encoding="utf-8")
        fm = parse_frontmatter(content)
        wikilinks = set(re.findall(r"\[\[([^\]|]+)", content))
        pages[md.stem] = {
            "path": md,
            "rel": str(rel),
            "type": fm.get("type", "post"),
            "title": fm.get("title", md.stem),
            "parent": fm.get("parent", ""),
            "outgoing": wikilinks,
        }
    return pages


def update_moc_concepts(wd: Path, pages: dict):
    moc_dir = wd / "moc"
    if not moc_dir.exists():
        return
    for moc_file in moc_dir.glob("MOC-*.md"):
        moc_name = moc_file.stem
        content = moc_file.read_text(encoding="utf-8")
        children = []
        for name, info in pages.items():
            parent = info.get("parent", "")
            if moc_name in parent and info["type"] in ("concept", "entity"):
                children.append((info["type"], info["title"], name))
        if not children:
            continue

        concepts = [c for c in children if c[0] == "concept"]
        entities = [c for c in children if c[0] == "entity"]
        replacement = "## 개념 지도\n\n"
        if concepts:
            replacement += "### 개념\n"
            for _, title, slug in sorted(concepts, key=lambda x: x[1]):
                replacement += f"- [[{slug}|{title}]]\n"
            replacement += "\n"
        if entities:
            replacement += "### 기술/도구\n"
            for _, title, slug in sorted(entities, key=lambda x: x[1]):
                replacement += f"- [[{slug}|{title}]]\n"
            replacement += "\n"

        content = re.sub(
            r"## 개념 지도\s*\n\n.*?(?=\n## |\Z)",
            replacement, content, flags=re.DOTALL,
        )
        moc_file.write_text(content, encoding="utf-8")
        log.info("  MOC: %s (+%d concepts, +%d entities)", moc_file.name, len(concepts), len(entities))


def generate_index(wd: Path, pages: dict):
    mocs = {n: p for n, p in pages.items() if p["type"] == "moc"}
    concepts = {n: p for n, p in pages.items() if p["type"] == "concept"}
    entities = {n: p for n, p in pages.items() if p["type"] == "entity"}
    posts = {n: p for n, p in pages.items() if p["type"] not in ("moc", "concept", "entity")}

    lines = [
        "# Knowledge Wiki",
        "",
        f"> {len(posts)}개 블로그 포스트에서 추출한 개발 지식 체계",
        "",
        "## 지식 지도",
        "",
    ]
    for moc_name in sorted(mocs.keys()):
        moc = mocs[moc_name]
        child_count = sum(1 for p in pages.values() if moc_name in p.get("parent", ""))
        lines.append(f"- [[{moc_name}|{moc['title']}]] -- {child_count}개 개념/기술")

    lines.extend([
        "",
        "## 통계",
        "",
        f"- MOC: {len(mocs)}개",
        f"- Concept: {len(concepts)}개",
        f"- Entity: {len(entities)}개",
        f"- Post: {len(posts)}개",
    ])

    index_path = wd / "_index.md"
    index_path.write_text("\n".join(lines), encoding="utf-8")
    log.info("_index.md: MOC %d, concept %d, entity %d, post %d",
             len(mocs), len(concepts), len(entities), len(posts))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--wiki-dir", default=str(_wiki_dir()))
    args = parser.parse_args()

    wd = Path(args.wiki_dir)
    pages = collect_pages(wd)
    log.info("총 %d 페이지", len(pages))

    update_moc_concepts(wd, pages)
    generate_index(wd, pages)

    # Orphan 리포트
    all_outgoing = set()
    for info in pages.values():
        all_outgoing.update(info["outgoing"])
    orphans = [n for n, p in pages.items()
               if p["type"] in ("concept", "entity") and n not in all_outgoing]
    if orphans:
        log.warning("Orphan %d건: %s", len(orphans), orphans[:10])


if __name__ == "__main__":
    main()
