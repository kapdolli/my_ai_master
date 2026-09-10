# 갑돌이마스터 (my_ai_master)

내 개인용 서비스/에이전트를 한 곳에서 관리하는 상위 저장소.

각 서비스는 **로컬 Python 스크립트**로 실행되며(Windows 작업 스케줄러 등이 정해진 시각에 트리거), 결과는 텔레그램 등 지정 채널로 전달된다.
저장소는 로직을 담는 곳이라기보다 **"어떤 서비스가 무엇을, 언제, 어떤 프롬프트로 실행하는지"를 기록·관리하는 사양서** 역할을 한다.

> 이전에는 Claude Code Cloud Schedule로 실행했으나, Anthropic sandbox egress 정책으로 텔레그램 발송이 차단되어 2026-07-31에 로컬 Python 실행으로 전환했다. 배경은 [`docs/archive/2026-07-31-egress-blocked.md`](docs/archive/2026-07-31-egress-blocked.md) 참조.

---

## 실행 모델

```
[Windows 작업 스케줄러] ──정해진 시각──▶ [로컬 Python 스크립트]
                                                │
                                     ┌──────────┴──────────┐
                                     ▼                     ▼
                              claude -p               Telegram Bot API
                              (Claude Code CLI         (직접 호출)
                               헤드리스 모드,
                               WebSearch 내장)
```

- 서비스 로직의 핵심(검색·분석·요약)은 **`services/<name>/prompt.md`** 에 자연어로 기술한다.
- 각 서비스는 자기 폴더에 `run_local.py`를 두고, 이 스크립트가 `prompt.md`를 읽어 `claude -p` 서브프로세스로 넘긴 뒤 stdout 응답을 채널로 발송한다.
- 인증은 **Claude Code subscription**(Pro/Max)의 장기 토큰(`claude setup-token`)을 사용한다. Anthropic API 키·별도 과금 없음.
- 텔레그램 봇 토큰·chat_id 등 채널 자격 증명은 `shared/` 아래 `*.local.*` 파일에만 두고 스크립트가 직접 로드한다 (git 커밋 차단됨).

---

## 폴더 규약

```
my_ai_master/
├─ README.md                # 이 파일
├─ services/                # 서비스별 격리 폴더
│   └─ <service_name>/
│       ├─ prompt.md        # 검색·분석·요약 지시사항 (claude -p 에 stdin으로 전달)
│       ├─ run_local.py     # 로컬 실행 진입점 (prompt.md 로드 → claude 서브프로세스 → 채널 발송)
│       ├─ README.md        # 서비스 개요·세팅·운영 절차
│       ├─ logs/            # 일자별 실행 로그 (아카이브)
│       └─ samples/         # 초기 수동 결과물 (프롬프트 튜닝 대조용)
├─ shared/                  # 서비스 간 공용 자산
│   ├─ claude_code/         # Claude Code CLI 인증(subscription 토큰) 가이드
│   ├─ telegram/            # 봇 토큰·chat_id + 사용 가이드
│   ├─ github/              # kapdolli PAT + Claude App 사용 가이드 (현재 서비스에서 미사용)
│   └─ cloudflare/          # tg-relay Worker (로컬 실행 전환으로 현재 미사용, 삭제 검토 대상)
└─ docs/                    # 원본 요청서, 이전 진행 기록 등
    ├─ 초기요청사항.txt
    └─ archive/             # 이전 계획서 및 여정 기록 (인덱스: archive/README.md)
```

