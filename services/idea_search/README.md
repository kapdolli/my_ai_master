# 아이디어검색가

Reddit, HackerNews, Product Hunt, IndieHackers, 한국 커뮤니티 등에서 유망 사업 아이디어·AI 활용 아이템·수익화 정보를 매일 수집·요약해 텔레그램으로 전달하는 서비스.

관심 가는 아이템이 나오면 [아이템분석가](../item_analyzer/README.md)로 넘겨 심층 분석한다.

| 항목 | 값 |
|------|-----|
| **실행 방식 (2026-07-31 전환)** | **로컬 Python + Claude Code CLI** — Windows 작업 스케줄러 → [`run_daily.ps1`](run_daily.ps1) → `python run_local.py` → `claude -p` |
| 실행 시각 | 매일 18:00 KST (사용자 PC 기준) |
| 인증 | Claude Code subscription (Pro/Max) — 별도 API 과금 없음 |
| 전달 채널 | Telegram Bot API (`api.telegram.org` 직접 호출) |
| 프롬프트 | [`prompt.md`](prompt.md) — `run_local.py`가 stdin으로 `claude -p`에 전달 |
| 로그 | `logs/YYYY-MM-DD.md` (리포트 본문) · `logs/_runs.log` (실행 이력 1줄/회) · `logs/_last_run.{out,err}.txt` (직전 실행 출력) |

이전 Claude Cloud Schedule 실행 방식(sandbox egress로 텔레그램 발송 차단됨)의 여정은 [`../../docs/archive/2026-07-31-egress-blocked.md`](../../docs/archive/2026-07-31-egress-blocked.md) 참고.

---

## 동작 흐름

```
[Windows 작업 스케줄러] ──매일 18:00 KST──▶ run_daily.ps1 (래퍼: 경로 고정 + 실행 로그)
                                                    │
                                                    ▼
                                              python run_local.py
                                                    │
                                     ┌──────────────┴──────────────┐
                                     ▼                             ▼
                              claude -p (Claude Code CLI)     최종 응답 stdout
                              (WebSearch 등 내장 툴 사용)    (Markdown 리포트)
                                                                   │
                                                                   ▼
                                                       Telegram Bot API
                                                      (3800자 단위 분할)
```

- `run_daily.ps1`이 python·claude 절대경로와 UTF-8 인코딩을 고정한 뒤 `run_local.py`를 호출하고, 결과를 `logs/_runs.log`에 남긴다
- `run_local.py`가 `prompt.md`를 읽어 `claude -p` 서브프로세스에 stdin으로 전달
- `--allowedTools WebSearch WebFetch`로 검색 툴 권한을 명시 부여 (헤드리스에는 권한 프롬프트에 답할 사람이 없다)
- Claude가 WebSearch 등 내장 도구로 5개 소스 검색·분석
- stdout으로 받은 마크다운 리포트를 `logs/YYYY-MM-DD.md`에 저장
- Telegram Bot API로 3800자 단위 분할 발송

---

## 최초 세팅 (1회성)

### 1. Claude Code CLI 인증

[`../../shared/claude_code/README.md`](../../shared/claude_code/README.md) 절차대로 `claude setup-token` 완료.

Python 패키지 추가 설치는 없다 — 표준 라이브러리만 사용.

### 2. Telegram 봇 확인

`shared/telegram/config.local.json` 이 이미 존재하는지 확인 (기존 봇 `@JamesMyHomeBot` 재사용). 없으면 [`../../shared/telegram/README.md`](../../shared/telegram/README.md) 참조.

### 3. 수동 테스트

```powershell
# 실행할 claude 명령만 미리 보기 (진단용)
python services/idea_search/run_local.py --show-cmd

# 텔레그램 발송 없이 리포트만 생성 (로그 파일만 남김)
python services/idea_search/run_local.py --dry-run

# 정상 실행 (텔레그램까지 전송)
python services/idea_search/run_local.py

# 스케줄러가 실제로 타는 경로 그대로 리허설 (발송 생략)
cd services\idea_search; .\run_daily.ps1 -DryRun
```

성공 시 콘솔에 `[claude] exec: ... [log] ... [telegram] chunk 1/N sent ... [done]` 순서로 출력되고 텔레그램 봇으로 리포트가 도착한다.

### 4. Windows 작업 스케줄러 등록

`idea-search-agent` 작업을 매일 18:00에 등록한다 (관리자 권한 불필요):

```powershell
$script = "C:\Users\elf17\work\myai\my_ai_master\services\idea_search\run_daily.ps1"
$a = New-ScheduledTaskAction -Execute "powershell.exe" `
  -Argument "-NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File `"$script`"" `
  -WorkingDirectory (Split-Path $script)
$t = New-ScheduledTaskTrigger -Daily -At 18:00
$s = New-ScheduledTaskSettingsSet -StartWhenAvailable -AllowStartIfOnBatteries `
  -DontStopIfGoingOnBatteries -ExecutionTimeLimit (New-TimeSpan -Minutes 30) `
  -MultipleInstances IgnoreNew
