# Development History

MyDocsViewer는 한 번에 큰 그림을 그리고 만든 게 아니라, **요청 한 줄 → 적용 → 다음 요청** 식으로 누적된 결과물이다. 이 문서는 각 단계에서 어떤 결정이 있었고 왜 그렇게 했는지를 기록한다.

## 0. 시작점

`server.py` 한 파일짜리 단순 마크다운 뷰어. 트리 + 콘텐츠 영역 + 폭 토글(Width 800/1100/1400/Full)만 있었다. CDN의 marked + mermaid를 사용. 외부 의존성 없이 `python3 server.py`로 즉시 동작.

## 1. 폰트 크기 토글 + 새 파일 새로고침

요청: "폰트 크기를 설정할 수 있게, 그리고 새로 추가된 파일을 리프레쉬할 수 있게."

- 본문 폰트: `--content-font` 변수 추가, 13/14/16/18/20/22 버튼 그룹.
- 새로고침: `loadTree()`가 트리를 비우고 다시 렌더하도록 수정. `↻ Refresh` 버튼은 트리 + 현재 파일을 같이 갱신.
- 토글 상태는 `localStorage` 저장 (이후 모든 토글에 동일 패턴).

## 2. 빈 디렉토리 의문

요청: "왜 docs가 안 보이지?"

진단: `build_tree()`가 자식이 없는 디렉토리를 누락한다. `find ... -name "*.md"`로 확인 결과 `docs/`, `docs-manager/`는 마크다운이 0개라 정상적으로 숨김 처리된 것. 사용자에게 빈 폴더를 보이게 할지 묻고, 본인 의도가 다른 곳이었음을 확인.

→ 코드 변경 없음. 동작이 의도대로라는 것을 확인하는 단계였다.

## 3. 파서 루트 변경

요청: "진행해" (상위 폴더를 루트로 띄우기)

`MD_ROOT=/Users/kds/WorkSpace/claude-code python3 server.py`로 재시작. 사이드바에 형제 프로젝트들(awesome-design-md, learning-stack 등)이 모두 보이도록.

## 4. Apple 디자인 시스템 도입 + 사이드바 폰트 크기

요청: "사이드바 폰트도 키울 수 있게 + `awesome-design-md/`의 Apple 디자인을 적용."

가장 큰 변화. `awesome-design-md/design-md/apple/DESIGN.md`의 토큰을 한 번에 다 들이부었다.

- **컬러**: Action Blue `#0066cc` 단일 액센트, ink `#1d1d1f`, parchment `#f5f5f7`. 다크 모드는 tile-1 `#272729` + Sky Link Blue `#2997ff`.
- **타이포**: SF Pro Display(헤딩) + SF Pro Text(본문), letter-spacing -0.022em ("Apple tight"). 본문 17px / line-height 1.47.
- **버튼**: pill (`border-radius: 9999px`), `transform: scale(0.95)` press 상태.
- **툴바**: 상단 sticky + `backdrop-filter: blur(20px) saturate(180%)` 프로스티드 글래스.
- **그림자**: 본문 이미지에만 시그니처 product-shadow `rgba(0,0,0,0.22) 3px 5px 30px`.
- **사이드바 폰트**: `--sidebar-font` 변수, 12/13/15/17 토글 추가.

이 단계에서 Width / Body / Sidebar 세 개의 폰트·폭 그룹이 갖춰졌다.

## 5. 배경 테마 토글

요청: "배경색도 Apple 디자인에 맞게 변경할 수 있게."

`:root[data-theme="..."]` 선택자로 5종 + Auto 테마를 정의. Apple 가이드의 `canvas / parchment / pearl / tile / black` surface 토큰을 그대로 옮겼다.

핵심 디자인 결정:

- **Auto 모드 보존**: `data-theme` 속성을 제거하면 미디어쿼리가 동작. `:root:not([data-theme]) { ... }`로 Auto와 명시 모드를 깨끗하게 분리.
- **툴바 배경 = 테마 추종**: 하드코딩된 `rgba(255, 255, 255, 0.8)`를 `color-mix(in srgb, var(--content-bg) 80%, transparent)`로 대체해 모든 테마에서 자동으로 어울리게 함.
- **다크 surface에서 자동 액센트 변환**: `tile`, `black` 테마는 `--accent`를 Sky Link Blue로 덮어써서 가독성 보장 (Apple의 "Action Blue는 다크 타일에서 사라진다" 규칙).

## 6. 사이드바 SVG 아이콘

요청: "사이드바에 아이콘도 추가."

이모지(📄)는 OS별로 모양이 달라지고 단색 컨트롤이 안 되므로, **인라인 SVG 4종**으로 교체:

- 셰브론(› 90° 회전)
- 폴더 닫힘 (filled)
- 폴더 열림 (outlined)
- 파일 (document outline)

`fill: currentColor` / `stroke: currentColor`만 사용해서 테마/활성 상태에 따라 색이 자연스럽게 따라가게 함. CSS만으로 펼침/접힘 상태에 따라 두 폴더 SVG 중 하나만 보이도록 토글.

## 7. 기본 접힘

요청: "기본 상태를 접혀 있게."

`renderNode(node, isRoot)`에서 `isRoot ? ' open' : ''` 분기를 제거. 모든 디렉토리가 처음에 접힌 상태로 렌더되어 큰 트리에서도 시야가 깔끔해짐.

## 8. 리네이밍 & 문서화

요청: "MyDocsViewer로 이름 변경, README + docs/ 작성."

폴더 `md-viewer/` → `MyDocsViewer/`. `<title>`과 콘솔 banner를 새 이름으로 갱신. README는 한 화면짜리 인덱스로 두고, 자세한 내용은 이 `docs/` 디렉토리(architecture / design-system / features / development-history) 4편으로 분리.

## 회고: 적용된 패턴

| 패턴 | 어디서 |
|------|--------|
| **단일 파일 + 인라인 HTML/CSS/JS** | 0~8 모든 단계 — 파일을 안 늘리는 게 우선순위 |
| **CSS 변수만 토글** | 폭/폰트/사이드바 폰트/테마 전부 동일한 메커니즘 |
| **`localStorage` 영속화** | 모든 사용자 토글 |
| **Apple 토큰 직역** | 색·타입·라운딩·스페이싱은 임의로 만들지 않고 가이드에 있는 값만 사용 |
| **점진적 추가** | 매 요청마다 한 가지 기능. 큰 리팩토링 없음 |

## 회고: 안 한 결정들 (의도)

- **빌드 파이프라인 도입 안 함**. Astro/Vite를 쓰는 자매 프로젝트 `learning-stack`이 옆에 있지만, 이 도구는 "아무 머신에 갖다 두면 그냥 도는 것"을 우선시.
- **파일 watcher 안 넣음**. inotify/fswatch는 OS별 구현이 갈리고, 단일 파일 원칙을 깨뜨린다. 대신 명시적 ↻ Refresh 버튼.
- **검색 안 넣음**. `learning-stack`이 Fuse.js 검색을 갖고 있고, MyDocsViewer는 그것의 대체가 아니라 "임시 폴더를 즉석에서 보는 도구" 역할.
- **CSS 프레임워크 안 씀**. Apple 토큰을 가져오는 데 Tailwind나 디자인 시스템 패키지가 끼어들 이유가 없다.
