# 다작 스팸형 앱 포트폴리오 실행 리포트 (2026-08-03)

> 이 문서는 [`2026-08-03-utility-app-research.md`](2026-08-03-utility-app-research.md)의 미결정 갈래 **A (다작 스팸형 모델)** 선택 이후 후속 리서치 결과다.
> 사용자가 다음 3~12개월 실행 계획으로 쓸 목적. general-purpose 에이전트가 국내(케빈·김윤후·프로그래밍좀비)와 해외(Max Artemov·Pieter Levels) 실사례 30+건을 근거로 통합.

---

## 사전 냉정한 판단 (본론 전에 반드시 읽을 것)

리서치 초반에 나온 두 가지 반증부터 정리하고 갑니다.

1. **"350개 앱 = 파이어"는 신화가 아니라 편향입니다.** 김윤후 님의 실제 인터뷰를 파고들면, 350개는 누적 생성 수이고 **수익의 80%는 "간단"(간헐적 단식) 앱 1개에서 나옵니다.** 나머지 15개 앱은 유지보수만 하고, 대부분은 휴면 상태입니다. 즉, "다작으로 리스크 분산"이 아니라 **"다작으로 히트를 확률적으로 뽑고, 히트에 몰빵"** 구조입니다. ([패스트캠퍼스 인터뷰](https://fastcampus.co.kr/story_article_indiehacker), [메일리 인터뷰](https://maily.so/josh/posts/1gz2v974r3q))

2. **인디해커 커뮤니티 대표 사례도 동일한 편향입니다.** $602K 매출을 낸 솔로 개발자 사례를 뜯어보면 HabitKit 1개가 전체 수익의 99% 이상을 차지합니다. ([Indie Hackers](https://www.indiehackers.com/post/tech/from-failed-app-to-30-app-portfolio-making-22k-mo-in-less-than-a-year-myy3U7K9evxGOVOHti8s))

따라서 이 리포트는 **"다작을 통해 히트 1개를 찾아내는 게임"** 으로 다작 모델을 재정의하고 작성합니다. 100개를 던지면 그 중 5개가 하루 $1~5, 1~2개가 월 100~500만원, 운 좋게 1개가 월 1천만원 이상으로 진화하는 통계 게임입니다.

---

## 섹션 1. 다작용 앱 소재 카탈로그 (100개)

각 소재는 **한국 스토어에서 실제 확인된 카테고리**만 넣었습니다. "이미 상위 앱이 확고한 소재"는 표시했고, "여전히 틈새가 있는 소재"는 우선순위로 배치했습니다.

기술 난이도 표기: 하 = 3일 이내 / 중 = 1~2주 / 상 = 배제.
광고 궁합 ★1~5: 사용 세션 길이·주기·재방문 빈도 기준.

### 카테고리 A. 계산기·환산 (총 12개, 대부분 강자 있음이나 롱테일 여지)

| 이름 | 설명 | 난이도 | 광고 | 시장 | 참고 앱 | AI 코딩 |
|---|---|---|---|---|---|---|
| BMI 계산기 | 체중·키 입력 → 체질량지수 | 하 | ★★ | 강자 있음(BMI Calculator 등) | [BMI 계산기](https://play.google.com/store/apps/details?id=bmicalculator.bmi.calculator.weightlosstracker) | Yes(2시간) |
| 복리 계산기 | 원금·이율·기간 → 만기금액 | 하 | ★★★ | 파편적 | [복리 계산기](https://play.google.com/store/apps/details?id=calculator.compound.interest) | Yes |
| 대출이자 계산기 | 원리금균등·원금균등 | 하 | ★★★ | 강자 있음 | 대출계산기(eonsoft) | Yes |
| 자동차세 계산기 | 배기량·연식별 세금 | 하 | ★★★ | 파편적 | [자동차세 계산기](https://play.google.com/store/apps/details?id=kr.co.deegle.cartax) | Yes |
| 양도소득세 계산기 | 부동산 양도세 | 중 | ★★★ | 틈새 있음 | [양도세 앱](https://apps.apple.com/kr/app/양도세/id6450972804) | Yes |
| 취등록세 계산기 | 자동차·부동산 | 하 | ★★★ | 파편적 | car.calculate.kr(웹) | Yes |
| 연차 계산기 | 근속연수 → 연차일수 | 하 | ★★ | 파편적 | - | Yes |
| 퇴직금 계산기 | 근속·평균임금 | 하 | ★★★ | 파편적 | - | Yes |
| 환율 계산기 | 통화 실시간 환산 | 하 | ★★ | 강자 있음 | - | Yes |
| 요리 단위 환산 | 컵/스푼/그램 | 하 | ★ | 파편적 | - | Yes |
| 나이 계산기 | 만나이/서양나이/띠 | 하 | ★★ | 강자 있음 | - | Yes |
| 임신주수 계산기 | 배란일·출산예정일 | 하 | ★★★★ | 강자 있음 | - | Yes |

### 카테고리 B. 위젯·홈스크린 (총 12개, 커플·D-Day 시장 확고)

| 이름 | 설명 | 난이도 | 광고 | 시장 | 참고 앱 | AI 코딩 |
|---|---|---|---|---|---|---|
| 시험 D-Day | 수능·공무원·자격증 | 중 | ★★★ | 강자 있음 | [더데이](https://play.google.com/store/apps/details?id=com.firstscreen.testdday) | Yes |
| 커플 D-Day 위젯 | 사귄 날짜 카운트 | 중 | ★★★ | 강자 있음 | [The Couple](https://apps.apple.com/kr/app/id1116889464), [커플로그](https://play.google.com/store/apps/details?id=com.gonigon.couplelog) | Yes |
| 기념일 D-Day | 생일·기념일 알림 | 하 | ★★★ | 강자 있음([TheDayBefore](https://play.google.com/store/apps/details?id=com.aboutjsp.thedaybefore)) | Yes |
| 아기 D-Day | 100일·200일 위젯 | 하 | ★★★ | 틈새 있음 | - | Yes |
| 군인 D-Day | 입대·전역 카운트 | 하 | ★★★★ | 파편적 | - | Yes |
| 디지털 시계 위젯 | 홈스크린 커스텀 시계 | 중 | ★★ | 강자 있음 | [DIGI Clock](https://play.google.com/store/apps/details?id=sk.michalec.SimpleDigiClockWidget) | Yes |
| 명언 위젯 | 매일 명언 새로고침 | 하 | ★★★ | 강자 있음([모두의 명언](https://play.google.com/store/apps/details?id=com.konStudio.quote_diary_android)) | Yes |
| 일정/할일 위젯 | 오늘 할일 위젯 | 중 | ★★ | 강자 있음 | - | Yes |
| 지출 기록 위젯 | 원터치 지출 입력 | 중 | ★★★ | 틈새 있음 | - | Yes |
| 날씨 위젯 | 지역별 날씨 | 중 | ★★★ | 강자 있음 | - | Yes |
| 미세먼지 위젯 | 지역별 대기질 | 중 | ★★★★ | 강자 있음([미세미세](https://apps.apple.com/kr/app/id1091911730)) | Yes |
| 주식 종목 위젯 | 관심주식 실시간 | 중 | ★★★★ | 파편적 | - | Yes |

### 카테고리 C. 알림·타이머 (총 10개, 헬스/생활)

| 이름 | 설명 | 난이도 | 광고 | 시장 | 참고 앱 | AI 코딩 |
|---|---|---|---|---|---|---|
| 물마시기 알림 | 시간별 알람 | 하 | ★★★ | 강자 있음([Drink Water](https://play.google.com/store/apps/details?id=com.northpark.drinkwater)) | Yes |
| 약 복용 알림 | 약별 알람 | 중 | ★★★★ | 강자 있음(김윤후 Take, [약 알림 태양이](https://play.google.com/store/apps/details?id=com.artifyapp.mcare)) | Yes |
| 스트레칭 알림 | 앉은지 X분 알람 | 하 | ★★★ | 파편적 | - | Yes |
| 눈 깜빡임 알림 | 화면 응시 알림 | 하 | ★★ | 파편적 | - | Yes |
| 인터벌 타이머 | 운동/명상 인터벌 | 하 | ★★★ | 파편적 | - | Yes |
| 라면 타이머 | 3분·조리 프리셋 | 하 | ★★ | 파편적 | - | Yes |
| 계란 타이머 | 반숙·완숙별 | 하 | ★ | 파편적 | - | Yes |
| 포모도로 타이머 | 25/5분 반복 | 하 | ★★ | 강자 있음 | - | Yes |
| 아기 수유 알림 | 3시간마다 | 중 | ★★★★ | 파편적 | - | Yes |
| 걷기 알림 | 시간·거리 목표 | 중 | ★★★ | 강자 있음 | - | Yes |

### 카테고리 D. 조회·정보 (총 12개, API 기반)

| 이름 | 설명 | 난이도 | 광고 | 시장 | 참고 앱 | AI 코딩 |
|---|---|---|---|---|---|---|
| 로또번호 생성기 | 랜덤·통계 기반 | 하 | ★★★★ | 강자 있음([모두의 로또](https://play.google.com/store/apps/details?id=com.my.Lotto645), [로또사주](https://apps.apple.com/kr/app/id1468078492)) | Yes |
| 로또당첨확인 QR | QR 스캔 당첨 | 중 | ★★★★ | 강자 있음([로또복권 당첨확인](https://play.google.com/store/apps/details?id=com.posko777.tools.lotto)) | Yes |
| 지하철 도착정보 | 서울/부산 실시간 | 중 | ★★★ | 강자 있음(공식 앱, [공공데이터 API](https://www.data.go.kr/data/15058052/openapi.do)) | Yes |
| 버스 도착정보 | 지역별 실시간 | 중 | ★★★ | 지역별 파편적([대전 버스](https://apps.apple.com/kr/app/id1494747066)) | Yes |
| 오늘의 운세 | 띠·별자리 | 하 | ★★★★ | 강자 있음([헬로우봇](https://apps.apple.com/kr/app/id1294957719), [포스텔러](https://apps.apple.com/kr/app/id1262949138)) | Yes |
| 사주 만세력 | 생년월일 사주 | 중 | ★★★ | 강자 있음(포스텔러) | Yes |
| 별자리 운세 | 12별자리 데일리 | 하 | ★★★ | 강자 있음 | Yes |
| 미세먼지 조회 | 지역별 실시간 | 중 | ★★★★ | 강자 있음 | Yes |
| 물때 조석 | 낚시·해뜨는시간 | 중 | ★★★★ | 강자 있음([물때 타이드](https://apps.apple.com/kr/app/id585223877)) | Yes |
| 공휴일·24절기 | 절기·기념일 달력 | 하 | ★★ | 강자 있음([절기달력](https://play.google.com/store/apps/details?id=com.hydroponicglass.anniversary)) | Yes |
| 급식표 조회 | 초·중·고 급식 | 중 | ★★★ | 강자 있음([김급식](https://play.google.com/store/apps/details?id=start.FoodTime)) | Yes |
| 학교 시간표 | 학교별 시간표 | 중 | ★★★ | 강자 있음(김급식 통합) | Yes |

### 카테고리 E. 랜덤·엔터테인먼트 (총 10개)

| 이름 | 설명 | 난이도 | 광고 | 시장 | 참고 앱 | AI 코딩 |
|---|---|---|---|---|---|---|
| 랜덤 뽑기 | 이름·번호 추첨 | 하 | ★★ | 강자 있음([손가락 뽑기](https://play.google.com/store/apps/details?id=com.happyverse.fingerchooser)) | Yes |
| 사다리타기 | 온라인 사다리 | 하 | ★★ | 강자 있음 | Yes |
| 룰렛 | 선택 룰렛 | 하 | ★★ | 강자 있음([룰렛+](https://play.google.com/store/apps/details?id=com.komorebi.roulette)) | Yes |
| 심리테스트 | MBTI·자아유형 | 하 | ★★★★ | 강자 있음([MBTI Test](https://play.google.com/store/apps/details?id=com.mbtiapplication)) | Yes |
| 궁합 테스트 | 이름·생일 궁합 | 하 | ★★★★ | 강자 있음 | Yes |
| 밸런스 게임 | 이거 vs 저거 | 하 | ★★★★ | 강자 있음(픽폼) | Yes |
| 이상형 월드컵 | 32강 토너먼트 | 중 | ★★★★ | 파편적 | Yes |
| 타로 카드 뽑기 | 데일리 타로 | 하 | ★★★★ | 강자 있음 | Yes |
| 진실게임 | 커플·친구용 질문 | 하 | ★★★ | 파편적 | Yes |
| 코인 던지기 | 앞뒤 판정 | 하 | ★ | 강자 있음 | Yes |

### 카테고리 F. 카메라·이미지 (총 8개)

| 이름 | 설명 | 난이도 | 광고 | 시장 | 참고 앱 | AI 코딩 |
|---|---|---|---|---|---|---|
| QR 스캐너 | QR·바코드 | 하 | ★★★ | 강자 있음([QR 코드 리더](https://play.google.com/store/apps/details?id=tw.mobileapp.qrcode.banner)) | Yes |
| 거울 앱 | 전면 카메라 활용 | 하 | ★★ | 파편적 | Yes |
| 손전등 앱 | 후면 플래시 | 하 | ★ | 강자 있음 | Yes |
| 이미지 리사이즈 | 크기·용량 조절 | 중 | ★★ | 파편적 | Yes |
| PDF 변환 | 이미지→PDF | 중 | ★★★ | 강자 있음 | Yes |
| 색상 추출 | 사진에서 컬러 | 하 | ★★ | 파편적 | Yes |
| 스캔 문서 | 종이→PDF | 중 | ★★★★ | 강자 있음 | Yes |
| 얼굴 나이 측정 | 재미 필터 | 중 | ★★★★ | 파편적 | Yes(AI API 사용) |

### 카테고리 G. 유틸리티 소음·미디어 (총 6개)

| 이름 | 설명 | 난이도 | 광고 | 시장 | 참고 앱 | AI 코딩 |
|---|---|---|---|---|---|---|
| 백색소음 | 15+ 사운드 믹스 | 중 | ★★★ | 강자 있음([백색소음-수면](https://apps.apple.com/kr/app/id1671685536)) | Yes |
| 아기 재우기 소리 | 자궁·심장 소리 | 하 | ★★★★ | 파편적 | Yes |
| 명상 음악 | 5분·10분 트랙 | 중 | ★★★ | 강자 있음 | Yes |
| 자연 소리 | 비·파도·숲 | 하 | ★★ | 강자 있음 | Yes |
| 이명 마스킹 | 이명 완화 톤 | 중 | ★★★ | 틈새 있음 | Yes |
| 알람 벨소리 | 클래식·자연 | 하 | ★★ | 파편적 | Yes |

### 카테고리 H. 게임 유사 극단순 (총 8개, 리텐션 높아 광고 궁합 좋음)

| 이름 | 설명 | 난이도 | 광고 | 시장 | AI 코딩 |
|---|---|---|---|---|---|
| 색맞추기 | 색 비교 반응 게임 | 중 | ★★★★ | 파편적 | Yes |
| 2048 클론 | 숫자 병합 | 중 | ★★★★ | 강자 있음 | Yes |
| 숫자 퍼즐 | 스도쿠 유사 | 중 | ★★★★ | 강자 있음 | Yes |
| 반응속도 테스트 | 클릭 지연 측정 | 하 | ★★★ | 파편적 | Yes |
| 타자 연습 | 한글 타자 | 중 | ★★ | 강자 있음 | Yes |
| 기억력 게임 | 카드 짝맞추기 | 하 | ★★★★ | 파편적 | Yes |
| 파이프 잇기 | 물길 퍼즐 | 중 | ★★★★ | 강자 있음 | Yes |
| IQ 테스트 | 간이 지능 | 하 | ★★★★ | 파편적 | Yes |

### 카테고리 I. 학습·암기 (총 6개)

| 이름 | 설명 | 난이도 | 광고 | 시장 | 참고 앱 | AI 코딩 |
|---|---|---|---|---|---|---|
| 플래시카드 | 자체 단어장 | 중 | ★★★ | 강자 있음([Quizlet](https://apps.apple.com/kr/app/quizlet/id546473125), [원보카](https://apps.apple.com/kr/app/id1242173441)) | Yes |
| 영단어 데일리 | 하루 10단어 | 하 | ★★★ | 강자 있음 | Yes |
| 자격증 CBT 회독 | 기출문제 회독 | 중 | ★★★★ | 강자 있음([오늘학습](https://apps.apple.com/kr/app/id1589469032), [오르조](https://apps.apple.com/kr/app/id1529046013)) | Yes |
| 구구단 게임 | 아이용 곱셈 | 하 | ★★★ | 파편적 | Yes |
| 한자 암기 | 8급~1급 | 하 | ★★★ | 파편적 | Yes |
| 명언 필사 | 하루 한 문장 | 하 | ★★ | 강자 있음([박한평 문장집](https://apps.apple.com/kr/app/id6748083993)) | Yes |

### 카테고리 J. 국내 특화 니치 (총 8개, AI 코딩 궁합 최상, 시장 아직 파편적)

| 이름 | 설명 | 난이도 | 광고 | 시장 | AI 코딩 |
|---|---|---|---|---|---|
| 부동산 계산기 | 취득세·중개수수료·양도세 통합 | 중 | ★★★★ | 강자 있음([부동산 계산기](https://apps.apple.com/us/app/id1234534354)) | Yes |
| 자동차 번호판 조회 | 차량 정보 | 중 | ★★★★ | 파편적 | Yes |
| 병원·약국 위치 | 지역별 야간·주말 | 중 | ★★★★ | 파편적 | Yes |
| 주민등록번호 검증 | 형식 유효성 | 하 | ★ | 파편적 | Yes |
| 청년 정책 지원금 | 지자체별 정리 | 중 | ★★★★ | 틈새 있음 | Yes |
| 재난문자 필터 | 지역별 알림 | 중 | ★★★ | 파편적 | Yes |
| 국가장학금 신청일 | 학기별 D-Day | 하 | ★★★★ | 파편적 | Yes |
| 국민연금 예상액 | 나이·소득 입력 | 중 | ★★★★ | 파편적 | Yes |

### 카테고리 K. 부가 8개 (기타)

| 이름 | 설명 | 난이도 | 광고 | 시장 | AI 코딩 |
|---|---|---|---|---|---|
| 하루 지출 기록 | 미니 가계부 | 중 | ★★★ | 강자 있음 | Yes |
| 습관 트래커 | 체크리스트 | 중 | ★★★ | 강자 있음 | Yes |
| 필기 노트 위젯 | 잠금화면 메모 | 중 | ★★ | 파편적 | Yes |
| 감정 기록 | 이모지 데일리 무드 | 하 | ★★ | 파편적 | Yes |
| 뽀모도로 통계 | 집중시간 리포트 | 중 | ★★ | 파편적 | Yes |
| 걷기 만보기 | 걸음수·칼로리 | 중 | ★★★★ | 강자 있음(삼성헬스) | Yes |
| 여행 체크리스트 | 짐 싸기 리스트 | 하 | ★★ | 파편적 | Yes |
| 나이대별 신체지수 | 성인병 리스크 | 중 | ★★★ | 파편적 | Yes |

**총 100개 소재 완료.** 시장 감으로 볼 때 완전 포화 카테고리(로또·D-Day·사주·급식·QR)에서는 **"특정 니치를 좁힌 변주"** 로 진입해야 하고, 파편적 카테고리(자동차세·양도세·부동산 계산기·병원위치·청년정책)는 **롱테일 키워드로 상위 진입 가능성**이 있습니다.

---

## 섹션 2. 템플릿화된 개발 파이프라인

### 2-1. 기술 스택 선택 — **결론: Flutter + Firebase + RevenueCat**

다작 모델에서 스택 선택의 유일한 기준은 **"코드 재사용성과 스토어 커버리지"** 입니다.

- **Kotlin 네이티브**: 케빈·프로그래밍좀비 선택. Android 단독이면 최고 속도. 하지만 iOS 미커버. 프로그래밍좀비 스택은 Kotlin + Spring Boot + JPA + MySQL로 서버까지 소유하는 무거운 구조 ([메일리](https://maily.so/indiehackerlab/posts/g1o45916rve))
- **React Native / Expo**: 웹 배경이면 학습 곡선 낮음. Bolt·Lovable AI 코딩 도구가 Expo 템플릿 지원 ([Bubble 비교](https://bubble.io/blog/v0-vs-bolt-vs-bubble-comparison/))
- **Flutter**: Max Artemov의 30앱 포트폴리오 스택 ([Indie Hackers](https://www.indiehackers.com/post/tech/from-failed-app-to-30-app-portfolio-making-22k-mo-in-less-than-a-year-myy3U7K9evxGOVOHti8s)). iOS/Android 동시, 위젯 지원(3.13+), gen_l10n 다국어 자동화 ([공식 문서](https://docs.flutter.dev/ui/internationalization))

**추천: Flutter.** 이유:
- Max Artemov 실측 사례 (30앱, 12개월, $22K MRR)
- Firebase로 백엔드 우회 가능
- 위젯 커버(카테고리 B) 가능
- AI 코딩 도구(Claude Code) 프롬프트 대응력 우수

**Android 우선, iOS 후순위**: 한국 안드로이드 70%+, AdMob 안드로이드 인터스티셜 $11.23 (2024 Q4, [Adnimation](https://www.adnimation.com/mobile-optimization-in-2025-turning-every-tap-into-revenue/)), 리워드 $29 (Q1 2024). iOS는 검증된 앱만 3~4번째 배포.

### 2-2. 재사용 템플릿 구조

**한 개 앱 = "템플릿 + 소재 데이터 + 화면 1~3개"** 구조:

```
apps-template/
├── core/                    # 절대 안 바꾸는 부분
│   ├── admob_wrapper.dart
│   ├── iap_wrapper.dart     # RevenueCat
│   ├── review_prompt.dart   # 인앱 리뷰
│   ├── privacy_screen.dart  # 개인정보 처리방침
│   ├── settings_screen.dart # 광고제거·언어·라이센스
│   └── analytics.dart       # Firebase Analytics
├── content/                 # 앱마다 교체
│   ├── strings.arb
│   ├── config.json          # 색상·아이콘·이름
│   └── data.json            # 소재별 데이터
├── screens/                 # 1~3개만 갈아끼움
│   ├── home_screen.dart
│   └── detail_screen.dart
└── fastlane/
    ├── Appfile
    ├── Fastfile             # supply·screengrab
    └── metadata/            # 스크린샷·설명 자동 업로드
```

**핵심 표준화 5종**:
1. **광고 SDK** — AdMob 단독 또는 AdMob + AppLovin MAX 미디에이션 (Max Artemov는 CAS)
2. **IAP** — RevenueCat 무료 티어 (월 $2.5K MTR까지 무료). 표준 3상품 ([Flutter 가이드](https://www.revenuecat.com/blog/engineering/flutter-subscriptions-tutorial))
3. **인앱 리뷰** — Google Play In-App Review API, 트리거: 설치 7일+, 세션 3회+, 크래시 없음, 90일 미노출 ([공식](https://developer.android.com/guide/playcore/in-app-review))
4. **개인정보처리방침** — [개인정보위 공식 생성기](https://m.privacy.go.kr/front/per/inf/perInfStep01.do) + [App Privacy Policy Generator](https://mobile-privacy.github.io/generator/)
5. **다국어** — 한국어·영어 최소, ARB 파일 + Claude Code 자동 번역

### 2-3. AI 코딩 활용 (Claude Code)

Claude Code는 2025년 5월 출시 후 46% "most loved" ([WaveSpeed AI](https://wavespeed.ai/blog/ko/posts/cursor-vs-claude-code-comparison-2026/)). 다작 궁합 이유:
- 파일시스템 접근 → 템플릿 클론·리네임·리소스 치환 CLI 지시
- 여러 파일 걸친 리팩터링 자동 (스토리지 키, 앱 ID, 패키지명 일괄)
- git·pubspec·fastlane 명령어 실행

**신규 앱 생성 프롬프트 스켈레톤** (실전):

```
apps-template 저장소를 lotto-fortune이라는 새 앱으로 복제해라.
- 앱 이름: "로또 사주 번호"
- 패키지명: com.jameskim.lottofortune
- 색상 팔레트: config.json의 primary를 #FFD700, accent를 #8B0000
- data.json에 사주 기반 로또번호 생성 로직 (생년월일 → 6개 숫자) 추가
- home_screen.dart를 사주 입력 폼으로 교체
- detail_screen.dart를 6개 번호 + AdMob 인터스티셜 트리거 화면으로 교체
- fastlane/metadata/ko-KR/description.txt에 ASO 최적화된 설명 생성
- flutter run으로 컴파일 확인
```

**실측 단축**: Claude Code 도입 시 김윤후·케빈 언급 "하루 1~5개 앱" 수준이 개인 개발자에게 현실화. 프로그래밍좀비: "6개월 걸린 앱보다 1일 걸린 앱이 수익이 훨씬 많은 경우 잦음" ([Maily](https://maily.so/indiehackerlab/posts/g1o45916rve)).

### 2-4. 스토어 등록 반자동화

**Fastlane**: `supply`로 Google Play 자동 업로드, `screengrab`로 다국어 스크린샷 자동, `Firebase App Distribution`으로 12인 테스터 자동 배포 ([Fastlane 문서](https://docs.fastlane.tools/actions/capture_android_screenshots/), [Firebase](https://firebase.google.com/docs/app-distribution/android/distribute-fastlane?hl=ko)).

**스크린샷**: Figma 템플릿 5장 준비, 텍스트만 앱별 교체. Screenshot Studio, AppMockUp, previewed.app 활용.

**스토어 설명 다국어**: Claude Code에 "이 앱을 한국어·영어·일본어로 ASO 최적화된 800자 설명" → 30초 완료.

---

## 섹션 3. ASO 전략 (다작 모델의 유일한 수익 상수)

### 3-1. 롱테일 키워드 전략

**한국 검색 습관 핵심**: 조사·수식어·시험/기관 이름 조합 패턴 유효 ([DelightRoom](https://medium.com/delightroom/스토어-키워드-발굴하기-cfb84af1d706)).

예시:
- "디데이" 단독 (경쟁 극심) → "정보처리기사 디데이", "군인 전역 디데이", "출산 디데이" (경쟁 낮음)
- "계산기" 단독 → "1가구2주택 양도세 계산기", "전기차 자동차세 계산기"
- "운세" 단독 → "2026 뱀띠 운세", "쌍둥이자리 이번주 운세"

**Max Artemov 기준**: popularity > 20, difficulty < 60 조합. **키워드부터 정하고 앱을 만든다** ([Indie Hackers](https://www.indiehackers.com/post/tech/from-failed-app-to-30-app-portfolio-making-22k-mo-in-less-than-a-year-myy3U7K9evxGOVOHti8s)).

**무료 도구**:
- Play Console 자체 "검색어" (자동완성)
- [AppTweak 무료](https://www.apptweak.com/ko/aso-blog/best-aso-keyword-research-tools)
- Astro, FoxData (Max Artemov 사용)
- Google Trends

### 3-2. 스토어 등록 페이지 최적화

**Google Play Store Listing Experiments** ([공식](https://play.google.com/intl/ko/console/about/store-listing-experiments/)):
- 아이콘 A/B 우선 (검색 결과 유일한 크리에이티브)
- 5개 지역별 or 1개 기본 실험 병행
- 아이콘·스크린샷·설명 동시 변경 금지

**스크린샷 첫 3장 공식**:
1. 앱 이름 + 셀링포인트 텍스트 (예: "정보처리기사 D-Day • 홈화면 위젯")
2. 실제 화면 + 한 줄 설명
3. 리뷰 or 사용자 수 소셜 프루프

**설명 첫 3줄**: Play Console 확장 없이 보이는 부분. 핵심 키워드 3개 + 사용 시나리오 1문장.

### 3-3. 리뷰 확보

김윤후 강조: **"리뷰 요청 타이밍이 진짜 중요"** ([패스트캠퍼스](https://fastcampus.co.kr/story_article_indiehacker)). 26,000+ 리뷰 4.8점 달성.

**타이밍 규칙**:
- 주 기능 성공 완료 직후 (D-Day: 첫 등록 후, 계산기: 결과 화면 3초 응시 후)
- 크래시 없는 세션만
- 90일 쿨다운

**초기 리뷰 확보** (12인 테스터):
- [클로즈드테스팅 12명 매칭](https://closedtesting12.com/ko/index)
- 카톡 오픈채팅 "안드로이드 앱 테스터" 검색
- 지인 12명 카톡 안내 텍스트 표준화

**별점 필터링 우회**: "만족도 5점 여부" → 5점만 스토어 리뷰, 그 미만은 이메일 폼 라우팅. **주의**: Google Play 정책 회색지대. 안전은 in-app review API만.

### 3-4. 카테고리·순위

- **소분류 선정**: "도구", "생활 편의", "라이프스타일" 강자 밀집도 낮음. "생산성" 극심.
- **허니문 효과**: Play Store 신규 등록 후 3~7일 추천 슬롯 노출 상승. 광고 없이 오가닉 200~500 다운로드 가능.
- **시즌성 소재**: 신년(운세·D-Day) / 3월(급식·시간표) / 5월(어린이날 뽑기) / 11월(수능 D-Day) / 12월(내년 운세)

---

## 섹션 4. 다작 개발자 실제 워크플로우·리스크

### 4-1. 실제 워크플로우

**케빈**: 정점기 하루 5개 앱 배포. 셸 스크립트 + Fastlane 자동화. LG 트윈스 우승 당일 팬 커뮤니티 앱 제작·출시 완료 ([Maily](https://maily.so/josh/posts/xyowmnv8z28)). **"60점짜리 5개 만드세요. 하나 터지면 4개 실패 커버합니다."**

**김윤후**: 캐나다 풀타임 개발자 시절 퇴근 후 개발. 현재 4개 액티브 유지, 나머지 12개는 OS 호환 업데이트만. 마케팅 예산 월 50만원 미만, 인스타 광고 위주. 고객 지원은 카톡 챗봇 자동화 (일일 50건→1~2건) ([Maily](https://maily.so/josh/posts/1gz2v974r3q)).

**프로그래밍좀비**: 하루 10시간 코딩. 육아 분담 후 놀이터 → 오전 코딩 → 저녁·주말 집중. "샤워, 여행, 업무 중 아이디어 수집" ([Maily](https://maily.so/indiehackerlab/posts/g1o45916rve)).

**추천 주 단위 사이클 (2주 1앱)**:
- W1 월: 소재 확정 + 키워드 리서치 (2시간). AppTweak/Astro로 popularity, difficulty 확인
- W1 화·수: 템플릿 클론 → Claude Code 프롬프트로 화면 1~3개 재작성 (총 8시간)
- W1 목·금: API 연동, 광고 배치, 리뷰 트리거, 폴리싱 (총 6시간)
- W2 월·화: 12인 비공개 테스트 등록, 스크린샷 촬영, 스토어 메타데이터 (총 4시간)
- W2 수~일: 14일 테스트 대기 (실제로는 다음 앱 W1 시작)

**실패 판단 기준**:
- 출시 후 30일 총 다운로드 < 200 → 유지보수만
- 30일 광고 수익 < $1/일 → 신규 기능 투자 중단
- 3개월 다운로드 지속 성장 or 수익 $5/일 이상 → 몰빵 후보 (김윤후 "간단" 앱 패턴)

### 4-2. 광고 SDK·수익화 표준

**AdMob 필수**:
- 인터스티셜: 앱 실행 30초 후, 화면 전환 3회당 1회, 세션 첫 트리거 15초 후
- 리워드: 프리미엄 기능(고급 계산·추가 뽑기·사주 상세) 게이트 → 광고 시청 → 즉시 이용
- 배너: 홈 하단 고정 (계산기·조회 앱만. D-Day·위젯 앱은 배너 제외)

**미디에이션 (3개월차부터)**:
- AdMob = 기본 수요원
- AppLovin MAX = 경쟁 입찰 추가
- ironSource LevelPlay 옵션 ([Teqblaze](https://teqblaze.com/blog/mobile-app-monetization-for-publishers))
- 매출 개선 폭 20~40%

**Firebase 무료**: Analytics + Crashlytics + Remote Config. Remote Config로 앱마다 광고 노출 빈도 서버 조정이 핵심.

**IAP 표준 3상품** (김윤후 사례):
- 광고제거 (일회성) 3,300원
- 프리미엄 월 구독 2,500원
- 프리미엄 연 구독 15,000원

김윤후 프리미엄 전환율 10~20%. **"몸무게 기능 노출 = 매출 3배 상승"** — 결제 게이트 배치가 UI/UX보다 매출 결정 ([패스트캠퍼스](https://fastcampus.co.kr/story_article_indiehacker)).

### 4-3. 다중 계정·정책 리스크

**Google Play 다중 계정**: 공식 허용, 실무는 회색지대.
- 계정마다 다른 결제수단 ([GoLogin](https://gologin.com/blog/multiple-google-play-developer-accounts/))
- 동일 기기·IP 계정 여러 개 신속 생성 시 링크 처리 위험
- 반복/심각 정책 위반 시 "관련 Google Play 개발자 계정 모두 해지" 명시 ([공식](https://support.google.com/googleplay/android-developer/answer/9899234?hl=ko))

**실무**: 계정 1개로 시작. 100개 앱까지 단일 계정 무리 없음. 계정 분리는 리스크군(도박·성인·의료)만.

**저작권·API 리스크** (구체):
- **로또**: 동행복권 로고·상표 사용 금지. 명칭·기능 자체는 합법. QR 당첨 확인은 로고 없이 QR 파싱만
- **지하철 노선도**: 서울시 [공식 디자인](https://news.seoul.go.kr/culture/archives/522224) 저작권 있음. 자체 그린 다이어그램 or 공공데이터 API 반환만
- **사주 콘텐츠**: 만세력 계산은 알고리즘(저작권 없음). 해석 문구는 저작권 있으므로 자체 or GPT API 생성
- **급식**: 나이스 교육정보개방포털 API가 공식

**공공데이터 API**: [공공데이터포털](https://www.data.go.kr) 인증키 필요. 트래픽 초과 시 활용 제한. 상업 이용 가능/불가 구분 필수.

**개인정보처리방침**: 앱마다 필수. [개인정보위](https://m.privacy.go.kr/front/per/inf/perInfStep01.do) + [App Privacy Policy Generator](https://mobile-privacy.github.io/generator/). 자체 도메인(예: james-apps.com/privacy/{앱ID}) 하나로 여러 앱 동시 관리.

**계정 정지 리스크**: 도메인 만료로 앱 미작동 → 위반 처리 실사례 있음 ([Dongmin Kim](https://real21c.github.io/google-dev-account-block/)). 종료 앱은 반드시 스토어에서 언리스트.

**사업자 등록**: 소득 발생 시 개인사업자 등록 권장. 간이과세자(연매출 4,800만원 미만) 시작 → 부가세 신고 단순. 종합소득세 5월, 부가세 1월·7월. 개발 장비·클라우드·광고비 모두 필요경비 처리 ([Hitek](https://hiteksoftware.co.kr/blog/registration-of-app-development-business/), [i_jemin](https://ijemin.com/blog/앱스토어-개발자-세금-가이드-부가세-1-2/)).

### 4-4. 실측 매출 밴드

| 티어 | 개발자 | 앱 수 | 월 매출 | 근거 |
|---|---|---|---|---|
| 상단 | 케빈 | 3,000+ | 월 8억 이상 (연 100억) | [Maily 케빈](https://maily.so/josh/posts/xyowmnv8z28) |
| 상중단 | 프로그래밍좀비 | 300+ | 월 수천만 (퇴사 가능) | [Maily](https://maily.so/indiehackerlab/posts/g1o45916rve) |
| 중단 | 김윤후 | 350 (활성 4) | 월 1,000만원+ | [패스트캠퍼스](https://fastcampus.co.kr/story_article_indiehacker) |
| 중단(해외) | Max Artemov | 30 | 월 $22K (약 3,000만원) | [Indie Hackers](https://www.indiehackers.com/post/tech/from-failed-app-to-30-app-portfolio-making-22k-mo-in-less-than-a-year-myy3U7K9evxGOVOHti8s) |
| 하단 | 클리앙/OKKY | 5~20 | AdMob 월 $500~$4,000 | [2023.04 $3,829](https://mydevspace.blogspot.com/2023/05/2023-4-1.html), [OKKY 6만 다운](https://okky.kr/articles/1408080) |
| 입문 | 부업 | 3~10 | 월 30~200만원 | [클리앙](https://www.clien.net/service/board/lecture/15758114) |

**매출 대략 함수**:
- 앱 1개당 평균은 의미 없음. **분포가 극단적 파레토**.
- 100개 던지면 통계적으로: 1개가 전체의 60~80%, 5~10개가 나머지 20~30%, 90개는 광고비 미만
- 즉 다작의 진짜 이유는 **"어떤 앱이 히트할지 사전에 몰라서 100개 던져 1개 확률적으로 뽑는 것"**

### 4-5. 실패 리스크 Top 5 + 완화

1. **"100개 다 안 뜸" (가장 흔한 실패)** — 이유: 소재 감으로 던짐. **완화**: 소재 확정 전 AppTweak/Astro로 popularity>20, difficulty<60 확인 (Max Artemov 원칙)
2. **계정 정지 (연쇄 파괴)** — 이유: 유사 앱 대량 등록 "스팸" 판정, 종료 앱 미언리스트 "미작동" 판정. **완화**: 앱 이름·아이콘·설명 동일 패턴 회피, 매 앱 최소 화면 3개 차별화, 종료 앱 즉시 언리스트
3. **광고 eCPM 하락** — 2024 Q4 → 2025 H1 안드로이드 인터스티셜 -11%, 리워드 -7% ([Adnimation](https://www.adnimation.com/mobile-optimization-in-2025-turning-every-tap-into-revenue/)). **완화**: IAP 3상품 병행, 미디에이션 도입
4. **번아웃 (심리적)** — 6개월간 15~20개 실패 지속 시 흔함. 김윤후도 초기 $0.52. **완화**: "실패 판단 기준" 사전 명확화, 실패 앱 미련 없이 언리스트, "실패 = 데이터 수집" 프레이밍
5. **저작권·정책 지뢰** — 로또 로고·지하철 노선도·음원 무단 사용. **완화**: 이미지 100% 자체 or Unsplash·Freepik(라이선스 확인), 데이터는 공공데이터포털만, 사주·운세 텍스트는 자체 or GPT API

---

## 첫 12주 액션 플랜

**W1**: 스택 셋업. Flutter 3.24 설치, Firebase 프로젝트, AdMob 계정, RevenueCat 계정, 개인사업자 신청. Claude Code로 apps-template 스켈레톤 생성.

**W2**: 템플릿 컴포넌트 5종 완성 (광고 wrapper, IAP wrapper, 리뷰 트리거, 설정 화면, 다국어). Fastlane supply·screengrab 설정. Google Play 개발자 계정 등록($25).

**W3~4**: **첫 앱 = "정보처리기사 D-Day 위젯"** (검증 소재 + 롱테일 키워드 + 위젯 학습). 3주차 개발, 4주차 12인 테스트 등록 + 오픈채팅 매칭.

**W5~6**: **두 번째 앱 = "1가구2주택 양도세 계산기"** (파편적 시장 + 세무 니즈). 첫 앱 광고 수익 지표 첫 관측.

**W7~8**: **세 번째 앱 = "군인 D-Day 전역 위젯"** (첫 앱 성공 시 D-Day 시리즈 확장, 실패 시 다른 니치). Fastlane 자동화 정교화.

**W9~10**: **네 번째 앱 = "청년 정책 지원금 D-Day 알림"** (틈새 + 국내 특화). 앱 3개 지표 종합 리뷰. 상위 1개 A/B 시작.

**W11~12**: **다섯 번째 앱 = "지역별 병원·약국 야간 조회"** (공공데이터 API 학습). 3개월 지표 정리, 가장 잘 되는 앱 1개에 신규 기능 3개 추가 예정 (몰빵 시작).

**12주 기대치**: 앱 5개 출시, 다운로드 총 500~5,000, AdMob 수익 월 $50~$500. **이 시점에 히트작 후보 1개는 나옵니다.** 이후 20~30주는 히트작 확장 + 추가 앱 발사 병행.

---

## 즉시 착수 가능한 소재 Top 5

이 사용자(한국·백엔드 최소·AI 코딩·광고+IAP)에게 최적:

1. **정보처리기사 D-Day 위젯** — 시험 D-Day 시장 강자 있지만 특정 자격증(정보처리기사·산업기사)으로 좁히면 롱테일 진입. 위젯 = 리텐션 높고 광고 궁합 좋음. AI 코딩 최적.
2. **1가구2주택 양도세 계산기** — 파편적 시장, 세무 니즈 강함, 광고·IAP 궁합 최상. 국세청 로직 참고, 백엔드 불필요.
3. **군인 전역 D-Day 위젯** — 파편적, 커뮤니티 응집력(디시·군생활) 강해 오가닉 확산 가능. 커플 D-Day 강자 회피.
4. **청년 정책 지원금 D-Day + 알림** — 국내 특화, 지자체별 데이터 정리 = 진입장벽. 광고 궁합 최상 (돈 관심 유저).
5. **지역별 야간·주말 병원 조회** — 공공데이터 API. 페인포인트 강력, 검색 유입 확실. 광고 궁합 최상 (긴급 상황 유저 = 광고 클릭률 높음).

---

## 마지막 냉정한 한 마디

이 모델의 진짜 리스크는 "100개 다 안 뜨는 것"이 아니라 **"20개까지 다 안 뜬 시점에 그만두는 것"** 입니다. 김윤후도 첫 수익 $0.52로 시작했고, 프로그래밍좀비는 5년 세미나에서 들은 말 하나로 6년을 버텼습니다. 이 사용자의 성격이 **"빠른 피드백 없이도 24개월을 버틸 수 있는가"** 가 이 모델 성패의 유일한 변수입니다. 24개월 못 버틸 것 같으면 다작 모델은 처음부터 접고, "잘 만든 하나에 3~6개월"로 되돌아가는 게 정직한 선택입니다.

---

## Sources

- [혼자서 앱 3000개를 만들고 연 매출 100억을 달성한 1인 개발자, 케빈님 (Maily)](https://maily.so/josh/posts/xyowmnv8z28)
- [6년간 앱 350개를 만들어 파이어를 달성한 1인 개발자 (Maily)](https://maily.so/josh/posts/wdr9vvy7zlx)
- [혼자서 200만 글로벌 단식 앱으로 월 1K를 버는 1인 개발자, 김윤후님 (Maily)](https://maily.so/josh/posts/1gz2v974r3q)
- [1인 앱 개발 김윤후의 진짜 이야기 (패스트캠퍼스)](https://fastcampus.co.kr/story_article_indiehacker)
- [6년간 300개 앱 만들고 퇴사한 프로그래밍좀비 (Maily)](https://maily.so/indiehackerlab/posts/g1o45916rve)
- [이미 성공한 앱을 복제해서 월 4,500만원을 버는 1인 개발자의 전략 (Maily)](https://maily.so/josh/posts/5xrx6lnqr2v)
- [혼자서 연 28억원을 버는 1인 개발자의 수익화, 자동화, AI (Maily)](https://maily.so/josh/posts/5xrxkxgyo2v)
- [From failed app to 30-app portfolio making $22k/mo (Indie Hackers)](https://www.indiehackers.com/post/tech/from-failed-app-to-30-app-portfolio-making-22k-mo-in-less-than-a-year-myy3U7K9evxGOVOHti8s)
- [I'm Launching 12 Startups in 12 Months — Pieter Levels](https://levels.io/12-startups-12-months)
- [1인 개발 앱 0에서 6만 다운로드 후기 (OKKY)](https://okky.kr/articles/1408080)
- [부업으로 어플 개발 후기 및 수익공개 (클리앙)](https://www.clien.net/service/board/lecture/15758114)
- [2023년 4월, 1인 앱 광고 수익 (애드몹) $3829](https://mydevspace.blogspot.com/2023/05/2023-4-1.html)
- [1인 앱개발을 시작하기 전에 알았으면 좋았을 것들 (브런치)](https://brunch.co.kr/@kiraku/2)
- [Mobile Optimization in 2025: eCPM Trends (Adnimation)](https://www.adnimation.com/mobile-optimization-in-2025-turning-every-tap-into-revenue/)
- [Google Play 새로운 개인 개발자 계정 앱 테스트 요구사항](https://support.google.com/googleplay/android-developer/answer/14151465?hl=ko)
- [BETA FLOW 클로즈드 테스트 12명 매칭](https://closedtesting12.com/ko/index)
- [스토어 등록정보 실험: Play Store A/B 가이드 (AppTweak)](https://www.apptweak.com/ko/aso-blog/store-listing-experiments-a-guide-to-play-store-a-b-testing)
- [Google Play In-App Reviews API](https://developer.android.com/guide/playcore/in-app-review)
- [Flutter Localization](https://docs.flutter.dev/ui/internationalization)
- [Fastlane capture_android_screenshots](https://docs.fastlane.tools/actions/capture_android_screenshots/)
- [RevenueCat Flutter 튜토리얼](https://www.revenuecat.com/blog/engineering/flutter-subscriptions-tutorial)
- [Cursor vs Claude Code (WaveSpeed AI)](https://wavespeed.ai/blog/ko/posts/cursor-vs-claude-code-comparison-2026/)
- [How to Run Multiple Google Play Developer Accounts (GoLogin)](https://gologin.com/blog/multiple-google-play-developer-accounts/)
- [앱스토어 개발자 세금 가이드 (i_jemin)](https://ijemin.com/blog/앱스토어-개발자-세금-가이드-부가세-1-2/)
- [유료 앱 개발자 개인 사업자 등록 (Hitek)](https://hiteksoftware.co.kr/blog/registration-of-app-development-business/)
- [스토어 키워드 발굴 (DelightRoom Medium)](https://medium.com/delightroom/스토어-키워드-발굴하기-cfb84af1d706)
- [Google Play 정책 위반 시행 절차](https://support.google.com/googleplay/android-developer/answer/9899234?hl=ko)
- [개인정보처리방침 만들기 (개인정보위)](https://m.privacy.go.kr/front/per/inf/perInfStep01.do)
- [App Privacy Policy Generator](https://mobile-privacy.github.io/generator/)
- [공공데이터포털 지하철 실시간 API](https://www.data.go.kr/data/15058052/openapi.do)
- [구글 플레이 개발자 계정 삭제부터 복원까지 (Dongmin Kim)](https://real21c.github.io/google-dev-account-block/)
- [AdMob vs AppLovin vs Unity Ads vs ironSource (Teqblaze)](https://teqblaze.com/blog/mobile-app-monetization-for-publishers)
