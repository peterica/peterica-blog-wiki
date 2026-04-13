"""shard JSONL 파일들을 병합하여 data/posts.jsonl을 생성한다.

사용법:
    python scripts/merge.py
    python scripts/merge.py --in 'data/shards/*.jsonl' --out data/posts.jsonl
"""
from __future__ import annotations

import argparse
import glob
import sys
from pathlib import Path

from _common import ROOT, ensure_dirs, get_logger, read_jsonl, write_jsonl

log = get_logger("merge")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--in", dest="pattern", default="data/shards/*.jsonl")
    parser.add_argument("--out", dest="out", default="data/posts.jsonl")
    args = parser.parse_args()

    ensure_dirs()
    pattern = args.pattern if Path(args.pattern).is_absolute() else str(ROOT / args.pattern)
    out = (ROOT / args.out) if not Path(args.out).is_absolute() else Path(args.out)

    files = [Path(p) for p in glob.glob(pattern)
             if not p.endswith(".retry.jsonl") and not p.endswith(".raw.jsonl")]
    if not files:
        log.error("병합 대상 없음: %s", pattern)
        return 2

    by_id: dict[str, dict] = {}
    total_read = 0
    for f in files:
        for rec in read_jsonl(f):
            total_read += 1
            rid = rec.get("id")
            if not rid:
                continue
            prev = by_id.get(rid)
            if prev is None or (rec.get("generated_at", "") > prev.get("generated_at", "")):
                by_id[rid] = rec

    merged = sorted(by_id.values(), key=lambda r: int(r.get("id") or 0))
    n = write_jsonl(out, merged)
    log.info("%d files / %d records -> unique %d -> %s", len(files), total_read, n, out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
