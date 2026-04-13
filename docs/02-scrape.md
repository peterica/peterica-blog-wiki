# 02. 스크래핑 (Scrape)

## 문제

각 포스트 URL에서 제목, 날짜, 본문, 카테고리를 추출해야 한다. 블로그 테마마다 HTML 구조가 다르다.

## 다중 셀렉터 폴백

하나의 CSS 셀렉터로는 모든 테마를 커버할 수 없다. 각 필드에 대해 우선순위 순으로 여러 셀렉터를 시도한다:

```yaml
# config.yaml
scrape:
  selectors:
    title:
      - 'meta[property="og:title"]'   # Open Graph (가장 안정적)
      - "h1.tit_post"                  # Tistory 기본 테마
      - ".article-header h1"           # 커스텀 테마
      - "h1"                           # 폴백
    body:
      - ".tt_article_useless_p_margin" # Tistory 기본
      - ".entry-content"               # WordPress 호환
      - "article"                      # 범용
```

위에서부터 매칭되는 첫 번째 셀렉터를 사용한다. 새 블로그에 적용할 때는 브라우저 DevTools로 셀렉터를 확인하고 config.yaml에 추가하면 된다.

## source_hash와 증분 처리

본문의 SHA-256 해시(`source_hash`)를 저장한다. 증분 실행(`--incremental`) 시 해시가 같으면 재파싱을 건너뛴다. 블로그 글이 수정된 경우에만 재처리된다.

```python
source_hash = sha256_hex(body)  # "sha256:a1b2c3..."
```

## Rate Limiting

`robots.txt` 준수를 위해 요청 간격을 1초로 제한한다 (`config.yaml`의 `scrape.rate_limit`). 429 응답 시 지수 백오프로 재시도한다.

## 실제 결과

987 URL 스크래핑에 약 6분 소요. 파싱 성공률 100%. 본문이 50자 미만인 페이지(이미지만 있는 글 등)는 자동 제외된다.
