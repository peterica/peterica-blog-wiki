# 01. URL 수집 (Discover)

## 문제

블로그의 전체 게시글 URL을 수집해야 한다. Tistory의 경우 두 가지 경로가 있다.

## 전략: Sitemap 우선, Archive 폴백

```python
# discover.py 핵심 로직
urls = discover_via_sitemap(limiter)      # /sitemap.xml 파싱
if len(urls) < 100:
    urls = discover_via_archive(limiter)  # /?page=N 순회
```

**Sitemap 방식** (`/sitemap.xml`):
- XML 파싱으로 URL 일괄 추출. 빠르고 정확하다.
- 단, 일부 블로그는 sitemap이 없거나 불완전하다.

**Archive 방식** (`/?page=N`):
- 아카이브 페이지를 1부터 순회하며 `<a href>` 태그에서 URL 추출.
- 빈 페이지가 3회 연속이면 종료 (무한 루프 방지).
- 모든 Tistory에서 동작하지만 느리다.

## 실제 결과

Peterica 블로그에서는 sitemap이 987개 URL을 정확히 반환했다. archive 폴백은 사용하지 않았다.

## 범용화: config.yaml

URL 패턴은 블로그마다 다르다. `config.yaml`의 `scrape.url_pattern` 정규식으로 포스트 URL을 식별한다:

```yaml
scrape:
  url_pattern: "^https://your-blog\\.tistory\\.com/(\\d+)$"
```

첫 번째 캡처 그룹이 포스트 ID가 된다. WordPress 등 다른 플랫폼은 패턴만 바꾸면 된다.

## 증분 갱신

`--incremental` 플래그로 기존 `urls.txt`에 신규 URL만 추가할 수 있다. 매일 자동 실행할 때 유용하다.
