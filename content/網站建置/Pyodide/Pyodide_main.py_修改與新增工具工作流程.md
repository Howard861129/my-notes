# Pyodide `main.py` 修改與新增工具工作流程

> 適用環境：Quartz 網站 + TypeScript 載入 Pyodide + `/app/main.py` 作為 Python 統一入口。  
> 用途：日後新增、修改或排查嵌入網頁的 Python GUI 工具。

## 1. `main.py` 的角色

`main.py` 是所有 Python 網頁工具的**統一啟動入口**。它會檢查當前 HTML 頁面是否具有某工具專屬的容器，只有找到容器時才啟動該工具。

執行關係：

```text
Quartz 網頁（HTML 容器）
    ↓
TypeScript 載入 Pyodide 並執行 main.py
    ↓
main() 檢查各工具容器是否存在
    ├── #gui-test-app       → gui_test.py 的 start_gui()
    ├── #lightup-app        → lightup.py 的 run_lightup()
    └── #tree-editor-app    → tree_editor.py 的 mount()
```

## 2. 這次發生的錯誤

出現訊息：

```text
AttributeError: 'JsNull' object has no attribute 'querySelector'
```

原本在 `main.py` 中的程式：

```python
if document.getElementById("tree-editor-app") is not None:
    mount("tree-editor-app")
else:
    unmount("tree-editor-app")
```

**問題原因：** 網頁不存在該容器時，JavaScript `getElementById()` 會得到 `null`。在 Pyodide 的 Python／JavaScript 互通環境中，此值可能呈現為 `JsNull`，而不是 Python `None`。因此 `is not None` 仍可能為 `True`，讓程式錯誤地進入 `mount()`，最後在對不存在的容器呼叫 `querySelector()` 時出錯。

**修正原則：** 不直接使用 `is not None` 來判斷 `getElementById()` 是否找到元素。改用 `querySelectorAll(...).length > 0`，回傳明確的布林判斷。

## 3. 修改前的完整 `main.py`（原始版本）

以下完整保留這次發生錯誤時，你提供的原始 `main.py`，方便日後與修正版逐行對照：

```python
# ==================================================
# Python 網頁程式入口
# ==================================================

from js import document  # pyright: ignore[reportMissingImports]

from gui_test import start_gui
from lightup import run_lightup
from tree_editor import mount, unmount

def main():
    """
    整個 Python 網頁程式的啟動入口。
    """

    if document.getElementById("gui-test-app"):
        start_gui()
    if document.getElementById("lightup-app"):
        run_lightup()
    if document.getElementById("tree-editor-app") is not None:
        mount("tree-editor-app")
    else:
        unmount("tree-editor-app")


if __name__ == "__main__":
    main()
```

**原始版本的關鍵問題**在於第三個工具使用 `is not None` 判斷 JavaScript DOM 的查找結果，與前兩個工具的判斷方式不同；當結果是 Pyodide 的 `JsNull` 時，會誤以為容器存在。修正版統一使用 `element_exists()`，並保留原有工具匯入、啟動及解除掛載邏輯。

## 4. 本次修改後的完整 `main.py`

```python
# ==================================================
# Python 網頁程式入口
# ==================================================

from js import document  # pyright: ignore[reportMissingImports]

from gui_test import start_gui
from lightup import run_lightup
from tree_editor import mount, unmount


def element_exists(element_id):
    """檢查 HTML 裡是否存在指定 ID 的元素。"""
    return document.querySelectorAll(
        f"#{element_id}"
    ).length > 0


def main():
    """依照目前網頁是否具有指定容器，啟動相應的 Python 工具。"""

    if element_exists("gui-test-app"):
        start_gui()

    if element_exists("lightup-app"):
        run_lightup()

    if element_exists("tree-editor-app"):
        mount("tree-editor-app")
    else:
        unmount("tree-editor-app")


if __name__ == "__main__":
    main()
```

### 修改重點

| 項目 | 修改前 | 修改後 |
|---|---|---|
| 判斷 HTML 元素是否存在 | `getElementById(...) is not None` | `element_exists("...")` |
| 判斷機制 | 可能混淆 JavaScript `null` 與 Python `None` | `querySelectorAll()` 的結果數量大於 0 |
| 工具啟動 | 容器不存在時仍可能誤啟動 | 只有找到容器才啟動 |
| 樹狀目錄工具的解除掛載 | `else: unmount(...)` | 保留原本的 `unmount()` 邏輯 |

