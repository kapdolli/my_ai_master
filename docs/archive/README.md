# docs/archive — 진행 기록 아카이브

갑돌이마스터 저장소에서 진행된 **서비스 구축·전략 리서치·의사결정**의 기록. 미래에 같은 주제를 다시 열 때 처음부터 다시 파지 않기 위한 자료.

각 문서는 자기 완결적으로 읽을 수 있게 작성되어 있고, 관련 문서가 있으면 상단·하단에서 상호 링크한다.

---

## 📚 인덱스 (최근 순)

### 🧵 스레드 A. 광고 기반 유틸리티 앱 아이디어 리서치 (2026-08-03, 하루짜리)

같은 날 진행된 두 문서. **아래부터 순서대로 읽으면 된다.**

| # | 문서 | 내용 |
|---|-----|-----|
| 1 | [`2026-08-03-utility-app-research.md`](2026-08-03-utility-app-research.md) | **여정 decision log.** 후보 10개 리스트 → 3개(급식+학원, 다문화, 시험 D-Day) 심층 검증(전부 이미 잡힘) → 사주·로또·지하철 블라인드 스팟 자백 → A/B/C 갈래에서 **A(다작 스팸형)** 선택 |
| 2 | [`2026-08-03-portfolio-model-strategy.md`](2026-08-03-portfolio-model-strategy.md) | **A 갈래 세부 실행 리포트.** 소재 카탈로그 100개 · Flutter+Firebase+RevenueCat 스택 · 템플릿·Fastlane·Claude Code 활용 · ASO 롱테일 · 워크플로우·리스크·매출밴드 · 12주 액션플랜 · 즉시 착수 Top 5 소재 |

**미결정 (2026-08-03 종료 시점)**:
- 12주 액션플랜 W1(Flutter 스택 셋업 + 사업자 등록) 착수 여부
- 첫 앱 소재 확정 (정보처리기사 D-Day / 양도세 계산기 / 군인 전역 / 청년 정책 / 야간병원 중)

---

### 🧵 스레드 B. 아이디어검색가 서비스 구축·전환

시간순으로 아래에서 위로 진행됨.

| 날짜 | 문서 | 내용 |
|------|-----|-----|
| 2026-07-31 | [`2026-07-31-egress-blocked.md`](2026-07-31-egress-blocked.md) | **Cloud Sandbox Egress 벽 대응 여정.** Anthropic Cloud Routine sandbox의 좁은 egress 화이트리스트로 텔레그램 발송 불가 판정 → 5개 배달 경로 실패 → **로컬 Python 실행 + Windows 작업 스케줄러**로 전환 결정. 다음 세션 재개 시 시행착오 반복 방지가 목적. |
| 2026-07-30 | [`twinkling-finding-blossom.md`](twinkling-finding-blossom.md) | **초기 설계·구축 문서.** 서비스 개요·아키텍처·프롬프트·Chat ID 확보까지의 진행 기록. Cloud Routine 등록이 남았던 시점의 상태 스냅샷. |

---

## 📎 관련 자산

### 원본 요청서
- [`../초기요청사항.txt`](../초기요청사항.txt) — 사용자 최초 요청 (갑돌이마스터 개념, 서비스 리스트 요구사항)

### 저장소 상위 README
- [`../../README.md`](../../README.md) — 등록된 서비스 표, 폴더 규약, 실행 모델

### 관련 서비스 (실행 코드·로그 위치)
- [`../../services/idea_search/`](../../services/idea_search/README.md) — 매일 18:00 KST 자동 실행 IT/AI 아이디어 리포트 (스레드 B에서 구축)
- [`../../services/item_analyzer/`](../../services/item_analyzer/README.md) — 아이템 심층 분석 on-demand
- [`../../services/korean_teacher_items/`](../../services/korean_teacher_items/README.md) — 국어강사 페르소나 아이템 on-demand

---

## 🧭 활용 요령

1. **새 세션에서 특정 주제를 다시 열 때**: 이 인덱스에서 해당 스레드 확인 → 문서 상단 요약 읽기 → "미결정" 또는 "다음 액션" 섹션에서 재개 지점 파악
2. **문서 갱신 규칙**: 새 결정·리서치가 나오면 원 문서의 "다음 액션" 섹션 갱신 + 필요 시 후속 문서를 별도 파일로 추가하고 원 문서 하단에서 링크
3. **실행 결과 로그는 여기 아님**: `services/<name>/logs/` 참조 (일자별 산출물). 이 아카이브는 **의사결정과 리서치 여정**만 담는다
4. **새 문서 파일명**: `YYYY-MM-DD-{topic}.md` 형식 권장 (기존 규칙과 일치)
