"""Obsidian vault 설정 생성. wiki 파이프라인 Step 6.

사용법:
    python scripts/wiki_obsidian.py
"""
from __future__ import annotations

import json
from pathlib import Path

from _common import get_logger, wiki_dir

log = get_logger("wiki_obsidian")


def main():
    obsidian_dir = wiki_dir() / ".obsidian"
    obsidian_dir.mkdir(parents=True, exist_ok=True)

    # app.json
    (obsidian_dir / "app.json").write_text(json.dumps({
        "showLineNumber": True,
        "strictLineBreaks": False,
        "readableLineLength": True,
        "showFrontmatter": False,
    }, indent=2, ensure_ascii=False), encoding="utf-8")

    # graph.json -- 4색 그룹
    (obsidian_dir / "graph.json").write_text(json.dumps({
        "colorGroups": [
            {"query": "path:moc", "color": {"a": 1, "h": 0, "s": 80, "l": 65}},
            {"query": "path:concepts", "color": {"a": 1, "h": 170, "s": 60, "l": 55}},
            {"query": "path:entities", "color": {"a": 1, "h": 200, "s": 65, "l": 55}},
            {"query": "path:posts", "color": {"a": 1, "h": 130, "s": 40, "l": 70}},
        ],
        "showTags": False,
        "showAttachments": False,
        "showOrphans": True,
        "repelStrength": 10,
        "linkDistance": 250,
    }, indent=2, ensure_ascii=False), encoding="utf-8")

    # community-plugins.json
    (obsidian_dir / "community-plugins.json").write_text(
        json.dumps(["dataview", "tag-wrangler", "graph-analysis"], indent=2),
        encoding="utf-8",
    )

    log.info("Obsidian 설정 생성 완료: %s", obsidian_dir)


if __name__ == "__main__":
    main()
