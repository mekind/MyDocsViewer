#!/usr/bin/env python3
import http.server
import socketserver
import urllib.parse
import json
import os
from pathlib import Path

PORT = 8765
ROOT = Path(os.environ.get("MD_ROOT", ".")).resolve()

INDEX_HTML = """<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<title>MyDocsViewer — %ROOT%</title>
<style>
  :root {
    --action-blue: #0066cc;
    --action-blue-focus: #0071e3;
    --sky-link: #2997ff;
    --ink: #1d1d1f;
    --ink-muted-80: #333333;
    --ink-muted-48: #7a7a7a;
    --hairline: #e0e0e0;
    --divider-soft: #f0f0f0;
    --canvas: #ffffff;
    --parchment: #f5f5f7;
    --pearl: #fafafc;
    --sidebar-bg: var(--parchment);
    --content-bg: var(--canvas);
    --fg: var(--ink);
    --muted: var(--ink-muted-48);
    --accent: var(--action-blue);
    --tile-dark: #272729;
    --content-font: 17px;
    --sidebar-font: 13px;
    --content-width: 1100px;
  }
  @media (prefers-color-scheme: dark) {
    :root:not([data-theme]) {
      --sidebar-bg: #1d1d1f;
      --content-bg: #1d1d1f;
      --fg: #f5f5f7;
      --muted: #86868b;
      --accent: var(--sky-link);
      --hairline: #333336;
      --divider-soft: #2a2a2c;
      --pearl: #2a2a2c;
      --parchment: #272729;
    }
  }
  :root[data-theme="canvas"] {
    --sidebar-bg: var(--parchment);
    --content-bg: var(--canvas);
    --fg: var(--ink);
    --muted: var(--ink-muted-48);
    --accent: var(--action-blue);
    --hairline: #e0e0e0;
    --divider-soft: #f0f0f0;
  }
  :root[data-theme="parchment"] {
    --sidebar-bg: #ececef;
    --content-bg: #f5f5f7;
    --fg: var(--ink);
    --muted: var(--ink-muted-48);
    --accent: var(--action-blue);
    --hairline: #e0e0e0;
    --divider-soft: #ebebee;
    --parchment: #ececef;
  }
  :root[data-theme="pearl"] {
    --sidebar-bg: #f0f0f3;
    --content-bg: #fafafc;
    --fg: var(--ink);
    --muted: var(--ink-muted-48);
    --accent: var(--action-blue);
    --hairline: #e0e0e0;
    --divider-soft: #ebebee;
    --parchment: #f0f0f3;
  }
  :root[data-theme="tile"] {
    --sidebar-bg: #1d1d1f;
    --content-bg: #272729;
    --fg: #f5f5f7;
    --muted: #86868b;
    --accent: var(--sky-link);
    --hairline: #333336;
    --divider-soft: #2a2a2c;
    --pearl: #2a2a2c;
    --parchment: #2a2a2c;
  }
  :root[data-theme="black"] {
    --sidebar-bg: #0a0a0a;
    --content-bg: #000000;
    --fg: #f5f5f7;
    --muted: #86868b;
    --accent: var(--sky-link);
    --hairline: #2a2a2c;
    --divider-soft: #1a1a1c;
    --pearl: #1a1a1c;
    --parchment: #1a1a1c;
  }
  * { box-sizing: border-box; }
  html, body {
    margin: 0;
    font-family: "SF Pro Text", system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    background: var(--content-bg);
    color: var(--fg);
    -webkit-font-smoothing: antialiased;
    text-rendering: optimizeLegibility;
  }
  body { display: flex; height: 100vh; }

  /* Sidebar */
  #sidebar {
    width: 300px;
    flex-shrink: 0;
    border-right: 1px solid var(--hairline);
    background: var(--sidebar-bg);
    overflow: auto;
    padding: 24px 16px;
    font-size: var(--sidebar-font);
    letter-spacing: -0.01em;
  }
  #sidebar h3 {
    margin: 0 0 16px;
    font-family: "SF Pro Display", system-ui, sans-serif;
    font-size: calc(var(--sidebar-font) + 2px);
    font-weight: 600;
    color: var(--fg);
    letter-spacing: -0.02em;
    text-transform: none;
  }
  .tree ul { list-style: none; padding-left: 14px; margin: 2px 0; }
  .tree > ul { padding-left: 0; }
  .tree li { margin: 1px 0; }
  .tree .dir > .label {
    cursor: pointer;
    user-select: none;
    font-weight: 500;
    color: var(--fg);
    padding: 4px 6px;
    border-radius: 6px;
    display: flex;
    align-items: center;
    gap: 6px;
  }
  .tree .dir > .label:hover { background: var(--divider-soft); }
  .tree .dir > .label .chevron {
    width: 10px; height: 10px;
    color: var(--muted);
    transition: transform 0.15s ease;
    flex-shrink: 0;
  }
  .tree .dir.open > .label .chevron { transform: rotate(90deg); }
  .tree .dir > .label .icon { color: var(--accent); flex-shrink: 0; }
  .tree .dir.open > .label .icon-folder-closed { display: none; }
  .tree .dir:not(.open) > .label .icon-folder-open { display: none; }
  .tree .dir > ul { display: none; }
  .tree .dir.open > ul { display: block; }
  .tree a {
    color: var(--fg);
    text-decoration: none;
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 4px 8px;
    border-radius: 6px;
    transition: background 0.12s ease;
  }
  .tree a .icon { color: var(--muted); flex-shrink: 0; }
  .tree a:hover { background: var(--divider-soft); }
  .tree a.active { background: var(--accent); color: #ffffff; }
  .tree a.active .icon { color: #ffffff; }
  .tree .name { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }

  /* Sidebar search */
  #sidebar-search {
    display: flex;
    align-items: center;
    gap: 6px;
    background: var(--content-bg);
    border: 1px solid var(--hairline);
    border-radius: 9999px;
    padding: 6px 12px;
    margin: 0 0 14px;
    transition: border-color 0.12s ease;
    cursor: text;
  }
  #sidebar-search:focus-within { border-color: var(--accent); }
  #sidebar-search .icon { color: var(--muted); flex-shrink: 0; }
  #sidebar-search input {
    flex: 1;
    background: transparent;
    border: none;
    outline: none;
    color: var(--fg);
    font: inherit;
    font-size: var(--sidebar-font);
    letter-spacing: -0.01em;
    min-width: 0;
  }
  #sidebar-search input::placeholder { color: var(--muted); }
  #sidebar-search kbd {
    font: inherit;
    font-size: calc(var(--sidebar-font) - 1px);
    color: var(--muted);
    background: var(--divider-soft);
    border-radius: 4px;
    padding: 1px 6px;
    flex-shrink: 0;
  }

  /* Search modal */
  #search-overlay {
    position: fixed;
    inset: 0;
    background: rgba(0, 0, 0, 0.4);
    -webkit-backdrop-filter: blur(8px);
    backdrop-filter: blur(8px);
    display: none;
    align-items: flex-start;
    justify-content: center;
    padding-top: 120px;
    z-index: 100;
  }
  #search-overlay.open { display: flex; }
  #search-modal {
    width: 600px;
    max-width: calc(100vw - 32px);
    max-height: calc(100vh - 200px);
    background: var(--content-bg);
    border: 1px solid var(--hairline);
    border-radius: 18px;
    overflow: hidden;
    display: flex;
    flex-direction: column;
    box-shadow: rgba(0, 0, 0, 0.22) 3px 5px 30px 0;
    font-size: 15px;
    letter-spacing: -0.01em;
  }
  #search-modal-header {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 14px 18px;
    border-bottom: 1px solid var(--hairline);
  }
  #search-modal-header .icon { color: var(--muted); flex-shrink: 0; }
  #search-input {
    flex: 1;
    background: transparent;
    border: none;
    outline: none;
    color: var(--fg);
    font: inherit;
    font-size: 17px;
    letter-spacing: -0.022em;
    min-width: 0;
  }
  #search-input::placeholder { color: var(--muted); }
  #search-results {
    overflow-y: auto;
    padding: 6px;
    flex: 1;
  }
  #search-results .empty-state {
    padding: 32px;
    text-align: center;
    color: var(--muted);
  }
  .search-result {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 10px 14px;
    border-radius: 11px;
    cursor: pointer;
  }
  .search-result .icon { color: var(--muted); flex-shrink: 0; }
  .search-result .name {
    flex-shrink: 0;
    color: var(--fg);
  }
  .search-result .name mark {
    background: transparent;
    color: var(--accent);
    font-weight: 600;
  }
  .search-result .path {
    color: var(--muted);
    font-size: 13px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }
  .search-result.active {
    background: var(--accent);
    color: #ffffff;
  }
  .search-result.active .icon,
  .search-result.active .name,
  .search-result.active .path { color: #ffffff; }
  .search-result.active .name mark { color: #ffffff; text-decoration: underline; }
  #search-modal-footer {
    display: flex;
    gap: 16px;
    padding: 10px 18px;
    border-top: 1px solid var(--hairline);
    color: var(--muted);
    font-size: 12px;
    letter-spacing: -0.01em;
  }
  #search-modal-footer kbd {
    font: inherit;
    font-size: 11px;
    background: var(--divider-soft);
    border-radius: 4px;
    padding: 1px 6px;
    color: var(--fg);
  }

  /* Toolbar */
  #content-wrap { flex: 1; overflow: auto; background: var(--content-bg); }
  #toolbar {
    position: sticky;
    top: 0;
    display: flex;
    flex-wrap: wrap;
    gap: 20px;
    align-items: center;
    padding: 12px 32px;
    background: color-mix(in srgb, var(--content-bg) 80%, transparent);
    -webkit-backdrop-filter: saturate(180%) blur(20px);
    backdrop-filter: saturate(180%) blur(20px);
    border-bottom: 1px solid var(--hairline);
    font-size: 12px;
    z-index: 10;
  }
  #toolbar .group { display: flex; gap: 6px; align-items: center; }
  #toolbar .group-label {
    color: var(--muted);
    font-size: 12px;
    letter-spacing: -0.01em;
    margin-right: 2px;
  }
  #toolbar button {
    background: transparent;
    border: 1px solid var(--hairline);
    color: var(--fg);
    padding: 5px 12px;
    border-radius: 9999px;
    cursor: pointer;
    font: inherit;
    font-size: 12px;
    letter-spacing: -0.01em;
    transition: transform 0.12s ease, background 0.12s ease, border-color 0.12s ease;
  }
  #toolbar button:hover { border-color: var(--accent); color: var(--accent); }
  #toolbar button:active { transform: scale(0.95); }
  #toolbar button.active {
    background: var(--accent);
    color: #ffffff;
    border-color: var(--accent);
  }
  #refresh-btn { padding: 5px 14px; }

  /* Content */
  #content {
    padding: 64px 48px 96px;
    max-width: var(--content-width);
    margin: 0 auto;
    font-size: var(--content-font);
    line-height: 1.47;
    letter-spacing: -0.022em;
  }
  #content h1, #content h2, #content h3, #content h4 {
    font-family: "SF Pro Display", system-ui, -apple-system, sans-serif;
    color: var(--fg);
    letter-spacing: -0.022em;
    font-weight: 600;
    margin-top: 1.6em;
    margin-bottom: 0.5em;
    line-height: 1.1;
  }
  #content h1 { font-size: 2.4em; letter-spacing: -0.028em; border: none; padding: 0; }
  #content h2 { font-size: 1.8em; letter-spacing: -0.024em; border: none; padding: 0; margin-top: 2em; }
  #content h3 { font-size: 1.35em; }
  #content h4 { font-size: 1.1em; }
  #content p { margin: 0 0 1.1em; }
  #content a { color: var(--accent); text-decoration: none; }
  #content a:hover { text-decoration: underline; }
  #content img {
    max-width: 100%;
    border-radius: 18px;
    box-shadow: rgba(0, 0, 0, 0.22) 3px 5px 30px 0;
    margin: 1.2em 0;
  }
  #content pre {
    background: var(--parchment);
    border: 1px solid var(--hairline);
    padding: 18px 20px;
    border-radius: 11px;
    overflow: auto;
    font-size: 0.92em;
    line-height: 1.55;
  }
  #content code {
    background: var(--divider-soft);
    padding: 2px 6px;
    border-radius: 5px;
    font-size: 0.88em;
    font-family: "SF Mono", ui-monospace, "Menlo", monospace;
  }
  #content pre code { background: transparent; padding: 0; border-radius: 0; }
  #content table {
    border-collapse: collapse;
    margin: 1.4em 0;
    font-size: 0.95em;
  }
  #content th, #content td {
    border-bottom: 1px solid var(--hairline);
    padding: 10px 16px;
    text-align: left;
  }
  #content th { font-weight: 600; color: var(--ink-muted-80); background: var(--parchment); }
  @media (prefers-color-scheme: dark) {
    #content th { color: var(--fg); }
  }
  #content blockquote {
    border-left: 3px solid var(--accent);
    margin: 1.2em 0;
    padding: 4px 20px;
    color: var(--muted);
  }
  #content ul, #content ol { padding-left: 1.4em; }
  #content li { margin: 0.3em 0; }
  #content hr { border: none; border-top: 1px solid var(--hairline); margin: 2.4em 0; }
  .empty {
    color: var(--muted);
    padding: 96px 32px;
    text-align: center;
    font-size: 17px;
    letter-spacing: -0.022em;
  }
</style>
</head>
<body>
<div id="sidebar">
  <h3>%ROOT%</h3>
  <label id="sidebar-search" for="sidebar-search-input">
    <svg class="icon" width="13" height="13" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linecap="round"><circle cx="7" cy="7" r="4.5"/><path d="M10.5 10.5 L14 14"/></svg>
    <input id="sidebar-search-input" type="text" placeholder="Search files…" autocomplete="off" spellcheck="false" />
    <kbd>⌘K</kbd>
  </label>
  <div id="tree" class="tree"></div>
</div>
<div id="search-overlay" role="dialog" aria-modal="true">
  <div id="search-modal">
    <div id="search-modal-header">
      <svg class="icon" width="16" height="16" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linecap="round"><circle cx="7" cy="7" r="4.5"/><path d="M10.5 10.5 L14 14"/></svg>
      <input id="search-input" type="text" placeholder="Search files by name…" autocomplete="off" spellcheck="false" />
    </div>
    <div id="search-results"></div>
    <div id="search-modal-footer">
      <span><kbd>↑</kbd><kbd>↓</kbd> 이동</span>
      <span><kbd>Enter</kbd> 열기</span>
      <span><kbd>Esc</kbd> 닫기</span>
    </div>
  </div>
</div>
<div id="content-wrap">
  <div id="toolbar">
    <div class="group" id="width-ctl">
      <span class="group-label">Width</span>
      <button data-w="800">800</button>
      <button data-w="1100" class="active">1100</button>
      <button data-w="1400">1400</button>
      <button data-w="100%">Full</button>
    </div>
    <div class="group" id="font-ctl">
      <span class="group-label">Body</span>
      <button data-f="14">14</button>
      <button data-f="15">15</button>
      <button data-f="17" class="active">17</button>
      <button data-f="19">19</button>
      <button data-f="21">21</button>
    </div>
    <div class="group" id="sidebar-font-ctl">
      <span class="group-label">Sidebar</span>
      <button data-sf="12">12</button>
      <button data-sf="13" class="active">13</button>
      <button data-sf="15">15</button>
      <button data-sf="17">17</button>
    </div>
    <div class="group" id="theme-ctl">
      <span class="group-label">Theme</span>
      <button data-th="auto" class="active" title="시스템 설정">Auto</button>
      <button data-th="canvas" title="Pure White #ffffff">Canvas</button>
      <button data-th="parchment" title="Parchment #f5f5f7">Parchment</button>
      <button data-th="pearl" title="Pearl #fafafc">Pearl</button>
      <button data-th="tile" title="Near-Black Tile #272729">Tile</button>
      <button data-th="black" title="Pure Black #000000">Black</button>
    </div>
    <div class="group">
      <button id="refresh-btn" title="파일 트리 새로고침">↻ Refresh</button>
    </div>
  </div>
  <div id="content"><div class="empty">왼쪽에서 .md 파일을 선택하세요</div></div>
</div>
<script src="https://cdn.jsdelivr.net/npm/marked@12/marked.min.js"></script>
<script type="module">
  import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs';
  const dark = matchMedia('(prefers-color-scheme: dark)').matches;
  mermaid.initialize({ startOnLoad: false, theme: dark ? 'dark' : 'default', securityLevel: 'loose' });
  window.__mermaid = mermaid;
</script>
<script>
marked.use({
  renderer: {
    code(code, lang) {
      let text = code, language = lang;
      if (typeof code === 'object' && code !== null) {
        text = code.text;
        language = code.lang;
      }
      if ((language || '').trim() === 'mermaid') {
        return '<div class="mermaid">' + text + '</div>';
      }
      return false;
    }
  }
});
async function renderMermaid() {
  if (!window.__mermaid) { setTimeout(renderMermaid, 50); return; }
  const blocks = document.querySelectorAll('#content .mermaid');
  for (let i = 0; i < blocks.length; i++) {
    const el = blocks[i];
    const src = el.textContent;
    try {
      const { svg } = await window.__mermaid.render('m' + Date.now() + i, src);
      el.innerHTML = svg;
    } catch (e) {
      el.innerHTML = '<pre style="color:#c00">mermaid error: ' + (e.message || e) + '</pre>';
    }
  }
}
let __flatFiles = [];
function flattenTree(node, acc) {
  for (const child of node.children || []) {
    if (child.type === 'dir') {
      flattenTree(child, acc);
    } else {
      const path = child.path;
      const i = path.lastIndexOf('/');
      acc.push({ name: child.name, path, dir: i >= 0 ? path.slice(0, i) : '' });
    }
  }
  return acc;
}
async function loadTree() {
  const r = await fetch('/api/tree');
  const data = await r.json();
  const tree = document.getElementById('tree');
  tree.innerHTML = '';
  tree.appendChild(renderNode(data, true));
  __flatFiles = flattenTree(data, []);
}
const ICON_CHEVRON = '<svg class="chevron" viewBox="0 0 10 10" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><path d="M3.5 1.5 L7 5 L3.5 8.5"/></svg>';
const ICON_FOLDER_CLOSED = '<svg class="icon icon-folder-closed" width="14" height="14" viewBox="0 0 16 16" fill="currentColor"><path d="M1.5 4.5A1.5 1.5 0 0 1 3 3h3.5l1.5 1.5H13a1.5 1.5 0 0 1 1.5 1.5v6A1.5 1.5 0 0 1 13 13.5H3A1.5 1.5 0 0 1 1.5 12V4.5z"/></svg>';
const ICON_FOLDER_OPEN = '<svg class="icon icon-folder-open" width="14" height="14" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linejoin="round"><path d="M1.7 5.5V12A1.5 1.5 0 0 0 3.2 13.5H12.5L14.5 7H3.5z" fill="currentColor" fill-opacity="0.18"/><path d="M1.7 5.5V4A1.5 1.5 0 0 1 3.2 2.5h3.3l1.5 1.5h4.5A1.5 1.5 0 0 1 14 5.5v1.5"/></svg>';
const ICON_FILE = '<svg class="icon" width="13" height="13" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.3" stroke-linejoin="round"><path d="M3.5 1.5h6L13 5v9.5H3.5z"/><path d="M9.5 1.5V5H13"/></svg>';

function renderNode(node, isRoot) {
  const ul = document.createElement('ul');
  for (const child of node.children || []) {
    const li = document.createElement('li');
    if (child.type === 'dir') {
      li.className = 'dir';
      const label = document.createElement('span');
      label.className = 'label';
      label.innerHTML = ICON_CHEVRON + ICON_FOLDER_CLOSED + ICON_FOLDER_OPEN + '<span class="name"></span>';
      label.querySelector('.name').textContent = child.name;
      label.onclick = () => li.classList.toggle('open');
      li.appendChild(label);
      li.appendChild(renderNode(child, false));
    } else {
      const a = document.createElement('a');
      a.innerHTML = ICON_FILE + '<span class="name"></span>';
      a.querySelector('.name').textContent = child.name;
      a.href = '#' + encodeURIComponent(child.path);
      a.onclick = (e) => { e.preventDefault(); location.hash = encodeURIComponent(child.path); };
      li.appendChild(a);
    }
    ul.appendChild(li);
  }
  return ul;
}
async function loadFile() {
  const path = decodeURIComponent(location.hash.slice(1));
  document.querySelectorAll('#tree a').forEach(a => a.classList.toggle('active', decodeURIComponent(a.getAttribute('href').slice(1)) === path));
  if (!path) return;
  const r = await fetch('/api/file?path=' + encodeURIComponent(path));
  if (!r.ok) { document.getElementById('content').innerHTML = '<div class="empty">파일을 불러올 수 없습니다</div>'; return; }
  const text = await r.text();
  document.getElementById('content').innerHTML = marked.parse(text);
  document.getElementById('content-wrap').scrollTop = 0;
  renderMermaid();
}
function setWidth(w) {
  const val = w === '100%' ? '100%' : (w + 'px');
  document.documentElement.style.setProperty('--content-width', val);
  document.querySelectorAll('#width-ctl button').forEach(b => b.classList.toggle('active', b.dataset.w === String(w)));
  localStorage.setItem('md-width', w);
}
document.querySelectorAll('#width-ctl button').forEach(b => {
  b.onclick = () => setWidth(b.dataset.w);
});
setWidth(localStorage.getItem('md-width') || '1100');

function setFont(f) {
  document.documentElement.style.setProperty('--content-font', f + 'px');
  document.querySelectorAll('#font-ctl button').forEach(b => b.classList.toggle('active', b.dataset.f === String(f)));
  localStorage.setItem('md-font', f);
}
document.querySelectorAll('#font-ctl button').forEach(b => {
  b.onclick = () => setFont(b.dataset.f);
});
setFont(localStorage.getItem('md-font') || '17');

function setSidebarFont(f) {
  document.documentElement.style.setProperty('--sidebar-font', f + 'px');
  document.querySelectorAll('#sidebar-font-ctl button').forEach(b => b.classList.toggle('active', b.dataset.sf === String(f)));
  localStorage.setItem('md-sidebar-font', f);
}
document.querySelectorAll('#sidebar-font-ctl button').forEach(b => {
  b.onclick = () => setSidebarFont(b.dataset.sf);
});
setSidebarFont(localStorage.getItem('md-sidebar-font') || '13');

function setTheme(t) {
  if (t === 'auto') {
    document.documentElement.removeAttribute('data-theme');
  } else {
    document.documentElement.setAttribute('data-theme', t);
  }
  document.querySelectorAll('#theme-ctl button').forEach(b => b.classList.toggle('active', b.dataset.th === t));
  localStorage.setItem('md-theme', t);
}
document.querySelectorAll('#theme-ctl button').forEach(b => {
  b.onclick = () => setTheme(b.dataset.th);
});
setTheme(localStorage.getItem('md-theme') || 'auto');

document.getElementById('refresh-btn').onclick = async () => {
  const btn = document.getElementById('refresh-btn');
  btn.disabled = true;
  const orig = btn.textContent;
  btn.textContent = '↻ ...';
  try {
    await loadTree();
    if (location.hash) await loadFile();
    btn.textContent = '✓ Refreshed';
  } catch (e) {
    btn.textContent = '✗ Failed';
  }
  setTimeout(() => { btn.textContent = orig; btn.disabled = false; }, 800);
};

// ----- Filename search -----
function fuzzyScore(name, query) {
  if (!query) return { score: 0, indices: [] };
  const n = name.toLowerCase();
  const q = query.toLowerCase();
  const indices = [];
  let qi = 0;
  let score = 0;
  let prevMatch = -2;
  for (let i = 0; i < n.length && qi < q.length; i++) {
    if (n[i] === q[qi]) {
      indices.push(i);
      let bonus = 1;
      if (i === prevMatch + 1) bonus += 8;
      const prev = i > 0 ? n[i - 1] : '';
      if (prev === '' || prev === '/' || prev === '-' || prev === '_' || prev === '.' || prev === ' ') bonus += 5;
      if (i === 0) bonus += 5;
      score += bonus;
      prevMatch = i;
      qi++;
    }
  }
  if (qi < q.length) return null;
  score -= n.length * 0.05;
  return { score, indices };
}
function searchFiles(query) {
  const trimmed = query.trim();
  if (!trimmed) return __flatFiles.slice(0, 50).map(f => ({ ...f, indices: [] }));
  const out = [];
  for (const f of __flatFiles) {
    const r = fuzzyScore(f.name, trimmed);
    if (r) out.push({ ...f, score: r.score, indices: r.indices });
  }
  out.sort((a, b) => b.score - a.score);
  return out.slice(0, 50);
}
function highlightName(name, indices) {
  if (!indices.length) { const span = document.createElement('span'); span.textContent = name; return span; }
  const frag = document.createDocumentFragment();
  let last = 0;
  const set = new Set(indices);
  for (let i = 0; i < name.length; i++) {
    if (set.has(i)) {
      if (i > last) frag.appendChild(document.createTextNode(name.slice(last, i)));
      const m = document.createElement('mark');
      m.textContent = name[i];
      frag.appendChild(m);
      last = i + 1;
    }
  }
  if (last < name.length) frag.appendChild(document.createTextNode(name.slice(last)));
  return frag;
}

const FILE_ICON_SVG = '<svg class="icon" width="14" height="14" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.3" stroke-linejoin="round"><path d="M3.5 1.5h6L13 5v9.5H3.5z"/><path d="M9.5 1.5V5H13"/></svg>';
let __searchActive = 0;
let __searchResults = [];

function renderSearchResults(query) {
  const list = document.getElementById('search-results');
  __searchResults = searchFiles(query);
  __searchActive = 0;
  list.innerHTML = '';
  if (!__searchResults.length) {
    const empty = document.createElement('div');
    empty.className = 'empty-state';
    empty.textContent = query ? '검색 결과가 없습니다' : '파일이 없습니다';
    list.appendChild(empty);
    return;
  }
  __searchResults.forEach((f, i) => {
    const row = document.createElement('div');
    row.className = 'search-result' + (i === 0 ? ' active' : '');
    row.dataset.index = i;
    row.innerHTML = FILE_ICON_SVG;
    const nameEl = document.createElement('span');
    nameEl.className = 'name';
    nameEl.appendChild(highlightName(f.name, f.indices));
    row.appendChild(nameEl);
    const pathEl = document.createElement('span');
    pathEl.className = 'path';
    pathEl.textContent = f.dir || '(root)';
    row.appendChild(pathEl);
    row.onmouseenter = () => setActiveResult(i);
    row.onclick = () => openResult(i);
    list.appendChild(row);
  });
}
function setActiveResult(i) {
  const items = document.querySelectorAll('#search-results .search-result');
  if (!items.length) return;
  __searchActive = (i + items.length) % items.length;
  items.forEach((el, idx) => el.classList.toggle('active', idx === __searchActive));
  const el = items[__searchActive];
  if (el) el.scrollIntoView({ block: 'nearest' });
}
function openResult(i) {
  if (typeof i === 'number') __searchActive = i;
  const f = __searchResults[__searchActive];
  if (!f) return;
  closeSearch();
  location.hash = encodeURIComponent(f.path);
}
function openSearch(seed) {
  const overlay = document.getElementById('search-overlay');
  const input = document.getElementById('search-input');
  overlay.classList.add('open');
  input.value = seed || '';
  renderSearchResults(input.value);
  setTimeout(() => input.focus(), 0);
}
function closeSearch() {
  const overlay = document.getElementById('search-overlay');
  overlay.classList.remove('open');
  document.getElementById('sidebar-search-input').value = '';
}

document.getElementById('search-input').addEventListener('input', (e) => {
  renderSearchResults(e.target.value);
});
document.getElementById('search-input').addEventListener('keydown', (e) => {
  if (e.key === 'ArrowDown') { e.preventDefault(); setActiveResult(__searchActive + 1); }
  else if (e.key === 'ArrowUp') { e.preventDefault(); setActiveResult(__searchActive - 1); }
  else if (e.key === 'Enter') { e.preventDefault(); openResult(); }
  else if (e.key === 'Escape') { e.preventDefault(); closeSearch(); }
});
document.getElementById('search-overlay').addEventListener('click', (e) => {
  if (e.target.id === 'search-overlay') closeSearch();
});
document.getElementById('sidebar-search-input').addEventListener('focus', (e) => {
  openSearch(e.target.value);
});
document.getElementById('sidebar-search-input').addEventListener('input', (e) => {
  if (!document.getElementById('search-overlay').classList.contains('open')) {
    openSearch(e.target.value);
  } else {
    document.getElementById('search-input').value = e.target.value;
    renderSearchResults(e.target.value);
  }
});
window.addEventListener('keydown', (e) => {
  const isMod = e.metaKey || e.ctrlKey;
  if (isMod && (e.key === 'k' || e.key === 'K')) {
    e.preventDefault();
    if (document.getElementById('search-overlay').classList.contains('open')) closeSearch();
    else openSearch();
  } else if (e.key === 'Escape' && document.getElementById('search-overlay').classList.contains('open')) {
    closeSearch();
  }
});

window.addEventListener('hashchange', loadFile);
loadTree().then(loadFile);
</script>
</body>
</html>
"""


