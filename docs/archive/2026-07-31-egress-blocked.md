# 2026-07-31 여정 기록 — Anthropic Cloud Sandbox Egress 벽

> 이 문서의 목적: 다음 세션에서 이 서비스 재개 시 같은 실수·같은 시행착오를 반복하지 않도록 결정적 사실만 정리.

---

## 오늘 확정된 핵심 사실

1. **Claude Cloud Routine의 sandbox는 매우 좁은 egress 화이트리스트를 사용**
2. **Individual 플랜으로는 이 화이트리스트를 수정할 수 없음** (Team/Enterprise 전용)
3. **결과**: 사용자 개인 리포에 push, 텔레그램/Discord/Slack 등 알림 서비스 호출, 서드파티 서버리스(Cloudflare Workers 등) 호출 모두 원천 차단
4. **그럼에도 STEP 1~2(WebSearch·분석·리포트 생성)는 완벽 동작** — 즉 검색·분석 도구로서는 여전히 유효

---

## 성공한 것 (유지 자산)

| 자산 | 위치 | 상태 |
|------|------|------|
| 저장소 골격 (README, .gitignore, services/, shared/, docs/) | repo | ✅ |
| Stop Hook (Claude 세션 종료 시 자동 커밋+푸시) | `.claude/settings.local.json` | ✅ 동작 |
| Cloud Routine 등록 (`trig_014gH3d4moi4fhd2J2JyDfw2`) | Anthropic Cloud | ✅ 매일 09:00 UTC 자동 실행 |
| Cloudflare Worker (`tg-relay.elfcarpin.workers.dev`) | Cloudflare | ✅ 로컬에서 호출 시 정상 (sandbox에서만 차단) |
| Telegram Bot (`@JamesMyHomeBot`) | Telegram | ✅ chat_id 확보, `shared/telegram/config.local.json` |
| GitHub PAT (kapdolli) | `shared/github/config.local.json` | ✅ Contents:R/W 권한 |
| Claude GitHub App | github.com/settings/installations | ⚠ Authorized만, Install은 read-only |

## 실패한 배달 경로 (5회 시도 결과)

| # | 방법 | 결과 |
|---|------|------|
| 1 | `WebFetch` GET → `api.telegram.org` | 403 Policy Denial |
| 2 | `gh issue create` via GitHub MCP | 403 Resource not accessible by integration |
| 3 | `git commit + push` (App 인증) | 로컬 커밋은 성공, push 403 |
| 4 | `curl + PAT` → `api.github.com/repos/.../issues` | GitHub access not enabled for this session |
| 5 | `curl` → `tg-relay.elfcarpin.workers.dev` (Cloudflare Worker 릴레이) | connect_rejected 403 (도메인이 화이트리스트에 없음) |

---

## 다음 세션 재개 시 권장 옵션

### 옵션 1) 로컬 Python 스크립트 (권장 — 유일한 확실한 해)

**필요한 것들**
- Anthropic API 키 (console.anthropic.com에서 발급, 소액 과금)
- Python 3.10+ (이미 설치됨: `C:\Users\D4003412\AppData\Local\Programs\Python\Python310\`)
- `anthropic`, `requests` 패키지 (`pip install`)

**구조 제안**
```
services/idea_search/
├─ prompt.md (기존 유지 — 프롬프트 자체는 재사용)
├─ run_local.py (신규 — 로컬 실행 진입점)
└─ README.md (로컬 실행 절차 추가)

shared/anthropic/
├─ config.local.json (API 키)
└─ README.md
```

**run_local.py 로직 개요**
1. `services/idea_search/prompt.md` 읽음
2. Anthropic API로 Claude에 프롬프트 전송 (WebSearch/WebFetch는 로컬 툴로 대체 필요 — httpx로 직접 호출)
3. 결과 마크다운을 텔레그램 Bot API로 직접 전송
4. 로그를 `services/idea_search/logs/YYYY-MM-DD.log`로 저장

**스케줄 등록**
- Windows 작업 스케줄러 → 새 작업 → 매일 18:00 → `python "D:\MyBench\work\my_ai_master\services\idea_search\run_local.py"`

**주의**
- PC가 18:00에 켜져 있어야 함 (절전/최대절전 상태여도 wake trigger로 실행 가능)
- Claude Cloud Routine은 disable 하거나 그대로 두되 delivery 실패 감수
- WebSearch 대체 필요 — Anthropic API 자체엔 WebSearch 툴 있지만 사용법 확인 필요

### 옵션 2) Discord Webhook 프로브 (짧게 시도 가치)

**논리**: Cloudflare Workers는 화이트리스트 밖이 확실. 하지만 Discord는 개발자 커뮤니티가 커서 Anthropic이 명시적으로 허용했을 수도 있음.

**5분 프로브 방법**: 라우틴에 임시 프롬프트 등록해서 `curl -sS -I https://discord.com/`만 실행 → 응답 코드로 판정. 통과 시 Discord 방식 세팅 진행.

### 옵션 3) Pull-only 유지 (아무것도 안 함)

라우틴은 이미 매일 자동 실행되고 리포트를 세션에 남기므로, 매일 https://claude.ai/code/routines/trig_014gH3d4moi4fhd2J2JyDfw2 열어 읽는 것으로 갈음. 스마트폰 홈에 URL 바로가기 추가하면 조금 완화.

---

## 이번에 얻은 교훈 (다음번 판단에 사용)

1. **Anthropic Cloud Routine은 GitHub-centric workflow(PR/이슈 처리)를 위해 설계됨.** 외부 알림 서비스 push는 Individual 플랜에서 실질적으로 불가.
2. **egress 정책이 명시된 공식 문서를 찾을 수 없어 시행착오로만 확인 가능함.** 신규 도메인 시도 전에 라우틴 안에서 `curl -I` 프로브를 먼저 돌리는 것이 시간 절약.
3. **Cloud sandbox 대신 로컬 실행이 개인 프로젝트에는 더 합리적.** API 과금은 소액이고, 로컬 네트워크는 제약 없음.
4. **Individual 플랜 사용자는 Claude Cloud Routine을 "발신자 없는 검색·분석 파이프라인"으로만 활용** — 결과는 세션 로그에서 pull.

---

## 관련 자산 참조

- 최상위 [`README.md`](../../README.md) — 저장소 규약
- [`../../services/idea_search/README.md`](../../services/idea_search/README.md) — 서비스 현재 상태 + 재개 옵션 (본 문서와 중복 요약)
- [`../../services/idea_search/prompt.md`](../../services/idea_search/prompt.md) — 라우틴에 등록된 최신 프롬프트
- [`../../shared/cloudflare/README.md`](../../shared/cloudflare/README.md) — Worker 사양 (재활용 대비 유지)
- [`../../shared/github/README.md`](../../shared/github/README.md) — PAT/App 사용 규약
- [`../../shared/telegram/README.md`](../../shared/telegram/README.md) — Bot 사용 규약
- [`twinkling-finding-blossom.md`](twinkling-finding-blossom.md) — 최초 계획서 (Cloud Schedule 방식 채택 근거, 로컬 폴백 옵션 예견)
