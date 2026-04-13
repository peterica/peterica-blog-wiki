# 04. 위키 빌드 6단계

## 전제 조건

`data/posts.jsonl`이 준비된 상태. 각 레코드에 id, title, url, summary, tags, category, keywords가 있다.

## Step 1: 카테고리 재정리 (`wiki_categorize.py`)

LLM이 생성한 카테고리는 같은 주제를 다른 이름으로 분류한다: "DevOps", "CI/CD", "Infrastructure". 이것을 12개 MOC로 통합한다.

```yaml
# config.yaml
wiki:
  moc_map:
    DevOps: DevOps
    Jenkins: DevOps    # Jenkins는 DevOps MOC에
    Docker: Kubernetes # Docker는 Kubernetes MOC에
    LLM: LLM
```

실제 프로젝트에서는 69개 -> 12개로 축소했다 (84% 감소). 매핑에 없는 카테고리는 `fallback_moc`(기본: "Life")로 분류된다.

## Step 2: MOC 페이지 생성 (`wiki_moc.py`)

각 MOC에 대해 진입점 페이지를 생성한다:

```markdown
# DevOps
> 140개 포스트

## 주요 태그
`kubernetes` (43) / `jenkins` (28) / `docker` (23)

## 개념 지도
_(concept 생성 후 자동 채워짐)_

## 포스트
### 2025 (32)
- 2025-03-15 / **Jenkins Pipeline 최적화** -- ...
```

## Step 3: 위키링크 삽입 (`wiki_wikilink.py`)

각 포스트 md 파일의 하단에 `[[MOC-DevOps]]`와 `#tag` 링크를 자동 삽입한다. `<!-- wiki-links -->` 마커로 중복 삽입을 방지한다.

## Step 4: Concept/Entity LLM 생성 (`wiki_generate.py`)

**이 단계가 핵심이다.** Local LLM이 MOC별 포스트 메타데이터를 읽고, 공통 주제를 추출하여 Concept 페이지와 Entity 페이지를 생성한다.

### 토큰 절약: 메타데이터만 전달

포스트 전문이 아닌 **요약+태그+키워드**만 LLM에 전달한다:

```
[492] Ingress Controller 설치
  요약: Minikube 환경에서 nginx ingress controller를 설치하고...
  태그: kubernetes, ingress, minikube
  키워드: ingress, controller, minikube
```

건당 ~80자로, 전문 대비 84% 절감.

### 배치 분할

DevOps(147건), LLM(151건) 같은 대형 MOC는 한 번에 넣으면 타임아웃. 60건씩 배치 분할한다:

```python
MAX_POSTS_PER_BATCH = 60
batches = [posts[i:i + MAX_POSTS_PER_BATCH]
           for i in range(0, len(posts), MAX_POSTS_PER_BATCH)]
```

### 결과

122 Concepts + 61 Entities 생성. ~30분 소요 (qwen3:8b 로컬).

## Step 5: 크로스링크 (`wiki_crosslink.py`)

1. MOC 페이지의 "개념 지도" 섹션을 실제 concept/entity로 채운다.
2. `_index.md` 위키 진입점을 생성한다.
3. Orphan(아무도 참조하지 않는) 페이지를 리포트한다.

## Step 6: Obsidian 설정 (`wiki_obsidian.py`)

그래프 뷰 4색 그룹:
- 빨강: MOC (카테고리 허브)
- 청록: Concept (지식 단위)
- 파랑: Entity (기술/도구)
- 연두: Post (원본)

처음에는 Post가 MOC에 직접 연결되어 계층이 안 보였다. Post -> Concept 역링크를 삽입하고 MOC 직접 링크를 제거하여 `MOC -> Concept -> Post` 3계층이 시각적으로 드러나게 했다.
