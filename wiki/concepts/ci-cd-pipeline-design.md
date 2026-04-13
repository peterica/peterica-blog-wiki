---
type: concept
title: "CI/CD 파이프라인 설계"
parent: "[[MOC-DevOps]]"
related: ["[[infrastructure-as-code]]", "[[devops-automation-practices]]"]
tags: [devops, concept]
confidence: high
post_count: 5
---

# CI/CD 파이프라인 설계

## 한 줄 정의
> 코드 변경을 자동화하여 빌드, 테스트, 배포를 연속적으로 수행하는 프로세스

## 핵심 개념
GitHub Actions, Jenkins, Bamboo 등의 도구를 활용해 개발 단계에서 배포까지 자동화합니다. 이는 팀 협업 효율성 향상과 배포 오류 감소에 기여하며, 지속적인 통합과 배포를 통해 빠른 피드백 루프를 형성합니다.

## 내가 경험한 것
저자는 GitHub Actions에서 Node.js 버전 업그레이드 문제 해결, Jenkins Pipeline을 통한 주기적 쉘 스크립트 실행 등 CI/CD 프로세스 최적화 경험을 공유합니다.

## 관련 포스트
- [[0716-Git-GitHub-Actions-노드-버전-문제-해결하기-node20-업그레이드-방법]]
- [[0814-Docker-Uptime-Kuma-사용법]]
- [[0861-Jenkins-pipeline에서-SSH-Agent를-이용한-원격서버-관리방법]]
- [[0899-Jenkins-Jenkins-Pipeline으로-쉘-스크립트를-주기적으로-실행하기]]
- [[0945-SRE-SRE-참고서로서-The-Art-of-Capacity-Planning]]

## 관련 개념
- [[infrastructure-as-code]]
- [[devops-automation-practices]]
