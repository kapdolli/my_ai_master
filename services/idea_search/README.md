# 아이디어 서치 에이전트

Reddit, HackerNews, Product Hunt, IndieHackers, 한국 커뮤니티 등에서 유망 사업 아이디어·AI 활용 아이템·수익화 정보를 매일 수집·요약해 사용자에게 알림 전달하는 서비스.

| 항목 | 값 |
|------|-----|
| **상태 (2026-07-31 기준)** | ⚠ **배달 차단됨** — 검색·분석은 정상, 텔레그램/GitHub 등 외부 전송이 Anthropic 클라우드 sandbox의 egress 정책으로 봉쇄. 재개 방향 하단 참조. |
| 실행 방식 | Claude Cloud Schedule (routine `trig_014gH3d4moi4fhd2J2JyDfw2`) |
| 실행 시각 | 매일 18:00 KST (09:00 UTC) — 자동 트리거 활성 |
| 관리 URL | https://claude.ai/code/routines/trig_014gH3d4moi4fhd2J2JyDfw2 |
| 프롬프트 | [`prompt.md`](prompt.md) — 현재 라우틴에 등록된 최신 버전(Cloudflare Worker 경유 방식) |
| 결과 예시 (구) | [`samples/2026-07-30.md`](samples/2026-07-30.md) — 수동 작업 결과물 |

---

## 현재 동작 상태 (검증됨)

- ✅ **STEP 1 (검색)**: WebSearch로 5개 소스 병렬 검색 정상. 매 실행마다 15~25개 후보 수집
- ✅ **STEP 2 (분석)**: 카테고리·난이도·수익성·AI활용도 4축 평가 후 상위 10개 선별 정상
- ✅ **리포트 생성**: 마크다운 포맷의 완결된 리포트가 세션 로그에 남음
- ❌ **STEP 3 (배달)**: 텔레그램/GitHub/Cloudflare Worker 등 모든 외부 전송이 sandbox egress에 차단

**즉 리포트 자체는 매일 정상 생성되며, 세션 URL 접속하면 읽을 수 있는 상태 (pull-based로는 이미 동작).** 자동 push 알림만 안 됨.

---

## 배달 차단 원인 (2026-07-31 확인)

Anthropic 클라우드 sandbox는 **매우 좁은 도메인 화이트리스트**를 사용. 사용자가 이 목록을 수정하려면 Team/Enterprise 플랜 필요 (Individual 플랜에서는 접근 불가).

| 시도한 경로 | 결과 |
|-------------|------|
| `api.telegram.org` 직접 호출 (GET/POST) | 403 Policy Denial — 메시징 서비스 남용 방지로 원천 차단 |
| `api.github.com` + PAT | 403 — GitHub API는 Claude GitHub App 연결이 없으면 차단 |
| GitHub App 설치 후 `gh issue create` | 403 Resource not accessible by integration — App이 read-only 권한만 있음 |
| `git push` (App 인증) | 403 — 동일 사유, App에 Contents write 없음 |
| `curl` to `*.workers.dev` (Cloudflare Worker 릴레이) | connect_rejected 403 — 사용자 정의 서드파티 도메인도 화이트리스트 밖 |

**Individual 플랜에서는 이 화이트리스트 안에서만 동작 가능**. 파악된 허용 범위는 대체로 WebSearch/WebFetch가 다루는 공용 웹 콘텐츠 정도.

---

## 다음 세션 재개 방향 3가지

### 옵션 1) 로컬 Python 스크립트 + Windows 작업 스케줄러 ⭐ 권장

- **원리**: PC의 Python이 매일 18시 실행 → Anthropic API로 검색·분석 → Telegram 직접 호출 (로컬에서는 egress 정책 없음)
- **장점**: 확실. 텔레그램 원상 복구. sandbox 정책 완전 우회
- **단점**: PC 켜져 있어야 함. Claude API 소액 과금 (일 1회 실행이면 월 몇천원)
- **세팅 시간**: 60분 (스크립트 + Anthropic API 키 + 작업 스케줄러 등록)
- **참고**: 이 옵션은 `docs/archive/twinkling-finding-blossom.md` 원본 계획서에도 "로컬 폴백 옵션"으로 언급되어 있음
- **버릴 것**: Claude Cloud routine 자체는 disable (또는 남겨두고 로컬로 대체 실행)

### 옵션 2) Discord Webhook 실험 (5분 프로브)

- Discord 계정 + 개인 서버 + 채널 Webhook URL 생성 → 라우틴 프롬프트에서 그 URL로 POST
- Cloudflare가 막혔으니 Discord도 안 될 확률 높음 — **먼저 sandbox에서 `curl https://discord.com/`이 통과하는지 프로브 테스트** 필요
- 통과하면: 채널 변경(Telegram → Discord) 감수하고 클라우드 라우틴 유지 가능
- 안 통과하면: 옵션 1로

### 옵션 3) Pull 방식 유지 (현 상태 그대로)

- 매일 세션 URL 열어서 리포트 읽음 → https://claude.ai/code/routines/trig_014gH3d4moi4fhd2J2JyDfw2
- 자동 알림은 없음. 세팅 0
- 습관 형성만 되면 실용상 나쁘지 않음

---

## 관련 자산 (모두 유지)

- **Claude Cloud Routine** `trig_014gH3d4moi4fhd2J2JyDfw2` — 매일 09:00 UTC 자동 실행 중. 프롬프트에 Cloudflare Worker URL 박혀있음
- **Cloudflare Worker** `tg-relay.elfcarpin.workers.dev` — 텔레그램 릴레이. 로컬 curl에선 동작 확인됨, sandbox에서만 차단. [`shared/cloudflare/README.md`](../../shared/cloudflare/README.md) 참조
- **Telegram Bot** `@JamesMyHomeBot` — chat_id 확보. `shared/telegram/config.local.json`
- **GitHub App (Claude)** — Authorized 됐지만 write 권한 없음. Individual 플랜 제약

---

## 참고

- 원본 요청서: [`../../docs/초기요청사항.txt`](../../docs/초기요청사항.txt)
- 이전 진행 문서: [`../../docs/archive/twinkling-finding-blossom.md`](../../docs/archive/twinkling-finding-blossom.md)
- 2026-07-31 여정 상세: [`../../docs/archive/2026-07-31-egress-blocked.md`](../../docs/archive/2026-07-31-egress-blocked.md)
