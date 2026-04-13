# 06. Obsidian 설정과 그래프 뷰

## Obsidian Vault 구조

`wiki/` 디렉토리를 Obsidian vault로 열면 바로 사용할 수 있다.

```
wiki/
├── .obsidian/           # 설정 (자동 생성)
│   ├── app.json         # 기본 설정
│   ├── graph.json       # 그래프 뷰 색상 그룹
│   └── community-plugins.json
├── _index.md            # 위키 진입점
├── moc/                 # MOC 페이지 (12개)
├── concepts/            # Concept 페이지 (122개)
├── entities/            # Entity 페이지 (61개)
└── posts/               # 블로그 원본 (987개)
    ├── 2020/
    ├── 2021/
    └── ...
```

## 그래프 뷰 4색 그룹

`wiki_obsidian.py`가 `.obsidian/graph.json`에 4개 색상 그룹을 설정한다:

| 경로 | 색상 | 의미 |
|---|---|---|
| `path:moc` | 빨강 | 카테고리 허브 (12개, 큰 노드) |
| `path:concepts` | 청록 | 지식 단위 (122개) |
| `path:entities` | 파랑 | 기술/도구 (61개) |
| `path:posts` | 연두 | 블로그 원본 (987개, 작은 노드) |

## 3계층 시각화 최적화

처음 그래프를 열면 Post가 MOC에 직접 연결되어 계층이 안 보인다. 해결:

1. **Post -> Concept 역링크 삽입**: Concept 페이지의 `related_posts`에 있는 포스트에 `[[concept-slug]]` 역링크를 추가.
2. **MOC 직접 링크 제거**: Concept가 있는 포스트에서는 `[[MOC-*]]` 직접 링크를 제거.
3. **결과**: `MOC(빨강) -> Concept(청록) -> Post(회색)` 3계층이 그래프에서 클러스터별로 시각 분리.

## 추천 플러그인

| 플러그인 | 용도 |
|---|---|
| **Dataview** | frontmatter 기반 동적 테이블. MOC에서 concept 목록 자동 생성 |
| **Tag Wrangler** | 태그 일괄 편집, 이름 변경 |
| **Graph Analysis** | 그래프 통계, 중심성 분석 |

## 직접 열어보기

```bash
# Obsidian 설치 후
# File -> Open Vault -> wiki/ 폴더 선택
```

왼쪽 사이드바에서 `_index.md`를 열면 전체 지식 지도를 볼 수 있다. 그래프 뷰(Ctrl/Cmd+G)에서 색상별 클러스터를 확인할 수 있다.
