# REST API vs GraphQL — Debate & Critic 결과 보고서

> 생성일: 2026-04-10 | 패턴: ⚔️ Debate & Critic | Rounds: 2

---

## 주제

프로젝트에 REST API와 GraphQL 중 어떤 것을 선택할 것인가?

## 참여 에이전트

| 역할 | 담당 |
|------|------|
| 💡 Proposer | REST API 옹호 |
| ⚔️ Opponent | GraphQL 옹호 |
| 🔍 Critic | 중립 평가 |
| 🧩 Synthesizer | 종합·결론 |
| 📋 Scribe | 문서화 (본 문서) |

---

## Round 1 요약

### Proposer (REST)
- HTTP 캐싱(ETag, Cache-Control, CDN) 네이티브 활용
- OpenAPI/Swagger 기반 압도적 생태계
- URL 기반 직관적 설계, 낮은 학습 곡선
- 엔드포인트별 세분화된 보안/Rate Limiting

### Opponent (GraphQL)
- Over/Under-fetching 완전 해결
- 강력한 타입 시스템 (스키마 = 계약)
- 단일 요청으로 복잡한 데이터 조회
- Subscription 기반 실시간 지원

### Critic 평가
- REST의 HTTP 캐싱은 진짜 강점
- GraphQL의 Over/Under-fetching 해결은 REST가 반박 못 함
- 양측 모두 "어떤 프로젝트인가" 핵심 맥락 누락
- **판정: NOT_CONVERGED — 시나리오 기반 비교 필요**

---

## Round 2 요약 (시나리오 기반)

### 시나리오 1: 공개 API 플랫폼

| 기준 | REST | GraphQL |
|------|------|---------|
| 캐싱 | HTTP 캐싱 네이티브 | Persisted Queries + CDN |
| 버전 관리 | v1/v2 다중 유지 부담 | @deprecated 점진적 진화 |
| 보안 | 엔드포인트별 직관적 | depth limit, cost analysis 필요 |
| **판정** | | **GraphQL 근소 우위 ★★★☆☆** |

### 시나리오 2: 모바일 앱 BFF

| 기준 | REST | GraphQL |
|------|------|---------|
| 페이로드 | gzip 압축으로 축소 | 필요 필드만 요청 (50-70% 감소) |
| 라운드트립 | BFF 패턴으로 완화 | 단일 요청으로 해결 |
| 개발 생산성 | 화면별 엔드포인트 유지 | 프론트엔드 자율적 쿼리 수정 |
| **판정** | | **GraphQL 명확 우위 ★★★★☆** |

### 시나리오 3: 내부 마이크로서비스

| 기준 | REST/gRPC | GraphQL |
|------|-----------|---------|
| 성능 | 경량, 파싱 오버헤드 없음 | 쿼리 파싱·검증 오버헤드 |
| 인프라 | 서비스 메시 네이티브 호환 | 메시 통합 미성숙 |
| 관측성 | URL 기반 메트릭 즉시 가능 | 단일 엔드포인트로 분석 어려움 |
| **판정** | **REST/gRPC 명확 우위 ★★★★★** | |

---

## 최종 결론

### ✅ CONVERGED: "시나리오가 답을 결정한다"

| 시나리오 | 권장 기술 | 확신도 |
|---------|----------|--------|
| 공개 API 플랫폼 | GraphQL | ★★★☆☆ |
| 모바일 앱 BFF | GraphQL | ★★★★☆ |
| 내부 마이크로서비스 | REST/gRPC | ★★★★★ |

### 의사결정 체크리스트

1. **클라이언트가 다양한가?** → Yes면 GraphQL
2. **응답 형태가 고정인가?** → Yes면 REST/gRPC
3. **네트워크 비용이 민감한가?** → Yes면 GraphQL
4. **서비스 메시/인프라 표준이 있는가?** → Yes면 REST/gRPC
5. **API 버전 관리 부담이 큰가?** → Yes면 GraphQL

### 공통 주의사항

- GraphQL 도입 시 쿼리 복잡도 제한(depth limit, cost analysis) 필수
- REST 선택 시 OpenAPI 스펙 자동화 없으면 문서 부채 누적
- **혼합 사용은 정상** — 외부는 GraphQL, 내부는 gRPC가 실무 최적해인 경우 다수

> **"무엇이 더 좋은가"가 아니라 "어디에 쓰는가"가 정답이다.**
