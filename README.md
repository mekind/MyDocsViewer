# MyDocsViewer

로컬 마크다운 트리를 Apple 디자인 시스템으로 보여주는 **단일 파일 Python 뷰어**.

```bash
MD_ROOT=/path/to/docs python3 server.py
# → http://127.0.0.1:8765
```

서버 측 의존성 0개 (Python 표준 라이브러리만), 클라이언트는 CDN의 `marked` + `mermaid`를 사용합니다.

## 핵심 기능

- 임의 디렉토리(`MD_ROOT`)의 `.md` / `.markdown`을 트리로 탐색
- Mermaid 다이어그램 렌더
- 본문 폭 / 본문 글꼴 크기 / 사이드바 글꼴 크기 / 테마(배경) / 새로고침 토글 — 모두 `localStorage`에 저장
- Apple 디자인 토큰 기반 UI (Action Blue 단일 액센트, SF Pro Display/Text, pill 버튼, 단일 product-shadow)
- 사이드바: 셰브론 + 폴더(열림/닫힘) + 파일 SVG 아이콘, 기본 접힘 상태

## 어떻게 만들어졌는가

1. **단일 파일 stdlib 서버** — `http.server.BaseHTTPRequestHandler` + `socketserver.ThreadingTCPServer`로 `/`, `/api/tree`, `/api/file` 세 엔드포인트만 제공.
2. **클라이언트 사이드 렌더** — 서버는 마크다운 원문을 그대로 보내고, 브라우저에서 `marked`가 HTML로, `mermaid`가 코드 블록을 SVG로 변환.
3. **Apple 디자인 적용** — `awesome-design-md/design-md/apple/DESIGN.md`의 토큰(컬러, 타이포, 라운딩, 스페이싱)을 CSS 변수로 옮김.
4. **테마 시스템** — `:root[data-theme="..."]` 선택자로 5종 + Auto 전환, `color-mix()`로 툴바 프로스티드 글래스를 테마 추종 처리.
5. **점진적 개선** — 폰트 크기 → 새로고침 → 사이드바 폰트 → 배경 테마 → 사이드바 아이콘 → 기본 접힘 순으로 한 단계씩 추가.

세부 문서는 [`docs/`](./docs)에 있습니다.

## 문서

- [`docs/architecture.md`](./docs/architecture.md) — 서버 구조, 요청 흐름, 보안 가드
- [`docs/design-system.md`](./docs/design-system.md) — Apple 토큰 매핑 (컬러/타입/컴포넌트)
- [`docs/features.md`](./docs/features.md) — 툴바 컨트롤과 키 동작
- [`docs/development-history.md`](./docs/development-history.md) — 빌드된 순서와 결정 기록
