# Quartz + Pyodide 多 Python 功能模組新增流程

## 1. 架構目的

目前網站採用：

```text
Quartz
+
GitHub Pages
+
TypeScript 啟動器
+
Pyodide
+
Python
```

其中各檔案的角色固定如下：

```text
python.inline.ts
= 通用 Python 啟動器
= 負責啟動 Pyodide、載入 Python 專案
= 一般新增 Python 功能時不需要再修改

manifest.json
= Python 檔案清單
= 告訴 python.inline.ts 要把哪些 .py 檔下載進 Pyodide

main.py
= Python 專案總入口
= 判斷目前頁面需要啟動哪個 Python 功能

其他 .py
= 各功能真正的 GUI、邏輯與演算法
```

---

## 2. 建議資料夾結構

例如：

```text
quartz/
└─ static/
   └─ python/
      ├─ manifest.json
      ├─ main.py
      ├─ gui_test.py
      ├─ akari_gui.py
      └─ matrix_tool.py
```

Quartz 自訂 TypeScript：

```text
quartz/
└─ custom/
   └─ scripts/
      └─ python.inline.ts
```

---

## 3. `python.inline.ts` 的角色

目前 `python.inline.ts` 已經改成通用啟動器。

它負責：

```text
目前頁面
↓
檢查是否存在 data-python-app
↓
啟動 Pyodide
↓
讀取 manifest.json
↓
下載 manifest.json 內列出的 Python 檔案
↓
放入 Pyodide 的 /app 虛擬資料夾
↓
執行 main.py
```

因此：

> 一般新增新的 Python 功能時，不需要再修改 `python.inline.ts`。

只有未來要修改：

- Pyodide 載入方式
- Python 專案下載方式
- 網站根路徑判斷方式
- 虛擬檔案系統架構

才需要再動 `python.inline.ts`。

---

## 4. `manifest.json` 的角色

`manifest.json` 用來告訴 TypeScript：

> 目前 Python 專案有哪些 `.py` 檔案需要下載。

例如：

```json
{
  "entry": "main.py",
  "files": [
    "main.py",
    "gui_test.py",
    "akari_gui.py",
    "matrix_tool.py"
  ]
}
```

其中：

```json
"entry": "main.py"
```

代表：

> 所有 Python 檔案載入完成後，從 `main.py` 開始執行。

而：

```json
"files": [...]
```

則是完整 Python 檔案清單。

---

## 5. `main.py` 的角色

`main.py` 是 Python 專案的總入口。

它不負責實際功能，而是：

1. 匯入各功能的啟動函數
2. 判斷目前頁面有哪些 App 容器
3. 啟動對應功能

例如：

```python
from js import document  # pyright: ignore[reportMissingImports]

from gui_test import start_gui
from akari_gui import start_akari
from matrix_tool import start_matrix


def main():

    if document.getElementById("gui-test-app"):
        start_gui()

    if document.getElementById("akari-app"):
        start_akari()

    if document.getElementById("matrix-app"):
        start_matrix()


if __name__ == "__main__":
    main()
```

因此：

```text
main.py
↓
檢查目前頁面
↓
有 gui-test-app？
→ 執行 start_gui()

有 akari-app？
→ 執行 start_akari()

有 matrix-app？
→ 執行 start_matrix()
```

---

## 6. Markdown 頁面的角色

每一個 Python 功能頁面需要放一個對應的 HTML 容器。

例如 GUI 測試：

```html
<div id="gui-test-app" data-python-app></div>
```

數燈工具：

```html
<div id="akari-app" data-python-app></div>
```

矩陣工具：

```html
<div id="matrix-app" data-python-app></div>
```

這裡有兩個重要部分。

### `data-python-app`

```html
data-python-app
```

用途：

> 告訴 `python.inline.ts`：這個頁面需要啟動 Python。

因此 TypeScript 不需要知道這是哪一種功能。

---

### `id`

例如：

```html
id="akari-app"
```

用途：

> 告訴 `main.py`：目前頁面要啟動哪一個 Python 功能。

因此可以記成：

```text
data-python-app
= 給 TypeScript 看

id="..."
= 給 Python main.py 看
```

---

# 7. 新增一個 Python 功能的固定流程

假設現在要新增：

```text
statistics.py
```

而它負責一個統計工具。

---

## 步驟 1：新增 `.py` 檔案

在：

```text
quartz/static/python/
```

