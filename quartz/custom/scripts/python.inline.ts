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
// 2. 判斷 Quartz 網站根目錄
// ==================================================

function getSiteRoot(): URL {
  const currentURL =
    new URL(window.location.href)


  // 本機
  if (
    currentURL.hostname === "localhost" ||
    currentURL.hostname === "127.0.0.1"
  ) {
    return new URL(
      "/",
      currentURL.origin
    )
  }


  // GitHub Pages
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


  // 其他網站
  return new URL(
    "/",
    currentURL.origin
  )
}


// ==================================================
// 3. 載入整個 Python 專案
// ==================================================

async function loadPythonProject(
  pyodide: any
) {
  const siteRoot =
    getSiteRoot()

  const pythonRoot =
    new URL(
      "static/python/",
      siteRoot
    )


  // ------------------------------------------------
  // 讀取 manifest.json
  // ------------------------------------------------

  const manifestURL =
    new URL(
      "manifest.json",
      pythonRoot
    )

  const manifestResponse =
    await fetch(
      manifestURL,
      { cache: "no-store" }
    )

  if (!manifestResponse.ok) {
    throw new Error(
      `無法載入 manifest.json：${manifestResponse.status}`
    )
  }

  const manifest =
    await manifestResponse.json()


  // ------------------------------------------------
  // 建立 Pyodide 虛擬 Python 資料夾
  // ------------------------------------------------

  const appRoot =
    "/app"

  pyodide.FS.mkdirTree(
    appRoot
  )


  // ------------------------------------------------
  // 把所有 Python 檔案下載進 Pyodide
  // ------------------------------------------------

  for (const file of manifest.files) {

    const fileURL =
      new URL(
        file,
        pythonRoot
      )

    console.log(
      "載入 Python：",
      fileURL.href
    )


    const response =
      await fetch(
        fileURL,
        { cache: "no-store" }
      )


    if (!response.ok) {
      throw new Error(
        `無法載入 Python 檔案：${file}\n` +
        `HTTP ${response.status}`
      )
    }


    const data =
      new Uint8Array(
        await response.arrayBuffer()
      )


    const targetPath =
      `${appRoot}/${file}`


    // 如果 Python 檔案位於子資料夾，
    // 自動建立對應目錄
    const slash =
      targetPath.lastIndexOf("/")

    const targetDirectory =
      targetPath.substring(
        0,
        slash
      )

    pyodide.FS.mkdirTree(
      targetDirectory
    )


    // 寫入 Pyodide 虛擬檔案系統
    pyodide.FS.writeFile(
      targetPath,
      data
    )
  }


  // ------------------------------------------------
  // 告訴 Python：
  // /app 是 Python 模組搜尋位置
  // ------------------------------------------------

  await pyodide.runPythonAsync(`
import sys

if "/app" not in sys.path:
    sys.path.insert(0, "/app")
  `)


  // ------------------------------------------------
  // 執行入口 Python
  // ------------------------------------------------

  const entry =
    manifest.entry ?? "main.py"

  await pyodide.runPythonAsync(`
import runpy

runpy.run_path(
    "/app/${entry}",
    run_name="__main__"
)
  `)
}


// ==================================================
// 4. 啟動 Python App
// ==================================================

async function setupPythonApp() {

  // 尋找目前頁面上是否有任何需要 Python 的功能
  const root =
    document.querySelector<HTMLElement>(
      "[data-python-app]"
    )


  // 目前頁面沒有 Python 功能
  if (!root) {
    return
  }


  // 避免 Quartz SPA 重複啟動
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
      "正在載入 Python 專案..."


    await loadPythonProject(
      pyodide
    )

  } catch (error) {

    console.error(error)

    root.textContent =
      "Python GUI 啟動失敗：\n" +
      String(error)

    delete root.dataset.pythonReady
  }
}


// ==================================================
// 5. 第一次載入
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