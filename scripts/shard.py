"""URL 목록을 배치(shard) 파일로 분할한다.

사용법:
    python scripts/shard.py
    python scripts/shard.py --size 50
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from _common import ROOT, SHARDS_DIR, cfg, ensure_dirs, extract_post_id, get_logger

log = get_logger("shard")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--in", dest="inp", default="data/urls.txt")
    parser.add_argument("--out", dest="out", default="data/shards/")
    parser.add_argument("--size", type=int, default=None)
    args = parser.parse_args()

    ensure_dirs()
    size = args.size or cfg("batch.shard_size", 50)
    inp = (ROOT / args.inp) if not Path(args.inp).is_absolute() else Path(args.inp)
    out_dir = (ROOT / args.out) if not Path(args.out).is_absolute() else Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    if not inp.exists():
        log.error("입력 파일 없음: %s", inp)
        return 2

    urls = [u.strip() for u in inp.read_text(encoding="utf-8").splitlines() if u.strip()]
    urls = [u for u in urls if extract_post_id(u)]
    if not urls:
        log.error("유효 URL 없음")
        return 2

    urls.sort(key=lambda u: int(extract_post_id(u) or 0))

    for old in out_dir.glob("[0-9][0-9][0-9][0-9].txt"):
        old.unlink()

    total_shards = (len(urls) + size - 1) // size
    for i in range(total_shards):
        chunk = urls[i * size : (i + 1) * size]
        shard_id = f"{i + 1:04d}"
        shard_path = out_dir / f"{shard_id}.txt"
        shard_path.write_text("\n".join(chunk) + "\n", encoding="utf-8")

    log.info("총 %d URL -> %d shard (size=%d) @ %s", len(urls), total_shards, size, out_dir)
    return 0


if __name__ == "__main__":
    sys.exit(main())