新增：

```text
statistics.py
```

例如：

```python
from js import document  # pyright: ignore[reportMissingImports]


def start_statistics():

    root = document.getElementById("statistics-app")

    if root is None:
        raise RuntimeError("找不到 #statistics-app")

    root.innerHTML = ""

    title = document.createElement("h2")
    title.textContent = "統計工具"

    root.appendChild(title)
```

每個獨立功能最好提供自己的啟動函數，例如：

```python
def start_statistics():
```

---

## 步驟 2：修改 `manifest.json`

原本：

```json
{
  "entry": "main.py",
  "files": [
    "main.py",
    "gui_test.py",
    "akari_gui.py"
  ]
}
```

新增：

```json
"statistics.py"
```

變成：

```json
{
  "entry": "main.py",
  "files": [
    "main.py",
    "gui_test.py",
    "akari_gui.py",
    "statistics.py"
  ]
}
```

目的：

> 讓 `python.inline.ts` 知道還要下載 `statistics.py`。

---

## 步驟 3：修改 `main.py`

加入：

```python
from statistics import start_statistics
```

再在：

```python
def main():
```

裡加入：

```python
if document.getElementById("statistics-app"):
    start_statistics()
```

完整概念：

```python
from js import document  # pyright: ignore[reportMissingImports]

from gui_test import start_gui
from akari_gui import start_akari
from statistics import start_statistics


def main():

    if document.getElementById("gui-test-app"):
        start_gui()

    if document.getElementById("akari-app"):
        start_akari()

    if document.getElementById("statistics-app"):
        start_statistics()


if __name__ == "__main__":
    main()
```

---

## 步驟 4：在 Markdown 頁面放 App 容器

例如：

```html
<div id="statistics-app" data-python-app></div>
```

流程：

```text
Markdown
↓
data-python-app
↓
python.inline.ts 啟動 Pyodide
↓
main.py
↓
發現 statistics-app
↓
start_statistics()
↓
statistics.py 建立 GUI
```

---

# 8. 新增功能時要修改哪些檔案

之後新增獨立 Python 功能，可以固定記成：

```text
1. 新增新的 .py
2. manifest.json 加入該 .py 名稱
3. main.py 加入 from ... import ...
4. main.py 加入 if ... : 啟動函數()
5. Markdown 加入對應 <div id="..." data-python-app>
```

而：

```text
python.inline.ts
```

通常：

```text
不用修改
```

---

# 9. 最簡化記憶版

## 新增功能

假設新增：

```text
akari_gui.py
```

### Python 檔

```python
def start_akari():
    ...
```

### `manifest.json`

```json
"akari_gui.py"
```

### `main.py`

```python
from akari_gui import start_akari
```

以及：

```python
if document.getElementById("akari-app"):
    start_akari()
```

### Markdown

```html
<div id="akari-app" data-python-app></div>
```

---

# 10. 整體架構圖

```text
Quartz Markdown
│
│ <div id="akari-app" data-python-app>
│
▼
python.inline.ts
│
│ 發現 data-python-app
│
▼
Pyodide
│
▼
manifest.json
│
│ 讀取所有 .py
│
▼
/app 虛擬 Python 專案
│
▼
main.py
│
│ 判斷 id="akari-app"
│
▼
start_akari()
│
▼
akari_gui.py
│
▼
建立 GUI / 執行 Python 功能
```

---

# 11. 各檔案職責總結

| 檔案 | 職責 | 新增功能時是否通常要改 |
|---|---|---|
| `python.inline.ts` | 啟動 Pyodide、載入 Python 專案 | 否 |
| `manifest.json` | 列出所有 Python 檔案 | 是 |
| `main.py` | 判斷頁面、啟動對應功能 | 是 |
| `xxx.py` | 實際功能、GUI、演算法 | 新增 |
| `xxx.md` | 放置對應 App 容器 | 是 |

---

# 12. 核心原則

可以把目前架構記成四句：

```text
python.inline.ts
= Python 引擎啟動器

manifest.json
= Python 檔案清單

main.py
= Python 功能調度器

其他 .py
= 真正功能
```

新增功能時：

```text
新增 .py
↓
加入 manifest.json
↓
在 main.py import
↓
在 main.py 加 if 判斷
↓
Markdown 加對應 div
```

這樣之後即使網站增加很多 Python 工具，也不需要反覆修改底層的 `python.inline.ts`。
