# Design System (Apple)

UI는 [`awesome-design-md/design-md/apple/DESIGN.md`](../../awesome-design-md/design-md/apple/DESIGN.md)의 토큰을 그대로 CSS 변수로 옮긴 것이다. 정확한 출처와 의도(왜 17px 본문인지, 왜 weight 500이 없는지)는 그 문서를 참고.

## CSS 변수 매핑

```css
:root {
  /* Brand & Accent */
  --action-blue:        #0066cc;   /* primary */
  --action-blue-focus:  #0071e3;
  --sky-link:           #2997ff;   /* dark surfaces only */

  /* Ink */
  --ink:                #1d1d1f;
  --ink-muted-80:       #333333;
  --ink-muted-48:       #7a7a7a;

  /* Surface */
  --canvas:             #ffffff;
  --parchment:          #f5f5f7;
  --pearl:              #fafafc;

  /* Hairlines */
  --hairline:           #e0e0e0;
  --divider-soft:       #f0f0f0;

  /* Variable */
  --content-font:       17px;
  --sidebar-font:       13px;
  --content-width:      1100px;
}
```

## 테마 (data-theme)

라이트/다크 자동 전환 외에 다섯 개의 명시적 테마를 `:root[data-theme="..."]`로 제공한다. 토글이 변수만 갈아끼우면 모든 영역이 동시에 반응하도록 설계.

| `data-theme` | 콘텐츠 배경 | 사이드바 배경 | 액센트 | 출처 토큰 |
|---|---|---|---|---|
| (없음, 시스템 라이트) | `#ffffff` | `#f5f5f7` | Action Blue | `canvas` / `parchment` |
| (없음, 시스템 다크) | `#1d1d1f` | `#1d1d1f` | Sky Link Blue | `ink` |
| `canvas` | `#ffffff` | `#f5f5f7` | Action Blue | `canvas` |
| `parchment` | `#f5f5f7` | `#ececef` | Action Blue | `canvas-parchment` |
| `pearl` | `#fafafc` | `#f0f0f3` | Action Blue | `surface-pearl` |
| `tile` | `#272729` | `#1d1d1f` | Sky Link Blue | `surface-tile-1` |
| `black` | `#000000` | `#0a0a0a` | Sky Link Blue | `surface-black` |

다크 surface로 갈수록 `--accent`가 자동으로 `Sky Link Blue (#2997ff)`로 바뀌는데, Apple 가이드의 "Action Blue는 다크 타일에서 사라지므로 Sky Link Blue를 쓴다" 규칙을 따른 것이다.

## 타이포그래피

| 위치 | 폰트 | 사이즈 | weight | tracking |
|---|---|---|---|---|
| 본문 | SF Pro Text | 17px (가변) | 400 | -0.022em |
| 헤딩 | SF Pro Display | 1.1–2.4em | 600 | -0.024 ~ -0.028em |
| 사이드바 | SF Pro Text | 13px (가변) | 400/500 | -0.01em |
| 툴바 라벨/버튼 | SF Pro Text | 12px | 400 | -0.01em |
| 코드 | SF Mono | 0.88em | 400 | 0 |

`-apple-system, BlinkMacSystemFont, "Segoe UI"` 스택으로 macOS/iOS에서는 진짜 SF Pro가 잡히고, 다른 플랫폼에서는 시스템 폰트로 fallback 된다.

## 컴포넌트 ↔ Apple 토큰

| MyDocsViewer | 매핑된 Apple 컴포넌트 |
|---|---|
| 툴바 (sticky, blur 80%) | `floating-sticky-bar` + `sub-nav-frosted` |
| 툴바 버튼 (pill) | `button-secondary-pill` 변형 — 작은 사이즈 |
| 툴바 active 버튼 | `button-primary` (Action Blue 채움) |
| 사이드바 영역 | `footer` 톤(parchment) + `dense-link` 그리드 느낌 |
| 활성 파일 항목 | `button-primary` 배경 + 흰 텍스트 |
| 본문 이미지 | 시그니처 product shadow `rgba(0,0,0,0.22) 3px 5px 30px` |
| 코드 블록 | parchment 배경 + 1px hairline + `rounded.md` (11px) |
| 표 헤더 | parchment 배경, hairline 구분선 |
| 인용 | 좌측 3px solid `--accent` |

## 모양 (Border Radius)

| 토큰 | 값 | MyDocsViewer 사용처 |
|---|---|---|
| `none` | 0 | 사이드바 / 콘텐츠 분리 |
| `sm` | 6–8px | 사이드바 항목 hover 박스 |
| `md` | 11px | 코드 블록 |
| `lg` | 18px | 본문 이미지 |
| `pill` | 9999px | **모든 버튼** — Apple 시그니처 |

## 마이크로 인터랙션

```css
#toolbar button:active { transform: scale(0.95); }
```

Apple 가이드의 "press 상태는 색이 아니라 `scale(0.95)`로 표현한다"를 그대로 적용. hover는 의도적으로 무겁게 두지 않는다 (Apple 가이드: "Never document hover").

## 디테일

- **표면 색 변경 = 섹션 분리**. 보더나 그림자로 분리하지 않고 색만 바꾼다. 사이드바 ↔ 본문도 1px hairline + 미세한 톤 차이로만 구분.
- **그림자는 단 한 곳**. UI 칩에는 그림자를 쓰지 않고, 본문 `<img>`에만 product shadow를 넣어 사진이 표면 위에 놓인 것처럼 보이게 한다.
- **그라디언트 0개**. 분위기는 사진(있을 경우)이 만들고, CSS 그라디언트는 토큰에서 제거되어 있다.
- **frosted glass**: `backdrop-filter: saturate(180%) blur(20px)` + `color-mix(in srgb, var(--content-bg) 80%, transparent)`. 테마가 바뀌면 툴바 배경도 자동으로 따라간다.
