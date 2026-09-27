---
title: .bat 啟動 Obsidian 指定 Vault
tags:
  - bat
  - Obsidian
---
## 1. 程式碼

```bat
@echo off
start "" "obsidian://open?vault=72f5e1c436beda85"
exit
```

這段 `.bat` 的功能是：

> 使用 Windows 的 Obsidian URI 開啟指定 Vault，然後讓這個批次檔本身結束並關閉 CMD 視窗。

```bat
@echo off
```

> 不要顯示正在執行哪些 CMD 指令。

```bat
start "" "obsidian://open?vault=72f5e1c436beda85"
```

> Windows，請另外啟動 Obsidian，並開啟指定的 Vault。

```bat
exit
```

> 工作已經完成，關閉這個 CMD。

---

### (1) 第一行

```bat
@echo off
```

> 不要把批次檔正在執行的每一條指令顯示在 CMD 視窗中。

如果沒有這行，執行 `.bat` 時可能會看到：

```text
C:\xxx>start "" "obsidian://open?vault=72f5e1c436beda85"

C:\xxx>exit
```

加入：

```bat
@echo off
```

之後，這些指令本身就不會顯示，畫面會比較乾淨。

---

```bat
echo off
```

> 關閉 CMD 的「指令回顯」。

也就是執行指令時，不再把指令內容顯示出來。

---

```text
@
```

代表：

> 連目前這一行本身也不要顯示。

因此：

```bat
@echo off
```

> 從現在開始，不要顯示正在執行的批次指令，而且這一行自己也不要顯示。

---

### (2) 第二行

```bat
start "" "obsidian://open?vault=72f5e1c436beda85"
```

這是整份程式最重要的一行，可以拆成：

```text
start
│
├─ ""
│
└─ "obsidian://open?vault=72f5e1c436beda85"
```

`start` 是 Windows CMD 的內建指令，用來啟動：程式、文件、網址、URI

例如：

```bat
start notepad.exe
```

會開啟記事本。

又例如：

```bat
start https://www.google.com
```

會使用預設瀏覽器開啟 Google。

因此：

```bat
start "" "obsidian://open?vault=72f5e1c436beda85"
```

就是要求 Windows：

> 另外啟動一個程式來處理這個 `obsidian://` URI。

Windows 知道 `obsidian://` 是由 Obsidian 註冊處理，因此會把這個 URI 交給 Obsidian。

---

```text
""
```

不是網址，也不是 Obsidian 的參數。

它代表的是：

> `start` 指令的「視窗標題」。

`start` 有一個比較特殊的語法規則：如果 `start` 後面的第一個參數被雙引號包起來，CMD 會把它當成視窗標題。

例如：

```bat
start "我的視窗" notepad.exe
```

可以理解成：

```text
視窗標題 = 我的視窗
執行程式 = notepad.exe
```

因此，如果真正要執行的內容本身也需要雙引號，通常會故意先放一個空字串：

```bat
start "" "真正要開啟的東西"
```

意思是：

```text
視窗標題 = 空白
真正要執行 = 後面的內容
```

`""` 看起來雖然很多餘，其實是在避免 `start` 誤判參數。

---

```text
obsidian://open?vault=72f5e1c436beda85
```

這叫做 **Obsidian URI**。

一般網頁網址會使用：

```text
https://
```

而 Obsidian 可以使用：

```text
obsidian://
```

讓 Windows 把特定操作交給 Obsidian 處理。

---

```text
obsidian://
```

代表：

> 使用 Obsidian 的 URI 協定。

Windows 如果已安裝 Obsidian，通常會知道：

```text
obsidian://
```

應該交給 Obsidian 程式處理。

---

```text
open
```

代表：

> 執行「開啟」動作。

也就是要求 Obsidian 開啟某個 Vault 或檔案。

---

```text
?
```

代表：

> 後面開始放參數。

這種格式和一般網址的 Query String 很類似。

例如：

```text
https://example.com?id=123
```

其中：

```text
?id=123
```

就是傳入額外參數。

---

```text
vault=72f5e1c436beda85
```

代表：

> 指定要開啟哪一個 Obsidian Vault。

其中：

```text
vault=
```

是參數名稱。

而：

```text
72f5e1c436beda85
```

是該 Vault 對應的識別值。

因此整句：

```text
obsidian://open?vault=72f5e1c436beda85
```

可以理解成：

> 請 Obsidian 開啟 ID 為 `72f5e1c436beda85` 的 Vault。

---

### (3) 第三行

```bat
exit
```

這行代表：

> 結束目前這個 CMD。

因此當前面的：

```bat
start "" "obsidian://open?vault=72f5e1c436beda85"
```

已經把 Obsidian 另外啟動之後，`.bat` 就不需要繼續存在了。

所以執行：

```bat
exit
```

把自己的 CMD 視窗關閉。

---

## 2. 執行流程

執行流程如下：

```text
雙擊 .bat
   ↓
Windows 開啟 CMD
   ↓
執行 @echo off
   ↓
隱藏批次指令內容
   ↓
執行 start
   ↓
把 obsidian:// URI 交給 Windows
   ↓
Windows 判斷 obsidian:// 應由 Obsidian 處理
   ↓
Obsidian 開啟指定 Vault
   ↓
.bat 執行 exit
   ↓
CMD 視窗關閉
   ↓
Obsidian 繼續獨立運作
```

---

## 3. 補充

為什麼 CMD 關閉後 Obsidian 不會一起關閉？關鍵在：

```bat
start
```

`start` 的概念可以理解成：

> 「另外啟動這個東西。」

因此目前的 CMD 並不是一直控制著 Obsidian。

流程比較像：

```text
CMD
 │
 │ start
 ▼
Windows
 │
 ▼
Obsidian
```

當 Windows 已經把 Obsidian 啟動後：

```text
CMD → 可以結束
Obsidian → 繼續執行
```

因此：

```bat
exit
```

只會關閉目前這個批次檔所在的 CMD，不會把 Obsidian 一起關掉。

