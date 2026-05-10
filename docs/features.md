# Features

## 툴바 컨트롤

상단 sticky 툴바에는 네 개의 그룹과 하나의 액션 버튼이 있다. 모든 토글은 `localStorage`에 저장되므로 다음 방문에도 유지된다.

### Width — 본문 폭

| 버튼 | `--content-width` |
|------|-------------------|
| 800  | 800px |
| 1100 | 1100px (기본) |
| 1400 | 1400px |
| Full | 100% |

`max-width: var(--content-width)` 속성을 본문 컨테이너에 걸어두기 때문에 콘텐츠는 가운데 정렬된 채로 폭만 변한다.

### Body — 본문 글꼴 크기

14 / 15 / 17 / 19 / 21 px. 기본 17px (Apple body 토큰).

`--content-font` 변수만 바꾸므로 라인하이트(1.47)와 letter-spacing(-0.022em)은 그대로 유지된다.

### Sidebar — 사이드바 글꼴 크기

12 / 13 / 15 / 17 px. 기본 13px.

`#sidebar { font-size: var(--sidebar-font); }` 단일 지점에서 사이드바 전체가 비례 확대된다. `h3` 헤딩은 `calc(var(--sidebar-font) + 2px)`로 약간 더 크게 잡힌다.

### Theme — 배경 (Apple 토큰 기반)

| 라벨 | 색 | 액센트 |
|------|-----|--------|
| Auto | 시스템 prefers-color-scheme 따름 | 자동 |
| Canvas | `#ffffff` | Action Blue |
| Parchment | `#f5f5f7` | Action Blue |
| Pearl | `#fafafc` | Action Blue |
| Tile | `#272729` | Sky Link Blue |
| Black | `#000000` | Sky Link Blue |

선택 시 `<html>`에 `data-theme="canvas|parchment|pearl|tile|black"`이 붙고, Auto는 속성 자체가 제거된다(시스템 미디어쿼리에 위임).

### ↻ Refresh

파일 트리를 다시 가져온다. 워크플로:

1. `/api/tree` 재호출 → 사이드바 다시 렌더
2. 현재 `location.hash`가 있으면 `/api/file`도 다시 호출 → 콘텐츠 갱신
3. 800ms 동안 버튼이 `✓ Refreshed` / `✗ Failed`로 피드백 후 원상복귀

새 마크다운 파일을 추가했거나 기존 파일을 외부 에디터로 수정했을 때 새로고침 없이 반영하는 용도.

## 사이드바

### 트리 동작

- **기본 상태: 모든 디렉토리 접힘.** 클릭(또는 셰브론)으로 펼친다.
- 디렉토리 라벨 클릭 시 `li.classList.toggle('open')` — 자식 컨테이너 `display`만 전환.
- 파일 클릭 시 `location.hash = encodeURIComponent(path)` → `hashchange` 이벤트가 `loadFile()` 트리거.
- 활성 파일은 Action Blue 배경 + 흰 텍스트.

### 아이콘 (인라인 SVG)

| 항목 | 아이콘 | 색 |
|------|--------|----|
| 디렉토리 셰브론 | `›` (열림 시 90° rotate) | `--muted` |
| 디렉토리 (닫힘) | filled folder | `--accent` |
| 디렉토리 (열림) | outlined folder | `--accent` |
| 파일 | document outline | `--muted` (활성 시 흰색) |

모두 `currentColor`로 그려지기 때문에 테마가 바뀌면 색도 따라간다.

## 콘텐츠 렌더

- **마크다운**: marked v12, GitHub Flavored 스타일.
- **Mermaid**: ` ```mermaid ` 코드 블록을 인터셉트해 SVG로 변환. 다이어그램 테마는 시스템 다크/라이트 따라 `default` ↔ `dark` 자동 선택 (페이지 로드 시 한 번 결정).
- **이미지**: `border-radius: 18px` + 시그니처 product shadow 자동 적용.
- **표**: hairline 1px 구분선, 헤더는 parchment 배경.
- **코드 인라인**: `--divider-soft` 배경 + 5px radius. 코드 블록은 11px radius + 1px hairline.

## URL & 단축

- 파일을 선택하면 URL이 `…/#<상대경로>` 형태가 된다 → 새 탭에 그대로 붙여넣어 공유 가능.
- 단축키는 정의되어 있지 않다. 모든 인터랙션은 클릭 + `localStorage`로 단순화.

## 알려진 제약

- 기본 포트 8765 고정 (`PORT` 상수 수정 필요).
- 외부 CDN(jsDelivr) 의존 — 오프라인에서는 marked / mermaid가 로드되지 않는다.
- 트리는 매 `/api/tree` 호출마다 풀 스캔. 매우 큰 트리(수만 파일)에서는 느릴 수 있다.
- 파일 변경 감지(watch)는 없음 — 새 파일을 보려면 ↻ Refresh를 눌러야 한다.
