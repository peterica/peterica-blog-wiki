---
id: "492"
title: "인그레스(Ingress) 컨트롤러로 Minikube에서 인그레스 설정하기"
url: "https://peterica.tistory.com/492"
published_at: "2024-01-17"
category: "Kubernetes"
tags: ["ingress-configuration", "minikube-setup", "kubernetes-tutorial", "docker-networking", "hyperkit-troubleshooting"]
keywords: ["Ingress", "Minikube", "Kubernetes", "Hyperkit", "Docker"]
word_count: 778
source_hash: "sha256:3ef8a6bdde063d055d6b29fd04a99c84f0260744e85f75d32eee806f0d69df0a"
model: "qwen3:8b"
generated_at: "2026-04-10T14:17:51Z"
---

# 인그레스(Ingress) 컨트롤러로 Minikube에서 인그레스 설정하기

> 원본: [https://peterica.tistory.com/492](https://peterica.tistory.com/492)  ·  작성일: 2024-01-17  ·  카테고리: `Kubernetes`

## 요약

Minikube에서 NGINX Ingress 컨트롤러를 설정해 클러스터 외부에서 파드 접근을 구현한 후, Docker 네트워크 문제로 인한 트러블슈팅을 통해 Hyperkit 드라이버로 전환하여 정상 작동을 확인했습니다. Ingress 리소스 생성 및 테스트 과정을 다루고 있습니다.

**태그**: `ingress-configuration` `minikube-setup` `kubernetes-tutorial` `docker-networking` `hyperkit-troubleshooting`

## 본문



[kubernetes] 쿠버네티스 목차

ㅁ 들어가며

클러스터 외부에서 파드로 접근할 때 주로 L7 영역의 통신을 담당하는 Ingress를 공부를 하였다. 쿠버네티스의 공식문서를 살펴 보는 중
NGINX 인그레스(Ingress) 컨트롤러로 Minikube에서 인그레스 설정하기
라는 좋은 실습내용이 있어서 내용을 정리하였다.

실습 과정 중 minikube driver가 docker인 경우 ingress 테스트가 불가하여 트러블 슈팅으로 hyperkit으로 변경하는 작업을 같이 수행하게 되었다.
이 과정은

Minikube 드라이브 Hyperkit 설치하기
에 정리함.



ㅁ 인그레스 컨트롤러 활성화

$ minikube addons enable ingress



ㅇ 인그레스를 활성화 활성화한다.




앱 생성 및 Service 연결까지


ㅁ NGINX 인그레스 컨트롤러 확인

$ kubectl get pods -n ingress-nginx





ㅁ hello, world 앱 배포하기

$ kubectl create deployment web --image=gcr.io/google-samples/hello-app:1.0





ㅁ Deployment 노출, Service 생성

$ kubectl expose deployment web --type=NodePort --port=8080



ㅇ 서비스 web이 생성되었다.



ㅁ Service 생성확인

$ kubectl get service web





ㅁ minikube service url 연결

$ minikube service web --url





ㅁ URL 확인

$ curl http://127.0.0.1:50399
Hello, world!
Version: 1.0.0
Hostname: web-548f6458b5-pqtn2






Ingress 생성




ㅁ Ingress 생성

apiVersion: networking.k8s.io/v1
  kind: Ingress
  metadata:
    name: example-ingress
    annotations:
      nginx.ingress.kubernetes.io/rewrite-target: /$1
  spec:
    rules:
      - host: hello-world.info
        http:
          paths:
            - path: /
              pathType: Prefix
              backend:
                service:
                  name: web
                  port:
                    number: 8080



ㅇ

example-ingress.yaml 생성한다.



ㅁ Apply

$ kubectl apply -f example-ingress.yaml
ingress.networking.k8s.io/example-ingress created





ㅁ Ingress 확인

$ kubectl get ingress
NAME              CLASS   HOSTS              ADDRESS        PORTS   AGE
example-ingress   nginx   hello-world.info   192.168.49.2   80      5m37s

ㅇ 도커의 네트워크를 이해 차원에서 Docker network를 살표보겠다.



ㅁ Docker network

$ docker network ls
NETWORK ID     NAME                          DRIVER    SCOPE
f39c92ffeb4f   aged                          bridge    local
218a2510c4c5   bridge                        bridge    local
7c2f47b7c251   host                          host      local
18c489a67724   jenkins-quick-start_default   bridge    local
c979884d4a31   minikube                      bridge    local
2320feb87aa6   mongodb_default               bridge    local
797806d61a0d   none                          null      local

ㅇ 현재 Docker에서 사용 중인 network 목록이다.



$ docker network inspect minikube | jq                                                           ✔  7251  10:57:21
[
  {
    "Name": "minikube",
    "Id": "c979884d4a3111f1292e9fea6bb6178593a71f9492cb344b7e13aec92ceaba1a",
    "Created": "2022-02-20T10:24:52.111593012Z",
    "Scope": "local",
    "Driver": "bridge",
    "EnableIPv6": false,
    "IPAM": {
      "Driver": "default",
      "Options": {},
      "Config": [
        {
          "Subnet": "192.168.49.0/24",
          "Gateway": "192.168.49.1"
        }
      ]
    },
    "Internal": false,
    "Attachable": false,
    "Ingress": false,
    "ConfigFrom": {
      "Network": ""
    },
    "ConfigOnly": false,
    "Containers": {
      "23c826eda952fd3cad3ec983dc3064644e47961339147cec6d9064c861a630b3": {
        "Name": "minikube-m02",
        "EndpointID": "35d0f1ba76d839759fd4fe724e707f9c7b2be09cfaa07f30b5bbaea33a60db60",
        "MacAddress": "02:42:c0:a8:31:03",
        "IPv4Address": "192.168.49.3/24",
        "IPv6Address": ""
      },
      "5f167319e3fde422f299b80113190b53963bb49f4830e27a8e0211987863b97c": {
        "Name": "minikube",
        "EndpointID": "ca3ddf20c429434c10a71b0d390baa1ed9d42874b07016f72afcb90e5359f853",
        "MacAddress": "02:42:c0:a8:31:02",
        "IPv4Address": "192.168.49.2/24",
        "IPv6Address": ""
      }
    },
    "Options": {
      "--icc": "",
      "--ip-masq": "",
      "com.docker.network.driver.mtu": "1500"
    },
    "Labels": {
      "created_by.minikube.sigs.k8s.io": "true"
    }
  }
]

ㅇ iptime을 사용하는 홈네트워크에 비유하자면,
ㄴ iptime = minikube gateway, 192.168.49.1

ㄴ com1  = minikube container

ㄴ com2 = minikube-m02 container



ㅇ 192.168.49.2/24 CIDR를 분석하면,




내용

값



첫 번째 IP

192.168.49.0



주소마지막 IP

192.168.49.255



주소IP 수

256



서브넷 범위

255.255.255.0



와일드 카드

0.0.0.255






ㅇ 정리하면, docker network 중  bridge 타입의 minikube network는 2개의 노드에 256의 IP를 제공해 주고 있다.

ㅇ bridge 비유를 들자면, 집에 있는 Mac mini의 wifi를
공유 접속
을 하면 접속한 컴퓨터와 네트워크가 연결된다.

ㄴ 접속한 컴퓨터도 NetworkInterface에 의해 IP를 가지고 상위인 Mac mini와 네트워크가 연결된다.





ㅁ Hosts 편집, Host network로 재귀

$ sudo vi /etc/hosts
##
# Host Database
#
# localhost is used to configure the loopback interface
# when the system is booting.  Do not change this entry.
##
127.0.0.1	localhost
255.255.255.255	broadcasthost
::1             localhost

192.168.49.2 hello-world.info  <====== 추가

# Added by Docker Desktop
# To allow the same kube context to work on the host and the container:
127.0.0.1 kubernetes.docker.internal
# End of section

ㅇ 위에서 minikube도 컨테이너의 일종이다. 그래서 bridge를 통해 host의 네트워크에 연결되어 있고, ingress 테스트를 위해 hello-workd.info 도메인을 자체 network로 재귀시켰다.

ㅇ 만약 host의 로컬 DNS에 없으면 Internet DNS를 검색 시 IP를 찾을 수 없다.





ㅁ curl를 통한 Ingress 접속 테스트

$ curl hello-world.info

ㅇ 실패다.

ㅇ 접속이 되지 않았다.

ㅇ 원인은 minikube의 container runtime driver가 docker이기 때문이었다.

ㅇ driver를 교체하여 minikube를 다시 실행하였다.





ㅇ 이 과정은
Minikube 드라이브 Hyperkit 설치하기
에 정리함.

ㅇ driver로 변경하고 Ingress 접속 테스트까지 다시 수행함.

ㅇ host의 ip는 192.168.66.4으로 변경되었다.





$ curl hello-world.info
Hello, world!
Version: 1.0.0
Hostname: web-57f46db77f-7sbrm

ㅇ 성공하였다.





ㅁ 두 번째 디플로이먼트 생성 및 확인

# 생성
$ kubectl create deployment web2 --image=gcr.io/google-samples/hello-app:2.0

# 확인
$ k get po
NAME                    READY   STATUS    RESTARTS   AGE
web-57f46db77f-7sbrm    1/1     Running   0          36m
web2-866dc4bcc8-4cr45   1/1     Running   0          64s



ㅁ두 번째 디플로이먼트 Service 생성

$ kubectl expose deployment web2 --port=8080 --type=NodePort
service/web2 exposed





ㅁ Ingress yaml 수정

- path: /v2
            pathType: Prefix
            backend:
              service:
                name: web2
                port:
                  number: 8080



ㅇ example-ingress.yaml에 path v2를 추가함.



ㅁ Ingress Apply

$ k apply -f example-ingress.yaml



ㅁ Ingress 테스트

$ curl hello-world.info
Hello, world!
Version: 1.0.0
Hostname: web-57f46db77f-7sbrm


$ curl hello-world.info/v2
Hello, world!
Version: 2.0.0
Hostname: web2-866dc4bcc8-4cr45







ㅁ 테스트 완료 후 minikube 정리

$ minikube stop
✋  "minikube" 노드를 중지하는 중 ...
🛑  1개의 노드가 중지되었습니다.

$ minikube delete
🔥  hyperkit 의 "minikube" 를 삭제하는 중 ...
💀  "minikube" 클러스터 관련 정보가 모두 삭제되었습니다



ㅁ 함께 보면 좋은 사이트

ㅇ
minikube driver hyperkit 공식문서

ㅇ
NGINX 인그레스(Ingress) 컨트롤러로 Minikube에서 인그레스 설정하기

<!-- wiki-links -->
<!-- wiki-concepts -->
**관련 개념**: [[kubernetes-networking-and-ingress]] · [[kubernetes-ingress-configuration]]


---

**태그**: #ingress-configuration #minikube-setup #kubernetes-tutorial #docker-networking #hyperkit-troubleshooting
