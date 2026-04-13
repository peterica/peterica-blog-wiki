# 00. 전체 아키텍처

## Karpathy LLM Wiki 3계층

Karpathy가 제안한 LLM Wiki의 핵심은 "RAG처럼 매번 원본을 검색하지 말고, LLM이 위키를 만들고 유지보수하게 하라"는 것이다.

```
Raw Sources (원본)  ->  Wiki (합성 지식)  ->  Schema (구조 규칙)
```

- **Raw Sources**: 변경하지 않는 원본 데이터. 블로그 글, 논문, 노트 등.
- **Wiki**: LLM이 원본을 읽고 합성한 지식 페이지. 개별 글의 요약이 아니라 여러 글의 공통 주제를 추출한 것.
- **Schema**: 위키의 구조 규칙. 어떤 유형의 페이지가 있고, 어떻게 연결되는지를 정의.

## 이 프로젝트의 매핑

| Karpathy Layer | 구현 | 역할 |
|---|---|---|
| Raw Sources | `wiki/posts/` (987개 md) | 블로그 원본, 수정하지 않음 |
| Wiki | `wiki/concepts/`, `entities/`, `moc/` | LLM이 합성한 지식 페이지 |
| Schema | `config.yaml` + `CLAUDE.md` | 구조 규칙과 자동화 설정 |

## 위키 4계층

최종 산출물은 4가지 유형의 페이지로 구성된다:

```
_index.md (진입점)
  └── MOC (12개) — 카테고리 허브
        └── Concept (122개) — 여러 글에서 합성한 지식
        └── Entity (61개) — 기술/도구 정의
              └── Post (987개) — 블로그 원본
```

**포스트 목록과 지식 위키의 차이**: INDEX.md는 "어떤 글이 있는지"를 보여준다. Concept 페이지는 "내가 이 주제에 대해 무엇을 이해하고 있는지"를 보여준다. 예를 들어 "Kubernetes 네트워킹" Concept은 Service, Ingress, CNI에 대한 8개 포스트를 읽고 합성한 결과물이다.

## 파이프라인 6단계

```
Step 1. 카테고리 재정리     wiki_categorize.py    69 카테고리 -> 12 MOC
Step 2. MOC 페이지 생성     wiki_moc.py           카테고리별 진입점
Step 3. 위키링크 삽입       wiki_wikilink.py      포스트에 [[MOC-*]] 링크
Step 4. Concept/Entity 생성 wiki_generate.py      Local LLM으로 벌크 생성
Step 5. 크로스링크          wiki_crosslink.py     상호 참조 + _index.md
Step 6. Obsidian 설정       wiki_obsidian.py      그래프 뷰 4색 그룹
```

이 6단계 앞에 "블로그 스크래핑 -> 요약/태깅" 파이프라인이 선행된다 (discover -> scrape -> summarize -> evaluate -> merge). 두 파이프라인은 `run_pipeline.sh`로 원커맨드 실행 가능하다.

## 토큰 절약 설계

LLM 호출이 필요한 단계는 두 곳이다:

1. **summarize.py**: 포스트 본문 -> 요약/태그/키워드 (건당 1회)
2. **wiki_generate.py**: 포스트 메타데이터 -> Concept/Entity 페이지 (MOC당 1~2회)

Step 4에서 포스트 전문을 넣으면 건당 ~500자. 이미 생성된 요약+태그+키워드만 넣으면 건당 ~80자. **84% 절감**.

```
포스트 전문: 500자 x 8건 = 4,000자
요약+태그:   80자 x 8건 =   640자
```

Ollama + qwen3:8b는 로컬에서 무료. 6단계 중 LLM이 필요한 건 Step 4뿐이고, 나머지 5단계는 Python 스크립트로 결정적(deterministic) 처리한다.