IGNORED_DIRS = {"node_modules", "dist", "build", ".next", ".astro", "__pycache__", ".venv", "venv"}


def build_tree(base: Path):
    def walk(p: Path):
        node = {"name": p.name or str(p), "type": "dir", "children": []}
        try:
            entries = sorted(p.iterdir(), key=lambda x: (x.is_file(), x.name.lower()))
        except PermissionError:
            return node
        for e in entries:
            if e.name.startswith("."):
                continue
            if e.is_dir() and e.name in IGNORED_DIRS:
                continue
            if e.is_dir():
                child = walk(e)
                if child["children"]:
                    node["children"].append(child)
            elif e.suffix.lower() in (".md", ".markdown"):
                node["children"].append({
                    "name": e.name,
                    "type": "file",
                    "path": str(e.relative_to(base)),
                })
        return node
    return walk(base)


class Handler(http.server.BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        print(f"[{self.address_string()}] {fmt % args}")

    def _send(self, code, body, ctype="text/plain; charset=utf-8"):
        data = body.encode("utf-8") if isinstance(body, str) else body
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        u = urllib.parse.urlparse(self.path)
        if u.path == "/":
            html = INDEX_HTML.replace("%ROOT%", str(ROOT.name or ROOT))
            self._send(200, html, "text/html; charset=utf-8")
        elif u.path == "/api/tree":
            self._send(200, json.dumps(build_tree(ROOT)), "application/json")
        elif u.path == "/api/file":
            q = urllib.parse.parse_qs(u.query)
            rel = q.get("path", [""])[0]
            target = (ROOT / rel).resolve()
            if not str(target).startswith(str(ROOT)) or not target.is_file():
                self._send(404, "not found")
                return
            if target.suffix.lower() not in (".md", ".markdown"):
                self._send(400, "not markdown")
                return
            self._send(200, target.read_text(encoding="utf-8", errors="replace"), "text/plain; charset=utf-8")
        else:
            self._send(404, "not found")


def main():
    socketserver.ThreadingTCPServer.allow_reuse_address = True
    with socketserver.ThreadingTCPServer(("127.0.0.1", PORT), Handler) as s:
        print(f"MyDocsViewer: http://127.0.0.1:{PORT}  (root: {ROOT})")
        try:
            s.serve_forever()
        except KeyboardInterrupt:
            pass


if __name__ == "__main__":
    main()
