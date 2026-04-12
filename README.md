# 🤖 Copilot CLI — Multi-Agent Patterns

> GitHub Copilot CLI를 활용한 **멀티 에이전트 협업 패턴** 레퍼런스 프로젝트

여러 AI 에이전트가 역할을 분담하여 협업하는 패턴들을 정의하고,
[GitHub Copilot CLI](https://docs.github.com/copilot)의 `--agent` 옵션으로 바로 실행할 수 있는 샘플을 제공합니다.

## 프로젝트 구조

```
github-copilot-cli-squad/
├── AGENTS.md                           # 모든 에이전트 공통 가드레일 (Harness)
├── init.sh                             # Codespace 환경 셋업 스크립트
├── .devcontainer/
│   └── devcontainer.json               # Codespace 시작 시 init.sh 자동 실행
├── .github/agents/                     # Copilot CLI 에이전트 정의 (팀 구성·라우팅·다이어그램 포함)
│   ├── orchestrator.agent.md           # 오케스트레이터 — 요청 분석 후 패턴 자동 선택
│   ├── code_generation.agent.md        # 코드 설계→구현→리뷰 패턴 에이전트
│   ├── planner_executor.agent.md       # 계획-실행 패턴 에이전트
│   ├── debate_critic.agent.md          # 토론-비평 패턴 에이전트
│   └── generator_evaluator.agent.md    # 생성-평가 패턴 에이전트
└── .copilot/
    └── mcp-config.json                 # MCP 서버 설정
```

## 시작하기

### 사전 요구 사항

- [GitHub Codespaces](https://github.com/features/codespaces) 또는 Node.js 22+ 환경
- [GitHub Copilot](https://github.com/features/copilot) 구독

### 방법 1: Codespace (권장)

이 레포를 Codespace로 열면 `init.sh`가 자동 실행되어 아래 도구들이 설치됩니다:

| 도구 | 설명 |
|------|------|
| [GitHub Copilot CLI](https://docs.github.com/copilot) | `copilot` 명령으로 에이전트 실행 |
| [Azure CLI](https://learn.microsoft.com/cli/azure/) | Azure 리소스 관리 |
| [uv](https://docs.astral.sh/uv/) | Python 패키지 매니저 |

### 방법 2: 로컬 환경

```bash
git clone https://github.com/<owner>/github-copilot-cli-squad.git
cd github-copilot-cli-squad
./init.sh
```

## 에이전트 실행 방법

### Copilot CLI로 에이전트 실행

```bash
# 오케스트레이터 — 요청을 분석하여 최적의 패턴 팀을 자동 선택
copilot --agent orchestrator --yolo

# 개별 패턴 에이전트를 직접 지정하여 실행
copilot --agent planner_executor --yolo
copilot --agent debate_critic --yolo
copilot --agent generator_evaluator --yolo
copilot --agent code_generation --yolo

# 기본 Copilot CLI (에이전트 없이)
copilot
```

---

## 에이전트 패턴

### 🎯 Orchestrator (오케스트레이터)

> 사용자 요청을 분석하고 최적의 패턴 팀을 자동 선택하는 라우터

```bash
copilot --agent orchestrator --yolo
```

| 사용자 의도 | 선택 패턴 |
|------------|----------|
| "구현해줘", "셋업해줘", "마이그레이션" | 📐 Planner-Executor |
| "비교해줘", "장단점", "뭐가 나을까" | ⚔️ Debate & Critic |
| "생성해줘", "리뷰해줘", "개선해줘" | ⚡ Generator-Evaluator |
| "설계하고 구현해줘", "코드 작성하고 리뷰해줘" | 🏗️ Code Generation |

---

### 🧩 Agent Teams 개념

**Agent Team**은 하나의 작업을 여러 전문 에이전트가 **역할을 분담**하여 협업으로 수행하는 단위입니다.

```
┌─────────────────────────────────────────────────┐
│                  Agent Team                     │
│                                                 │
│   ┌──────────┐   ┌──────────┐   ┌──────────┐   │
│   │ Role A   │──▶│ Role B   │──▶│ Role C   │   │
│   │ (생성/제안)│   │ (평가/반론)│   │ (종합/기록)│   │
│   └──────────┘   └──────────┘   └──────────┘   │
│        ▲                              │         │
│        └──────── 피드백 루프 ──────────┘         │
└─────────────────────────────────────────────────┘
```

#### 핵심 원칙

| 원칙 | 설명 |
|------|------|
| **역할 분리** | 각 에이전트는 하나의 명확한 책임만 수행 |
| **피드백 루프** | 산출물 → 평가 → 개선의 반복으로 품질 향상 |
| **수렴 조건** | 무한 반복 방지를 위해 최대 반복 횟수 설정 |
| **Scribe 기록** | 모든 팀에 Scribe가 포함되어 과정/결과를 문서화 |
| **공통 가드레일** | [`AGENTS.md`](AGENTS.md)를 통해 모든 팀에 동일한 안전 규칙 적용 |

#### 패턴별 팀 비교

| | 📐 Planner-Executor | ⚔️ Debate & Critic | ⚡ Generator-Evaluator | 🏗️ Code Generation |
|---|---|---|---|---|
| **목적** | 체계적 실행 | 최선의 결론 도출 | 반복 개선으로 품질 향상 | 설계 기반 코드 생성 |
| **팀 구성** | Planner → Executor → Validator | Proposer ↔ Opponent → Critic → Synthesizer | Generator → Evaluator → Refiner | Architect → Developer → Reviewer |
| **핵심 루프** | 계획 → 실행 → 검증 | 제안 → 반론 → 평가 | 생성 → 평가 → 개선 | 설계 → 구현 → 리뷰 |
| **최대 반복** | Revise 후 재실행 | 3 Rounds | 3 Cycles | 3 Cycles |
| **적합한 작업** | 구현, 마이그레이션, 셋업 | 기술 선택, 아키텍처 비교 | 코드 생성, 문서 작성, 리뷰 | 코드 설계·구현·리뷰 통합 |

---

### 📖 예시 시나리오

#### 시나리오 1: "모노레포 vs 멀티레포, 우리 팀에 뭐가 맞을까?"

> **선택 패턴:** ⚔️ Debate & Critic

| 단계 | 에이전트 | 수행 내용 |
|------|---------|----------|
| Round 1 | **Proposer** | "모노레포를 채택해야 합니다. 코드 공유가 쉽고, CI/CD 파이프라인을 통합 관리할 수 있습니다." |
| | **Opponent** | "멀티레포가 낫습니다. 팀별 독립 배포가 가능하고, 저장소 크기가 작아 빌드가 빠릅니다." |
| | **Critic** | "Proposer의 CI 통합 주장은 강력하나, 팀 규모(5명)에서는 모노레포 관리 부담이 클 수 있습니다." |
| | **Synthesizer** | 아직 수렴 불가 — 팀 규모와 배포 빈도 기준으로 Round 2 진행 |
| Round 2 | **Synthesizer** | ✅ **수렴** — "초기에는 모노레포 + Turborepo, 팀 10명 이상 시 분리 검토" 권고 |
| 최종 | **Scribe** | 논의 과정·근거·최종 권고안을 문서화 |

#### 시나리오 2: "사용자 인증 API를 만들어줘"

> **선택 패턴:** ⚡ Generator & Evaluator

| 단계 | 에이전트 | 수행 내용 |
|------|---------|----------|
| Cycle 1 | **Generator** | JWT 기반 인증 API 초안 생성 |
| | **Evaluator** | 보안 6/10 (토큰 만료 누락) → ❌ Fail |
| | **Refiner** | 토큰 만료 설정, refresh token rotation 추가 |
| Cycle 2 | **Evaluator** | 보안 8/10 (rate limiting 미적용) → ❌ Fail |
| | **Refiner** | express-rate-limit 미들웨어 적용 |
| Cycle 3 | **Evaluator** | 보안 9/10, 코드 품질 9/10 → ✅ Pass |
| 최종 | **Scribe** | Cycle별 개선 이력과 최종 API 명세 문서화 |

#### 시나리오 3: "결제 시스템 통합을 계획하고 실행해줘"

> **선택 패턴:** 📐 Planner & Executor

| 단계 | 에이전트 | 수행 내용 |
|------|---------|----------|
| 계획 | **Planner** | 태스크 분해: ① PG사 SDK 설치 → ② 결제 모델 → ③ API 구현 → ④ 웹훅 → ⑤ 테스트 |
| 실행 | **Executor** | 태스크 ①②③ 순서대로 구현 |
| 검증 | **Validator** | ③ ❌ Revise — "환불 처리 로직 누락" |
| 수정 | **Planner** | 태스크 ③에 환불 엔드포인트 추가 |
| 재실행 | **Executor** | 수정된 ③④⑤ 재구현 → 모든 태스크 ✅ Pass |
| 최종 | **Scribe** | 전체 계획·실행·검증 이력 문서화 |

#### 시나리오 4: "사용자 프로필 API를 설계하고 구현하고 리뷰해줘"

> **선택 패턴:** 🏗️ Code Generation

| 단계 | 에이전트 | 수행 내용 |
|------|---------|----------|
| 설계 | **Architect** | 파일 구조 설계: services/profile.js + routes/profile.js, RESTful 인터페이스 정의, 기존 auth 미들웨어 재사용 |
| 구현 | **Developer** | Architect 설계에 따라 CRUD API 코드 구현 |
| 리뷰 (Cycle 1) | **Reviewer** | ❌ Revise — "입력 검증 누락, SQL Injection 위험" |
| 수정 | **Developer** | express-validator 적용, 파라미터 이스케이핑 추가 |
| 리뷰 (Cycle 2) | **Reviewer** | ✅ Pass — 보안 8/10, 코드 품질 9/10, 설계 준수 10/10 |
| 최종 | **Scribe** | 설계·구현·리뷰 과정과 최종 API 명세 문서화 |

---

## 가드레일 (AGENTS.md)

모든 에이전트는 [`AGENTS.md`](AGENTS.md)에 정의된 Harness Rules를 준수합니다:

- 🔴 **`git push` 절대 금지** — 모든 원격 반영은 `gh pr create --draft`를 통한 PR 기반 워크플로우로 진행
- 코드가 원격 저장소에 반영되기 전 반드시 사람의 검토를 거침

## 라이선스

MIT
