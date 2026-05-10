# Plan: Filename Search

## Goal

Find a markdown file by its filename without expanding the sidebar tree.

## Decisions (locked)

| # | 결정 |
|---|------|
| 1 | **UI**: ⌘K/Ctrl+K 모달 + 사이드바 상단 input — 두 입구가 같은 모달을 같은 방식으로 연다. 사이드바 input에 포커스하면 모달이 뜨고, 입력값이 모달 input으로 그대로 전달됨. |
| 2 | **매칭**: Fuzzy (글자 순서만 맞으면 매칭, 연속/단어 경계 가산점) |
| 3 | **범위**: 파일명(basename)만. 폴더 경로는 결과에 부가 정보로만 표시 |
| 4 | **결과 표시**: 별도 모달 결과 리스트. 사이드바 트리는 변경 없음 |
| 5 | **결과 클릭**: 기존 트리 클릭과 동일 (`location.hash` 변경) |
| 6 | **인덱싱**: 클라이언트 (`/api/tree` 결과를 평면화). 서버 API 추가 없음 |

## Open questions

These are the design choices that shape the implementation. Please pick one per row before I start coding.

| # | Question | Options |
|---|----------|---------|
| 1 | **UI 위치** | (a) 사이드바 상단 항상 표시 검색 input · (b) ⌘K 단축키로 뜨는 모달 팔레트 · (c) 툴바에 input 추가 |
| 2 | **검색 범위** | (a) 파일명만 (basename) · (b) 상대경로 전체 (예: `docs/features.md`) |
| 3 | **매칭 방식** | (a) 단순 substring (대소문자 무시) · (b) fuzzy (예: `feat` → `features.md`, 글자 순서만 맞으면 매칭) |
| 4 | **결과 표시** | (a) 트리를 필터링 (매칭된 파일만 보이고 부모 폴더 자동 펼침) · (b) 별도 결과 리스트(트리는 그대로 두고 검색 결과만 띄움) |
| 5 | **결과 클릭 동작** | (a) 기존 트리 클릭과 동일(`location.hash` 변경) · (b) 새 탭 |
| 6 | **인덱싱 위치** | (a) 클라이언트(현재 `/api/tree`를 이미 받으므로 추가 API 불필요) · (b) 서버에 `/api/search?q=` 신설 |

## My recommendation (변경 가능)

> **1-b · 2-a · 3-b · 4-b · 5-a · 6-a**
>
> ⌘K로 뜨는 모달 팔레트 + 파일명 fuzzy 검색 + 별도 결과 리스트 + 클라이언트 인덱싱.
>
> 이유:
> - **⌘K 모달**: Apple의 Spotlight·Linear·Raycast가 익숙한 패턴. 사이드바를 건드리지 않아 트리의 접힘 상태가 유지됨.
> - **fuzzy 매칭**: 짧은 파일명(README.md, features.md, design-system.md…)에서 substring보다 회수율이 좋고 오타에 관대.
> - **별도 결과 리스트**: 트리를 펼쳤다 닫았다 하지 않아 시각적 노이즈가 적음.
> - **클라이언트 인덱싱**: 트리 데이터를 이미 받기 때문에 서버 변경 없이 끝남. 단일 파일 원칙 유지.

## Sketch (recommendation 기준)

### UI

```
┌──────────────────────────────────────────────┐
│  ⌘K 누르면 등장                             │
│                                              │
│   ╔════════════════════════════════════════╗ │
│   ║  🔍  feat                              ║ │
│   ╠════════════════════════════════════════╣ │
│   ║  📄 features.md       docs/            ║ │
│   ║  📄 readme.md         (root)           ║ │
│   ║  📄 design-system.md  docs/            ║ │
│   ╚════════════════════════════════════════╝ │
│                                              │
│  Esc 닫기 · ↑↓ 이동 · Enter 열기            │
└──────────────────────────────────────────────┘
```

- Apple 토큰: 모달 배경 `--canvas`, 1px hairline, 18px radius (`rounded.lg`),
  `backdrop-filter: blur(20px) saturate(180%)`,
  배경 오버레이 `rgba(0,0,0,0.4)`.
- 모달 폭 600px, 화면 상단에서 ~120px 떨어진 위치 (Spotlight 스타일).
- 결과 항목: 파일 SVG 아이콘 + 파일명(매칭된 글자 highlight) + 회색 폴더 경로.

### 데이터 흐름

```
loadTree()                  // 기존
  └─ flat = flatten(tree)   // 신규: 파일 노드만 평면 배열로 모음 [{name, path}]

⌘K 누름 → input focus
입력 → fuzzyFilter(flat, query) → 결과 리스트 갱신 (최대 50개)
↑↓ → 활성 인덱스 이동
Enter → location.hash = encodeURIComponent(activeItem.path); 모달 닫기
Esc / 바깥 클릭 → 모달 닫기
```

### Fuzzy 알고리즘 (단순 버전)

VS Code/Sublime에서 쓰는 가벼운 점수 매기기:

- 쿼리 글자가 파일명에 등장 순서대로 모두 포함되면 매칭
- 점수: 연속 매칭 가산(+10), 단어 경계 매칭 가산(+5), 위치 가까움 가산(-i)
- 결과는 점수 내림차순 정렬, 상위 50개만 표시

코드는 ~30줄짜리 `fuzzyScore(name, query)` 함수면 충분. 외부 라이브러리 도입 안 함.

### 키보드

| 키 | 동작 |
|----|------|
| ⌘K / Ctrl+K | 모달 열기, input 포커스 |
| Esc | 모달 닫기 |
| ↑ / ↓ | 결과 항목 이동 |
| Enter | 활성 항목 열기, 모달 닫기 |
| 바깥 클릭 | 모달 닫기 |

### 비-목표

- 본문 내용(full-text) 검색은 이번 범위 아님.
- 검색 기록 저장 / 자동 완성 사전 안 함.
- 정규식 입력 안 함.

## 작업 단위 (recommendation 기준)

1. `flattenTree(node)` 헬퍼 — 파일 노드만 `[{name, path}]`로 평면화.
2. `fuzzyScore(name, query)` 함수.
3. 모달 마크업 + CSS (Apple 토큰만 사용).
4. ⌘K / Ctrl+K 핸들러, 결과 렌더링, 키보드 내비게이션.
5. README/`features.md`에 단축키와 동작 추가.

규모: server.py 한 파일 안에 100~150줄 추가. 신규 파일 없음.

## 결정 후 진행 순서

1. 위 6개 질문에 답을 주시면,
2. 그 결정을 이 문서 상단에 "Decisions" 섹션으로 고정시키고,
3. 코드를 한 번에 적용한 뒤 `features.md`/README 업데이트.
