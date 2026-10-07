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

      // 如果 Pyodide 尚未載入
      if (!(window as any).loadPyodide) {

        const script =
          document.createElement("script")

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
      }

      // Pyodide 已經存在
      else {

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
// 2. 判斷 Quartz 網站根目錄
// ==================================================

function getSiteRoot(): URL {

  const currentURL =
    new URL(window.location.href)


  // ------------------------------------------------
  // 本機開發環境
  //
  // http://localhost:8080/...
  // ------------------------------------------------

  if (
    currentURL.hostname === "localhost" ||
    currentURL.hostname === "127.0.0.1"
  ) {

    return new URL(
      "/",
      currentURL.origin
    )
  }


  // ------------------------------------------------
  // GitHub Pages
  //
  // https://使用者.github.io/my-notes/...
  //
  // 第一層路徑 my-notes
  // 就是 Repository 網站根目錄
  // ------------------------------------------------

  if (
    currentURL.hostname.endsWith(
      ".github.io"
    )
  ) {

    const pathParts =
      currentURL.pathname
        .split("/")
        .filter(Boolean)

    if (pathParts.length > 0) {

      const repositoryName =
        pathParts[0]

      return new URL(
        `/${repositoryName}/`,
        currentURL.origin
      )
    }
  }


  // ------------------------------------------------
  // 其他情況
  // 預設使用網域根目錄
  // ------------------------------------------------

  return new URL(
    "/",
    currentURL.origin
  )
}


// ==================================================
// 3. 載入 main.py
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
    "Quartz 網站根目錄：",
    siteRoot.href
  )

  console.log(
    "main.py 網址：",
    pythonURL.href
  )


  const response =
    await fetch(pythonURL)


  if (!response.ok) {

    throw new Error(
      `無法載入 main.py：${response.status}\n` +
      `路徑：${pythonURL.href}`
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


  // 此頁沒有 Python App
  if (!root) {
    return
  }


  // 防止 Quartz SPA 重複啟動
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


    // 啟動 Pyodide
    const pyodide =
      await getPyodide()


    root.textContent =
      "正在載入 Python GUI..."


    // 執行 main.py
    await loadPythonMain(
      pyodide
    )


  } catch (error) {

    console.error(error)


    root.textContent =
      "Python GUI 啟動失敗：\n" +
      String(error)


    // 如果失敗，允許之後重新嘗試
    delete root.dataset.pythonReady
  }
}


// ==================================================
// 5. 第一次進入頁面
// ==================================================

setupPythonApp()


// ==================================================
// 6. Quartz SPA 換頁
// ==================================================

document.addEventListener(
  "nav",
  setupPythonApp
)


document.addEventListener(
  "render",
  setupPythonApp
)