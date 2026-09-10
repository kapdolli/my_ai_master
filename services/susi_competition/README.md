# 수시경쟁률 (2027 수시 저경쟁 학과)

2027학년도 수시 원서접수 기간 동안 **경쟁률이 낮은 학과**를 주기적으로 수집해, 수도권·충청권 **전체 대학**의 농어촌·논술·기회균형 전형을 추려 웹 페이지로 배포하는 서비스.
[`major_univs.txt`](major_univs.txt) 에 지정한 **주요대학**에는 ★ 표시가 붙고, 페이지에서 "주요대학만" 으로 좁혀 볼 수 있다.

원서 마감 직전까지 경쟁률이 계속 움직이므로, "지금 어디가 비어 있는가"를 10분마다 갱신해 보여주는 것이 목적이다.

**결과 페이지**: https://kapdolli.github.io/my_ai_master/

| 항목 | 값 |
|------|-----|
| **실행 방식** | **로컬 스크래핑 + Actions 배포** — 작업 스케줄러 → `refresh_all.ps1` → git push → GitHub Actions가 Pages 배포 |
| 실행 주기 | **10분 간격** (작업 스케줄러 `SusiRefresh`) |
| 전달 채널 | GitHub Pages (텔레그램 미사용) |
| 데이터 출처 | 경기도교육청 Apps Script(대학 목록 + **마감일시** `lastday`/`lasttime`) + 진학사 `addon.jinhakapply.com`(학과별 경쟁률) |
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
        [2] 농특/논술 전 전형 수집         (주요대학·전형세부유형)      + 관심학과 상단 고정
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
| [`filter_top50.py`](filter_top50.py) | 제외규칙 적용(전체 대학), `major_univs.txt` 의 대학에 `rank`/`주요대학` 태깅, 전형세부유형(농어촌_교과/종합/일반, 논술, 기회균형) 태깅. **행을 버리지 않고 전체 대학을 남긴다** |
| [`build_html.py`](build_html.py) | 최종 단일 HTML 생성 (검색·정렬·필터 UI 포함, 외부 의존 없음) |
| `major_univs.txt` | **주요대학 목록**(★ 기준). `순위<탭>단축명(캠퍼스)` 형식. 괄호를 비우면 전 캠퍼스 |
| `top50_univ100_2026.txt` | 대학백과 2026 순위 50위 원본. 지금은 `major_univs.txt` 의 순위 출처로만 참고 (코드가 읽지 않음) |
| `exclusions.txt` | 제외 대학 규칙. `all_women_univ` 토큰 = 여대 전체 제외, `고려대학교(세종)`처럼 캠퍼스 지정 가능 |
| `uni_defaults.txt` | 페이지를 처음 열었을 때 기본으로 체크될 대학 목록 (한 줄에 하나). 비우면 전체 대학. **모든 브라우저에 공통 적용** |
| `susi_2027_low_competition.csv` | [1단계] 전체 수집 결과 (관심학과 조회용 원본, ~15,000행). `deadline_day`/`deadline_time` 컬럼 포함 |
| `susi_2027_nong_nonsul_low.csv` | [2단계] 농어촌·논술 **전 전형** (경쟁률 컷 없음, ~2,200행). 컷을 두면 건국대(서울)처럼 최저 경쟁률이 높은 대학이 통째로 빠져서 컷을 없앴다 |
| `susi_2027_top50_nong_nonsul.csv` | [3단계] 태깅 결과 — **전체 대학**(제외규칙 적용 후). 주요대학만 `rank`/`주요대학=O` 를 가진다. 페이지 본문 테이블 소스 (파일명은 이력상 `top50` 이지만 내용은 전체 대학) |
| `susi_2027_top50.html` | [4단계] 배포되는 페이지 (Actions가 `_site/index.html`로 복사) |
| `version.json` | 갱신 감지용 소형 파일 `{"generated","rows"}`. 열려 있는 페이지가 900KB 를 다시 받지 않고 이것만 확인한다 |

관심 학과(페이지 상단 고정)는 `build_html.py`의 `PINNED` 리스트에서 관리한다 — 대학·학과 부분매치, 전형 키워드, 선호 캠퍼스로 지정.

### 페이지 필터

