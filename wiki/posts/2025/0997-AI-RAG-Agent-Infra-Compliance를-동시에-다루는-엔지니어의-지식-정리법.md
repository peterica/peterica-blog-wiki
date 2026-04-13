---
id: "997"
title: "[AI] RAG·Agent·Infra·Compliance를 동시에 다루는 엔지니어의 지식 정리법"
url: "https://peterica.tistory.com/997"
published_at: "2025-12-06"
category: "LLM"
tags: ["llm", "rag", "ai-agent", "knowledge-base", "engineering-asset", "ai-infrastructure"]
keywords: ["LLM", "RAG", "Agent", "AI Infra", "Knowledge Base"]
word_count: 548
source_hash: "sha256:db5d35bf3f814a4e9b5302873d7d7f0381cd861e33e05c7fa2c91a0a221f9d83"
model: "gemma4:26b-a4b-it-q4_K_M"
generated_at: "2026-04-10T16:18:02Z"
---

# [AI] RAG·Agent·Infra·Compliance를 동시에 다루는 엔지니어의 지식 정리법

> 원본: [https://peterica.tistory.com/997](https://peterica.tistory.com/997)  ·  작성일: 2025-12-06  ·  카테고리: `LLM`

## 요약

LLM, RAG, Agent, AI 인프라 및 컴플라이언스를 동시에 다루는 엔지니어로서, 단순한 기술 습득을 넘어 이미 경험한 지식들을 체계적으로 구조화하는 방법을 제시합니다. 개인의 지식 베이스를 재사용 가능한 엔지니어링 자산이자 자신을 위한 파인튜닝 데이터셋으로 정의하며, Concept, System Design, Experiment & Failure 모듈로 분류하여 관리하고자 합니다.

**태그**: `llm` `rag` `ai-agent` `knowledge-base` `engineering-asset` `ai-infrastructure`

## 본문



[AI] Peterica의 AI공부와 비젼 정리

ㅁ 들어가며

ㅇ LLM, RAG, Agent, AI Infra, Compliance를 동시에 다루는 단계에 도달했다.

ㅇ

지금 필요한 것은 "새로운 기술"이 아니라 "이미 해온 것들의 구조화"다.

ㅇ

개인 Knowledge Base는 공부 노트가 아니라

재사용 가능한 엔지니어링 자산
이 되어야 한다.

ㅇ

나는 지금 나만의

AI Knowledge Base = 나 자신을 위한 파인튜닝 데이터셋
을 만들고 있다.



ㅁ API를 쓰는 단계는 이미 지났다

많은 사람들이 여전히 ChatGPT, Claude, Gemini 같은 LLM을
도구(API)
로만 사용한다.
하지만 어느 순간부터 나는 이런 질문을 더 많이 하게 됐다.


이 응답은 왜 이렇게 나왔을까?

Retrieval이 실패한 이유는 무엇일까?

이 Agent는 왜 무한 루프에 빠졌을까?

이 양자화 모델은 왜 이 구간에서만 성능이 무너질까?


이 질문들이 쌓이면서, 내 업무는 자연스럽게 다음 영역으로 확장됐다.


✅ LLM 엔지니어 + AI SRE + AI 플랫폼 아키텍트




나는 이제 단순한 API 사용자가 아니라,
LLM 시스템을 설계하고, 검증하고, 운영하는 쪽에 서 있다.



ㅁ 내가 실제로 다루고 있는 영역들

지금 내가 동시에 다루고 있는 영역은 다음과 같다.


LLM-MAS (Multi-Agent System)


Planner / Executor / Evaluator / SRE Agent / Security Agent

Policy Chain, LLM Gateway, Observability



RAG + VectorDB + 음성 파이프라인 (IntentFlow)


STT → Embedding → Weaviate → LLM → TTS



LLM 양자화 & 로컬 추론 최적화


GGUF, GPTQ, AWQ, Apple MPS 기반 추론



Vertical AI + 오픈소스 Compliance


코드 유사도, 라이선스 분류, Import-only 자동 판별



LLM 기반 DevOps 자동화


PR 리뷰 Agent, 로그 요약, 장애 원인 추론




이제 와서 보면, 이 조합은 꽤 희귀하다.


✅ "AI Infra + Agent + RAG + Compliance"를 동시에 다루는 포지션






ㅁ 그런데, 지금 내게 더 필요한 건 "새로운 기술"이 아니었다



어느 순간 깨달았다.


❝ 지금 내게 더 필요한 건 새로운 기술이 아니라,
이미 해온 것들을 체계적으로 정리해서
‘재사용 가능한 지식 베이스’로 만드는 것이다 ❞






나는 이미 수많은 실험을 해왔고,
수많은 실패를 겪었고,
수많은 구조를 설계했다.

하지만 그것들은 대부분 다음 상태였다.


머릿속에 흩어져 있거나

프로젝트 폴더 여기저기에 흩어져 있거나

MD, Jira, Wiki에 부분적으로 남아 있거나


이건
엔지니어 자산으로서 가장 위험한 상태
다.





ㅁ 그래서 나는 "AI Knowledge Base"를 다시 정의했다

많은 사람들이 Knowledge Base를 이렇게 생각한다.


공부 노트

정리용 문서

개인 위키


하지만 내가 정의한 Knowledge Base는 다르다.


✅ 재사용 가능한 Engineering Knowledge Base






나는 모든 문서를 다음 3가지 타입으로만 분류하기 시작했다.



ㅇ Concept Module (변하지 않는 기반 이론)


Transformer, Attention, Embedding, HNSW, Quantization

한 번 제대로 쓰면 평생 재사용 가능




ㅇ System Design Module (내가 설계한 구조)



LLM-MAS Agent 구조

LLM Gateway, Policy Chain

IntentFlow 아키텍처, OLIVE AI 검증 구조


👉 이 영역이 바로
나만의 자산
이다.



ㅇ Experiment & Failure Module (아무도 대신 못 쌓는 로그)


RAG Retrieval 실패

Agent 무한 루프

Quantization 성능 붕괴

OSS Hallucination 오탐


👉 이건 연봉과 직결되는 진짜 실력 로그다.



ㅁ 이 Knowledge Base는 결국 "나 자신을 위한 파인튜닝 데이터셋"이다

지금 내가 만들고 있는 이 Knowledge Base는 단순한 문서 모음이 아니다.


미래의 내가 RAG로 검색할 데이터

Agent가 참조할 Memory

LLM-MAS의 내부 Knowledge Source

AI 검증 시스템의 Ground Truth


즉,


❝ 나는 지금 나 자신을 위한 파인튜닝 데이터셋을 만들고 있는 셈 ❞




ㅁ 앞으로의 방향



앞으로 나는 이 Knowledge Base를 기반으로:


LLM-MAS Agent Pattern Reference 문서화

오픈소스 AI Verification 표준 설계서 정리

Quantization 벤치마크 리포트 공개

실패 사례 아카이브 구축


까지 확장해 나갈 계획이다.



ㅁ 마무리 한 줄


✅ "나는 이제 LLM을 쓰는 사람이 아니라, LLM 시스템을 설계하고 검증하고 운영하는 사람이다."






이 글이,
API 사용자를 넘어
AI 시스템 엔지니어로 성장하고 싶은 사람들에게
하나의 기준점이 되기를 바란다.

<!-- wiki-links -->
<!-- wiki-concepts -->
**관련 개념**: [[rag-system-architecture]] · [[context-engineering-agent-management]]


---

**태그**: #llm #rag #ai-agent #knowledge-base #engineering-asset #ai-infrastructure
