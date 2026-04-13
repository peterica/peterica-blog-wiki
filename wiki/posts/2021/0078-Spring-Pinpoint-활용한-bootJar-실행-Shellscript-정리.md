---
id: "78"
title: "[Spring] Pinpoint 활용한 bootJar 실행  Shellscript 정리"
url: "https://peterica.tistory.com/78"
published_at: "2021-01-08"
category: "DevOps"
tags: ["spring-boot", "pinpoint-agent", "shell-script", "local-testing", "devops", "application-monitoring"]
keywords: ["Pinpoint", "Spring Boot", "shell script", "local testing", "application monitoring"]
word_count: 375
source_hash: "sha256:5808df5ea96de684649d33055f0c145e97d9864ac7acb8374e9e0f86bddcc5a9"
model: "qwen3:8b"
generated_at: "2026-04-10T11:43:02Z"
---

# [Spring] Pinpoint 활용한 bootJar 실행  Shellscript 정리

> 원본: [https://peterica.tistory.com/78](https://peterica.tistory.com/78)  ·  작성일: 2021-01-08  ·  카테고리: `DevOps`

## 요약

Spring Boot 애플리케이션을 로컬에서 테스트하기 위한 Pinpoint 통합 shell 스크립트를 정리했습니다. 쉘 스크립트는 실행/중지/상태 확인 기능을 포함하며, Pinpoint 에이전트와 연동해 모니터링이 가능합니다. 빌드 후 자동 복사 및 재시작 로직이 포함되어 있어 개발 생산성을 높였습니다.

**태그**: `spring-boot` `pinpoint-agent` `shell-script` `local-testing` `devops` `application-monitoring`

## 본문



로컬에 개발환경을 구축하면서 사용하였던 bootJar 실행 shell문을 정리하였습니다.



로컬환경 세팅 이유

Intellij에서 개발한 것을 개발계에 올리기 직전에 로컬에서 테스트하기 위해 환경을 구성하였습니다.

로컬에 PinPoint를 구축하여서,

프론트개발자가 로컬에서 테스트  진행 시 모니터링 및 버그확인이 아주 쉬웠습니다.



로컬 빌드 방법

Intellij에서 bootJar 빌드를 마치면 jar파일이 생성되고,

쉘을 통해 jar 복사 및 SpringBoot 재가동하는 쉘을 만들었습니다.



Shell의 개요

크게 3개 파트로 구성하였습니다.
- 재사용을 위한 환경세팅 부분,
- function 선언부분
- case문으로 실행 분기를 하는 부분입니다.





bootJar.sh의 내용

#!/bin/bash

# app 구분자
readonly APP_NAME="appName"

#jar
readonly DAEMON="/Users/deseo/server/bootJar.jar"

# pinpoint 설정
readonly PINPOINT_APP_NAME="app_name"
readonly PINPOINT_APP_GROUP="app_group"
readonly AGENT_PATH="/Users/deseo/study/pinpoint/pinpoint-agent"

# spring 설정
readonly SPRING_PROFILE="dev"
readonly JAVA_OPT="-Xms512m -Xmx1024m -XX:PermSize=256m -XX:MaxPermSize=1024m"

# log 설정
readonly LOCAL_LOG_NAME="app.log"

# 시작
# 이미 작동 중이면 stop을 실행한다. 
start()
{
    echo "----------------------"
    echo "Starting  $APP_NAME"
    if [ -n $(get_status) ]; then
        echo "$APP_NAME is already running"
        echo "try kill server..."
        stop
    fi

    # nohup java -jar -Dspring.profiles.active=$SPRING_PROFILE $JAVA_OPT $DAEMON > /dev/null 2>&1 &
    nohup java -jar -javaagent:$AGENT_PATH/pinpoint-bootstrap-1.8.4.jar \
                -Dpinpoint.agentId=$PINPOINT_APP_GROUP \
                -Dpinpoint.applicationName=$PINPOINT_APP_NAME \
                -Dspring.profiles.active=$SPRING_PROFILE \
                -Dserver.port=7070 -Dprofile=real \
                -Dproc.name=$APP_NAME  $JAVA_OPT \
                $DAEMON >> $LOCAL_LOG_NAME  2>&1 &

    INDEX=10
    while [ -z $(get_status) ]
    do
      sleep 1;
      echo ${get_status}
      INDEX=$((INDEX - 1))
      echo "$INDEX 가동 대기중"
      if [ ${INDEX} -eq 0 ]; then
        break
      fi
    done

    if [ -n $(get_status) ]; then
        echo " - Starting..."
        echo " - Created Process ID in $(get_status)"
        echo " - PID is $(get_status)"
    else
        echo " - failed to start."
    fi
}

# 중지
stop(){
    echo "----------------------"
    echo "Stoping  $APP_NAME"
    local PID=$(get_status)
    
    if [ -z ${PID} ];
    then
 	echo "$APP_NAME was not running."
    else
	kill -15 $PID
	sleep 3
	echo " Shutdown ...."
    fi
}

# 상태확인
status()
{
#    echo "[$(get_status)]";
    local PID=$(get_status)
    if [ -z ${PID} ]; 
    then
        echo "$APP_NAME is stopped"
    else
        echo "$APP_NAME is running"
    fi
}


# 프로세스 확인
get_status()
{
    ps ux | grep $APP_NAME | grep -v grep | awk '{print $2}'
}

get_jar()
{
    # jar 복사 경로
    cp ~/git/project/build/libs/bootJar.jar /Users/deseo/server/bootJar.jar
    echo "copy done"
}

case "$1" in
    start)
        start
        sleep 4
        ;;
    stop)
        stop
	status
        ;;
    restart)
        get_jar
	stop
        start
	sleep 10
	status
        ;;
    status)
        status
        ;;
    copy)
        get_jar
        ;;
    *)
    echo "Usage: $0 {start | stop | status | restart | copy }"
esac
exit 0



실행방법

sh test.sh status



소스는
여기
에

<!-- wiki-links -->
<!-- wiki-concepts -->
**관련 개념**: [[devops-practices]]

---

**태그**: #spring-boot #pinpoint-agent #shell-script #local-testing #devops #application-monitoring