| 필터 | 설명 |
|------|------|
| 경쟁률공개 | `전체` / `공개중` / `공개종료` / `공개마감 미상`. 경쟁률 페이지가 스스로 공지한 공개 종료 시각 기준 |
| 마감 | 대학별 원서 마감시각 칩 (이른 순). 2027 수시는 **9/11 18:00 이 1,359행, 9/11 17:00 이 327행**으로 대부분을 차지한다. 이미 지난 시각은 칩에 취소선 |
| 대학군 | `전체` / `★ 주요대학만`(`major_univs.txt` 지정) / `그 외 대학만` |
| 대학 | `전체 대학 (N) ▾` 버튼 → 가나다순 전체 대학 체크박스 패널. 대학명 검색, `★ 주요대학 모두 체크` / `모두 체크` / `모두 해제` 지원. 아무것도 체크하지 않거나 전부 체크하면 무필터 |
| 경쟁률 ≤ | 상한 없음. 기본 2.0 — 숫자를 올리면 경쟁률이 높은 학과·대학까지 보인다 |

순위 열의 `—` 는 주요대학이 아닌 곳, `#n` 은 주요대학의 대학백과 2026 순위다.
마감이 지난 행은 흐리게+취소선으로 표시되고, 2시간 안에 마감되는 행은 마감 시각이 빨간색이다
(뷰어의 로컬 시각 기준으로 페이지가 열릴 때 계산).
통계 타일의 `아직 접수중` 은 현재 필터 결과 중 마감 전인 행 수다.

### 갱신 감지 (자동 새로고침 안 함)

페이지는 정적 파일이라 열어둔 탭이 저절로 바뀌지 않는다. 그래서 **자동 새로고침
대신** 새 버전이 배포되면 헤더 오른쪽에 `🔄 새로고침 (HH:MM)` 버튼이 **깜박인다.**

- 90초마다 `version.json` 만 확인한다 (수십 바이트). 탭이 백그라운드면 건너뛰고,
  탭으로 돌아오는 순간 즉시 한 번 확인한다.
- GitHub Pages 가 `Cache-Control: max-age=600` 을 붙이므로 CDN 캐시를 피하려고
  `version.json?t=<현재시각>` 으로 매번 다른 URL을 쓴다.
- 버튼을 누르면 `?v=<생성시각>` 을 붙여 이동한다. 그냥 `location.reload()` 하면
  캐시 때문에 옛 페이지가 다시 뜰 수 있다 (실제로 겪었다).
  필터·대학 선택은 localStorage 에 있어 그대로 복원된다.

### 접수마감 vs 경쟁률마감

대학마다 **경쟁률을 언제까지 공개하는지가 다르다.** 접수는 9/11 18:00까지 받으면서
경쟁률은 12:00에 끊는 식이라, 마감 직전 몇 시간은 "지금 몇 대 1인지" 알 수 없다.

| 열 | 뜻 |
|----|-----|
| 접수마감 | 원서접수 마감시각 (경기도교육청 `lastday`/`lasttime`) |
| 경쟁률마감 | 경쟁률 공개가 끊기는 시각. 경쟁률 페이지의 안내 문구에서 파싱 |
| 기준 | **지금 보고 있는 경쟁률이 언제 집계된 것인지.** 대학마다 갱신 주기가 달라(10분/1시간/하루 2회) 같은 화면 안에서도 신선도가 섞인다 |

- 경쟁률마감이 지나면 `종료` 배지가 붙고 회색이 된다 — 그 대학 숫자는 더 오르지 않는다.
- 파싱에 실패하면 **`미상`(주황)** 으로 두고 추측하지 않는다. 현재 약 73개 중 59개 대학 파싱.
- 셀에 마우스를 올리면 **그 대학 경쟁률의 기준시각 + 공지 원문**이 뜬다.
- 날짜 칸(접수마감·경쟁률마감·기준)은 자료가 전부 9월이라 월을 떼고 `11 18:00`
  형태로 줄였다. 전체 값은 툴팁에 있다. 기준은 오늘 것이면 시:분만 보여준다.
- 아직 경쟁률을 공개 중인데 기준이 **2시간 넘게 묵으면 주황색**으로 표시한다
  (공개가 이미 끝난 대학은 멈춰 있는 게 정상이므로 표시하지 않는다).
- 헤더의 `경쟁률 기준시각(대학별 상이)` 은 전체 대학 기준시각의 최소~최대 범위다.
  대학마다 갱신 주기(10분/1시간/하루 2회)가 달라 한 페이지 안에서도 신선도가 섞여 있다.

**필터 변경은 [검색] 을 눌러야 반영된다.** (입력칸에서 Enter 도 동일)
행이 2,000개라 타이핑마다 다시 그리지 않도록 모아서 적용한다. 반영 대기 중에는
검색 버튼이 주황색 `검색 •` 으로 바뀐다. 표 헤더 클릭(정렬)은 검색 없이 즉시 반영된다.

