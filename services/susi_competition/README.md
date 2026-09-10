# 수시경쟁률 (2027 수시 저경쟁 학과)

2027학년도 수시 원서접수 기간 동안 **경쟁률이 낮은 학과**를 주기적으로 수집해, 수도권·충청권 **전체 대학**의 농어촌·논술·기회균형 전형을 추려 웹 페이지로 배포하는 서비스.
상위 50위권 대학(대학백과 2026 순위)에는 ★ 표시가 붙고, 페이지에서 "주요대학만" 으로 좁혀 볼 수 있다.

원서 마감 직전까지 경쟁률이 계속 움직이므로, "지금 어디가 비어 있는가"를 10분마다 갱신해 보여주는 것이 목적이다.

**결과 페이지**: https://kapdolli.github.io/my_ai_master/

| 항목 | 값 |
|------|-----|
| **실행 방식** | **로컬 스크래핑 + Actions 배포** — 작업 스케줄러 → `refresh_all.ps1` → git push → GitHub Actions가 Pages 배포 |
| 실행 주기 | **10분 간격** (작업 스케줄러 `SusiRefresh`) |
| 전달 채널 | GitHub Pages (텔레그램 미사용) |
| 데이터 출처 | 경기도교육청 Apps Script(대학 목록) + 진학사 `addon.jinhakapply.com`(학과별 경쟁률) |
| 의존성 | `requests`, `beautifulsoup4` ([`requirements.txt`](requirements.txt)) — 이 서비스만 예외적으로 pip 패키지 사용 |
| 배포 워크플로 | [`../../.github/workflows/refresh.yml`](../../.github/workflows/refresh.yml) |

> ⚠️ 다른 서비스와 달리 `prompt.md` / `run_local.py` / `claude -p`를 쓰지 않는다. Claude 호출 없이 순수 스크래핑·집계만 하는 서비스다.

---

## 왜 로컬에서 스크래핑하는가

처음에는 GitHub Actions에서 5분 간격 cron으로 스크래핑까지 모두 돌렸다. 그러나 **Actions runner(US IP)는 진학사/유웨이에서 차단**되어 약 60% 대학의 경쟁률 페이지가 유실됐다. 2026-09-09부터 스크래핑은 국내 IP의 로컬 PC에서 돌리고, Actions는 로컬이 push한 HTML/CSV를 Pages로 **배포만** 한다.

```
[작업 스케줄러 SusiRefresh] ──10분 간격──▶ refresh_all.ps1 (로컬, 국내 IP)
                                                │
                     ┌──────────────────────────┼──────────────────────────┐
                     ▼                          ▼                          ▼
        [1] find_low_competition.py   [3] filter_top50.py      [4] build_html.py
            전체 데이터 수집               제외규칙 적용 + 태깅         단일 HTML 생성
        [2] 농특/논술 <2.0 필터            (주요대학·전형세부유형)      + 관심학과 상단 고정
                                                │
                                                ▼
                                    git commit + push (-Push)
                                                │
                                                ▼
                             GitHub Actions (refresh.yml) → GitHub Pages
```

---

## 파일 구성

| 파일 | 역할 |
|------|------|
| [`refresh_all.ps1`](refresh_all.ps1) | 4단계 통합 실행 진입점. 스케줄러가 이 파일을 부른다 |
| [`find_low_competition.py`](find_low_competition.py) | 대학 목록 추출 + 진학사 경쟁률 페이지 병렬 수집·파싱 (스크래퍼) |
| [`filter_top50.py`](filter_top50.py) | 제외규칙 적용(전체 대학), 상위50 대학에 `rank`/`주요대학` 태깅, 전형세부유형(농어촌_교과/종합/일반, 논술, 기회균형) 태깅. **행을 버리지 않고 전체 대학을 남긴다** |
| [`build_html.py`](build_html.py) | 최종 단일 HTML 생성 (검색·정렬·필터 UI 포함, 외부 의존 없음) |
| `top50_univ100_2026.txt` | 대학 순위 50위 목록 (출처: 대학백과 2026 대학 순위) |
| `exclusions.txt` | 제외 대학 규칙. `all_women_univ` 토큰 = 여대 전체 제외, `고려대학교(세종)`처럼 캠퍼스 지정 가능 |
| `susi_2027_low_competition.csv` | [1단계] 전체 수집 결과 (관심학과 조회용 원본, ~15,000행) |
| `susi_2027_nong_nonsul_low.csv` | [2단계] 농어촌·논술 경쟁률 2.0 미만 |
| `susi_2027_top50_nong_nonsul.csv` | [3단계] 태깅 결과 — **전체 대학**(제외규칙 적용 후). 상위50 대학만 `rank`/`주요대학=O` 를 가진다. 페이지 본문 테이블 소스 (파일명은 이력상 `top50` 이지만 내용은 전체 대학) |
| `susi_2027_top50.html` | [4단계] 배포되는 페이지 (Actions가 `_site/index.html`로 복사) |

관심 학과(페이지 상단 고정)는 `build_html.py`의 `PINNED` 리스트에서 관리한다 — 대학·학과 부분매치, 전형 키워드, 선호 캠퍼스로 지정.

### 페이지 필터

