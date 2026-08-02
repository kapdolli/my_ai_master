# 국어강사아이템

> ⚠ **on-demand 전용 서비스** — 사용자가 명시적으로 요청할 때만 실행한다. Windows 작업 스케줄러에 등록하지 말 것.
> `idea_search`(매일 자동)와는 완전히 별개의 독립 서비스이며, 서로 실행 시각·프롬프트·로그를 공유하지 않는다.

특정 페르소나(**중고등 국어강사 · 학원 운영 10년 · 국문과 출신 · 50대 중반 여성**)에 맞춰
**본인 경험을 자산 삼아 시작할 수 있는 부업 · 1인 창업 · 경력 전환 아이템**을 국내외 사례와 함께 조사·정리해
텔레그램으로 리포트를 전달하는 서비스.

| 항목 | 값 |
|------|-----|
| **실행 방식** | 로컬 Python + Claude Code CLI — **on-demand** (스케줄 없음) |
| **트리거** | 사용자가 갑돌이 CLI에서 명시적으로 요청 (예: "갑돌아 국어강사아이템 돌려줘") |
| 인증 | Claude Code subscription (Pro/Max) — 다른 서비스와 공유 |
| 전달 채널 | Telegram Bot API (`@JamesMyHomeBot`) |
| 프롬프트 | [`prompt.md`](prompt.md) — 페르소나 프로필 + 검색 소스 지정 |
| 로그 | `logs/YYYY-MM-DD_HHMMSS.md` (호출 시각별) |

---

## 대상 페르소나 (고정값)

| 항목 | 값 |
|------|-----|
| 직업 | 현직 국어강사 (학원) |
| 나이 · 성별 | 50대 중반 · 여성 |
| 경력 | 국어강사 장기 경력 + 학원 운영 약 10년 (현재는 강사 재직) |
| 담당 | 중학교·고등학교 국어 전문 (문학·비문학·문법·독해·수능/내신) |
| 학력 | 국어국문학과 출신, 글쓰기 · 첨삭 · 논술 지도 가능 |
| 상황 | 학령인구·강사 자리 감소. 그동안의 경험(강의·운영·글쓰기)을 살릴 새 수익원 필요 |

프로필이 바뀌면 [`prompt.md`](prompt.md) 상단의 **"대상 페르소나"** 표를 편집한다.

---

## 산출물 (리포트 구조)

카테고리별로 아이템을 분류해 총 10개 선별.

- 📝 1:1 지도·코칭 / 🎥 콘텐츠 크리에이터 / 📚 지식상품 판매 / 🏫 커뮤니티·클래스 / 💼 B2B·프리랜서 / 🌱 경력 전환·자격
- 각 아이템: 진입난이도, 경험 적합도(★1~5), 수익성(★1~5), AI 활용도(★1~5), 왜 이 페르소나에 맞는지, 국내 사례, 첫 3개월 실행 스텝, 지속성 코멘트, 원문 URL
- 마지막: 즉시 실행 추천 픽 Top 3 + 피해야 할 유형

리포트 포맷 전체는 [`prompt.md`](prompt.md) STEP 3 참조.

---

## 사용법

### 갑돌이(Claude Code)에게 자연어로 요청

```
갑돌아 국어강사아이템 돌려줘
갑돌아 국어강사 부업 아이템 조사 부탁해
갑돌아 국어강사아이템 dry-run 으로 미리보기만
```

갑돌이가 파싱해서 아래 명령을 실행한다.

### PowerShell에서 직접

```powershell
# 정상 실행 (리포트 생성 + 텔레그램 발송)
python services/korean_teacher_items/run_local.py

# 텔레그램 발송 없이 로그만 (실행 전 미리보기)
python services/korean_teacher_items/run_local.py --dry-run

# 실행할 claude 명령만 확인 (진단용)
python services/korean_teacher_items/run_local.py --show-cmd
```

성공 시 콘솔에 `[claude] exec: ... [log] ... [telegram] chunk 1/N sent ... [done]` 순서로 출력되고 `@JamesMyHomeBot` 으로 리포트가 도착한다.

---

## 최초 세팅

기존 `idea_search`가 이미 세팅되어 있다면 별도 준비 없음. 같은 Claude Code CLI 인증과 텔레그램 봇 자격증명을 공유한다.

- Claude Code 인증: [`../../shared/claude_code/README.md`](../../shared/claude_code/README.md)
- Telegram 봇 자격증명: [`../../shared/telegram/README.md`](../../shared/telegram/README.md) (`shared/telegram/config.local.json`)

Python 패키지 추가 설치 없음 — 표준 라이브러리만 사용.

**Windows 작업 스케줄러에는 등록하지 않는다.** on-demand 특성상 자동 실행되면 안 됨.

---

## 운영

| 상황 | 조치 |
|------|------|
| 리포트 재생성 | `python run_local.py` 재실행 (호출 시각별로 로그 파일이 새로 생성됨) |
| 발송 없이 리허설 | `python run_local.py --dry-run` |
| 명령 확인 | `python run_local.py --show-cmd` |
| 모델 교체 | 환경변수 `KOREAN_TEACHER_MODEL=sonnet` 또는 `opus` |
| 타임아웃 조정 | 환경변수 `KOREAN_TEACHER_TIMEOUT=1200` (기본 900초) |
| claude 경로 지정 | 환경변수 `CLAUDE_BIN=C:\path\to\claude.exe` |
| 페르소나 프로필 변경 | [`prompt.md`](prompt.md) 상단 "대상 페르소나" 표 편집 |
| 검색 소스 변경 | [`prompt.md`](prompt.md) STEP 1 편집 |

---

## 참고

- 최상위 저장소 개요: [`../../README.md`](../../README.md)
- 연관 서비스(다른 페르소나·주제): [`../idea_search/README.md`](../idea_search/README.md) — 매일 자동 실행되는 IT/AI 아이템 리포트
- 아이템 심층 분석: [`../item_analyzer/README.md`](../item_analyzer/README.md) — 이 리포트에서 관심 아이템 하나를 골라 넘기면 실행 가능성·경쟁 분석까지
