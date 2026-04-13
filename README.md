# Blog Wiki Builder

**블로그 글을 Obsidian 지식 위키로 변환하는 파이프라인.**

Karpathy의 [LLM Wiki](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f) 아이디어를 블로그에 적용한 프로젝트입니다. 987개 블로그 글을 스크래핑하고, LLM으로 요약/태깅한 뒤, 4계층 Obsidian 지식 위키로 재구성한 과정과 도구를 공유합니다.

## 핵심 아이디어

Karpathy의 LLM Wiki는 3계층 구조를 제안합니다:

```
Raw Sources (원본)  ->  Wiki (합성 지식)  ->  Schema (구조 규칙)
```

이 프로젝트에서는 이렇게 구현했습니다:

| Layer | 구현 | 역할 |
|---|---|---|
| Raw Sources | `wiki/posts/` | 블로그 원본 (수정 안 함) |
| Wiki | `wiki/concepts/`, `entities/`, `moc/` | LLM이 합성한 지식 페이지 |
| Schema | `config.yaml` + 스크립트 | 구조 규칙과 자동화 |

## 위키 4계층

| 유형 | 역할 | 예시 |
|---|---|---|
| **MOC** | 카테고리 진입점 (Map of Content) | MOC-DevOps, MOC-Kubernetes |
| **Concept** | 여러 글에서 합성한 지식 단위 | "CI/CD 파이프라인 설계" |
| **Entity** | 기술/도구 정의 + 사용 경험 | Docker, Jenkins |
| **Post** | 블로그 원본 | 개별 블로그 글 |

## Quick Start

### 1. 설치

```bash
git clone <this-repo>
cd peterica-blog-wiki
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

### 2. 설정

`config.yaml`을 자신의 블로그에 맞게 수정합니다:

```yaml
blog:
  url: "https://your-blog.tistory.com"    # 블로그 URL
  platform: "tistory"                      # tistory | wordpress | rss

llm:
  provider: "ollama"                       # ollama (무료) | openai | anthropic
  model: "qwen3:8b"                        # 사용할 모델

wiki:
  moc_map:                                 # 카테고리 -> MOC 매핑
    DevOps: DevOps
    Python: Programming
    # ... 자신의 카테고리에 맞게 수정
```

### 3. LLM 준비 (Ollama 사용 시)

```bash
# Ollama 설치: https://ollama.com
ollama pull qwen3:8b
ollama serve  # 서버 시작
```

### 4. 실행

```bash
# 전체 파이프라인 (URL 수집 -> 스크래핑 -> 요약 -> 위키 빌드)
bash scripts/run_pipeline.sh

# 위키 빌드만 (이미 posts.jsonl이 있을 때)
bash scripts/run_pipeline.sh --wiki-only

# 스크래핑 건너뛰기 (이미 raw.jsonl이 있을 때)
bash scripts/run_pipeline.sh --skip-scrape
```

### 5. 결과 확인

Obsidian에서 `wiki/` 폴더를 vault로 열면 4색 그래프 뷰로 지식 네트워크를 볼 수 있습니다.

## 파이프라인 구조

```
Step 0: discover.py     URL 수집 (sitemap/archive)
Step 1: shard.py        배치 분할 (50건 단위)
Step 2: scrape.py       HTML 파싱, 본문 추출
Step 3: summarize.py    LLM 요약/태깅/카테고리 분류
     -> evaluate.py     Rubric 품질 검증
     -> merge.py        shard 병합
Step 4: wiki_categorize -> wiki_moc -> wiki_generate -> wiki_wikilink
Step 5: wiki_crosslink  크로스링크 + _index.md
Step 6: wiki_obsidian   Obsidian 설정
     -> wiki_evaluate   위키 품질 평가
```

## 토큰 절약 전략

LLM에 포스트 전문을 넘기면 건당 ~500자. 하지만 이미 생성된 요약/태그/키워드만 전달하면 건당 ~80자. **84% 토큰 절감**.

```
포스트 전문: 500자 x 8건 = 4,000자
요약+태그:   80자 x 8건 =   640자  -> 84% 절감
```

Ollama + qwen3:8b는 로컬에서 무료로 실행됩니다. 클라우드 API 비용 없이 987건 처리 가능.

## 과정 문서

이 파이프라인을 만든 과정과 판단 근거를 `docs/`에 정리했습니다:

- [00-architecture.md](docs/00-architecture.md) -- 전체 아키텍처
- [01-discover.md](docs/01-discover.md) -- URL 수집
- [02-scrape.md](docs/02-scrape.md) -- 스크래핑
- [03-summarize.md](docs/03-summarize.md) -- LLM 요약, 토큰 절약
- [04-wiki-build.md](docs/04-wiki-build.md) -- 위키 빌드 6단계
- [05-quality.md](docs/05-quality.md) -- 품질 검증
- [06-obsidian.md](docs/06-obsidian.md) -- Obsidian 설정

## 실제 적용 결과

Peterica 블로그 (https://peterica.tistory.com, 987글)에 적용한 결과:

- 12 MOC + 122 Concept + 61 Entity 생성
- Rubric PASS: 98.2% (970/987)
- 위키 품질 PASS: 100% (183/183)
- 전체 처리 시간: ~4시간 (로컬 LLM)

## 참고

- [Karpathy LLM Wiki](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f)
- [OmegaWiki](https://github.com/skyllwt/OmegaWiki) -- 연구 논문 LLM Wiki 구현

## 기술 스택

- Python (httpx, selectolax) -- 스크래핑/파이프라인
- Ollama + qwen3:8b -- 로컬 LLM (무료)
- Obsidian -- 지식 위키 시각화
- YAML -- config 기반 범용 설정