| 필터 | 설명 |
|------|------|
| 대학군 | `전체` / `★ 주요대학만`(상위50) / `그 외 대학만` |
| 대학 | `전체 대학 (N) ▾` 버튼 → 가나다순 전체 대학 체크박스 패널. 대학명 검색, `★ 주요대학 모두 체크` / `모두 체크` / `모두 해제` 지원. 아무것도 체크하지 않거나 전부 체크하면 무필터 |

순위 열의 `—` 는 상위50 밖 대학, `#n` 은 주요대학 순위다.

---

## 최초 세팅 (1회성)

### 1. 의존성 설치

```powershell
pip install -r services/susi_competition/requirements.txt
```

### 2. 수동 테스트

```powershell
cd services\susi_competition
.\refresh_all.ps1 -NoStage      # git 건드리지 않고 생성만
```

정상이면 `[i] 13x개 대학의 2027 경쟁률 페이지를 수집합니다...` → `[i] 필터 후 1xxxx개 학과` 가 찍히고 `susi_2027_top50.html`이 갱신된다.
**수집 대학 수가 0개로 나오면 아래 "인코딩 함정"을 먼저 확인할 것.**

### 3. 작업 스케줄러 등록 (`SusiRefresh`, 10분 간격)

```powershell
$script = "C:\Users\elf17\work\myai\my_ai_master\services\susi_competition\refresh_all.ps1"
$a = New-ScheduledTaskAction -Execute "powershell.exe" `
  -Argument "-NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File `"$script`" -Push" `
  -WorkingDirectory (Split-Path $script)
$t = New-ScheduledTaskTrigger -Once -At (Get-Date).AddMinutes(1) `
  -RepetitionInterval (New-TimeSpan -Minutes 10)
$s = New-ScheduledTaskSettingsSet -StartWhenAvailable -AllowStartIfOnBatteries `
  -DontStopIfGoingOnBatteries -ExecutionTimeLimit (New-TimeSpan -Minutes 9) `
  -MultipleInstances IgnoreNew
Register-ScheduledTask -TaskName "SusiRefresh" -Action $a -Trigger $t -Settings $s -Force
```

`-Push`가 있어야 갱신분을 커밋·push 해서 실제 배포까지 간다. 이 저장소에는 auto-commit 프로세스가 상시 떠 있지 않으므로 `-Push` 없이 등록하면 파일만 stage 된 채 배포가 되지 않는다.

### 4. GitHub Pages 설정

저장소 Settings → Pages → Source = **GitHub Actions** (1회 설정).

---

## 운영

| 상황 | 조치 |
|------|------|
| 즉시 갱신 | `.\refresh_all.ps1 -Push` |
| 생성만, git 미변경 | `.\refresh_all.ps1 -NoStage` |
| 스케줄 작업 상태 | `Get-ScheduledTaskInfo -TaskName SusiRefresh` (`LastTaskResult: 0`이면 정상) |
| 스케줄 작업 즉시 실행 | `Start-ScheduledTask -TaskName SusiRefresh` |
| 배포 결과 확인 | `gh run list --limit 3` / 페이지 하단 `생성: YYYY-MM-DD HH:MM` |
| 잠시 중단 | `Disable-ScheduledTask -TaskName SusiRefresh` |
| 관심 학과 변경 | `build_html.py`의 `PINNED` 수정 |
| 제외 대학 변경 | `exclusions.txt` 수정 |
| 순위 기준 변경 | `top50_univ100_2026.txt` 교체 |
| 캐시 무시하고 재수집 | 1단계가 `--refresh`로 항상 fresh — 필요시 `.cache/` 삭제 |

---

## 알려진 함정

### 인코딩 — `refresh_all.ps1`은 반드시 UTF-8 **with BOM**

BOM이 없으면 Windows PowerShell 5.1이 파일을 CP949로 읽어 스크립트 안의 한글 인자(`--regions 서울 경기 …`, `--admission-contains 농어촌 논술`)가 깨진다. 그러면 지역 매칭이 전부 실패해 **수집 대상이 0개 대학**이 되고, "조건에 맞는 학과가 없습니다"만 출력된 뒤 3·4단계가 옛 CSV로 HTML을 다시 그려 **겉보기에는 성공한 것처럼 보인다**. 2026-09-09에 실제로 이 증상으로 서비스가 멈춰 있었다.

확인: `python -c "print(open('refresh_all.ps1','rb').read(3) == b'\xef\xbb\xbf')"` → `True` 여야 정상.

### Actions에서 스크래핑 금지

`refresh.yml`에 스크래핑 단계를 되살리지 말 것. runner IP가 차단되어 데이터 60%가 유실된다 (위 "왜 로컬에서 스크래핑하는가" 참조).

### 사이트 마크업 변경

`extract_universities()`가 `BOOTSTRAP not found in page` 로 실패하면 경기도교육청 Apps Script 페이지 구조가 바뀐 것이다. `find_low_competition.py`의 이중 JS 언이스케이프 로직을 손봐야 한다.

---

## 참고

- 결과 페이지: https://kapdolli.github.io/my_ai_master/
- 배포 워크플로: [`../../.github/workflows/refresh.yml`](../../.github/workflows/refresh.yml)
- 순위 출처: https://www.univ100.kr/community/view/2224934 (2026 대학 순위, 대학백과)