**4가지 원칙**
1. 서비스는 `services/<name>/` 단위 폴더로 격리한다. 최소 `prompt.md` + `run_local.py` + `README.md`를 갖는다.
2. **로직의 지능은 Claude가 담당.** `run_local.py`는 얇은 래퍼(프롬프트 로드, `claude -p` 호출, 응답 저장/발송)이며 검색·분석·요약 로직은 `prompt.md`에만 기술한다. Python 표준 라이브러리만 사용 — 별도 pip 패키지 없음.
3. 공용 자산(토큰, 공통 스니펫)은 `shared/`에 둔다. 실제 자격 증명은 `*.local.*` 파일에만 두고 git에는 올리지 않는다. Claude CLI 자체 인증은 `~/.claude/`에 저장(저장소 밖).
4. 실행 로그는 `services/<name>/logs/`에 자동 저장된다. 프롬프트 튜닝 대조용 초기 수동 결과물은 `samples/`에 보관.

> 예외: [`services/susi_competition/`](services/susi_competition/README.md) 는 Claude 호출이 없는 순수 스크래핑 서비스라 `prompt.md`/`run_local.py` 대신 PowerShell 진입점(`refresh_all.ps1`)과 Python 스크립트를 두고, 유일하게 pip 패키지(`requests`, `beautifulsoup4`)를 사용한다.

---

## 등록된 서비스

| 이름 | 폴더 | 실행 트리거 | 채널 | 상태 |
|------|------|-------------|------|------|
| 아이디어검색가 | [`services/idea_search/`](services/idea_search/README.md) | 매일 18:00 KST (작업 스케줄러 `idea-search-agent`) | Telegram | 🟡 리포트 생성은 복구됨 — `shared/telegram/config.local.json` 부재로 발송만 대기 |
| 아이템분석가 | [`services/item_analyzer/`](services/item_analyzer/README.md) | On-demand (사용자가 후보 지정) | Telegram | 🟢 정상 — 아이디어검색가 후보 중 하나를 골라 1인·비전문가·부업 관점 실행 가능성 + 국내/해외 사례 분석 |
| 국어강사아이템 | [`services/korean_teacher_items/`](services/korean_teacher_items/README.md) | **On-demand 전용 (스케줄 없음 — 사용자가 요청할 때만 실행)** | Telegram | 🟡 대기 — 중고등 국어강사·학원운영 10년·50대 중반 여성 페르소나 맞춤 부업/경력전환 아이템 조사 |
| 수시경쟁률 | [`services/susi_competition/`](services/susi_competition/README.md) | **10분 간격** (작업 스케줄러 `SusiRefresh`) | [GitHub Pages](https://kapdolli.github.io/my_ai_master/) | 🟢 정상 — 2027 수시 저경쟁 학과(수도권·충청 전체 대학 농어촌·논술·기회균형, ★ 주요대학 19개교 필터, 접수·경쟁률 마감시각) 페이지 자동 갱신·배포 |

**연계 흐름**:
- IT/AI 트랙: 아이디어검색가(매일 자동) → 관심 아이템 선택 → 아이템분석가(on-demand)로 심층 분석 → 실행 여부 판단.
- 수시 트랙: 독립 서비스 — Claude 호출 없이 로컬 스크래핑 결과를 GitHub Pages 로 배포한다 (다른 트랙과 연계 없음).
- 국어강사 트랙: 국어강사아이템(on-demand — "갑돌아 국어강사아이템 돌려줘"로 호출) → 관심 아이템이 있으면 아이템분석가로 넘겨 심층 분석.

---

## 새 서비스 추가 절차

1. `services/<service_name>/` 폴더 생성 (snake_case)
2. `prompt.md` 작성 — 검색·분석·요약 지시사항 (Claude에 그대로 전달됨)
3. `run_local.py` 작성 — `idea_search/run_local.py`를 템플릿으로 복사 후 프롬프트 경로·발송 채널만 수정
4. `README.md` 작성 — 목적, 실행 시각, 세팅 절차, 운영 절차, 테스트 방법
5. `python services/<service_name>/run_local.py --dry-run` 으로 로컬 테스트
6. Windows 작업 스케줄러 등록 (idea_search README의 4번 절차 참고)
7. 최상위 `README.md`의 "등록된 서비스" 표에 한 줄 추가
