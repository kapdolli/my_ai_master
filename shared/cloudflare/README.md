# 공용 Cloudflare 자산

Anthropic 클라우드 sandbox의 egress 제약 우회를 위해 만들어진 Cloudflare Worker 릴레이.

**⚠ 현재 상태 (2026-07-31)**: Worker 자체는 정상 배포·동작하지만, Anthropic sandbox가 `*.workers.dev`를 화이트리스트에 두지 않아 **라우틴에서 호출하면 `connect_rejected 403`으로 차단**. 로컬에서 curl로 호출하면 정상 동작 확인됨. 향후 이 제약이 풀리면 즉시 재활용 가능하도록 유지.

---

## 파일

- `config.local.json` (gitignore) — Worker 이름·URL·SHARED_SECRET

---

## Worker 사양

| 항목 | 값 |
|------|-----|
| 이름 | `tg-relay` |
| URL | `https://tg-relay.elfcarpin.workers.dev` |
| 계정 | elfcarpin (Cloudflare 무료 플랜) |
| 인증 | `X-Shared-Secret` HTTP 헤더 |
| 동작 | POST 요청 받아 텔레그램 Bot API로 포워딩 (자동 3800자 분할) |

## 엔드포인트 스펙

**Request**
```
POST https://tg-relay.elfcarpin.workers.dev
Content-Type: application/json; charset=utf-8
X-Shared-Secret: <config.local.json의 shared_secret>

{
  "message": "전송할 텍스트 (길이 무관 — Worker가 3800자 단위로 자동 분할)",
  "parse_mode": "Markdown"  // 선택. 생략 시 plain text
}
```

**Response (성공)**
```json
{
  "ok": true,
  "chunks": 1,
  "results": [
    {"status": 200, "body": "{...Telegram API 응답...}"}
  ]
}
```

**Response (실패)** — HTTP 502
```json
{
  "ok": false,
  "chunks": N,
  "results": [{"status": ..., "body": "..."}]
}
```

**인증 실패**: HTTP 401 (Shared Secret 불일치)
**메소드 오류**: HTTP 405 (POST 이외)
**JSON 파싱 오류**: HTTP 400
**필드 누락**: HTTP 400 ("Missing message field")

---

## Worker 환경변수 (Cloudflare에 Secret 타입으로 저장됨)

| Name | 용도 |
|------|------|
| `TELEGRAM_TOKEN` | 텔레그램 Bot API 인증 토큰 (`shared/telegram/config.local.json`의 `bot_token`) |
| `TELEGRAM_CHAT_ID` | 메시지 수신자 chat ID (동 파일의 `chat_id`) |
| `SHARED_SECRET` | Worker 무단 호출 방지 헤더 값 |

Cloudflare 대시보드 → Workers & Pages → `tg-relay` → Settings → Variables and Secrets 에서 관리.

## Worker 소스 코드

배포된 코드는 Cloudflare 대시보드 → `tg-relay` → Edit code에서 확인. 참고용 사본:

```javascript
export default {
  async fetch(request, env) {
    if (request.method !== "POST") {
      return new Response("POST only", { status: 405 });
    }
    const secret = request.headers.get("X-Shared-Secret");
    if (!env.SHARED_SECRET || secret !== env.SHARED_SECRET) {
      return new Response("Unauthorized", { status: 401 });
    }
    let payload;
    try {
      payload = await request.json();
    } catch {
      return new Response("Invalid JSON", { status: 400 });
    }
    let text = payload.message;
    if (!text || typeof text !== "string") {
      return new Response('Missing "message" field', { status: 400 });
    }
    // Telegram 4096자 제한 회피 — 3800자 단위 분할 (개행 경계 우선)
    const chunks = [];
    while (text.length > 0) {
      let cutoff = 3800;
      if (text.length > cutoff) {
        const nl = text.lastIndexOf("\n", cutoff);
        if (nl > cutoff * 0.5) cutoff = nl;
      } else {
        cutoff = text.length;
      }
      chunks.push(text.slice(0, cutoff));
      text = text.slice(cutoff);
    }
    const results = [];
    for (const chunk of chunks) {
      const tgBody = { chat_id: env.TELEGRAM_CHAT_ID, text: chunk };
      if (payload.parse_mode) tgBody.parse_mode = payload.parse_mode;
      const r = await fetch(
        `https://api.telegram.org/bot${env.TELEGRAM_TOKEN}/sendMessage`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(tgBody),
        }
      );
      results.push({ status: r.status, body: await r.text() });
    }
    const allOk = results.every((r) => r.status === 200);
    return new Response(
      JSON.stringify({ ok: allOk, chunks: results.length, results }, null, 2),
      {
        status: allOk ? 200 : 502,
        headers: { "Content-Type": "application/json" },
      }
    );
  },
};
```

---

## 로컬 테스트 (동작 확인용)

```bash
python -c "
import json, urllib.request
with open('shared/cloudflare/config.local.json', encoding='utf-8') as f:
    cfg = json.load(f)
payload = json.dumps({'message': '테스트 메시지'}, ensure_ascii=False).encode('utf-8')
req = urllib.request.Request(
    cfg['worker_url'],
    data=payload,
    headers={
        'Content-Type': 'application/json; charset=utf-8',
        'X-Shared-Secret': cfg['shared_secret'],
    },
    method='POST',
)
with urllib.request.urlopen(req, timeout=30) as resp:
    print(resp.status, resp.read().decode('utf-8'))
"
```

정상 시 텔레그램 봇 채팅방에 메시지 도착 + `HTTP 200 {"ok": true, ...}` 응답.

---

## 향후 활용 시나리오

1. **Anthropic가 workers.dev를 허용 목록에 추가** — 이 Worker 그대로 재사용
2. **다른 서비스가 로컬에서 텔레그램 알림 필요할 때** — 이 Worker에 POST하면 됨 (봇 토큰 재사용)
3. **Worker 삭제하고 다른 채널로 전환** — Cloudflare 대시보드에서 Delete 후 이 폴더도 삭제

---

## 주의사항

| 항목 | 내용 |
|------|------|
| Shared Secret 유출 | 유출 시 Cloudflare 대시보드에서 즉시 재설정 + `config.local.json` 갱신 |
| Cloudflare 무료 한도 | 하루 100,000 요청 (개인 알림 용도로는 충분) |
| Worker 로그 | Cloudflare 대시보드 → `tg-relay` → Logs 실시간 확인 가능 |
