# TODO REST API — Planner-Executor 결과 보고서

> 생성일: 2026-04-10 | 패턴: 📐 Planner-Executor | 태스크: 4개

---

## 주제

기존 JWT 인증 API에 TODO CRUD REST API 추가 (인증된 사용자 전용)

## 참여 에이전트

| 역할 | 담당 |
|------|------|
| 📐 Planner | 태스크 분해, 의존성/순서/검증기준 수립 |
| 🔧 Executor | 태스크별 코드 구현 |
| 🧪 Validator | 13개 통합 테스트로 검증 |
| 📋 Scribe | 문서화 (본 문서) |

---

## 실행 계획

```
T1 (서비스) → T2 (라우터) → T3 (등록) → T4 (검증)
```

| # | 태스크 | 파일 | 결과 |
|---|--------|------|------|
| T1 | TODO 서비스 레이어 | `services/todo.js` | ✅ Pass |
| T2 | TODO 라우터 | `routes/todo.js` | ✅ Pass |
| T3 | server.js 등록 | `server.js` (+2줄) | ✅ Pass |
| T4 | 통합 테스트 | 13개 시나리오 | ✅ 13/13 Pass |

---

## 검증 결과 (T4)

| # | 테스트 | 기대 | 결과 |
|---|--------|------|------|
| 1 | 인증 없이 GET /todos | 401 | ✅ |
| 2 | 회원가입 | accessToken 반환 | ✅ |
| 3 | TODO 생성 | 201 + id 반환 | ✅ |
| 4 | 2번째 TODO 생성 | 201 | ✅ |
| 5 | 전체 조회 | 2건 | ✅ |
| 6 | 단건 조회 | 200 | ✅ |
| 7 | 수정 (completed=true) | completed: true | ✅ |
| 8 | 필터링 completed=true | 1건 | ✅ |
| 9 | 정렬 desc | 최신순 정렬 | ✅ |
| 10 | 삭제 | 200 | ✅ |
| 11 | 삭제 후 조회 | 404 | ✅ |
| 12 | 다른 유저 격리 | 0건 | ✅ |
| 13 | Health check | 200 | ✅ |

---

## 최종 산출물

```
app/
├── services/todo.js      # CRUD 비즈니스 로직 (userId 격리, 필터/정렬)
├── routes/todo.js         # 5개 엔드포인트 + authenticateToken
└── server.js              # +2줄 (import + app.use)
```

### API 엔드포인트

| Method | Path | 설명 | 인증 |
|--------|------|------|------|
| GET | /todos | 전체 조회 (?completed, ?sort, ?order) | ✅ |
| GET | /todos/:id | 단건 조회 | ✅ |
| POST | /todos | 생성 (title 필수) | ✅ |
| PUT | /todos/:id | 수정 (title, description, completed) | ✅ |
| DELETE | /todos/:id | 삭제 | ✅ |

### 핵심 특징
- userId별 데이터 격리 (다른 유저 TODO 접근 불가)
- 기존 서비스 레이어 패턴 준수 ({ status, data } / { error, status })
- 필터링 (completed=true/false) + 정렬 (createdAt asc/desc)
- Revise 없이 1회 실행으로 전체 Pass
