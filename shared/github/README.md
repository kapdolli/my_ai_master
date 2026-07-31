# 공용 GitHub 자산

여러 서비스가 공통으로 사용하는 GitHub 자격 증명 및 push/API 사용 규약.

이 저장소 자체의 원격은 `github.com/kapdolli/my_ai_master`이며, PAT는 push·리포 관리·향후 서비스가 GitHub API 호출할 때 재사용된다.

---

## 파일

- `config.local.json` (gitignore) — `account`, `token` 값. 형식:
  ```json
  {
    "account": "kapdolli",
    "token": "github_pat_..."
  }
  ```

---

## PAT 발급 (fine-grained 권장)

1. `github.com` → 대상 계정(예: `kapdolli`)으로 로그인
2. 프로필 → **Settings** → **Developer settings** → **Personal access tokens** → **Fine-grained tokens** → **Generate new token**
3. 입력 값:
   - **Token name**: 예 `my_ai_master-push`
   - **Expiration**: 90일 권장 (짧을수록 안전, 만료 시 재발급)
   - **Repository access**: **Only select repositories** → `kapdolli/my_ai_master`
   - **Repository permissions** → **Contents**: **Read and write** ← push 필수
   - (선택) **Metadata**: Read-only (자동 부여됨)
4. **Generate token** → **한 번만 표시되는 토큰(`github_pat_...`)을 즉시 `config.local.json`에 저장**

> Classic PAT도 동작하지만 fine-grained가 권한 범위가 좁아 더 안전.

---

## Windows 자격 증명 관리자 (GCM) 사용

첫 push 시 GCM이 프롬프트를 띄우고, 여기 PAT를 붙여넣으면 자동으로 암호화 저장된다. 이후 push는 자동 인증.

### 최초 등록 (또는 계정 교체)

기존에 다른 계정 자격이 저장돼 있다면 먼저 제거:

- **UI 방식**: 시작 → "자격 증명 관리자" → **Windows 자격 증명** 탭 → `git:https://github.com` 항목 → **제거**
- **명령 방식** (Git Bash):
  ```bash
  printf 'protocol=https\nhost=github.com\n\n' | git credential reject
  ```

그 후 push 실행:
```bash
git push origin main
```
- **Username**: `config.local.json`의 `account` 값 (예: `kapdolli`)
- **Password**: `config.local.json`의 `token` 값 (PAT 붙여넣기, GitHub 로그인 비밀번호 아님)

성공하면 GCM에 자동 저장.

### 저장된 자격 확인

```bash
printf 'protocol=https\nhost=github.com\n\n' | git credential fill
```

---

## 계정 여러 개를 한 PC에서 쓰는 경우

여러 GitHub 계정을 병행해야 하면 SSH 별칭 방식이 정공법:

1. 계정별 SSH 키 생성:
   ```bash
   ssh-keygen -t ed25519 -C "kapdolli" -f ~/.ssh/id_ed25519_kapdolli
   ```
2. 공개키(`.pub`)를 대상 계정의 GitHub → Settings → SSH keys에 등록
3. `~/.ssh/config`에 별칭 추가:
   ```
   Host github.com-kapdolli
     HostName github.com
     User git
     IdentityFile ~/.ssh/id_ed25519_kapdolli
   ```
4. 저장소 원격을 별칭으로 변경:
   ```bash
   git remote set-url origin git@github.com-kapdolli:kapdolli/my_ai_master.git
   ```

이 방식은 PAT 관리와 무관하게 SSH 키 기반으로 동작 → GCM 계정 충돌 걱정 없음.

---

## 향후 서비스에서 GitHub API 호출할 때

Python 서비스나 스케줄 프롬프트에서 `token`을 참조할 수 있도록 환경변수로 주입:

- **로컬 스크립트**: `python -c "import json; print(json.load(open('shared/github/config.local.json'))['token'])"` 로 값 읽어 `GITHUB_TOKEN` 환경변수에 세팅
- **Claude Cloud Schedule**: `/schedule` 등록 시 환경변수 `GITHUB_TOKEN`에 값을 직접 넣기 (텔레그램과 동일 패턴)

프롬프트 안에서는 `Authorization: Bearer $GITHUB_TOKEN` 헤더로 API 호출.

---

## 제약 및 주의사항

| 항목 | 내용 |
|------|------|
| 토큰 저장 위치 | `config.local.json`에만. `.gitignore`의 `*.local.*`로 커밋 제외 중 |
| 유출 대응 | 유출 즉시 GitHub → Settings → Developer settings에서 해당 토큰 **Revoke** 후 재발급 |
| 만료 관리 | 90일 만료 설정 시 만료 임박 알림을 GitHub이 이메일로 발송 — 도착 시 즉시 재발급하고 `config.local.json` + GCM 갱신 |
| 권한 최소화 | 필요 이상의 권한(예: `admin:org`, `delete_repo`)은 부여하지 말 것 — fine-grained로 저장소·권한 좁게 |
| 백업 | `config.local.json` 자체를 별도 안전한 곳(패스워드 매니저 등)에 백업해두면 PC 이전·포맷 시 편리 |
