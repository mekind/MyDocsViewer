# Architecture

MyDocsViewer는 한 개의 파일(`server.py`) 안에 모든 것이 들어 있다. 외부 의존성을 깔지 않아도 `python3 server.py`로 즉시 실행된다는 게 설계의 첫 번째 원칙이다.

## 구성 요소

```
server.py
├── INDEX_HTML        ← 클라이언트 SPA (CSS + JS 인라인)
├── build_tree()      ← 디렉토리 → JSON 트리 변환
├── Handler           ← BaseHTTPRequestHandler 서브클래스
└── main()            ← ThreadingTCPServer 부트스트랩
```

서버는 **두 개의 JSON API + 한 개의 HTML 셸**만 노출한다. 마크다운 → HTML 변환은 모두 브라우저에서 일어난다.

## 엔드포인트

| Path | 응답 | 비고 |
|------|------|------|
| `GET /` | `INDEX_HTML` (라이브 SPA) | `%ROOT%`만 치환 |
| `GET /api/tree` | `{name, type, children[]}` | `MD_ROOT` 하위 재귀 스캔 |
| `GET /api/file?path=` | `text/plain` 원문 | path traversal 가드 후 read |

## 트리 빌드 규칙

`build_tree()`는 다음 규칙으로 노드를 만든다.

- 점(`.`)으로 시작하는 항목 무시 → `.git`, `.DS_Store` 등 자동 숨김
- `.md` / `.markdown` 확장자만 파일 노드로 채택
- 자식이 비어있는 디렉토리는 트리에서 제외 (마크다운 없는 폴더는 안 보임)
- 파일은 `path=` 상대 경로로 식별

> **사이드 효과**: 빈 `docs/` 폴더가 사이드바에 보이지 않는 이유가 이것이다. 파일을 한 개라도 넣어야 표시된다.

## 보안 가드

`/api/file` 핸들러는 두 가지 검사를 통과해야 응답한다.

```python
target = (ROOT / rel).resolve()
if not str(target).startswith(str(ROOT)) or not target.is_file():
    self._send(404, "not found"); return
if target.suffix.lower() not in (".md", ".markdown"):
    self._send(400, "not markdown"); return
```

- `resolve()` 후 `ROOT` 접두 검사 → `..` 기반 path traversal 차단
- 확장자 화이트리스트 → 임의의 시스템 파일 노출 방지

## 동시성

`ThreadingTCPServer`로 떴기 때문에 각 요청이 별 스레드에서 처리된다. 트리 빌드가 큰 폴더에서 무거워도 다른 요청을 막지 않는다.

`allow_reuse_address = True` 덕분에 재시작 시 `TIME_WAIT` 소켓이 남아도 즉시 다시 바인딩 가능.

## 클라이언트 렌더 파이프라인

```
location.hash 변경
   ↓
fetch('/api/file?path=...')
   ↓
marked.parse(text)             ← 마크다운 → HTML
   ↓
content.innerHTML = ...
   ↓
renderMermaid()                ← <div class="mermaid"> → SVG
```

코드 블록 가로채기는 `marked.use({ renderer: { code(...) } })`로 처리한다. `lang === 'mermaid'`이면 `<div class="mermaid">`로 통과시키고, 그 외는 `return false`로 marked의 기본 렌더러에 위임한다.

## 상태 보관

UI 토글(폭/폰트/사이드바 폰트/테마)은 모두 `localStorage`에 저장된다. 서버는 사용자 설정을 모르고, 브라우저가 새로고침될 때마다 setter를 다시 호출한다.

| Key | 값 | 기본 |
|-----|----|----|
| `md-width` | 800/1100/1400/100% | 1100 |
| `md-font` | 14–21 | 17 |
| `md-sidebar-font` | 12–17 | 13 |
| `md-theme` | auto/canvas/parchment/pearl/tile/black | auto |

## 왜 이 구조인가

- **단일 파일**: 학습/이식이 쉽고, 어떤 노트북에 갖다 둬도 `python3` 한 번이면 동작.
- **서버 의존성 0**: 회사 머신에서 pip 설치를 못해도 그대로 사용 가능.
- **클라이언트 사이드 렌더**: 서버에 마크다운 라이브러리를 넣으면 단일 파일이 아니게 되고, 캐시 무효화도 복잡해진다. 원문을 그대로 보내고 브라우저에 맡긴다.
- **CDN 사용**: marked / mermaid는 다운받아 번들링하는 대신 CDN에서 ES 모듈로 로드. 오프라인 환경에서는 동작하지 않는 대가로 페이지가 짧다.
