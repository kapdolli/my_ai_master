# 아이디어 서치 에이전트

Reddit, HackerNews, Product Hunt, IndieHackers, 한국 커뮤니티 등에서 유망 사업 아이디어·AI 활용 아이템·수익화 정보를 매일 수집·요약해 **텔레그램**으로 전달하는 서비스.

| 항목 | 값 |
|------|-----|
| 실행 방식 | Claude Cloud Schedule (`/schedule`) |
| 실행 시각 | 매일 18:00 KST (= UTC 09:00) |
| 전달 채널 | Telegram Bot |
| 리포트 언어 | 한국어 |
| 프롬프트 | [`prompt.md`](prompt.md) |
| 결과 예시 | [`samples/`](samples/) |

---

## 최초 등록 절차

1. **자격 증명 준비** — [`../../shared/telegram/config.local.json`](../../shared/telegram/README.md) 에서 `bot_token`, `chat_id` 값 확인.
   - Chat ID를 아직 못 받은 경우: `shared/telegram/README.md` "Chat ID 확인 방법" 참조.
2. **프롬프트 복사** — 이 폴더의 [`prompt.md`](prompt.md) 파일을 열어 **전체 본문**을 복사.
3. **Claude Code에서 `/schedule` 실행** — 아래 값 입력:
   - **이름**: `idea-search-agent`
   - **주기**: 매일 09:00 UTC (= KST 18:00)
   - **환경변수**:
     - `TELEGRAM_TOKEN` = `config.local.json`의 `bot_token`
     - `TELEGRAM_CHAT_ID` = `config.local.json`의 `chat_id`
   - **프롬프트**: 방금 복사한 `prompt.md` 내용을 붙여넣기
4. **즉시 테스트** — 스케줄 생성 UI의 "지금 실행" → 텔레그램 메시지 수신 확인.
5. 성공하면 최상위 `README.md`의 서비스 표 상태를 **"정상 운영"**으로 갱신.

---

## 프롬프트 수정 후 갱신 절차

1. [`prompt.md`](prompt.md) 수정 → 커밋
2. Claude Code의 스케줄 관리 UI에서 `idea-search-agent`를 찾아 **프롬프트 필드 전체를 새 내용으로 교체**
3. "지금 실행"으로 즉시 검증
4. 결과가 만족스러우면 그 실행 결과를 `samples/YYYY-MM-DD.md`로 아카이빙

---

## 문제 해결

| 증상 | 확인 순서 |
|------|-----------|
| 텔레그램 메시지 미수신 | ① Bot Token 유효성 (BotFather에서 재확인) → ② Chat ID 정확성 → ③ 프롬프트 내 텔레그램 전송 블록의 URL 인코딩 여부 → ④ 메시지 4096자 초과 여부 |
| 검색 결과가 빈약함 | 프롬프트 STEP 1의 소스 목록 조정 후 "지금 실행"으로 재검증 |
| 텍스트가 깨져 보임 | `parse_mode=HTML` 유지, HTML 특수문자(`<`, `>`, `&`) 이스케이프 여부 확인 |

---

## 참고

- 원본 요청서: [`../../docs/초기요청사항.txt`](../../docs/초기요청사항.txt)
- 이 서비스의 이전 진행 기록: [`../../docs/archive/twinkling-finding-blossom.md`](../../docs/archive/twinkling-finding-blossom.md)
