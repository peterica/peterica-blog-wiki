"""위키 concept/entity 페이지 품질 평가.

사용법:
    python scripts/wiki_evaluate.py
"""
from __future__ import annotations

import argparse
import re
from pathlib import Path

import yaml

from _common import ROOT, REPORTS_DIR, get_logger, wiki_dir

log = get_logger("wiki_evaluate")


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


def evaluate_page(path: Path) -> dict:
    content = path.read_text(encoding="utf-8")
    fm = parse_frontmatter(content)

    results = {
        "frontmatter_valid": all(k in fm for k in ["type", "title", "parent", "tags"]),
        "type_correct": fm.get("type") in ("concept", "entity"),
        "has_definition": bool(re.search(r"## 한 줄 정의\s*\n>\s*\S", content)),
        "has_post_refs": bool(re.search(r"\[\[\d+\]\]", content)),
        "has_related": bool(fm.get("related")),
        "content_length": len(content) >= 200,
        "no_placeholder": "TODO" not in content and "작성 예정" not in content,
        "wikilink_count": len(re.findall(r"\[\[([^\]]+)\]\]", content)),
    }

    required = ["frontmatter_valid", "type_correct", "has_definition", "has_post_refs"]
    results["required_pass"] = all(results[k] for k in required)

    recommended = ["has_related", "content_length", "no_placeholder"]
    rec_pass = sum(1 for k in recommended if results[k])
    if results["required_pass"] and rec_pass >= 3:
        results["confidence"] = "high"
    elif results["required_pass"] and rec_pass >= 1:
        results["confidence"] = "medium"
    else:
        results["confidence"] = "low"

    results["file"] = path.name
    results["type"] = fm.get("type", "unknown")
    return results


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", default=str(REPORTS_DIR / "wiki_eval.md"))
    args = parser.parse_args()

    wd = wiki_dir()
    dirs = [wd / "concepts", wd / "entities"]
    all_results = []
    for d in dirs:
        if d.exists():
            for md in sorted(d.glob("*.md")):
                all_results.append(evaluate_page(md))

    if not all_results:
        log.warning("평가할 파일 없음")
        return

    total = len(all_results)
    req_pass = sum(1 for r in all_results if r["required_pass"])
    high = sum(1 for r in all_results if r["confidence"] == "high")
    medium = sum(1 for r in all_results if r["confidence"] == "medium")
    low = sum(1 for r in all_results if r["confidence"] == "low")

    log.info("총 %d, PASS: %d/%d (%.1f%%), confidence: high=%d medium=%d low=%d",
             total, req_pass, total, req_pass / total * 100, high, medium, low)

    report = Path(args.report)
    report.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Wiki Quality Report",
        "",
        f"PASS: {req_pass}/{total} ({req_pass / total * 100:.1f}%)",
        f"Confidence: high={high}, medium={medium}, low={low}",
        "",
        "| File | Type | Pass | Confidence |",
        "|------|------|------|-----------|",
    ]
    for r in all_results:
        p = "PASS" if r["required_pass"] else "FAIL"
        lines.append(f"| {r['file']} | {r['type']} | {p} | {r['confidence']} |")
    report.write_text("\n".join(lines), encoding="utf-8")
    log.info("report -> %s", report)


if __name__ == "__main__":
    main()
