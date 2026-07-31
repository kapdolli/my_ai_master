# 아이디어 서치 에이전트 — 실행 프롬프트

> **상태 (2026-07-31)**: 이 프롬프트는 라우틴 `trig_014gH3d4moi4fhd2J2JyDfw2`에 등록된 현행 버전.
> STEP 3의 Cloudflare Worker 호출이 sandbox egress에 차단되어 **배달은 실패**하지만, STEP 1~2는 정상 동작해 리포트 본문은 세션 로그에 남음.
> 재개 방향은 [`README.md`](README.md) 하단 참조.

---

오늘 날짜(KST 기준)를 확인하고, 다음 작업을 순서대로 수행하라.

## 목표
Reddit, HackerNews, Product Hunt 등 국내외 커뮤니티에서 오늘 주목할 만한
사업 아이디어 / AI 활용 아이템 / 수익화 방법을 수집하고 한국어로 요약한 뒤
Cloudflare Worker 릴레이를 경유해 텔레그램으로 전송한다.

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

## [STEP 3] Cloudflare Worker 경유 텔레그램 발송

리포트 본문을 아래 포맷으로 구성해 임시 파일로 저장하고, curl로 Worker에 POST한다.

### 리포트 포맷 (Markdown, 텔레그램은 plain text로 보이므로 가독성 우선)

```
📋 오늘의 아이디어 리포트 YYYY-MM-DD
총 {N}개 아이템 선별 (Reddit · HN · Product Hunt · IndieHackers · 한국)

🤖 AI 활용
────────────────────
① [아이템명]
  한 줄 요약: ...
  난이도: 하 | 수익성: ★★★★ | AI활용: ★★★★★
  핵심: ...
  원문: {URL}

② [아이템명]
...

🚀 창업 아이디어
────────────────────
...

💰 수익화 검증
────────────────────
...

📈 트렌딩 아이템
────────────────────
...

📌 오늘의 추천 픽 (즉시 실행 가능성 기준)
1. ...
2. ...
3. ...
```

### 발송 스크립트

```bash
DATE=$(TZ='Asia/Seoul' date +%Y-%m-%d)

# 리포트 본문을 임시 파일로 저장 (위 포맷으로 마굴보기 둘러싼 것)
cat > /tmp/report.txt <<'REPORT_EOF'
📋 오늘의 아이디어 리포트 [여기 $DATE 값 넣음]
총 N개 아이템 선별 ...

🤖 AI 활용
────────────────────
① [아이템명]
... (이하 생략)
REPORT_EOF

# JSON payload 만들기 (jq로 안전하게 이스케이프)
jq -n --rawfile r /tmp/report.txt '{message: $r}' > /tmp/payload.json

# Worker 호출
RESP=$(curl -sS -X POST https://tg-relay.elfcarpin.workers.dev \
  -H "Content-Type: application/json; charset=utf-8" \
  -H "X-Shared-Secret: YR6jTkUYKfEw2YcIavouxKbmGmMcOSKh2-8TujAKZ7M" \
  --data-binary @/tmp/payload.json)

echo "=== Worker 응답 ==="
echo "$RESP" | jq .
```

응답에 `"ok": true` 있으면 성공. Worker가 자동으로 3800자 단위로 분할해 텔레그램 여러 메시지로 보내므로 클라이언트에서는 분할 불필요.

실패(`"ok": false` 또는 HTTP != 200) 시: 응답 전체 + Worker URL + heredoc으로 머진 본문 앞 200자를 세션 로그에 남긴다.

성공 여부와 무관하게, 리포트 본문 전문을 세션 로그에 출력해 사용자가 세션에서도 내용을 볼 수 있게 한다.
