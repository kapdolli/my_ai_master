# 아이디어 서치 에이전트 — 실행 프롬프트

> 이 파일 전체를 Claude Code의 `/schedule` 프롬프트 입력란에 그대로 복사해 등록한다.
> 프롬프트 개정 = 서비스 개정. 수정 후에는 스케줄을 갱신하고 `samples/`에 새 결과를 아카이빙한다.

---

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
