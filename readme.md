# ETF 테마주 추천 챗봇 프로젝트

## 프로젝트 개요
ETF(상장지수펀드) 투자에 대한 개인 맞춤형 추천 챗봇을 개발하는 프로젝트입니다. 뉴스 감정 분석 기반으로 테마 ETF를 추천하며, 사용자 성향에 맞는 포트폴리오를 제공하여 투자 효율성을 극대화합니다.

## 팀원
- 박서현
- 오윤지
- 원태연
- 최현석

---

## 1. 추진 배경

### 주요 동기
- **개인 자금 관리의 중요성 증가**
  - 소액으로 분산 투자 가능.
  - 거래비용이 낮아 효율성 증가.
  - 매일 운용 자산 확인 가능.
- **ETF의 장점**
  - 투명성, 환금성, 낮은 거래 비용.
  - 다양한 상품 제공으로 초보 투자자의 접근성 증가.
- **복잡한 금융 환경**
  - 생소한 개념, 복잡한 상품 구조, 실시간 거래의 부담 등.
  - 개인화된 투자 가이드의 필요성 증가.

### 목표
- 사용자 투자 성향에 따른 맞춤형 ETF 추천.
- 뉴스 감정 분석을 통한 테마별 유망도 평가.

---

## 2. 데이터 수집 및 분석

### 데이터 소스
- **K-ETF**: 국내 테마주 ETF 데이터.
- **한국투자증권 API**: ETF 데이터.
- **네이버 금융**: 채권 ETF 데이터.
- **네이버 뉴스, SerpAPI**: 뉴스 및 감정 데이터.

### 데이터 처리
1. **ETF 데이터 수집 및 전처리**
   - K-ETF 데이터를 기반으로 CSV 수집.
   - 기타 테마로 표시된 데이터는 대체 가능 시 수정, 불가 시 삭제.
   - `FinanceDataReader`를 사용하여 CAGR, 변동성, 샤프지수 계산.

2. **뉴스 감정 분석**
   - 테마별 뉴스 헤드라인을 수집하여 감정 점수를 수치화.
   - 긍정/부정 평가를 통해 테마의 유망도를 적용.

3. **투자 성향 분석**
   - 안정형, 중립형, 공격형으로 성향 구분.
   - 성과, 안정성, 유동성, 펀더멘털 가중치로 ETF 점수화.

---

## 3. 챗봇 개발

### 주요 기능
- **LLM 기반 입력 처리**: 자연어 입력을 이해하여 사용자 질문 처리.
- **API 통합 활용**: 실시간 시장 전망 및 뉴스 데이터 제공.
- **사용자 성향 분석**: 투자 목적과 리스크 성향 분석.
- **포트폴리오 완성**: ETF 추천 및 사용자 맞춤형 포트폴리오 제공.

### 챗봇 흐름
1. **지식 확인**: 사용자의 ETF 관련 지식 수준 분석.
2. **성향 분석**: 사용자 투자 성향 파악.
3. **테마 출력**: 유망 테마와 실시간 전망 제공.
4. **ETF 추천**: 테마별 상위 ETF 추천.
5. **포트폴리오 완성**: 다중 선택을 통한 맞춤형 구성 제공.

---

## 4. 결론 및 개선 방향

### 결론
- 뉴스 감정 분석과 API 활용을 통해 사용자 맞춤형 ETF 추천 챗봇 개발.
- 복잡한 금융 정보를 간소화하여 효율적인 투자 환경 제공.

### 개선 방향
1. **일반 주식 추가**: ETF 외에도 개별 주식 추천 기능 개발.
2. **변동성 완화 자산 추가**: 다양한 자산을 포트폴리오에 포함.
3. **동적 데이터 활용**: 실시간 데이터를 기반으로 한 추천 개선.
4. **챗봇 성능 강화**: 빠른 응답 속도와 더 많은 기능 제공.

---

## 기술 스택
- **데이터 분석**: `Python`, `Pandas`, `FinanceDataReader`.
- **API 통합**: `한국투자증권 API`, `SerpAPI`.
- **모델링**: 뉴스 감정 분석, 투자 성향 분석.
- **챗봇 개발**: `Streamlit`, `OpenAI API`.

---

## 프로젝트 시연
- **챗봇 데모**: 사용자 투자 성향 분석 및 ETF 추천.
- **웹 앱**: Streamlit을 활용한 단순 사이트 구현.

---

## 프로젝트 파일 구조
```plaintext
.
├── data/            # 데이터 수집 및 전처리 파일
├── models/          # 투자 성향 분석 및 감정 분석 모델
├── chatbot/         # 챗봇 관련 코드 및 API 통합
├── app/             # Streamlit 웹 애플리케이션
└── README.md       # 프로젝트 설명 파일
```
