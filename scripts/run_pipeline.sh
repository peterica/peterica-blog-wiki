#!/usr/bin/env bash
# ============================================================
# Blog Wiki Builder — Full Pipeline
# ============================================================
# config.yaml 기반으로 블로그 → Obsidian 위키 전체 파이프라인 실행
#
# 사용법:
#   bash scripts/run_pipeline.sh              # 전체 실행
#   bash scripts/run_pipeline.sh --skip-scrape # 스크래핑 건너뛰기 (이미 데이터 있을 때)
#   bash scripts/run_pipeline.sh --wiki-only   # 위키 빌드만 (Step 4~6)
#
# 전제:
#   - Python 3.10+ 및 requirements.txt 의존성 설치
#   - config.yaml 의 blog.url, llm.provider 설정 완료
#   - LLM provider=ollama 사용 시 Ollama 서버 구동 중
# ============================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_ROOT"

# ---- 옵션 파싱 ----
SKIP_SCRAPE=false
WIKI_ONLY=false
PARALLEL=${PARALLEL:-2}

for arg in "$@"; do
    case "$arg" in
        --skip-scrape) SKIP_SCRAPE=true ;;
        --wiki-only)   WIKI_ONLY=true ;;
    esac
done

log() { echo "[$(date '+%H:%M:%S')] $*"; }

# ============================================================
# Phase 1: Discover + Scrape + Summarize
# ============================================================
if [ "$WIKI_ONLY" = false ]; then

    if [ "$SKIP_SCRAPE" = false ]; then
        log "Step 0: URL 수집 (discover)"
        python scripts/discover.py --out data/urls.txt

        URL_COUNT=$(wc -l < data/urls.txt | tr -d ' ')
        log "  수집된 URL: $URL_COUNT"

        log "Step 1: Shard 분할"
        python scripts/shard.py --in data/urls.txt --out data/shards/

        log "Step 2: 스크래핑 (parallel=$PARALLEL)"
        for shard in data/shards/[0-9][0-9][0-9][0-9].txt; do
            SHARD_ID=$(basename "$shard" .txt)
            RAW_OUT="data/shards/${SHARD_ID}.raw.jsonl"
            if [ -f "$RAW_OUT" ]; then
                log "  skip $SHARD_ID (이미 존재)"
                continue
            fi
            python scripts/scrape.py --in "$shard" --out "$RAW_OUT" &
            # 병렬 제한
            while [ "$(jobs -r | wc -l)" -ge "$PARALLEL" ]; do
                sleep 1
            done
        done
        wait
        log "  스크래핑 완료"
    fi

    log "Step 3: LLM 요약/태깅 (parallel=$PARALLEL)"
    for raw in data/shards/[0-9][0-9][0-9][0-9].raw.jsonl; do
        SHARD_ID=$(basename "$raw" .raw.jsonl)
        JSONL_OUT="data/shards/${SHARD_ID}.jsonl"
        python scripts/summarize.py --in "$raw" --out "$JSONL_OUT" --incremental &
        while [ "$(jobs -r | wc -l)" -ge "$PARALLEL" ]; do
            sleep 1
        done
    done
    wait
    log "  요약 완료"

    log "Step 3.5: Rubric 평가"
    for jsonl in data/shards/[0-9][0-9][0-9][0-9].jsonl; do
        SHARD_ID=$(basename "$jsonl" .jsonl)
        python scripts/evaluate.py --in "$jsonl" --report "reports/eval_${SHARD_ID}.md" || true
    done

    log "Step 3.6: 병합"
    python scripts/merge.py --in 'data/shards/*.jsonl' --out data/posts.jsonl

fi

# ============================================================
# Phase 2: Wiki Build (Step 4~6)
# ============================================================
log "Step 4a: 카테고리 -> MOC 매핑"
python scripts/wiki_categorize.py

log "Step 4b: MOC 페이지 생성"
python scripts/wiki_moc.py

log "Step 4c: Concept/Entity LLM 생성"
python scripts/wiki_generate.py

log "Step 4d: 위키링크 삽입"
python scripts/wiki_wikilink.py

log "Step 5: 크로스링크 + _index.md"
python scripts/wiki_crosslink.py

log "Step 6: Obsidian 설정"
python scripts/wiki_obsidian.py

# ============================================================
# Phase 3: 검증
# ============================================================
log "Step 7: 위키 품질 평가"
python scripts/wiki_evaluate.py

log "=========================================="
log "파이프라인 완료!"
log "Obsidian에서 wiki/ 폴더를 vault로 열어 확인하세요."
log "=========================================="
