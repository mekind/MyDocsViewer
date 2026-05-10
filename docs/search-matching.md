# Search Matching Strategy

파일명 검색에 쓰는 fuzzy 알고리즘의 정확한 동작과 점수 모델 정리. 외부 라이브러리 없이 ~30줄짜리 로컬 구현으로, 작은 트리(수백~수천 파일)에서 충분한 품질을 내는 것이 목표.

## 정의

> 쿼리 `q`의 모든 글자가 파일명 `n` 안에 **등장 순서를 유지한 채** 나타나면 매칭. 위치 차이는 허용 — 글자 사이에 다른 글자가 있어도 됨.

예:

| 쿼리 | 파일명 | 매칭? | 이유 |
|------|--------|------|------|
| `feat` | `features.md` | ✅ | f-e-a-t 순서대로 0,1,2,3 위치에 등장 |
| `arch` | `architecture.md` | ✅ | a-r-c-h가 0,1,2,3에 |
| `dvh` | `development-history.md` | ✅ | d(0), v(2), h(12) — 흩어져도 순서만 맞으면 OK |
| `fnm` | `feature.md` | ❌ | m이 e보다 먼저 와야 하는데 그 순서로 못 찾음 |

대소문자는 무시 (`name.toLowerCase()` 후 비교).

## 점수 모델

각 매칭마다 base **+1점**으로 시작해 다음 보너스를 더한다.

| 보너스 | 가산점 | 조건 |
|--------|--------|------|
| **연속 매칭** | +8 | 직전 매칭 인덱스의 다음 글자에서 매칭 (`prevMatch + 1 == i`) |
| **단어 경계** | +5 | 직전 글자가 구분자(`/`, `-`, `_`, `.`, 공백) 또는 첫 글자 |
| **첫 글자** | +5 | `i == 0` (단어 경계 보너스와 합쳐짐) |
| **이름 길이 페널티** | −0.05 × len | 짧은 이름이 같은 점수에서 우선 |

쿼리 글자가 모두 소진되지 않으면 (`qi < q.length`) 매칭 실패로 `null` 반환.

### 의도

- **연속 매칭에 +8을 강하게 가산**해서 `feat` 같은 prefix 검색이 흩어진 매칭(`f-e-a-t`이 군데군데)보다 항상 위로 오게 한다.
- **단어 경계 보너스**는 카멜·하이픈·언더스코어·확장자 분리 모두 한 규칙으로 처리. `setup.md`에서 `s` 매칭은 단어 경계 보너스를 받지만, `users.md`의 두 번째 `s`는 못 받는다.
- **길이 페널티**는 작게 (-0.05/글자) 두어 점수 동률이 났을 때만 영향을 준다. 짧은 `setup.md`가 긴 `setup-instructions.md`보다 살짝 위에 노출.

## 의사코드

```js
function fuzzyScore(name, query) {
  const n = name.toLowerCase();
  const q = query.toLowerCase();
  let qi = 0, score = 0, prev = -2;
  const indices = [];

  for (let i = 0; i < n.length && qi < q.length; i++) {
    if (n[i] !== q[qi]) continue;
    let bonus = 1;
    if (i === prev + 1) bonus += 8;
    const before = i > 0 ? n[i - 1] : '';
    if (before === '' || '/-_. '.includes(before)) bonus += 5;
    if (i === 0) bonus += 5;
    score += bonus;
    indices.push(i);
    prev = i;
    qi++;
  }
  if (qi < q.length) return null;
  score -= n.length * 0.05;
  return { score, indices };
}
```

`indices`는 결과 행에서 매칭된 글자에 `<mark>` 태그를 씌우는 데 사용된다.

## 정렬과 컷오프

```js
const out = [];
for (const f of __flatFiles) {
  const r = fuzzyScore(f.name, query);
  if (r) out.push({ ...f, score: r.score, indices: r.indices });
}
out.sort((a, b) => b.score - a.score);
return out.slice(0, 50);
```

- 점수 내림차순.
- 상위 **50개**만 반환 — 큰 결과 셋에서 DOM이 무거워지지 않게.
- 빈 쿼리는 점수 계산을 건너뛰고 `__flatFiles`의 첫 50개를 그대로 보여줌 (검색하지 않은 상태에서 모달을 열었을 때).

## 점수 예시

쿼리 `arch`로 검색했을 때:

| 파일명 | 매칭 인덱스 | 점수 분해 | 합계 |
|--------|------------|-----------|------|
| `architecture.md` | 0,1,2,3 | base 1+(첫글자+단어경계 10)+1+8(연속)+1+8+1+8 = | **38 − 0.75 = 37.25** |
| `search-matching.md` | 8,9,10,11 | (단어경계 5)+1+8+1+8+1+8+1 = | **33 − 0.85 = 32.15** |
| `architecture-old-revision.md` | 0,1,2,3 | 위와 동일하지만 길이가 김 | **38 − 1.40 = 36.60** |

→ 정확히 단어 시작에서 매칭되는 `architecture.md`가 항상 1위. 같은 패턴이라도 길이가 길면 다음 순위.

## 한계

이 알고리즘은 의도적으로 단순하다. 다음은 **하지 않는다**:

- 본문(full-text) 검색 — `/api/file`을 쿼리당 N회 호출해야 해서 단일 파일 stdlib 서버의 비용 모델을 넘어선다.
- 동의어/스테밍 — `auth`로 `authentication`은 fuzzy 매칭으로 잡히지만, `login`은 안 잡힌다.
- 오타 보정 — 글자 순서가 흐트러지면 매칭 실패. (`fetures` → `features.md` 매칭 안 됨.) 짧은 파일명에서 오타가 잘 안 나기 때문에 의도된 트레이드오프.
- 한국어 자모 분해 매칭 — 이번 범위 아님.

## 왜 외부 라이브러리를 안 썼는가

`fuse.js`(클라이언트) 또는 `rapidfuzz`(서버) 같은 옵션이 있지만:

- **단일 파일 원칙** — 새 파일을 만들고 npm/CDN 의존성을 늘리는 비용이 알고리즘 품질 향상보다 크다.
- **인덱스 데이터셋이 작다** — 수백~수천 파일이라 O(N·M) 단순 스캔으로도 입력마다 즉시 응답.
- **점수 모델이 명확** — 향후 가중치(연속 +8, 경계 +5)를 조절할 때 이 문서만 보면 된다.

품질이 부족해지는 시점(예: 파일명이 더 길어지고 토큰화가 필요해질 때)에 fuse.js로 갈아끼우는 것이 옵션 — `searchFiles()` 한 함수만 교체하면 된다.

## 향후 개선 후보

- **최근 사용 가산점**: `localStorage`에 클릭 히스토리를 저장하고, 같은 점수일 때 최근 열린 파일을 위로.
- **폴더 경로 매칭**: 현재 basename만 보지만, 쿼리에 `/`가 포함되면 path 전체를 대상으로 fuzzy 적용 (옵션 토글로).
- **하이라이트 클러스터링**: 인접한 인덱스를 묶어 `<mark>`를 한 번만 띄우는 식으로 마크업 정돈.
- **점수 디버그 모드**: 결과 행에 점수 표시(디버그 토글). 가중치 튜닝할 때만 켜는 용도.
