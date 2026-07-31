# 공용 Claude Code CLI 자산

로컬 Python 실행(예: [`services/idea_search/run_local.py`](../../services/idea_search/run_local.py))이 `claude -p` 헤드리스 모드로 Claude를 호출하기 위한 인증 세팅.

Anthropic API 키가 아니라 **Claude Code subscription**(Pro/Max)의 장기 토큰을 사용한다. 별도 API 과금 없이 subscription 안에서 실행된다.

---

## 왜 API 키가 아니라 CLI 인가

| 항목 | Anthropic API 키 | Claude Code subscription 토큰 |
|------|------------------|-----------------------------|
| 별도 결제 | 필요 (토큰 사용량 기반) | 불필요 (subscription 요금에 포함) |
| 인증 방식 | `sk-ant-api03-...` 헤더 | OAuth 장기 토큰 (`claude setup-token`) |
| 호출 방식 | Python SDK `anthropic.Anthropic()` | `subprocess.run(["claude", "-p", ...])` |
| 웹 검색 | `web_search_20260209` 서버 툴 | Claude Code 내장 WebSearch 도구 |
| 이 저장소의 선택 | ✗ | ✅ |

---

## 세팅 (1회성)

### 1. Claude Code 설치 확인

이 저장소에서 이 문서를 읽고 있다면 이미 Claude Code가 설치돼 있다. 확인:

```powershell
claude --version
```

버전 문자열이 나오면 OK.

### 2. Subscription 로그인

Claude Code를 처음 켠 뒤 `/login` 으로 이미 Claude Pro/Max 계정에 로그인해뒀다면 이 단계는 생략 가능. 확인:

```powershell
claude auth status
```

### 3. 장기 토큰 발급 (스크립트 자동 실행용)

Windows 작업 스케줄러가 사용자 로그인 없이도 스크립트를 돌리려면 장기 인증 토큰이 필요하다:

```powershell
claude setup-token
```

브라우저가 열려 subscription 계정 승인 → CLI에 토큰이 저장된다 (Windows의 경우 `%USERPROFILE%\.claude\` 아래 credential store).

이 토큰은 **subscription을 유지하는 한 유효**하며, 계정 로그아웃하지 않는 이상 재발급 불필요.

### 4. 헤드리스 실행 테스트

```powershell
echo "1 더하기 1은?" | claude -p --output-format text
```

`2` 또는 "1 더하기 1은 2입니다" 같은 응답이 stdout으로 나오면 성공. 이 시점부터 `services/*/run_local.py` 가 정상 동작한다.

---

## 주의사항

| 항목 | 내용 |
|------|------|
| Subscription 만료/취소 | `claude -p` 가 인증 오류로 실패. `claude setup-token` 재실행 |
| 여러 계정 스위치 | `claude auth logout` → `claude auth login` (또는 `setup-token` 다시) |
| 사용량 한도 | Subscription의 usage limit 도달 시 응답 실패. Claude Code UI에서 확인 |
| 저장소 공유 시 | 토큰은 각 PC의 `~/.claude/` 에만 존재 (커밋되지 않음). 다른 PC는 각자 `setup-token` |
| 스크립트 인자 | `--model` 로 모델 지정 가능 (`sonnet`, `opus`, `claude-opus-4-7` 등). 미지정 시 subscription의 default 모델 사용 |
