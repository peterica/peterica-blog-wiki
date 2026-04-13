# CLAUDE.md -- Blog Wiki Builder Governance

## 프로젝트 개요

블로그 -> Obsidian 지식 위키 변환 파이프라인. Karpathy LLM-Wiki 3계층 구조를 블로그에 적용.

## 위키 페이지 규칙

### 페이지 유형과 위치

| 유형 | 경로 | 파일명 패턴 |
|---|---|---|
| MOC | `wiki/moc/` | `MOC-{Name}.md` |
| Concept | `wiki/concepts/` | `{kebab-case}.md` |
| Entity | `wiki/entities/` | `{kebab-case}.md` |
| Post | `wiki/posts/{year}/` | `{id}-{slug}.md` |

### Frontmatter 필수 필드

**Concept/Entity:**
```yaml
type: concept | entity
title: "한국어 제목"
parent: "[[MOC-Name]]"
tags: [moc-name, concept|entity]
confidence: high | medium | low
post_count: N
```

**MOC:**
```yaml
type: moc
title: "MOC 이름"
tags: [moc, name]
post_count: N
```

### 위키링크 규칙

- Obsidian 형식: `[[파일명]]` 또는 `[[파일명|표시텍스트]]`
- 링크 방향: `_index -> MOC -> Concept/Entity -> Post`
- 포스트 ID 링크: `[[0722-slug]]` (숫자 ID 단독 사용 금지)

### 본문 구조

**Concept 페이지:**
1. `## 한 줄 정의` -- blockquote로 1~2문장
2. `## 핵심 개념` -- 3~5문장 설명
3. `## 내가 경험한 것` -- 포스트 기반 실무 경험
4. `## 관련 포스트` -- 위키링크 목록
5. `## 관련 개념` -- 교차 참조

**Entity 페이지:**
1. `## 한 줄 정의`
2. `## 내가 사용한 맥락`
3. `## 관련 포스트`
4. `## 관련 개념`

## 스크립트 규칙

- 모든 설정은 `config.yaml`에서 읽는다. 스크립트에 하드코딩 금지.
- `_common.py`의 `cfg()` 함수로 설정 접근: `cfg('llm.provider')`
- LLM 호출은 provider 추상화 레이어를 통해서만 한다.
- 경로는 `ROOT` 기준 상대 경로를 사용한다.

## 품질 기준 (Rubric)

- 요약: 한국어 2~6문장, 120~500자
- 태그: kebab-case 3~7개, 중복 없음
- 날짜: ISO-8601 (YYYY-MM-DD)
- 전체 PASS rate: 98% 이상
- 위키 페이지: frontmatter 완전, 한 줄 정의 존재, 포스트 참조 존재

## 디렉토리 구조

```
peterica-blog-wiki/
├── config.yaml          # 모든 설정의 단일 소스
├── scripts/             # 파이프라인 스크립트
├── wiki/                # Obsidian vault (산출물)
├── data/                # 중간 데이터 (urls.txt, shards/)
├── docs/                # 파이프라인 과정 문서
└── reports/             # 품질 리포트
```
