---
id: "136"
title: "[JenKins] Plugin Dependency error 조치,  Plugin수동 설치방법"
url: "https://peterica.tistory.com/136"
published_at: "2022-05-13"
category: "DevOps"
tags: ["jenkins-plugin", "dependency-error", "jaxb-plugin", "manual-installation", "plugin-dependency"]
keywords: ["Jenkins Plugin", "Dependency Error", "JAXB Plugin", "Manual Installation", "Plugin Dependency"]
word_count: 467
source_hash: "sha256:54a67f15d45dc3589b3d3c7451b800dfdfef148d12b8e7bc5b34ed181fd05f96"
model: "qwen3:8b"
generated_at: "2026-04-10T12:10:54Z"
---

# [JenKins] Plugin Dependency error 조치,  Plugin수동 설치방법

> 원본: [https://peterica.tistory.com/136](https://peterica.tistory.com/136)  ·  작성일: 2022-05-13  ·  카테고리: `DevOps`

## 요약

Jenkins 빌드 시 Dependency Error 발생으로 인해 JAXB 플러그인 의존성 문제 해결 과정. Jackson 2 API Plugin과의 충돌로 인해 수동으로 JAXB 플러그인을 HPI 파일로 설치하여 문제를 해결했습니다. 추가로 Kubernetes 클라우드 구성 재설정도 필요했습니다.

**태그**: `jenkins-plugin` `dependency-error` `jaxb-plugin` `manual-installation` `plugin-dependency`

## 본문



JenKins] Dependency error 조치 과정을 기론한다.





□ 개요

o 정기배포를 위해 Jenkins 빌드를 시도하였지만 Dependency Errors가 발견되어 조치했던 과정을 기록한다.

□ 빌드 시 에러 확인



o 빌드를 시도하였는데 에러가 발생하였다.

java.lang.NoSuchMethodError: No such DSL method 'containerTemplate' found among steps [archive, bat, build, catchError, checkout, deleteDir, dir, echo, error, fileExists, findBuildScans, getContext, git, input, isUnix, library, libraryResource, load, mail, milestone, node, parallel, powershell, properties, publishChecks, pwd, pwsh, readFile, readTrusted, resolveScm, retry, sh, sleep, stage, stash, step, timeout, timestamps, tm, tool, unarchive, unstable, unstash, waitUntil, warnError, withChecks, withContext, withCredentials, withEnv, withGradle, wrap, writeFile, ws] or symbols [GitUsernamePassword, all, allBranchesSame, always, ant, antFromApache, antOutcome, antTarget, apiToken, architecture, archiveArtifacts, artifactManager, authorizationMatrix, batchFile, bitbucketServer, booleanParam, buildButton, buildDiscarder, buildDiscarders, buildRetention, builtInNode, caseInsensitive, caseSensitive, certificate, choice, choiceParam, clock, command, credentials, cron, crumb, defaultFolderConfiguration, defaultView, demand, disableConcurrentBuilds, disableResume, dockerCert, dockerServer, dockerTool, downstream, dumb, durabilityHint, envVars, envVarsFilter, file, fileParam, filePath, fingerprint, fingerprints, frameOptions, freeStyle, freeStyleJob, fromDocker, fromScm, fromSource, git, gitBranchDiscovery, gitTagDiscovery, gitUsernamePassword, gradle, headRegexFilter, headWildcardFilter, hyperlink, hyperlinkToModels, inheriting, inheritingGlobal, installSource, jdk, jdkInstaller, jgit, jgitapache, jnlp, jobBuildDiscarder, jobName, lastDuration, lastFailure, lastGrantedAuthorities, lastStable, lastSuccess, legacy, legacySCM, list, local, location, logRotator, loggedInUsersCanDoAnything, mailer, masterBuild, maven, maven3Mojos, mavenErrors, mavenGlobalConfig, mavenMojos, mavenWarnings, modernSCM, myView, namedBranchesDifferent, nodeProperties, nonInheriting, none, organizationFolder, overrideIndexTriggers, paneStatus, parameters, password, pattern, permanent, pipeline, pipelineTriggers, plainText, plugin, pollSCM, projectNamingStrategy, proxy, pruneTags, queueItemAuthenticator, quietPeriod, rateLimit, rateLimitBuilds, resourceRoot, retainOnlyVariables, run, runParam, sSHLauncher, schedule, scmHttpClient, scmRetryCount, scriptApproval, scriptApprovalLink, search, security, shell, simpleBuildDiscarder, slave, sourceRegexFilter, sourceWildcardFilter, ssh, sshPublicKey, sshUserPrivateKey, standard, status, string, stringParam, suppressAutomaticTriggering, suppressFolderAutomaticTriggering, swapSpace, text, textParam, timestamper, timestamperConfig, timezone, tmpSpace, toolLocation, unsecured, untrusted, upstream, userSeed, usernameColonPassword, usernamePassword, viewsTabBar, weather, withAnt, x509ClientCert, zip] or globals [currentBuild, env, params, scm]
at org.jenkinsci.plugins.workflow.cps.DSL.invokeMethod(DSL.java:216)



ㅁ 플러그인 에러 확인



Some plugins could not be loaded due to unsatisfied dependencies. Fix these issues and restart Jenkins to re-enable these plugins.



o Jackson 2 API Plugin의 의존 관계가 있는 JAXB plugin의 업데이트가 필요하였다.

o 아래의 Plugin들은 Jackson 2의 의존관계가 있는 것들이 문제가 발생함을 보여주고 있다.

o
결국 Jackson2의 문제로 인해 모든 plugin에 문제가 발생하여 빌드가 되지 않고 있는 상황이다.

o 해결방법은 JAXB를 업그레이드를 하는 것이다.





ㅁ JAXB 업데이트 문제





ㅇ 플러그인의 업데이트를 시도하였지만 설치가능 목록에서 찾을 수가 없었다.

ㅇ 수정으로 설치하는 방법을 찾아야만 했다.





ㅁ Jenkins plugin 설치 사이트접속



ㅇ 경로:
https://plugins.jenkins.io/jaxb/

ㅇ 3가지 설치방법에 대해서 설명을 하고 있다.

1) UI를 통해 설치하는 방법이지만 이미 확인한 부분이다.

2)
jenkins-plugin-cli --plugins jaxb:2.3.6-1을 jenkins pod에서 실행하였지만 에러가 발생하였다.



3) hpi를 다운받아서 젠킨스에 직업 설치하는 방법이었다. 보안망이라 다운을 받아 설치하였다.





ㅁ Jenkins Web에 직접 hpi 파일을 통해 plugin설치하는 방법



ㅇ release 탭을 선택하여 jaxb.hpi를 다운받는다.





o jenkins 관리 > Plugin Manager > 고급으로 이동

o jaxb.hpi를 등록하고 deploy이 한다.





ㅇ 정상등록이 되어 에러가 해소되었다.



ㅁ 트라블 슈팅: No Kubernetes cloud was foud.



ㅇ 플러그인을 업데이트 하는 과정에서 kubernetes도 업데이트가 되면서 Configure Clouds가 초기화 되었다.





ㅇ Configure Cloud 설정을 다시 하였다.





ㅇ 정상빌드 확인





참고사이트

플러그인 설치 및 제거 방법 :
https://www.jenkins.io/doc/book/managing/plugins/#install-with-cli

<!-- wiki-links -->

---

**분류**: [[MOC-DevOps]]
**태그**: #jenkins-plugin #dependency-error #jaxb-plugin #manual-installation #plugin-dependency
