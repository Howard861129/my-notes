function setupBasicWidgets() {
  // =========================
  // 文字按鈕
  // =========================

  document
    .querySelectorAll<HTMLElement>('[data-js-widget="hello"]')
    .forEach((widget) => {
      if (widget.dataset.jsReady === "true") {
        return
      }

      const button = widget.querySelector<HTMLButtonElement>(
        '[data-js-action="hello"]',
      )

      const text = widget.querySelector<HTMLElement>(
        '[data-js-output="hello"]',
      )

      if (!button || !text) {
        return
      }

      widget.dataset.jsReady = "true"

      button.addEventListener("click", () => {
        text.textContent = "JavaScript 執行成功！"
      })
    })


  // =========================
  // 計數器
  // =========================

  document
    .querySelectorAll<HTMLElement>('[data-js-widget="counter"]')
    .forEach((widget) => {
      if (widget.dataset.jsReady === "true") {
        return
      }

      const button = widget.querySelector<HTMLButtonElement>(
        '[data-js-action="count"]',
      )

      const output = widget.querySelector<HTMLElement>(
        '[data-js-output="count"]',
      )

      if (!button || !output) {
        return
      }

      widget.dataset.jsReady = "true"

      let count = 0

      button.addEventListener("click", () => {
        count++
        output.textContent = String(count)
      })
    })
}


// 一般頁面載入
setupBasicWidgets()

// Quartz SPA 換頁
document.addEventListener("nav", setupBasicWidgets)

// 頁面內容被重新渲染
document.addEventListener("render", setupBasicWidgets)