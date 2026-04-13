---
type: concept
title: "모니터링 및 관측 가능성"
parent: "[[MOC-DevOps]]"
related: ["[[ci-cd-pipeline-design]]", "[[containerization-and-orchestration]]"]
tags: [devops, concept]
confidence: high
post_count: 1
---

# 모니터링 및 관측 가능성

## 한 줄 정의
> 시스템 상태를 실시간으로 추적하고, 데이터를 통해 문제를 예측 및 분석하는 기술

## 핵심 개념
Grafana, Uptime Kuma, Prometheus 등 도구를 사용해 시스템 성능, 장애, 사용량 등을 모니터링합니다. Four Golden Signals, RED Method 등 기준을 통해 서비스 신뢰성을 확보하며, 로그 분석과 지표 수집이 핵심입니다.

## 내가 경험한 것
블로그 저자는 k6를 활용한 부하 테스트 결과 시각화 및 SRE에서 SLI/SLO 기반 모니터링 구현 경험을 소개합니다.

## 관련 포스트
- [[0031-APM-PinPoint-APM]]

## 관련 개념
- [[ci-cd-pipeline-design]]
- [[containerization-and-orchestration]]