### 선택 유지

| 범위 | 방식 |
|------|------|
| 같은 브라우저 | [검색] 을 누를 때마다 필터 전체가 `localStorage` 에 저장되어 다음 방문에 복원된다 (헤더에 "저장된 선택을 불러왔습니다" 표시) |
| 모든 브라우저·기기 | `uni_defaults.txt` 에 적힌 대학이 기본 체크 상태가 된다. 페이지의 **[선택 내보내기]** 로 현재 체크 목록을 복사해 이 파일에 붙여넣고 커밋하면 다음 갱신(최대 10분) 때 반영 |

`초기화` 는 localStorage 저장분을 지우고 `uni_defaults.txt` 기본값으로 되돌린다.
정적 사이트라 서버 저장소가 없어, 브라우저 간 **자동** 동기화는 하지 않는다.

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
| 기본 체크 대학 변경 | `uni_defaults.txt` 수정 (페이지 [선택 내보내기] 결과를 붙여넣으면 편함) |
| 제외 대학 변경 | `exclusions.txt` 수정 |
| 주요대학 목록 변경 | `major_univs.txt` 에서 줄 추가·삭제. 캠퍼스는 괄호로 지정(`가천대(성남)`), 괄호를 비우면 전 캠퍼스(`경기대`) |
| 캐시 무시하고 재수집 | 1단계가 `--refresh`로 항상 fresh — 필요시 `.cache/` 삭제 |

---

## 알려진 함정

### 인코딩 — `refresh_all.ps1`은 반드시 UTF-8 **with BOM**

BOM이 없으면 Windows PowerShell 5.1이 파일을 CP949로 읽어 스크립트 안의 한글 인자(`--regions 서울 경기 …`, `--admission-contains 농어촌 논술`)가 깨진다. 그러면 지역 매칭이 전부 실패해 **수집 대상이 0개 대학**이 되고, "조건에 맞는 학과가 없습니다"만 출력된 뒤 3·4단계가 옛 CSV로 HTML을 다시 그려 **겉보기에는 성공한 것처럼 보인다**. 2026-09-09에 실제로 이 증상으로 서비스가 멈춰 있었다.

확인: `python -c "print(open('refresh_all.ps1','rb').read(3) == b'\xef\xbb\xbf')"` → `True` 여야 정상.

### Actions에서 스크래핑 금지

`refresh.yml`에 스크래핑 단계를 되살리지 말 것. runner IP가 차단되어 데이터 60%가 유실된다 (위 "왜 로컬에서 스크래핑하는가" 참조).

### 경쟁률 페이지 캐시는 반드시 만료되어야 한다

`find_low_competition.py` 의 `_fetch_comp_page` 에는 원래 만료 로직이 없어서,
`.cache/comp_*.html` 을 한 번 받으면 영원히 재사용했다. 2026-09-10 오전까지
**10분마다 돌면서도 전날 21:09 캐시를 계속 읽어** 경쟁률이 하나도 갱신되지 않았다.
(HTML 의 `생성:` 시각만 바뀌어서 겉보기에는 정상으로 보였다.)

지금은 `DEFAULT_CACHE_TTL = 300초`. 한 번의 실행 안에서 1·2단계가 같은 대학을
두 번 받지 않게 해주면서, 10분 주기의 다음 실행은 반드시 새로 받는다.
`--refresh` 는 TTL 0 과 같다. **TTL 을 10분 이상으로 올리지 말 것** — 갱신 주기와
같아지는 순간 다시 옛 데이터를 보게 된다.

확인: 연속 두 번 실행했을 때 `susi_2027_low_competition.csv` 가 변하는지,
또는 페이지 헤더의 `경쟁률 기준시각` 이 현재 시각을 따라오는지 본다.

### 사이트 마크업 변경

`extract_universities()`가 `BOOTSTRAP not found in page` 로 실패하면 경기도교육청 Apps Script 페이지 구조가 바뀐 것이다. `find_low_competition.py`의 이중 JS 언이스케이프 로직을 손봐야 한다.

---

## 참고

- 결과 페이지: https://kapdolli.github.io/my_ai_master/
- 배포 워크플로: [`../../.github/workflows/refresh.yml`](../../.github/workflows/refresh.yml)
- 순위 출처: https://www.univ100.kr/community/view/2224934 (2026 대학 순위, 대학백과)