Register-ScheduledTask -TaskName "idea-search-agent" -Action $a -Trigger $t -Settings $s -Force
```

등록 확인:

```powershell
Get-ScheduledTaskInfo -TaskName idea-search-agent   # NextRunTime 이 다음 18:00 인지 확인
```

- `-StartWhenAvailable` 덕분에 18:00에 PC가 꺼져 있었으면 다음 부팅 후 실행된다.
- 작업은 **현재 사용자로, 로그인 상태에서만** 실행된다. 로그인 여부와 무관하게 돌리려면 `taskschd.msc`에서 작업을 열어 "사용자의 로그인 여부에 관계없이 실행"을 체크한다 (계정 암호 입력 필요).
- PC·경로가 바뀌면 `run_daily.ps1` 상단의 `$py` / `$env:CLAUDE_BIN` 절대경로도 함께 고친다 (`where claude`, `where python` 으로 확인).

---

## 운영

| 상황 | 조치 |
|------|------|
| 최근 실행 이력 | `Get-Content logs\_runs.log -Tail 10` — 한 줄에 `OK`/`FAIL` + 종료코드 + 소요초 |
| 실행 실패 원인 | `logs\_last_run.err.txt` (직전 실행 stderr), `logs\_last_run.out.txt` (stdout) |
| 스케줄 작업 상태 | `Get-ScheduledTaskInfo -TaskName idea-search-agent` (`LastTaskResult: 0`이면 정상) |
| 스케줄 작업 즉시 실행 | `Start-ScheduledTask -TaskName idea-search-agent` |
| 잠시 중단 / 재개 | `Disable-ScheduledTask -TaskName idea-search-agent` / `Enable-ScheduledTask ...` |
| 허용 툴 변경 | 환경변수 `IDEA_SEARCH_TOOLS=WebSearch,WebFetch` (쉼표 구분) |
| 리포트 재발송 | `python run_local.py` 재실행 (로그 덮어씀) |
| 발송 없이 리허설 | `python run_local.py --dry-run` |
| 명령 확인 | `python run_local.py --show-cmd` |
| 모델 교체 | 환경변수 `IDEA_SEARCH_MODEL=sonnet` 또는 `opus` |
| 타임아웃 조정 | 환경변수 `IDEA_SEARCH_TIMEOUT=1200` (기본 900초) |
| claude 경로 지정 | 환경변수 `CLAUDE_BIN=C:\path\to\claude.exe` |
| 인증 만료 | `claude auth status` 로 확인 → `claude setup-token` 재실행 |

---

## 알려진 함정

### 헤드리스(`-p`)에서는 툴 권한을 명시해야 한다

`claude -p`에는 권한 프롬프트에 답할 사람이 없어서, 허용 목록에 없는 툴 호출은 **전부 자동 거부**된다.
`--allowedTools` 없이 돌리면 Claude가 WebSearch·WebFetch를 못 써서 검색 단계가 통째로 실패하고,
"권한이 없어 리포트를 생성하지 못했다"는 안내문만 로그에 남는다. 그런데 **스크립트 종료 코드는 0**이라
겉보기에는 성공한 실행으로 보인다. 2026-09-09에 이 증상을 확인했다.

`run_local.py`의 `build_claude_cmd()`가 `--allowedTools WebSearch WebFetch`를 붙여 해결한다.
파일·셸 툴은 일부러 허용하지 않는다 — 이 서비스는 검색과 텍스트 생성만 필요하다.

확인: `python run_local.py --show-cmd` 출력에 `--allowedTools WebSearch WebFetch` 가 있어야 정상.

### 실행 실패가 조용히 묻힌다

스케줄러에 `pythonw.exe`를 직접 등록하면 stdout·stderr가 어디에도 남지 않는다.
`run_daily.ps1` 래퍼를 거치면 매 실행이 `logs\_runs.log`에 한 줄씩 쌓이므로,
**마지막 줄의 날짜가 오늘이 아니면 서비스가 멈춰 있는 것**이다.

### `run_daily.ps1`은 UTF-8 with BOM 으로 저장한다

BOM이 없으면 Windows PowerShell 5.1이 CP949로 읽어 주석·문자열의 한글이 깨진다.
확인: `python -c "print(open('run_daily.ps1','rb').read(3) == b'\xef\xbb\xbf')"` → `True`

---

## 관련 자산 (유지)

- **Claude Cloud Routine** `trig_014gH3d4moi4fhd2J2JyDfw2` — 현재 disable 권장 (로컬 실행이 primary). 완전히 삭제하지 않고 남겨두면 pull-only fallback으로 활용 가능
- **Cloudflare Worker** `tg-relay.elfcarpin.workers.dev` — 로컬 실행에서는 불필요(직접 텔레그램 호출로 충분). 삭제해도 무방. [`../../shared/cloudflare/README.md`](../../shared/cloudflare/README.md)
- **Telegram Bot** `@JamesMyHomeBot` — 그대로 재사용
- **GitHub App** — 이 서비스에는 불필요

---

## 참고

- 원본 요청서: [`../../docs/초기요청사항.txt`](../../docs/초기요청사항.txt)
- 이전 진행 문서: [`../../docs/archive/twinkling-finding-blossom.md`](../../docs/archive/twinkling-finding-blossom.md)
- Cloud sandbox egress 벽 여정: [`../../docs/archive/2026-07-31-egress-blocked.md`](../../docs/archive/2026-07-31-egress-blocked.md)
