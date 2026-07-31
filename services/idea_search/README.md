# 아이디어검색가

Reddit, HackerNews, Product Hunt, IndieHackers, 한국 커뮤니티 등에서 유망 사업 아이디어·AI 활용 아이템·수익화 정보를 매일 수집·요약해 텔레그램으로 전달하는 서비스.

관심 가는 아이템이 나오면 [아이템분석가](../item_analyzer/README.md)로 넘겨 심층 분석한다.

| 항목 | 값 |
|------|-----|
| **실행 방식 (2026-07-31 전환)** | **로컬 Python + Claude Code CLI** — Windows 작업 스케줄러 → `python run_local.py` → `claude -p` |
| 실행 시각 | 매일 18:00 KST (사용자 PC 기준) |
| 인증 | Claude Code subscription (Pro/Max) — 별도 API 과금 없음 |
| 전달 채널 | Telegram Bot API (`api.telegram.org` 직접 호출) |
| 프롬프트 | [`prompt.md`](prompt.md) — `run_local.py`가 stdin으로 `claude -p`에 전달 |
| 로그 | `logs/YYYY-MM-DD.md` (실행 결과 아카이브) |

이전 Claude Cloud Schedule 실행 방식(sandbox egress로 텔레그램 발송 차단됨)의 여정은 [`../../docs/archive/2026-07-31-egress-blocked.md`](../../docs/archive/2026-07-31-egress-blocked.md) 참고.

---

## 동작 흐름

```
[Windows 작업 스케줄러] ──매일 18:00 KST──▶ python run_local.py
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

- `run_local.py`가 `prompt.md`를 읽어 `claude -p` 서브프로세스에 stdin으로 전달
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
```

성공 시 콘솔에 `[claude] exec: ... [log] ... [telegram] chunk 1/N sent ... [done]` 순서로 출력되고 텔레그램 봇으로 리포트가 도착한다.

### 4. Windows 작업 스케줄러 등록

`taskschd.msc` 실행 → **작업 만들기**:

- **일반** 탭: 이름 `idea-search-agent`, "사용자의 로그인 여부에 관계없이 실행" 체크
- **트리거**: 매일 18:00
- **동작**:
  - 프로그램: `pythonw.exe` 전체 경로 (예: `C:\Users\D4003412\AppData\Local\Programs\Python\Python310\pythonw.exe`)
  - 인수: `D:\work\james\work\my_ai_master\services\idea_search\run_local.py`
  - 시작 위치: `D:\work\james\work\my_ai_master`
- **조건**: "AC 전원 사용 시에만 실행" 해제 (노트북일 경우)
- **설정**: "요청 시 작업이 실행되도록 허용" 체크

콘솔 창을 띄우지 않으려면 `python.exe` 대신 `pythonw.exe` 사용.

> ⚠️ 작업 스케줄러가 다른 사용자 세션에서 실행되면 `claude` CLI가 PATH에 없을 수 있다. 그 경우 환경변수 `CLAUDE_BIN`에 절대경로(예: `C:\Users\D4003412\AppData\Local\Programs\claude-code\claude.exe`) 지정 필요. `where claude` 로 실제 경로 확인.

---

## 운영

| 상황 | 조치 |
|------|------|
| 실행 실패 확인 | `logs/YYYY-MM-DD.md` 없거나 상태 `empty`면 실패 |
| 리포트 재발송 | `python run_local.py` 재실행 (로그 덮어씀) |
| 발송 없이 리허설 | `python run_local.py --dry-run` |
| 명령 확인 | `python run_local.py --show-cmd` |
| 모델 교체 | 환경변수 `IDEA_SEARCH_MODEL=sonnet` 또는 `opus` |
| 타임아웃 조정 | 환경변수 `IDEA_SEARCH_TIMEOUT=1200` (기본 900초) |
| claude 경로 지정 | 환경변수 `CLAUDE_BIN=C:\path\to\claude.exe` |
| 인증 만료 | `claude auth status` 로 확인 → `claude setup-token` 재실행 |

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
