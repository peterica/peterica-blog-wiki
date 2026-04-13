"""Rubric 평가기 — JSONL 레코드의 품질을 검증하여 PASS/FAIL 판정.

품질 기준은 config.yaml의 quality 섹션에서 커스터마이즈 가능.

사용법:
    python scripts/evaluate.py --in data/shards/0001.jsonl --report reports/eval_0001.md
    python scripts/evaluate.py --in data/posts.jsonl --report reports/eval_full.md --strict
"""
from __future__ import annotations

import argparse
import re
import sys
from collections import Counter
from pathlib import Path

from _common import ROOT, cfg, ensure_dirs, get_logger, read_jsonl, write_jsonl

log = get_logger("evaluate")

REQUIRED = ("id", "title", "url", "summary", "tags")
KEBAB_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
LOOSE_TAG_RE = re.compile(r"^[a-z0-9가-힣]+(?:-[a-z0-9가-힣]+)*$")
ISO_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
KO_SENT_END_RE = re.compile(r"[가-힣]\.(?:\s|$)|[!?。！？](?:\s|$)")


def count_sentences(text: str) -> int:
    if not text:
        return 0
    matches = KO_SENT_END_RE.findall(text)
    return max(len(matches), 1)


def check_record(rec: dict, *, strict: bool = False) -> list[str]:
    fails: list[str] = []
    for k in REQUIRED:
        if not rec.get(k):
            fails.append(f"missing:{k}")

    summary = rec.get("summary", "") or ""
    if summary:
        length = len(summary)
        min_len = cfg("quality.summary_min_length", 120)
        max_len = cfg("quality.summary_max_length", 500)
        if not (min_len <= length <= max_len) and not rec.get("short_post"):
            fails.append(f"summary_length:{length}")
        sc = count_sentences(summary)
        min_sent = cfg("quality.summary_min_sentences", 2)
        max_sent = cfg("quality.summary_max_sentences", 6)
        if not (min_sent <= sc <= max_sent):
            fails.append(f"summary_sentences:{sc}")

    tags = rec.get("tags") or []
    if not isinstance(tags, list):
        fails.append("tags_type")
    else:
        min_tags = cfg("quality.tag_count_min", 3)
        max_tags = cfg("quality.tag_count_max", 7)
        if not (min_tags <= len(tags) <= max_tags):
            fails.append(f"tags_count:{len(tags)}")
        if len(set(tags)) != len(tags):
            fails.append("tags_duplicate")
        pattern = KEBAB_RE if strict else LOOSE_TAG_RE
        for t in tags:
            if not isinstance(t, str) or not pattern.match(t):
                fails.append(f"tag_format:{t}")
                break

    published = rec.get("published_at")
    if published and not ISO_DATE_RE.match(str(published)):
        fails.append(f"date_format:{published}")
    return fails


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--in", dest="inp", required=True)
    parser.add_argument("--report", dest="report", required=True)
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()

    ensure_dirs()
    inp = (ROOT / args.inp) if not Path(args.inp).is_absolute() else Path(args.inp)
    report_path = (ROOT / args.report) if not Path(args.report).is_absolute() else Path(args.report)

    if not inp.exists():
        log.error("입력 없음: %s", inp)
        return 2

    total = passed = 0
    fails_counter: Counter[str] = Counter()
    failed_records: list[dict] = []
    seen_ids: set[str] = set()
    dup_ids: list[str] = []

    for rec in read_jsonl(inp):
        total += 1
        rid = rec.get("id")
        if rid in seen_ids:
            dup_ids.append(rid)
        if rid:
            seen_ids.add(rid)
        issues = check_record(rec, strict=args.strict)
        if not issues:
            passed += 1
        else:
            for i in issues:
                fails_counter[i.split(":")[0]] += 1
            failed = dict(rec)
            failed["_fail_reasons"] = issues
            failed_records.append(failed)

    pass_rate = passed / total * 100 if total else 0.0
    lines = [
        f"# Evaluation Report -- `{inp.name}`",
        "",
        f"- 총 레코드: **{total}**",
        f"- PASS: **{passed} ({pass_rate:.1f}%)**",
        f"- FAIL: **{total - passed}**",
        f"- 중복 id: **{len(dup_ids)}**",
        "",
        "## 실패 유형 분포",
        "",
        "| 유형 | 개수 |",
        "|------|------|",
    ]
    for k, v in fails_counter.most_common():
        lines.append(f"| {k} | {v} |")
    if failed_records:
        lines += ["", "## FAIL 레코드 (상위 20)", "", "| id | 사유 |", "|----|------|"]
        for rec in failed_records[:20]:
            lines.append(f"| {rec.get('id')} | {', '.join(rec.get('_fail_reasons', []))} |")

    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    threshold = cfg("quality.pass_rate_threshold", 98.0)
    log.info("report -> %s (pass %.1f%%, threshold %.1f%%)", report_path, pass_rate, threshold)
    return 0 if pass_rate >= threshold and not dup_ids else 1


if __name__ == "__main__":
    sys.exit(main())
