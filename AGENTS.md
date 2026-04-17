# AGENTS.md — Agent Harness

> 모든 에이전트가 반드시 준수해야 하는 제약 조건 및 가드레일.
> 모든 에이전트는 역할(Role)에 관계없이 이 문서의 규칙을 따라야 한다.

---

## 적용 범위

- **대상:** **모든** 에이전트 (Developer, Architect, Reviewer 등 역할 무관)
- **시점:** 에이전트가 Git 명령어 또는 외부 시스템 호출을 실행하기 **전에** 이 문서를 참조해야 한다
- **우선순위:** 개별 에이전트 Charter와 이 Harness가 충돌할 경우, **Harness가 우선**한다

---

## Harness Rules

### Rule 1: `git push` 절대 금지

| 항목 | 내용 |
|------|------|
| **상태** | 🔴 절대 금지 (Absolute Prohibition) |

#### 금지 명령어 (Prohibited Commands)

다음 명령어 및 그 모든 변형은 **절대 실행해서는 안 된다**:

```
git push
git push origin
git push origin main
git push origin <any-branch>
git push --force
git push --force-with-lease
git push -f
git push -u origin <branch>
git push --set-upstream origin <branch>
git push --tags
git push --all
git push <any-remote> <any-refspec>
```

`git push`로 시작하는 **모든 형태의 명령어**가 금지 대상이다. 예외는 없다.

#### 이유 (Rationale)

1. **Human Review 보장**: 코드가 원격 저장소에 반영되기 전에 반드시 사람의 검토를 거쳐야 한다
2. **Protected Branch 보호**: `main`, `develop` 등 보호된 브랜치에 에이전트가 직접 push하는 사고를 원천 차단한다
3. **감사 추적 (Audit Trail)**: 모든 원격 반영은 PR을 통해 이루어져야 변경 이력과 승인 기록이 남는다
4. **되돌림 용이성**: PR 기반 워크플로우는 revert가 명확하고 안전하다

#### 대안 (Alternative)

에이전트가 변경 사항을 원격에 반영해야 할 때는 다음 절차를 따른다:

1. **로컬 커밋**: `git add` → `git commit`으로 변경 사항을 로컬에 기록한다
2. **PR 생성**: `gh pr create --draft` 명령으로 Draft PR을 생성한다
3. **사용자 알림**: "Push가 필요합니다"라고 사용자에게 명확히 알린다

```bash
# ✅ 허용되는 워크플로우
git checkout -b feat/my-change
git add .
git commit -m "feat: describe the change in English"
gh pr create --draft --base main --title "PR title in English" --body "PR description in English"

# ❌ 절대 금지
git push origin feat/my-change
```

#### 집행 (Enforcement)

- 에이전트는 `git` 명령어를 실행하기 전에 이 Harness를 확인해야 한다
- `git push`가 포함된 명령어를 생성하거나 실행하려는 시도 자체가 위반이다
- Shell script, alias, subprocess 등 우회 수단을 통한 push도 금지된다

---

### Rule 2: 커밋 메시지는 영문으로 작성

| 항목 | 내용 |
|------|------|
| **상태** | 🟢 필수 (Mandatory) |

#### 규칙

- 모든 `git commit` 메시지(제목·본문 모두)는 **영문(English)으로 작성**한다.
- [Conventional Commits](https://www.conventionalcommits.org/) 스타일(`feat:`, `fix:`, `docs:`, `chore:`, `refactor:`, `test:` 등)을 권장한다.
- 명령형 현재 시제(imperative mood)로 작성한다. 예: `Add`, `Fix`, `Update` (not `Added`, `Fixed`).
- PR 제목과 본문도 영문으로 작성한다.

#### 예시

```bash
# ✅ 올바른 예시
git commit -m "feat: add orchestrator routing table for new pattern"
git commit -m "fix: prevent infinite loop in debate-critic convergence check"
git commit -m "docs: update README with renamed repository URL"

# ❌ 잘못된 예시
git commit -m "오케스트레이터 라우팅 추가"
git commit -m "버그 수정"
```

#### 이유

- **일관성**: 오픈소스 생태계 표준과 정렬하여 외부 기여자 친화적 환경을 유지한다.
- **도구 호환성**: Changelog 생성기, semantic-release 등 자동화 도구가 영문 Conventional Commits를 전제로 한다.
- **검색성**: `git log --grep` 및 GitHub 검색에서 균일한 결과를 보장한다.

---

### Rule 3: PR은 항상 `main` 브랜치를 대상으로 생성

| 항목 | 내용 |
|------|------|
| **상태** | 🟢 필수 (Mandatory) |

#### 규칙

- 모든 PR은 **`main` 브랜치를 base로 생성**한다.
- `gh pr create` 실행 시 `--base main`을 **명시적으로 지정**한다 (기본 브랜치가 변경되어도 의도가 명확히 남도록).
- PR은 기본적으로 **Draft(`--draft`)로 생성**하여 사람의 리뷰·승인을 전제로 한다.

#### 예시

```bash
# ✅ 올바른 예시
gh pr create --draft --base main \
  --title "feat: add new agent pattern" \
  --body "Summary of the change in English."

# ❌ 잘못된 예시 (base 생략 / 다른 브랜치 대상)
gh pr create --title "변경"
gh pr create --base develop --title "feat: ..."
```

#### 이유

- **단일 통합 지점**: `main`을 유일한 통합 브랜치로 유지하여 릴리스 흐름을 단순화한다.
- **명시성**: `--base main`을 항상 지정하여 에이전트의 의도를 감사 로그에 명확히 기록한다.

---

### Rule 4: _(예약됨 — 향후 규칙 추가 시 이 형식을 따른다)_

> 새로운 Harness Rule을 추가할 때는 위 규칙들의 구조(규칙, 예시, 이유, 집행)를 동일하게 적용한다.

---

## 위반 시 처리

| 단계 | 조치 |
|------|------|
| **감지** | 에이전트 출력 로그에서 금지 명령어 실행 여부를 확인한다 |
| **즉시 중단** | 위반이 감지되면 해당 에이전트의 작업을 즉시 중단한다 |
| **보고** | 위반 내용을 사용자에게 알린다 |
| **복구** | 필요 시 `git reset`, `git revert` 등으로 원격 상태를 복구한다 |
