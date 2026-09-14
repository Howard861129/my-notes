# Pages CMS 文章管理流程

本文件整理目前網站使用 **Pages CMS + GitHub + Quartz** 時，新增、修改、刪除一般文章，以及修改首頁的操作流程。

---

## 一、整體運作方式

Pages CMS 會直接修改 GitHub `v5` 分支中的 Markdown 檔案。

```text
Pages CMS
   ↓
GitHub v5
   ↓
content/*.md
   ↓
GitHub Actions
   ↓
Quartz 重新建置
   ↓
網站更新
```

因此，使用 Pages CMS 編輯網站內容時，正常情況下不需要再手動執行：

```powershell
git add .
git commit
git push
```

---

## 二、新增一般文章

### 1. 進入 Pages CMS

進入：

```text
my-notes
→ v5
→ 文章
```

### 2. 選擇文章要放的位置

如果文章要放在 `content/` 根目錄，可按右上角：

```text
Add an entry
```

如果文章要放進既有資料夾，例如：

```text
5. 網站建置/
```

則找到該資料夾，按右側的：

```text
＋
```

這樣新文章會直接建立在該資料夾內。

### 3. 填寫檔名

Filename 建議直接輸入完整中文檔名，並包含 `.md`。

例如：

```text
網站架設筆記.md
```

不要只輸入：

```text
網站架設筆記
```

目前不建議依賴 Pages CMS 由中文標題自動產生檔名，因為自動 slug 處理可能無法正確保留中文。

### 4. 填寫標題

標題不需要加 `.md`。

例如：

```text
網站架設筆記
```

因此：

```text
Filename：網站架設筆記.md
標題：網站架設筆記
```

### 5. 撰寫文章內容

例如：

```markdown
# 網站架設筆記

這裡記錄網站建置過程。

## Pages CMS

Pages CMS 可以直接透過瀏覽器管理 Markdown 文章。
```

不需要自己在文章內容中加入：

```yaml
---
title: 網站架設筆記
---
```

Pages CMS 會依「標題」欄位自動建立 YAML frontmatter。

### 6. 儲存

完成後按：

```text
Save
```

例如文章建立在：

```text
content/
└── 5. 網站建置/
    └── 網站架設筆記.md
```

之後 GitHub Actions 會自動重新建置 Quartz，網站便會更新。

---

## 三、修改一般文章

### 1. 找到文章

進入：

```text
Pages CMS
→ 文章
```

找到要修改的文章。

### 2. 開啟編輯

按文章右側：

```text
Edit
```

### 3. 修改內容

可以修改：

- 標題
- 文章內容

文章內容右上角可切換：

```text
Editor | Source
```

`Editor` 適合一般編輯。

`Source` 可直接修改 Markdown 原始碼。

### 4. 儲存

修改完成後按：

```text
Save
```

Pages CMS 會直接更新 GitHub 中原本的 `.md` 檔案，之後 Quartz 會自動重新建置網站。

---

## 四、刪除一般文章

### 1. 找到文章

進入：

```text
Pages CMS
→ 文章
```

### 2. 開啟更多操作

找到文章右側的：

```text
⋮
```

### 3. 刪除

選擇：

```text
Delete
```

再確認刪除。

Pages CMS 會刪除 GitHub 中對應的 Markdown 檔案。

例如：

```text
content/5. 網站建置/網站架設筆記.md
```

重新部署後，網站上的文章也會消失。

---

## 五、修改首頁

網站首頁對應：

```text
content/index.md
```

首頁不放在一般「文章」清單中，而是由 Pages CMS 左側獨立的：

```text
首頁
```

項目管理。

### 1. 進入首頁

在 Pages CMS 左側選：

```text
首頁
```

### 2. 修改標題

例如：

```text
宇子禾的工程筆記
```

### 3. 修改首頁內容

例如：

```markdown
# 歡迎來到我的工程筆記

這裡整理我的工程、數學、程式與網站研究筆記。

## 主要內容

- 數學研究
- 程式研究
- 真空管研究
- Minecraft 研究
- 網站建置
```

可以使用：

```text
Editor
```

或：

```text
Source
```

進行編輯。

### 4. 儲存

完成後按：

```text
Save
```

Pages CMS 會直接修改：

```text
content/index.md
```

GitHub Actions 重新部署完成後，正式網站首頁就會更新。

---

## 六、日常使用速查

### 新增一般文章

```text
Pages CMS
→ 文章
→ 選資料夾
→ ＋
→ Filename：文章名稱.md
→ 標題：文章名稱
→ 撰寫內容
→ Save
```

### 修改一般文章

```text
Pages CMS
→ 文章
→ 找到文章
→ Edit
→ 修改
→ Save
```

### 刪除一般文章

```text
Pages CMS
→ 文章
→ 找到文章
→ ⋮
→ Delete
→ 確認
```

### 修改首頁

```text
Pages CMS
→ 首頁
→ 修改標題或內容
→ Save
```

---

## 七、注意事項

### 1. 中文檔名

新增文章時，建議手動輸入：

```text
文章名稱.md
```

例如：

```text
立方體路徑問題.md
```

標題則填：

```text
立方體路徑問題
```

不要在標題欄加入 `.md`。

### 2. 舊文章名稱顯示空白

如果 Pages CMS 的文章清單中出現空白名稱，通常代表該舊 Markdown 沒有：

```yaml
---
title: 文章標題
---
```

補上 `title` 後，文章名稱即可正常顯示。

### 3. Pages CMS 儲存後不必再手動 Git Push

使用 Pages CMS 按下 `Save` 後，內容會直接寫入 GitHub。

因此不需要再另外執行：

```powershell
git add .
git commit
git push
```

除非你另外在本機修改了網站檔案。

---

## 八、最簡化的工作方式

日後如果只是新增或修改網站文章：

```text
開啟瀏覽器
→ Pages CMS
→ 編輯
→ Save
```

即可完成網站內容更新。
