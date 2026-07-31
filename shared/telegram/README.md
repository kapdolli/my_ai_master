# 공용 텔레그램 자산

여러 서비스가 공통으로 사용하는 텔레그램 봇 설정 및 전송 스니펫.

---

## 파일

- `config.local.json` (gitignore) — `bot_token`, `chat_id` 값. 스케줄 등록 시 환경변수로 주입한다.

---

## Bot 생성 (1회성, 완료됨)

1. 텔레그램에서 `@BotFather` 검색 → 대화 시작
2. `/newbot` → 봇 이름·username 지정
3. 응답으로 받은 **Bot Token**을 `config.local.json`의 `bot_token`에 저장

---

## Chat ID 확인 방법

새 채팅방이나 봇을 추가한 뒤 아래 순서로 확인:

1. 텔레그램에서 해당 봇을 찾아 **아무 메시지 전송** (예: "안녕")
2. 브라우저에서 아래 URL 열기 (TOKEN은 BotFather에서 받은 값):
   ```
   https://api.telegram.org/bot{YOUR_TOKEN}/getUpdates
   ```
3. 응답 JSON에서 `result[0].message.chat.id` 값(숫자) 확인:
   ```json
   {
     "ok": true,
     "result": [{
       "message": {
         "chat": { "id": 123456789 }
       }
     }]
   }
   ```
4. 그 숫자를 `config.local.json`의 `chat_id`에 저장

> `result: []` 로 비어 있으면 봇에게 메시지를 먼저 보내지 않은 상태다. 1번부터 다시.

---

## 전송 스니펫 (GET, `WebFetch` 호환)

Claude Code의 `WebFetch` 도구는 GET 요청을 지원하므로 아래 URL 하나로 전송이 완결된다:

```
https://api.telegram.org/bot{TOKEN}/sendMessage
  ?chat_id={CHAT_ID}
  &text={URL인코딩된텍스트}
  &parse_mode=HTML
```

성공 응답:
```json
{"ok": true, "result": {...}}
```

---

## 제약 및 주의사항

| 항목 | 내용 |
|------|------|
| 메시지 최대 길이 | 4096자 (HTML 태그 포함) — 실용상 1500자 이하 권장, 초과 시 섹션 분할 |
| URL 인코딩 | 한글·특수문자는 반드시 인코딩. 미인코딩 시 400 응답 |
| HTML 이스케이프 | `parse_mode=HTML` 사용 시 본문의 `<`, `>`, `&` 는 `&lt;`, `&gt;`, `&amp;` 로 치환 |
| 자격 증명 | `bot_token` 은 유출 시 즉시 BotFather에서 재발급. 절대 커밋 금지 (`.gitignore`로 보호 중) |
