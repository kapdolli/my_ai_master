# 갑돌이마스터 (my_ai_master)

내 개인용 서비스/에이전트를 한 곳에서 관리하는 상위 저장소.

각 서비스는 **Claude Code의 Cloud Schedule**에 등록된 프롬프트로 실행되며, 결과는 텔레그램 등 지정 채널로 전달된다.
저장소는 로직을 담는 곳이라기보다 **"어떤 서비스가 무엇을, 언제, 어떤 프롬프트로 실행하는지"를 기록·관리하는 사양서** 역할을 한다.

---

## 실행 모델

```
[Claude Cloud Schedule] ──정해진 시각──▶ [Claude Agent]
                                              │
                              ┌───────────────┤
                              │  WebSearch     │  WebFetch
                              ▼                ▼
                        데이터 소스        Telegram Bot API
                        (Reddit, HN, …)   등 전달 채널
```

- 서비스 로직은 Python 코드가 아니라 **`services/<name>/prompt.md`** 에 자연어로 기술한다.
- 스케줄 등록 시 이 프롬프트 전체를 `/schedule` 입력란에 그대로 복사해 넣는다.
- 토큰·chat_id 등 자격 증명은 `shared/` 아래 `*.local.*` 파일에만 두고 스케줄 환경변수로 주입한다.

---

## 폴더 규약

```
my_ai_master/
├─ README.md                # 이 파일
├─ services/                # 서비스별 격리 폴더
│   └─ <service_name>/
│       ├─ prompt.md        # /schedule 에 붙여넣을 단일 소스 프롬프트
│       ├─ README.md        # 서비스 개요·등록·재개 절차
│       └─ samples/         # 실행 결과 예시 아카이브 (프롬프트 튜닝 대조용)
├─ shared/                  # 서비스 간 공용 자산
│   ├─ telegram/            # 봇 토큰·chat_id + 사용 가이드
│   ├─ github/              # kapdolli PAT + Claude App 사용 가이드
│   └─ cloudflare/          # tg-relay Worker (현재 sandbox egress에 차단됨, 로컬 사용 가능)
└─ docs/                    # 원본 요청서, 이전 진행 기록 등
    ├─ 초기요청사항.txt
    └─ archive/             # 이전 계획서 및 여정 기록
```

**4가지 원칙**
1. 서비스는 `services/<name>/` 단위 폴더로 격리한다. 최소 `prompt.md` + `README.md`를 갖는다.
2. **로직 소유자는 Claude Code 자체.** `prompt.md`가 유일한 실행 사양이며, 프롬프트 개정 = 서비스 개정.
3. 공용 자산(토큰, 공통 스니펫)은 `shared/`에 둔다. 실제 자격 증명은 `*.local.*` 파일에만 두고 git에는 올리지 않는다.
4. 실행 결과 예시는 `services/<name>/samples/`에 날짜별로 아카이빙한다.

---

## 등록된 서비스

| 이름 | 폴더 | 실행 시각 | 채널 | 상태 |
|------|------|-----------|------|------|
| 아이디어 서치 에이전트 | [`services/idea_search/`](services/idea_search/README.md) | 매일 18:00 KST (09:00 UTC) | Telegram (예정) | ⚠ **배달 차단** — 라우틴은 매일 정상 실행되고 리포트도 생성되나 Anthropic sandbox egress 정책으로 텔레그램 발송 불가. 재개 방향은 서비스 README 참조. 오늘까지의 여정은 `docs/archive/2026-07-31-egress-blocked.md` |

---

## 새 서비스 추가 절차

1. `services/<service_name>/` 폴더 생성 (snake_case)
2. `prompt.md` 작성 — `/schedule` 프롬프트 입력란에 그대로 복사할 수 있는 완결된 지시문
3. `README.md` 작성 — 목적, 실행 시각, 등록 절차, 재개 절차, 테스트 방법
4. Claude Code에서 `/schedule` 실행 → 이름, 주기, 환경변수, 프롬프트 입력
5. "지금 실행"으로 즉시 테스트
6. 최상위 `README.md`의 "등록된 서비스" 표에 한 줄 추가
