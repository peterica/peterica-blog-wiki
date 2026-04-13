# 03. LLM 요약과 토큰 절약

## 문제

각 포스트의 본문을 읽고 요약(2~4문장), 태그(3~7개), 카테고리, 키워드를 생성해야 한다. 987건을 클라우드 API로 처리하면 비용이 든다.

## LLM Provider 추상화

`config.yaml`의 `llm.provider`로 세 가지 옵션을 지원한다:

| Provider | 비용 | 속도 | 설정 |
|---|---|---|---|
| `ollama` | 무료 (로컬) | ~36초/건 (qwen3:8b) | Ollama 설치 + 모델 다운로드 |
| `openai` | 유료 | ~5초/건 | API 키 |
| `anthropic` | 유료 | ~5초/건 | API 키 |

```yaml
llm:
  provider: "ollama"       # 로컬 무료
  model: "qwen3:8b"
  ollama_url: "http://localhost:11434/api/generate"
```

스크립트 내부에서는 `call_llm(prompt)` 하나로 통일된다. provider별 차이는 함수 내부에서 처리한다.

## 프롬프트 설계

```
당신은 한국어 블로그 요약/분류 전문가입니다.
아래 블로그 본문을 읽고 단일 JSON 객체만 출력하세요.

JSON 스키마:
{
  "summary": "2~4문장, 150~400자 한국어 요약",
  "tags": ["kebab-case", "3~7개"],
  "category": "DevOps | Cloud | LLM | ...",
  "keywords": ["고빈도 키워드 최대 5개"]
}
```

핵심 제약:
- **JSON만 출력**: 설명, 주석, 코드블록 금지. 후처리를 정규식(`\{[\s\S]*\}`)으로 JSON 추출.
- **카테고리 예시 다양화**: 초기에는 "LLM" 예시만 넣었더니 DevOps 글도 "LLM"으로 분류하는 anchor 편향 발생. 18종 예시로 다양화하여 해결.
- **본문 길이 제한**: `max_body_chars: 6000`으로 프롬프트 폭주 방지.

## 모델 선택: 왜 qwen3:8b인가

세 모델을 A/B 비교했다:

| 모델 | Rubric PASS | 카테고리 일치 | 속도 |
|---|---|---|---|
| qwen3:8b | 100% | 기준 | 36초/건 |
| gemma4:e4b | 100% | **40%** (심각한 LLM 편향) | 24초/건 |
| gemma4:26b | 100% | 60% | 10초/건 |

gemma4:e4b는 AWS/Jenkins 글을 "LLM"으로 오분류하는 치명적 편향이 있었다. gemma4:26b는 속도는 빠르지만 카테고리 일치율이 낮았다. **qwen3:8b가 분류 정확도와 안정성에서 최선**이었다.

## 증분 처리와 실패 복구

`--incremental` 플래그로 `source_hash`가 같은 레코드는 스킵한다. LLM API 한도(quota)에 걸리면 부분 결과를 저장하고 종료 코드 3을 반환한다. 재실행 시 자동으로 미처리분만 처리한다.

## 실제 결과

- 987건 중 334건: Codex(GPT-5) 처리 (~18분)
- 나머지 653건: qwen3:8b 로컬 처리 (~3시간 25분)
- Codex quota 한도로 하이브리드 전환. `--incremental` 덕분에 기존 결과 손실 없이 이어서 처리.
