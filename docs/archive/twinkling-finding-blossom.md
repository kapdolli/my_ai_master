# 아이디어 서치 에이전트 — 전체 작업 문서

> 작성일: 2026-07-30  
> 상태: **진행 중** — Chat ID 확인 후 /schedule 등록만 남음

---

## 서비스 개요

매일 18:00 KST에 Reddit, HackerNews, Product Hunt, IndieHackers 등 국내외 커뮤니티에서 유망 사업 아이디어·AI 활용 아이템·트렌딩 수익화 정보를 자동 수집·요약해 **텔레그램**으로 전달하는 개인용 서비스.

| 항목 | 내용 |
|------|------|
| 실행 방식 | Claude Code 구독형 Cloud Schedule (API 과금 없음) |
| 전달 채널 | Telegram Bot |
| 리포트 언어 | 한국어 요약 |
| 실행 주기 | 매일 18:00 KST (= UTC 09:00) |

---

## 아키텍처

```
[Claude Cloud Schedule] ──매일 18:00 KST──▶ [Claude Agent]
                                                   │
                          ┌────────────────────────┤
                          │  WebSearch              │  WebFetch
                          ▼                         ▼
                    Reddit, HN,            Telegram Bot API
                    Product Hunt,          GET sendMessage
                    IndieHackers,
                    한국 커뮤니티
```

---

## 현재 진행 상황 (2026-07-30)

| 단계 | 상태 | 메모 |
|------|------|------|
| 텔레그램 봇 생성 (@BotFather) | ✅ 완료 | Bot Token 보유 중 |
| Chat ID 확인 | ⏳ 진행 중 | getUpdates 결과 `[]` — 봇에 메시지를 먼저 보내야 함 |
| /schedule 등록 | 대기 | Chat ID 확인 후 진행 |
| 테스트 실행 | 대기 | — |

---

## 다음에 해야 할 일 (재개 시 여기서부터)

### Step 1 — Chat ID 확인

1. Telegram 앱에서 본인이 만든 봇을 찾아 아무 메시지 전송 (예: "안녕")
2. 브라우저에서 아래 URL 열기 (TOKEN은 BotFather에서 받은 값):
   ```
   https://api.telegram.org/bot{YOUR_TOKEN}/getUpdates
   ```
3. 응답에서 `result[0].message.chat.id` 값 확인 (숫자)
   ```json
   {
     "ok": true,
     "result": [{
       "message": {
         "chat": {
           "id": 123456789   ← 이 숫자가 CHAT_ID
         }
       }
     }]
   }
   ```

### Step 2 — Claude Code에서 /schedule 등록

Claude Code 터미널(또는 앱)에서 `/schedule` 스킬 실행:

```
/schedule
```

입력할 내용:
- **이름**: `idea-search-agent`
- **주기**: 매일 09:00 UTC (= KST 18:00)
- **환경변수**:
  - `TELEGRAM_TOKEN` = (BotFather에서 받은 토큰)
  - `TELEGRAM_CHAT_ID` = (Step 1에서 확인한 숫자)
- **프롬프트**: 아래 "에이전트 프롬프트" 섹션 전체 복사

### Step 3 — 즉시 테스트 실행

스케줄 생성 후 "지금 실행" 옵션 선택 → 텔레그램에 메시지 수신 확인

---

## 에이전트 프롬프트 (스케줄에 등록할 전체 내용)

아래를 그대로 `/schedule` 프롬프트 입력란에 붙여넣기:

```
오늘 날짜와 시간을 확인하고, 다음 작업을 순서대로 수행하라.

## 목표
Reddit, HackerNews, Product Hunt 등 국내외 커뮤니티에서 오늘 주목할 만한
사업 아이디어 / AI 활용 아이템 / 수익화 방법을 수집하고 한국어로 요약한 뒤
텔레그램으로 전송한다.

## [STEP 1] 검색

아래 소스에서 최신 인기 게시글을 WebSearch로 검색한다:
- Reddit: r/entrepreneur, r/sidehustle, r/startups, r/SomebodyMakeThis, r/AITools, r/passive_income
- HackerNews: "side project money", "indie hacker revenue", "show HN new product"
- Product Hunt: 오늘 론칭된 신규 제품 (top products today)
- IndieHackers: 최신 수익화 성공 사례
- 한국: 클리앙 알뜰구매, 에펨코리아 핫딜, 네이버 블로그 창업 아이디어

각 소스에서 3~5개씩, 총 15~25개 후보를 수집한다.

## [STEP 2] 분석 및 평가

각 아이템을 다음 기준으로 평가한다:
- 카테고리: 🚀창업아이디어 / 🤖AI활용 / 💰수익화 / 📈트렌딩아이템
- 난이도: 상/중/하 (혼자 실행 가능 여부 기준)
- 수익 가능성: ★1~5
- AI 활용도: ★1~5 (AI로 자동화·확장 가능한 정도)

상위 10개를 선별한다.

## [STEP 3] 텔레그램 전송

아래 형식으로 메시지를 구성하고, WebFetch GET 요청으로 텔레그램에 전송한다.
메시지가 1500자 초과 시 섹션별로 분할해 여러 번 전송한다.

--- 메시지 포맷 ---
📋 오늘의 아이디어 리포트
{YYYY-MM-DD} | 총 {N}개 아이템
━━━━━━━━━━━━━━━━━━

🚀 창업아이디어
• [아이템명] 한 줄 요약
  난이도: 하 | 수익성: ★★★★ | AI활용: ★★★★★
  🔗 원문: {URL}

🤖 AI활용
• [아이템명] ...

💰 수익화
• [아이템명] ...

📈 트렌딩
• [아이템명] ...
--- 포맷 끝 ---

텔레그램 전송 URL (WebFetch GET):
https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage?chat_id={TELEGRAM_CHAT_ID}&parse_mode=HTML&text={URL인코딩된메시지}

환경변수 TELEGRAM_TOKEN, TELEGRAM_CHAT_ID를 사용한다.
전송 성공 시 "ok": true 응답을 확인한다.
```

---

## 텔레그램 전송 기술 메모

Telegram Bot API는 GET 방식 지원 → Claude의 `WebFetch`로 전송 가능:

```
https://api.telegram.org/bot{TOKEN}/sendMessage
  ?chat_id={CHAT_ID}
  &text={URL인코딩된텍스트}
  &parse_mode=HTML
```

- 메시지 최대 길이: 4096자 (HTML 태그 포함)
- 실용 권장 길이: 1500자 이하로 분할
- URL 인코딩 필수: 한글, 특수문자 포함 시

---

## 제약 및 고려사항

| 항목 | 내용 |
|------|------|
| Claude 구독 | API 과금 없음 — cloud schedule은 구독에 포함 |
| Telegram Bot API | 무료, Bot Token만 있으면 됨 |
| 메시지 길이 | 4096자 제한 → 섹션 분할로 처리 |
| 검색 품질 | WebSearch 결과에 의존 — 직접 스크래핑보다 제한적일 수 있음 |
| 시간대 | UTC 09:00 = KST 18:00 |

---

## 로컬 폴백 옵션 (Cloud Schedule 불가 시)

Python 스크립트 + Windows 작업 스케줄러로 대체 가능:

- Python 3.10: `C:\Users\D4003412\AppData\Local\Programs\Python\Python310\`
- 이미 설치된 패키지: `requests`, `httpx`, `python-dotenv`
- 프로젝트 위치: `D:\work\idea-agent\` 신규 생성
- 스케줄러: Windows 작업 스케줄러 → 매일 18:00 Python 스크립트 실행
