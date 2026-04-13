---
id: "201"
title: "[k8s] EKS를 이용한 Kubernetes 구축, EKS 생성"
url: "https://peterica.tistory.com/201"
published_at: "2022-07-29"
category: "Kubernetes"
tags: ["aws-eks", "kubernetes-setup", "aws-cli", "eksctl", "cloud-computing", "k8s-cluster"]
keywords: ["EKS", "Kubernetes", "AWS CLI", "eksctl", "AWS"]
word_count: 463
source_hash: "sha256:74d04b1b8bbb697093fb4031dddad9516bb4774e027ab884e4cf97a1adc200b2"
model: "qwen3:8b"
generated_at: "2026-04-10T12:18:27Z"
---

# [k8s] EKS를 이용한 Kubernetes 구축, EKS 생성

> 원본: [https://peterica.tistory.com/201](https://peterica.tistory.com/201)  ·  작성일: 2022-07-29  ·  카테고리: `Kubernetes`

## 요약

AWS EKS를 활용한 Kubernetes 클러스터 구축 방법을 자세히 설명합니다. eksctl과 AWS CLI를 사용한 설정 과정, 액세스 키 및 키페어 생성, AWS Config 설정을 포함하며, EKS 생성 비용 및 클러스터 삭제 방법도 다룹니다. 핵심 키워드: EKS, Kubernetes, AWS CLI, eksctl

**태그**: `aws-eks` `kubernetes-setup` `aws-cli` `eksctl` `cloud-computing` `k8s-cluster`

## 본문



ㅁ 개요

ㅇ AWS EKS를 이용하여 kubernetes 구축과정 정리하였다.



## 순서 ##
- EKS란
- EKS를 구성하는 방법
- 사용자 추가
- 액세스 키 생성
- 키페어 생성
- AWS CLI 설치
- AWS Config 설정
- eksctl 설치 방법
- eksctl 통한 EKS 생성





ㅁ EKS란

ㅇ Amazon Elastic Kubernetes Service(Amazon EKS)는 Kubernetes를 실행하는 데 사용할 수 있는 관리형 서비스이다.
ㅇ
AWS Kubernetes 제어 플레인 또는 노드를 설치, 작동 및 유지 관리할 필요가 없다.

ㅇ
Kubernetes는 컨테이너화된 애플리케이션의 배포, 조정 및 관리 자동화를 위한 오픈 소스 시스템이다.

ㅇ
시간당 0.1$달러 요금이 부과되고 무중단 한달 운영하면 78달러가 부과되며,

EKS이외의 요금은 별도로 계산
된다



ㅁ EKS를 구성하는 방법

ㅇ EKS를 사용해서 클러스터 구성하는 방법은 2가지 이다.
1. eksctl 사용하여 EKS를 생성

2. AWS Management Console 사용하기





ㅁ 사용자 추가



ㅇ EKS를 테스트 하기 위해 어드민 권한을 준 eks_peterica 계정을 생성하였다.





ㅁ 액세스 키 생성



ㅇ 과정에서는 생략하였지만 K8S 관리 인스턴스를 생성하였고, 이  인스턴스의 AWS 접속 권한을 설정하기 위해 액세스 키를 생성하였다.





ㅁ 키페어 생성



ㅇ EC2 > 키 페어 경로 진입하여 aws-login-key이라는 키 페어를 생성해 주었다.

ㅇ eks 설정 시 필요한 키페어이다.





ㅁ AWS CLI 설치

ㅇ AWS 인스턴스 생성 시 AWS CLI는 기본 설치가 되어 있다.

ㅇ 로컬에서 AWS CLI를 사용해서 AWS Config 설정을 해야 eks 클러스터에 접속할 수 있다.

ㅇ 로컬 환경에 따라 Linux, macOS, Windows 설치파일이 제공된다.

ㅇ
이곳
으로 이동하여 설치하면 된다.





최신 버전의 AWS CLI 설치 또는 업데이트 - AWS Command Line Interface

설치 관리자의 아무 위치에서나 Cmd+L을 눌러 설치에 대한 디버그 로그를 볼 수 있습니다. 이렇게 하면 로그를 필터링하고 저장할 수 있는 로그 창이 열립니다. 로그 파일도 /var/log/install.log에 자

docs.aws.amazon.com







ㅁ AWS Config 설정



[ec2-user@ip-172-31-43-214 ~]$ aws configure
AWS Access Key ID [None]: AKI**
AWS Secret Access Key [None]: TKP**
Default region name [None]: ap-northeast-2
Default output format [None]:

[ec2-user@ip-172-31-43-214 ~]$ aws sts get-caller-identity
{
    "Account": "94**",
    "UserId": "AID**",
    "Arn": "arn:aws:iam::94**:user/eks_peterica"
}

ㅇ aws configure 명령어로 aws 접속정보를 설정한다.

ㅇ aws sts get-caller-identity 명령어로 aws 접속정보를 확인한다.





ㅁ eksctl 설치 방법

ㅇ eksctl 설치 페이지로
이동
설치한다.

# eksctl 릴리스 다운로드
curl --silent --location "https://github.com/weaveworks/eksctl/releases/latest/download/eksctl_$(uname -s)_amd64.tar.gz" | tar xz -C /tmp

# 압축 해제
sudo mv /tmp/eksctl /usr/local/bin

# 설치확인
eksctl version







ㅁ eksctl 통한 EKS 생성

eksctl create cluster \ 
--name k8s-demo \
--region ap-northeast-2 \
--version 1.22 \
--nodegroup-name work-nodes \
--nodes 3 \
--nodes-min 1 \
--nodes-max 3 \
--node-type t3.medium \
--node-volume-size=20 \
--with-oidc \
--ssh-access \
--ssh-public-key aws-login-key \
--managed







ㅇ eks 설치가 완료되었다.





ㅁ kubectl 작동 테스트



ㅇ kubectl get po -n kube-system 명령어로 작동 테스트를 진행하였다.





ㅁ 생성된 EKS 삭제방법

eksctl delete cluster --name k8s-demo



ㅇ 과금관계로 테스트 후 바로 삭제하는 것이 좋다.





ㅁ 함께 보면 좋은 사이트

ㅇ AWS Cli 설치:

https://docs.aws.amazon.com/ko_kr/cli/latest/userguide/getting-started-install.html

ㅇ ec2 요금:
https://aws.amazon.com/ko/ec2/spot/pricing/

ㅇ eskctl 설치:

https://docs.aws.amazon.com/ko_kr/eks/latest/userguide/getting-started-eksctl.html

ㅇ eks spot instance 관련:

https://aws.amazon.com/ko/blogs/compute/cost-optimization-and-resilience-eks-with-spot-instances/

ㅇ eks 시작:
https://docs.aws.amazon.com/ko_kr/eks/latest/userguide/getting-started-eksctl.html

<!-- wiki-links -->
<!-- wiki-concepts -->
**관련 개념**: [[eks]] · [[kubernetes]]

---

**태그**: #aws-eks #kubernetes-setup #aws-cli #eksctl #cloud-computing #k8s-cluster
