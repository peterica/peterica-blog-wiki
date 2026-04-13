"""공통 유틸리티 — config 로더, HTTP 클라이언트, JSONL I/O, 해시."""
from __future__ import annotations

import hashlib
import json
import logging
import os
import re
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Iterator

import httpx
import yaml

# ---- 경로 상수 ----
ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
SHARDS_DIR = DATA_DIR / "shards"
REPORTS_DIR = ROOT / "reports"
CONFIG_PATH = ROOT / "config.yaml"


# ---- Config ----
_config_cache: dict | None = None


def load_config(path: Path | None = None) -> dict:
    """config.yaml 을 로드하고 캐시한다."""
    global _config_cache
    if _config_cache is not None and path is None:
        return _config_cache
    p = path or CONFIG_PATH
    if not p.exists():
        raise FileNotFoundError(f"config.yaml 없음: {p}")
    with p.open("r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)
    if path is None:
        _config_cache = cfg
    return cfg


def cfg(key: str, default: Any = None) -> Any:
    """점 표기법으로 config 값 읽기. 예: cfg('llm.provider')"""
    config = load_config()
    keys = key.split(".")
    val = config
    for k in keys:
        if isinstance(val, dict):
            val = val.get(k)
        else:
            return default
        if val is None:
            return default
    return val


# ---- 로깅 ----
def get_logger(name: str) -> logging.Logger:
    level = os.environ.get("LOG_LEVEL", "INFO").upper()
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )
    return logging.getLogger(name)


# ---- 디렉토리 ----
def ensure_dirs() -> None:
    wiki_dir = ROOT / cfg("wiki.output_dir", "wiki")
    for d in (DATA_DIR, SHARDS_DIR, REPORTS_DIR, wiki_dir):
        d.mkdir(parents=True, exist_ok=True)


def wiki_dir() -> Path:
    return ROOT / cfg("wiki.output_dir", "wiki")


# ---- HTTP ----
def http_client() -> httpx.Client:
    return httpx.Client(
        headers={
            "User-Agent": cfg("blog.user_agent", "blog-wiki-builder/0.1"),
            "Accept-Language": "ko,en;q=0.8",
        },
        timeout=cfg("scrape.timeout", 15.0),
        follow_redirects=True,
    )


class RateLimiter:
    """단일 프로세스 내 rate limiter."""

    def __init__(self, interval: float | None = None) -> None:
        self.interval = interval or cfg("scrape.rate_limit", 1.0)
        self._last = 0.0

    def wait(self) -> None:
        now = time.monotonic()
        delta = now - self._last
        if delta < self.interval:
            time.sleep(self.interval - delta)
        self._last = time.monotonic()


def fetch(client: httpx.Client, url: str, limiter: RateLimiter,
          *, retries: int | None = None) -> httpx.Response:
    """지수 백오프 재시도와 rate limit 이 적용된 GET."""
    max_retries = retries or cfg("scrape.retries", 3)
    last_exc: Exception | None = None
    delay = 1.0
    for _ in range(max_retries):
        limiter.wait()
        try:
            resp = client.get(url)
            if resp.status_code == 429:
                time.sleep(delay)
                delay *= 2
                continue
            resp.raise_for_status()
            return resp
        except httpx.HTTPError as exc:
            last_exc = exc
            time.sleep(delay)
            delay *= 2
    raise RuntimeError(f"fetch failed after {max_retries} retries: {url}") from last_exc


# ---- JSONL ----
def read_jsonl(path: Path) -> Iterator[dict]:
    if not path.exists():
        return
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                yield json.loads(line)


def write_jsonl(path: Path, records: Iterable[dict]) -> int:
    path.parent.mkdir(parents=True, exist_ok=True)
    count = 0
    with path.open("w", encoding="utf-8") as f:
        for rec in records:
            f.write(json.dumps(rec, ensure_ascii=False))
            f.write("\n")
            count += 1
    return count


# ---- 해시 ----
def sha256_hex(text: str) -> str:
    return "sha256:" + hashlib.sha256(text.encode("utf-8")).hexdigest()


# ---- URL 파싱 ----
def get_url_pattern() -> re.Pattern:
    return re.compile(cfg("scrape.url_pattern", r"^https://.*?/(\d+)$"))


def extract_post_id(url: str) -> str | None:
    m = get_url_pattern().match(url.strip())
    return m.group(1) if m else None


# ---- Shard 경로 ----
@dataclass(frozen=True)
class ShardPath:
    shard_id: str
    txt: Path
    raw_jsonl: Path
    jsonl: Path

    @classmethod
    def of(cls, shard_id: str) -> "ShardPath":
        return cls(
            shard_id=shard_id,
            txt=SHARDS_DIR / f"{shard_id}.txt",
            raw_jsonl=SHARDS_DIR / f"{shard_id}.raw.jsonl",
            jsonl=SHARDS_DIR / f"{shard_id}.jsonl",
        )
