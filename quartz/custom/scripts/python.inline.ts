let pyodideInstance: any = null
let pyodideLoading: Promise<any> | null = null


// ==================================================
// 1. 載入 Pyodide
// ==================================================

async function getPyodide() {
  if (pyodideInstance) {
    return pyodideInstance
  }

  if (pyodideLoading) {
    return pyodideLoading
  }

  pyodideLoading = new Promise(async (resolve, reject) => {
    try {
      if (!(window as any).loadPyodide) {
        const script = document.createElement("script")

        script.src =
          "https://cdn.jsdelivr.net/pyodide/v314.0.7/full/pyodide.js"

        script.onload = async () => {
          try {
            pyodideInstance =
              await (window as any).loadPyodide()

            resolve(pyodideInstance)

          } catch (error) {
            reject(error)
          }
        }

        script.onerror = () => {
          reject(
            new Error("Pyodide 載入失敗")
          )
        }

        document.head.appendChild(script)

      } else {
        pyodideInstance =
          await (window as any).loadPyodide()

        resolve(pyodideInstance)
      }

    } catch (error) {
      reject(error)
    }
  })

  return pyodideLoading
}


// ==================================================
// 2. 找到 Quartz 網站根目錄
// ==================================================

function getSiteRoot(): URL {

  const stylesheets =
    [...document.querySelectorAll<HTMLLinkElement>(
      'link[rel="stylesheet"]'
    )]

  const quartzCss =
    stylesheets.find((link) => {
      try {
        const url =
          new URL(link.href)

        return url.pathname.endsWith(
          "/index.css"
        )

      } catch {
        return false
      }
    })

  if (!quartzCss) {
    throw new Error(
      "找不到 Quartz 的 index.css"
    )
  }

  const cssURL =
    new URL(quartzCss.href)

  return new URL(
    "./",
    cssURL
  )
}


// ==================================================
// 3. 載入 Python GUI 程式 main.py
// ==================================================

async function loadPythonMain(
  pyodide: any
) {
  const siteRoot =
    getSiteRoot()

  const pythonURL =
    new URL(
      "static/python/main.py",
      siteRoot
    )

  console.log(
    "Python main.py URL:",
    pythonURL.href
  )

  const response =
    await fetch(pythonURL)

  if (!response.ok) {
    throw new Error(
      `無法載入 main.py：${response.status}\n${pythonURL.href}`
    )
  }

  const pythonCode =
    await response.text()

  await pyodide.runPythonAsync(
    pythonCode
  )
}


// ==================================================
// 4. 啟動 Python GUI
// ==================================================

async function setupPythonApp() {

  const root =
    document.getElementById(
      "python-app"
    )

  if (!root) {
    return
  }

  if (
    root.dataset.pythonReady ===
    "true"
  ) {
    return
  }

  root.dataset.pythonReady =
    "true"

  try {

    root.textContent =
      "正在啟動 Python..."

    const pyodide =
      await getPyodide()

    root.textContent =
      "正在載入 Python GUI..."

    await loadPythonMain(
      pyodide
    )

  } catch (error) {

    console.error(error)

    root.textContent =
      "Python GUI 啟動失敗：\n" +
      String(error)

    // 啟動失敗時允許重新嘗試
    delete root.dataset.pythonReady
  }
}


// ==================================================
// 5. 第一次載入頁面
// ==================================================

setupPythonApp()


// ==================================================
// 6. Quartz SPA 換頁後重新檢查
// ==================================================

document.addEventListener(
  "nav",
  setupPythonApp
)

document.addEventListener(
  "render",
  setupPythonApp
)