## 5. 以後新增 Python 網頁工具的標準流程

假設要新增 `new_tool.py`，啟動函式為 `start_new_tool()`，網頁容器 ID 為 `new-tool-app`。

### 步驟 A：建立 Python 工具檔案

```python
# new_tool.py
from js import document


def start_new_tool():
    container = document.getElementById("new-tool-app")
    # 在此加入工具初始化及 UI 建立程式
```

實際工具內容可自行擴充。這裡只示範入口函式與容器的對應關係。

### 步驟 B：在網頁新增 HTML 容器

```html
<div id="new-tool-app" data-python-app></div>
```

容器 ID 必須與 Python 啟動時使用的 ID **完全相同**，包括大小寫與連字號。

### 步驟 C：在 `main.py` 匯入工具函式

```python
from new_tool import start_new_tool
```

### 步驟 D：在 `main()` 中新增容器判斷

```python
if element_exists("new-tool-app"):
    start_new_tool()
```

### 步驟 E：確認 Python 檔案已被 Pyodide 載入

依照目前網站的載入機制，檢查 `manifest.json` 是否需要新增 `new_tool.py`，並確認其路徑、檔名及 `from ... import ...` 對應正確。

> 備註：新增工具通常**不需要**修改已經能共用載入流程的 `python.inline.ts`；但若新工具涉及不同的初始化時機、外部套件或資源路徑，仍需另外檢查。

## 6. 以後排除 Python GUI 啟動錯誤的順序

1. **找錯誤最後幾行**：例如 `JsNull`、`AttributeError`、`ModuleNotFoundError`、`ImportError`。
2. **檢查 HTML 容器**：在瀏覽器按 `F12`，於 Console 執行：

   ```javascript
   document.getElementById("tree-editor-app")
   ```

   若為 `null`，代表當下的網頁找不到容器。
3. **比對名稱**：HTML 的 `id`、`main.py` 的 `element_exists()`、Python 工具內的容器 ID 是否一致。
4. **檢查啟動條件**：應使用 `element_exists()`，避免 `getElementById(...) is not None`。
5. **檢查載入檔案**：若出現匯入錯誤，確認 `.py` 檔案及 `manifest.json` 是否一致。
6. **檢查初始化時機**：若容器稍後才出現在 DOM 中，應調整 TypeScript／Quartz SPA 的掛載時機，單靠 `element_exists()` 不會自動等待容器出現。
7. **重新載入並測試**：確認實際部署版本已更新；若舊檔仍被快取，可用瀏覽器強制重新整理，再觀察 Console。

## 7. 維護注意事項

- **`main.py` 只負責「載入哪個工具」**，各工具的 GUI、CSS、下載功能等應繼續留在自己的檔案中。
- 新增工具時，建議只增加 `import` 與 `main()` 內的一個判斷區塊，避免破壞其他工具。
- `unmount()` 是特定工具提供的解除掛載函式；**不是所有新工具都一定需要**。如果新增工具有事件監聽器、定時器或其他資源需要清理，應自行設計清理流程。
- `element_exists()` **只能確認執行當下的 DOM 有沒有容器**，不保證工具所需的子元素已經建立，也不會解決 Quartz SPA 頁面切換時的所有生命週期問題。
- 以目前的三個工具為例，**本次修正目標僅是容器判斷**，不需要刪除 `tree_editor.py` 原有的下載功能，也不需要更改樣式。

---

## 8. 每次修改的快速檢查表

- [ ] 新的 `.py` 工具檔已建立，啟動函式名稱正確
- [ ] `manifest.json` 已確認是否需新增工具檔案
- [ ] HTML 容器 ID 與 Python 使用的 ID 完全相同
- [ ] `main.py` 已新增正確的 `from ... import ...`
- [ ] `main()` 使用 `element_exists("...")` 判斷是否啟動
- [ ] 如需解除掛載，已設計對應的 `unmount()` 清理流程
- [ ] 在有工具容器的網頁能正常啟動
- [ ] 在沒有該工具容器的網頁不會誤啟動
- [ ] Quartz SPA 切換頁面後行為正常
- [ ] 原有功能（例如下載 SVG／PNG、Markdown）未受影響

**核心原則：先檢查 HTML 容器，再啟動對應 Python 工具。**
