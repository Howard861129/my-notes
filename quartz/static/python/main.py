from js import document
from pyodide.ffi import create_proxy


# ==================================================
# 1. 找到 Quartz 頁面中的 Python GUI 容器
# ==================================================

root = document.getElementById("python-app")

if root is None:
    raise RuntimeError("找不到 #python-app")


# 清空原本內容
root.innerHTML = ""


# ==================================================
# 2. 建立標題
# ==================================================

title = document.createElement("h2")
title.textContent = "Python GUI 測試"

root.appendChild(title)


# ==================================================
# 3. 建立 m 輸入欄位
# ==================================================

label_m = document.createElement("label")
label_m.textContent = "m："

input_m = document.createElement("input")
input_m.type = "number"
input_m.value = "5"
input_m.min = "1"

label_m.appendChild(input_m)

root.appendChild(label_m)


# ==================================================
# 4. 換行
# ==================================================

root.appendChild(
    document.createElement("br")
)


# ==================================================
# 5. 建立 n 輸入欄位
# ==================================================

label_n = document.createElement("label")
label_n.textContent = "n："

input_n = document.createElement("input")
input_n.type = "number"
input_n.value = "5"
input_n.min = "1"

label_n.appendChild(input_n)

root.appendChild(label_n)


# ==================================================
# 6. 再換行
# ==================================================

root.appendChild(
    document.createElement("br")
)

root.appendChild(
    document.createElement("br")
)


# ==================================================
# 7. 建立按鈕
# ==================================================

button = document.createElement("button")
button.textContent = "開始計算"

root.appendChild(button)


# ==================================================
# 8. 建立結果區
# ==================================================

output = document.createElement("pre")
output.textContent = "尚未計算"

root.appendChild(output)


# ==================================================
# 9. Python 按鈕事件
# ==================================================

def calculate(event):

    try:
        m = int(input_m.value)
        n = int(input_n.value)

        if m < 1 or n < 1:
            output.textContent = "m、n 必須大於等於 1"
            return

        result = m * n

        output.textContent = (
            f"輸入：m = {m}, n = {n}\n"
            f"Python 計算結果：{result}"
        )

    except ValueError:
        output.textContent = "請輸入有效整數"


# ==================================================
# 10. 把 Python 函式轉成瀏覽器 callback
# ==================================================

calculate_proxy = create_proxy(calculate)

button.addEventListener(
    "click",
    calculate_proxy
)