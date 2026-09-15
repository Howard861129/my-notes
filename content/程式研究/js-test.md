---
title: JavaScript 基礎測試
tags:
  - JavaScript
---

Quartz 的 Obsidian Markdown 處理器本身支援 raw HTML，因此 Markdown 中可以放 `<button>`、`<p>`、`<script>` 這類 HTML。

<!--
## 文字變化

<button id="hello-btn">點我</button>

<p id="hello-text">JavaScript 尚未執行</p>

## 計數器

<button id="count-btn">+1</button>

<p>
目前數字：<span id="count-number">0</span>
</p>

<script>
(() => {
  const quartzCss = [...document.querySelectorAll('link[rel="stylesheet"]')]
    .find(link => link.href.endsWith("/index.css"))

  if (!quartzCss) {
    console.error("找不到 Quartz 網站根目錄")
    return
  }

  const scriptURL = new URL("scripts/basic.js", quartzCss.href)

  if (!document.querySelector(`script[src="${scriptURL.href}"]`)) {
    const script = document.createElement("script")
    script.src = scriptURL.href
    document.body.appendChild(script)
  }
})()
</script>
-->

# JavaScript 基礎測試

## 文字測試

<div data-js-widget="hello">

<button data-js-action="hello">
點我
</button>

<p data-js-output="hello">
JavaScript 尚未執行
</p>

</div>


## 計數器

<div data-js-widget="counter">

<button data-js-action="count">
+1
</button>

<p>
目前數字：
<span data-js-output="count">0</span>
</p>

</div>