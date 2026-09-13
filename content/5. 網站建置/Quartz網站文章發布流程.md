---
title: Quartz網站文章發布流程
tags:
  - Quartz
---

這份文件整理日後透過 Obsidian、Quartz、Git 與 GitHub Pages 發布文章的固定流程。

## 網站資訊

- 本機專案：`C:\Users\howar\Documents\MyWebsite\site`
- 文章目錄：`C:\Users\howar\Documents\MyWebsite\site\content`
- Git 分支：`v5`
- 網站：[https://Howard861129.github.io/my-notes/](https://Howard861129.github.io/my-notes/)

## 開啟 VS Code 與 PowerShell

### 1. 開啟 VS Code

在 Windows 的「開始」選單搜尋並開啟：

```text
Visual Studio Code
```

進入：

```text
File（檔案）
→ Open Folder（開啟資料夾）
```

選擇網站專案資料夾：

```text
C:\Users\howar\Documents\MyWebsite\site
```

如果首頁的「最近使用」已經出現 `site`，直接點選即可。

### 2. 在 VS Code 開啟 PowerShell

在 VS Code 上方選單進入：

```text
Terminal（終端機）
→ New Terminal（新增終端機）
```

終端機會出現在畫面下方。右上方的終端機類型應為：

```text
PowerShell
```

若不是 PowerShell，可點終端機右上方的下拉箭頭，選擇 **PowerShell**。

### 3. 載入網站開發環境

在 PowerShell 輸入：

```powershell
cd C:\Users\howar\Documents\MyWebsite
.\start-dev.ps1
cd site
```

完成後，命令提示字元應顯示：

```text
PS C:\Users\howar\Documents\MyWebsite\site>
```

這表示目前已經位於正確的網站專案中，接下來可以使用 Quartz、npm 與 Git 指令。

如果 PowerShell 原本就已載入開發環境，而且位置已經是 `site`，便不必重複執行上述三行。

## 完整發布流程

### 1. 在 Obsidian 編輯文章

在下列資料夾新增或修改 Markdown 文章：

```text
C:\Users\howar\Documents\MyWebsite\site\content
```

例如：

```text
content\立方體路徑研究.md
```

> 注意：提交到 GitHub 的 `content` 內容都可能公開，發布前應確認沒有私人筆記、個人資料或不應公開的附件。

### 2. 在本機預覽

使用 VS Code 下方的 PowerShell。若目前不在網站專案，先進入網站目錄：

```powershell
cd C:\Users\howar\Documents\MyWebsite\site
```

啟動 Quartz 預覽：

```powershell
npx quartz build --serve
```

開啟終端機顯示的本機網址，通常是：

```text
http://localhost:8080
```

確認下列內容是否正常：

- 文章文字與標題
- 圖片與附件
- 數學公式
- 內部連結與外部連結
- 程式碼區塊與語法高亮

確認完畢後，在 PowerShell 按下 `Ctrl + C` 停止預覽。

### 3. 檢查即將發布的檔案

```powershell
git status
```

確認清單中沒有私人筆記或不應公開的檔案。

### 4. 將修改加入待提交區

```powershell
git add .
```

再次檢查：

```powershell
git status
```

準備發布的檔案應顯示在：

```text
Changes to be committed
```

Windows 出現「`CRLF will be replaced by LF`」通常只是換行格式提示，不是錯誤。

### 5. 建立版本紀錄

```powershell
git commit -m "本次更新內容"
```

例如：

```powershell
git commit -m "Add cube path article"
git commit -m "Update homepage"
git commit -m "Fix article formatting"
```

### 6. 上傳並自動發布

```powershell
git push origin v5
```

Push 成功時，終端機會顯示類似：

```text
v5 -> v5
```

GitHub Actions 隨後會自動執行：

```text
接收新的 Git 版本
→ 建置 Quartz 網站
→ 部署至 GitHub Pages
→ 更新公開網站
```

不需要手動上傳 `public` 資料夾，也不需要每次重新建立 `deploy.yml`。

### 7. 確認發布結果

1. 開啟 GitHub repository。
2. 進入 **Actions**。
3. 確認最新部署顯示綠色勾勾。
4. 開啟網站確認文章已更新：

[https://Howard861129.github.io/my-notes/](https://Howard861129.github.io/my-notes/)

第一次部署或網站更新可能需要幾分鐘才會生效。

## 日常精簡版

開啟 VS Code 的 `site` 資料夾，再開啟內建 PowerShell，載入開發環境：

```powershell
cd C:\Users\howar\Documents\MyWebsite
.\start-dev.ps1
cd site
```

啟動預覽：

```powershell
cd C:\Users\howar\Documents\MyWebsite\site
npx quartz build --serve
```

確認後按 `Ctrl + C`，再發布：

```powershell
git status
git add .
git status
git commit -m "本次更新內容"
git push origin v5
```

## 常見狀況

### 沒有任何內容可以提交

如果執行 `git commit` 時看到：

```text
nothing to commit, working tree clean
```

表示目前沒有尚未提交的修改。

### GitHub 登入視窗再次出現

選擇 Git Credential Manager 的 `manager` 登入方式，完成瀏覽器中的 GitHub 授權即可。

### GitHub Actions 出現紅色叉叉

進入：

```text
GitHub repository
→ Actions
→ 失敗的部署紀錄
```

展開紅色步驟查看錯誤。網站不會因為這次建置失敗而正確更新，應先排除錯誤後再重新發布。

### 中文檔名顯示成跳脫編碼

可以針對目前專案設定：

```powershell
git config core.quotepath false
```

之後 `git status` 會較容易直接顯示中文檔名。
