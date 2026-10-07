---
title: Windows 腳本與命令列基礎
tags:
  - ps1
  - bat
  - PowerShell
  - CMD
---
## 1. `.ps1` 與 `.bat` 分別使用什麼語言？

`.ps1` 和 `.bat` 都是 Windows 上的腳本檔，但使用的語言不同。

| 副檔名 | 使用語言 | 執行環境 |
|---|---|---|
| `.ps1` | **PowerShell** | PowerShell / PowerShell 7 |
| `.bat` | **Windows Batch（批次語言）** | CMD（命令提示字元） |

---

## 2. `.bat` 是什麼？

`.bat` 是 **Batch 批次檔**。它使用的是 Windows 的批次命令語言，本質上就是把平常在 `cmd.exe` 裡輸入的命令一行一行寫進檔案，讓 Windows 自動依序執行。

`.bat` 的特色：語法比較古老、通常由 `cmd.exe` 執行、適合簡單啟動流程，例如：開啟程式、切換資料夾、執行幾條命令、呼叫其他腳本等。實例：[[bat啟動Obsidian指定Vault]]。

---

## 3. `.ps1` 是什麼？

`.ps1` 是 **PowerShell 腳本檔**。它使用的是 PowerShell 語言。

例如：

```powershell
$env:PATH = "$PSScriptRoot\tools\node;$env:PATH"

Write-Host "啟動 Quartz"

npx quartz build --serve
```

PowerShell 比 Batch 完整很多，可以處理：變數、陣列、物件、函式、條件判斷、迴圈、例外處理、檔案操作、系統管理、自動化流程等。

---

## 4. `.bat`、`.ps1`、Python 簡單類比

| Python | PowerShell | Batch |
|---|---|---|
| `.py` | `.ps1` | `.bat` |
| `python.exe` | `powershell.exe` / `pwsh.exe` | `cmd.exe` |
| `print()` | `Write-Host` | `echo` |
| `x = 10` | `$x = 10` | `set x=10` |
| `if ...` | `if (...) {...}` | `if ...` |

其中：

- PowerShell 比 `.bat` 更接近真正的程式語言。
- Batch 比較像是把 CMD 指令一行一行存起來執行。

---

## 5. PowerShell 與 CMD 是什麼？

PowerShell 和 CMD 都可以理解成：Windows 裡讓使用者「直接輸入指令控制電腦」的環境。兩者的用途有部分重疊，但年代、設計理念和能力差很多。

| 名稱         | 全名                              | 主要用途                  | 常見腳本          |
| ---------- | ------------------------------- | --------------------- | ------------- |
| CMD        | Command Prompt                  | 執行傳統 Windows / DOS 指令 | `.bat`、`.cmd` |
| PowerShell | Windows PowerShell / PowerShell | 更強的系統管理與自動化           | `.ps1`        |

---

## 6. CMD 是什麼？

CMD 是 **命令提示字元**（Command Prompt），它是 Windows 傳統的命令列環境。CMD 的核心概念：使用者在 CMD 輸入指令、cmd.exe 解讀指令、Windows 執行。

例如可以輸入：

```cmd
dir
cd C:\MyWebsite
git status
```

分別代表：

```text
dir
→ 顯示目前資料夾內的檔案

cd C:\MyWebsite
→ 切換到 C:\MyWebsite

git status
→ 查看目前 Git 狀態
```

---

## 7. PowerShell 是什麼？

PowerShell 同樣可以輸入命令，但功能比 CMD 更完整。

例如：

```powershell
Get-ChildItem
Set-Location C:\MyWebsite
git status
```

其中：

```text
Get-ChildItem
≈ CMD 的 dir

Set-Location
≈ CMD 的 cd
```

PowerShell 不只是命令列工具，還同時是一套腳本語言。

例如：

```powershell
$files = Get-ChildItem

foreach ($file in $files) {
    Write-Host $file.Name
}
```

這段程式代表：

1. 取得目前資料夾裡的檔案。
2. 存進 `$files`。
3. 使用 `foreach` 一個一個處理。
4. 顯示每個檔案的名稱。

---

## 8. Windows、CMD、PowerShell 的關係

可以把整體關係想成：

```text
Windows
├─ CMD
│   └─ 傳統命令列工具
│
└─ PowerShell
    └─ 較新的命令列 + 腳本語言 + 系統管理工具
```

---

## 9. Windows Terminal、CMD、PowerShell 並非同一個東西

這點很容易混淆。

Windows Terminal 比較像是：一個可以裝不同命令列環境的「視窗」。它本身不等於 CMD，也不等於 PowerShell。

例如：

```text
Windows Terminal
    ↓
可以開
    ├─ CMD
    ├─ Windows PowerShell
    └─ PowerShell 7
```

所以：

```text
Windows Terminal
= 顯示命令列的外殼 / 視窗

CMD
= 一種命令列環境

PowerShell
= 另一種命令列環境
```

---

## 10. `.bat`、CMD、`.ps1`、PowerShell 的關係

最重要的對應關係是：

```text
Windows
│
├─ cmd.exe
│    └─ 執行 .bat / .cmd
│
└─ powershell.exe / pwsh.exe
     └─ 執行 .ps1
```