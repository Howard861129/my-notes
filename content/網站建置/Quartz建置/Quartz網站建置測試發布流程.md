---
title: Quartz網站建置測試發布流程
tags:
  - Quartz
---

這份文件整理目前網站的日常開發流程。

日後基本上只需要記住三個指令：

```powershell
.\start-dev.ps1
dev
pub
```

---

## 1. 開啟開發環境

在 VS Code 開啟網站專案後，在 PowerShell 執行：

```powershell
.\start-dev.ps1
```

`start-dev.ps1` 會自動：

- 載入專案內的 Node.js、npm、Git
- 設定 npm cache 路徑
- 設定 npm global 路徑
- 自動切換到 Quartz 網站目錄
- 建立 `dev` 指令
- 建立 `pub` 指令
- 顯示 Node.js、npm、Git 版本

執行完成後，就可以直接使用：

```powershell
dev
```

或：

```powershell
pub
```

---

## 2. 本機建置與測試網站

輸入：

```powershell
dev
```

這個指令等同於：

```powershell
npx quartz build --serve
```

Quartz 會：

1. 建置網站
2. 啟動本機測試伺服器
3. 持續監看網站內容

成功後會看到：

```text
Started a Quartz server listening at http://localhost:8080
```

接著在瀏覽器開啟：

```text
http://localhost:8080
```

即可預覽網站。

---

## 3. 開發期間可修改的內容

本機測試網站啟動後，可以修改例如：

```text
content/*.md
quartz.config.yaml
quartz/styles/custom.scss
```

常見用途：

- 新增 Markdown 文章
- 修改文章內容
- 修改網站配色
- 修改 Quartz 設定
- 修改版面與 CSS
- 調整插件設定

修改後可以重新整理瀏覽器確認效果。

---

## 4. 停止本機測試

修改完成後，在 PowerShell 按：

```text
Ctrl + C
```

即可停止 Quartz 本機伺服器。

---

## 5. 發布網站

停止本機測試後，輸入：

```powershell
pub
```

`pub` 會呼叫：

```text
publish.ps1
```

並自動執行網站發布流程。

---

## 6. `pub` 的完整發布流程

`publish.ps1` 會依序執行：

```text
npx quartz build
        ↓
檢查是否建置成功
        ↓
   成功      失敗
    ↓         ↓
 繼續發布    停止發布
    ↓
git status
    ↓
git add .
    ↓
輸入 Commit 訊息
    ↓
git commit
    ↓
git push origin v5
    ↓
GitHub 收到更新
    ↓
網站重新部署
```

因此，即使之前已經使用 `dev` 測試過，正式發布前仍會再執行一次：

```powershell
npx quartz build
```

作為最後的建置檢查。

---

## 7. 輸入 Commit 訊息

執行：

```powershell
pub
```

後，系統會要求輸入：

```text
Commit message:
```

例如：

```text
新增立方體路徑文章
```

腳本之後會自動執行：

```powershell
git commit -m "新增立方體路徑文章"
git push origin v5
```

---

## 8. 日常完整工作流程

平常開發網站時，可以按照以下流程：

```text
開啟 VS Code
    ↓
開啟 PowerShell
    ↓
.\start-dev.ps1
    ↓
dev
    ↓
瀏覽 http://localhost:8080
    ↓
修改 / 測試網站
    ↓
Ctrl + C
    ↓
pub
    ↓
輸入更新說明
    ↓
自動 Build
    ↓
自動 Git Add
    ↓
自動 Commit
    ↓
自動 Push
    ↓
網站發布
```

---

## 9. 三個主要指令

### 載入網站開發環境

```powershell
.\start-dev.ps1
```

用途：

- 設定 Node.js
- 設定 npm
- 設定 Git
- 切換網站資料夾
- 建立 `dev`
- 建立 `pub`

---

### 啟動本機網站測試

```powershell
dev
```

等同於：

```powershell
npx quartz build --serve
```

用途：

- 建置網站
- 啟動本機預覽
- 在瀏覽器使用 `http://localhost:8080` 測試

---

### 正式發布網站

```powershell
pub
```

用途：

- 再次檢查 Quartz 是否能正常建置
- `git add .`
- 建立 Commit
- Push 到 GitHub `v5` 分支
- 觸發網站重新部署

---

## 10. 最簡化記憶方式

只需要記得：

```text
start-dev = 載入環境
dev       = 開發與測試
pub       = 正式發布
```

也就是：

```powershell
.\start-dev.ps1
dev
pub
```

其中：

- `dev` 是開發測試
- `pub` 是正式發布
- `pub` 在上傳前還會重新 Build 一次，避免把無法建置的版本推送到 GitHub
