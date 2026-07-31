# 아이템분석가

사용자가 선택한 창업 아이템 후보 하나에 대해 **"지금 이 사람이 실행해도 될까"** 를 판단하는 서비스.
[아이디어검색가](../idea_search/README.md)가 매일 후보 리스트를 던져주면, 그중 하나를 골라 이 서비스로 심층 분석한다.

| 항목 | 값 |
|------|-----|
| **실행 방식** | 로컬 Python + Claude Code CLI — on-demand (스케줄 아님) |
| 트리거 | 사용자가 아이템 후보를 정한 시점 |
| 인증 | Claude Code subscription (Pro/Max) — 아이디어검색가와 동일 |
| 전달 채널 | Telegram Bot API (`@JamesMyHomeBot`) |
| 프롬프트 | [`prompt.md`](prompt.md) |
| 로그 | `logs/YYYY-MM-DD_HHMMSS_<slug>.md` (아이템별로 별도 파일) |

---

## 판단 기준 (사용자 프로필 고정값)

- **개발 인력**: 1인
- **기술 수준**: 비전문가 (풀스택 웹/앱 기본기 + LLM API 호출 정도)
- **시간 투입**: 부업 / 야간·주말 / 주 10~15시간
- **자금**: 초기 자본 최소화

프로필 값이 바뀌면 [`prompt.md`](prompt.md) 상단의 "판단 기준" 섹션을 편집한다.

---

## 산출물 (리포트 구조)

1. **STEP 1 — 실행 가능성 평가**: 1인·비전문가·시간·자금·진입장벽 5축, 각 상/중/하 + 근거
2. **STEP 2 — 국내 사례**: 유사·경쟁 서비스 3~5개 (BM, 규모, 차별점)
3. **STEP 3 — 해외 사례**: 유사·경쟁 서비스 3~5개 (BM, 성장 지표, 벤치마킹 포인트)
4. **STEP 4 — 종합 판단**: 🟢/🟡/🔴 등급 + 첫 2주 태스크 + 실패 리스크 Top 3

---

## 사용법

### PowerShell에서 직접

```powershell
# 인자로 아이템 넘기기 (가장 흔한 사용)
python services/item_analyzer/run_local.py "AI 튜터 챗봇 — 초등 저학년 국어·수학 개별 지도"

# 텔레그램 발송 없이 로그만
python services/item_analyzer/run_local.py "노코드 챗봇 셋업 대행" --dry-run

# 긴 설명을 stdin으로
type item_desc.txt | python services/item_analyzer/run_local.py --stdin
```

### Claude Code(갑돌이)에게 자연어로

```
갑돌아 이 아이템 분석해줘: AI 튜터 챗봇
갑돌아 어제 리포트 ① 노코드 챗봇 셋업 대행 심층 분석해줘
갑돌아 방금 분석 리포트 다시 보여줘
```

내가 파싱해서 인자 넘겨 실행합니다.

---

## 연계 워크플로우 (아이디어검색가 → 아이템분석가)

```
매일 18:00  ──▶ 아이디어검색가 (스케줄)
                    │
                    ▼
              10개 후보 리포트 (텔레그램 수신)
                    │
                    ▼ 사용자가 관심 있는 항목 골라
              "갑돌아 ⑧번 아이템 분석해줘"
                    │
                    ▼
              아이템분석가 (on-demand)
                    │
                    ▼
              🟢/🟡/🔴 종합 판단 + 첫 2주 태스크 (텔레그램 수신)
```

---

## 운영

| 상황 | 조치 |
|------|------|
| 리포트 재실행 | `python run_local.py "..."` 재호출 (로그 파일은 새 타임스탬프로 별도 저장) |
| 발송 없이 리허설 | `python run_local.py "..." --dry-run` |
| 명령 확인 | `python run_local.py --show-cmd` |
| 모델 교체 | 환경변수 `ITEM_ANALYZER_MODEL=sonnet` 등 |
| 타임아웃 조정 | 환경변수 `ITEM_ANALYZER_TIMEOUT=1200` (기본 900초) |
| 판단 기준 변경 | `prompt.md` 상단 "판단 기준" 섹션 편집 |

---

## 참고

- 원본 요청서: [`../../docs/초기요청사항.txt`](../../docs/초기요청사항.txt)
- 아이디어검색가(연계 서비스): [`../idea_search/README.md`](../idea_search/README.md)
- 공용 인증 세팅: [`../../shared/claude_code/README.md`](../../shared/claude_code/README.md)
- 텔레그램 봇 세팅: [`../../shared/telegram/README.md`](../../shared/telegram/README.md)
