---
id: "183"
title: "[Kubernetes] Kubernetes환경에서 graceful shutdown이란"
url: "https://peterica.tistory.com/183"
published_at: "2022-06-26"
category: "Kubernetes"
tags: ["kubernetes-graceful-shutdown", "spring-boot", "sigterm-sigkill", "502-error", "auto-scaling"]
keywords: ["Graceful Shutdown", "Kubernetes", "SIGTERM", "SIGKILL", "502 Error"]
word_count: 644
source_hash: "sha256:f43d65c6f64b8a88bf7f2f8d2f5c0249ff0341d1f1b9937d0826c338eb1f1dff"
model: "qwen3:8b"
generated_at: "2026-04-10T12:07:27Z"
---

# [Kubernetes] Kubernetes환경에서 graceful shutdown이란

> 원본: [https://peterica.tistory.com/183](https://peterica.tistory.com/183)  ·  작성일: 2022-06-26  ·  카테고리: `Kubernetes`

## 요약

Kubernetes 환경에서 Spring Boot 애플리케이션의 정상 종료를 위해 Graceful Shutdown이 필요하다. SIGTERM과 SIGKILL의 차이를 이해하고, 502 에러를 방지하기 위한 구현 방법을 설명했다.

**태그**: `kubernetes-graceful-shutdown` `spring-boot` `sigterm-sigkill` `502-error` `auto-scaling`

## 본문





ㅁ 개요

ㅇ Kubernetes가 배포 절차를 수행해 주지만 컨테이너 안에서

Spring Boot 애플리케이션의 정상적인 종료를 위해서는 Graceful shutdown이 필요하다.

ㅇ 트래픽에 따라 AutoScaling 되면서 502error가 발생하기 때문이다.

ㅇ 502 Error가 발생하는 과정을 설명하고 graceful shutdown의 적용필요성을 정리하였다.





ㅁ Graceful shutdown이란

우아한 종료라고 직역할 수 있을 것이다. 이 말을 생각해보면, 마무리를 잘하여 좋게 끝난다는 의미를 내포하고 있다. 다시 말해 할일을 다 마치고 우아하게 종료하는 것이다. 예를 들어 생각해보자. 우리가 문서작업을 할 때에 우리가 원하는 작업이 정상적으로 완료되면, 파일을 저장하고 해당 문서편집파일을 종료하게 된다 하지만 우아하지 않은 종료인 상황은 그냥 단전이 되어 그냥 꺼져 문서작업 데이터가 손실되는 상황일 것이다.

kubernetes 환경의 Spring에서 우아한 종료하고 한다면, Pod가 종료하는 동안 데이터는 데이터베이스에 성공적으로 저장되고, 네트워크 연결, 데이터베이스 연결 등이 성공적으로 닫혀야 할 것이다.





ㅁ SIGTERM, SIGKILL의 차이

ㅇ graceful shutdown을 이해하기 위해서 SIGTERM, SIGKILL에 대한 이해가 필요하다.

ㅇ 리눅스 등 환경에서 프로세스를 죽일 때에 kill을 사용하는데 크게 종류는 다음과 같다.

-9 : 강제종료
-15 : 정상종료

-15(SIGTERM)
:

자신이 하던 작업을 정상적으로 종료하는 절차를 진행하는 옵션이다. 다시 말해, 시스템 종료하기 전에 꼭 처리해야할 작업을 처리한 후에 종료하도록 일종의 trigger를 작동시킬 수 있는 여지는 주는 옵션인 것이다.

구체적으로 설명하면, graceful shutdown이 적용이 되어 있는 상황에서, -15이 오면, 우선적으로 외부에서 들어오는 요청을 받아들이는 Serverlet 객체(ApplicationListener)를 정지하여 더 이상의 요청을 받아들이지 않고 기존 진행되는 요청들이 끝날 때까지 기다렸다가 종료하게 된다. 그래서 -15로 종료하는 과정에서는 502가 아니라 연결거부상황이 발생하게 된다. graceful shutdown이 적용되어 있지 않다면,
시스템 종료 직전에 처리해야할 작업이 선언되어 있지 않기 때문에 즉시 종료와 같은 상황이 된다.




-9(SIGKILL)
:

진행 중이 작업이나 저장되지 않은 데이터와 상관없이, 즉시 프로세스를 종료하게 된다.

-9로 종료하게 되면, SpringBoot가 종료하는 찰라의 과정에서 요청을 받아들이는 객체는 살아있지만 DB자원등이 해제되면서 502가 발생할 수 있게 된다. 즉, 진행과정에서 필요자원의 해제로 인해 서버는 실행 불능의 상태가 발생하고 서버 exception 처리되는 것이다.



SIGTERM과 SIGKILL 관련 재미있는 그림이 있어 남겨본다.



SIGTERM은 1431이 죽기전에 자식들에게 유언을 남길 수 있는 시간을 주는 것이다.



SIGKILL은 인사할 시간도 없이 강제로 종결해 버린다





함께 보면 좋은 링크:
https://2kindsofcs.tistory.com/53





Graceful Shutdown과 SIGINT/SIGTERM/SIGKILL

1. Graceful Shutdown이란 무엇인가? 우아한 종료라고 직역하면 뭔가 어색하지만, 그 역의 경우를 생각해보면 제법 어울리는 표현이라는 생각이 든다. 우아한 종료는 프로그램이 종료될 때 최대한 side

2kindsofcs.tistory.com





ㅁ kubernetes ingress, service, pod 관계

kubernetes의 환경을 구체적으로 살펴보도록 하겠다. kubernetes로 트래픽이 들어오면, ingress -> service -> pod로 요청이 전달되는 과정을 거치게 된다.



AWS 환경에서 사용하고 있는 경우, Internet -> DNS -> Route53 -> LB -> 대상그룹 -> Ingress-controller -> nginx -> Service -> Pod들에게 전달된다. ingress 설정에도 개별 POD들의 정보가 아닌 serviceName을 지정하도록 되어있다.



graceful shutdown이 적용되어 있지 않은 경우, 새로운 Pod가 생성되고, 이전 pod가 terminated되면서 kubelet은 pod에 SIGTERM 신호를 보내게 되는데, ingress-controller의 설정이 갱신되기 전에 종료된 pod에 요청을 보내게 되면서 502 에러가 발생한다.

502 에러가 발생하지 않게 하기 위해서는 더 이상 새로운 요청을 받지 않도록 graceful Shutdown의 적용이 필요하다.



kubernetes환경에서의 pod 종료 과정에서 graceful shutdown 과정
과

Springboot에서 graceful shutdown 적용 방법
에 대해서 다음에 살펴보도록 하겠다.





ㅁ 함께 보면 좋은 사이트

ㅇ SpringBoot 2.3 이전 Embedded Tomcat GracefulShutdown 구현 및 테스트 방법





Graceful Shutdown Spring Boot Applications

This guide walks through the process of graceful shutdown a Spring Boot application. The implementation of this blog post is originally created by Andy Wilkinson and adapted by me to Spring Boot 2. The code is based on this GitHub comment. Introduction A l

blog.marcosbarbero.com



ㅇ kubernetes를 이용한 서비스 무중단 배포





kubernetes를 이용한 서비스 무중단 배포

Kubernetes는 컨테이너 오케스트레이션 영역에서 거의 표준으로 자리 잡은 오픈소스 시스템입니다. kubernetes를 사용하게 되면 여러대의 노드를 하나의 클러스터로 묶어서 사용가능하게 됩니다. 클

tech.kakao.com



ㅇ SpringBoot 2.3 이상 GracefulShutdown





Web Server Graceful Shutdown in Spring Boot | Baeldung

Learn how to take advantage of the new graceful shutdown feature in Spring Boot 2.3

www.baeldung.com



ㅇ Spring-Webflux-Netty-환경에서의-GracefulShutdown-구현





Spring Webflux - Netty 환경에서의 GracefulShutdown 구현

Eureka 환경에서 client들이 Registry 를 local cache에 저장하는 이유로 무중단 배포에 차질이 있었다. 이를 해결하기 위한 여러 방법을 모색하였고, 그 중 하나가 GracefulShutdown 을 이용하는 것이었다. 하

velog.io







[Stepping experience] Graceful Shutdown of Spring Webflux (Graceful Shutdown) - Fear Cat



blog.fearcat.in

<!-- wiki-links -->
<!-- wiki-concepts -->
**관련 개념**: [[kubernetes]]

---

**태그**: #kubernetes-graceful-shutdown #spring-boot #sigterm-sigkill #502-error #auto-scaling
