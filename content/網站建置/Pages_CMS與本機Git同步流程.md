---
title: Pages CMS與本機Git同步流程
tags:
  - Pages CMS
---

本文件整理目前網站使用 **Pages CMS + GitHub + Quartz + 本機 VS Code / PowerShell** 時的同步方式。

---

## 一、核心觀念

現在網站內容可能從兩個地方被修改：

```text
Pages CMS ──→ GitHub ←──→ 本機
                 │
                 ↓
             Quartz 網站
```

其中：

- **Pages CMS** 會直接修改 GitHub 上的 Markdown
- **本機** 會修改 Quartz、CSS、JavaScript、設定檔與文章
- **GitHub** 應視為中央版本
- **Quartz / GitHub Actions** 負責重新建置網站

因此，未來本機做重大修改時，不應直接把本機版本強制推上 GitHub，而應先同步 GitHub 上的最新內容。

---

## 二、平常只寫文章時

如果只是新增、修改或刪除文章：

```text
Pages CMS
→ 編輯文章
→ Save
→ GitHub 更新
→ Quartz 自動重新建置
```

此時通常不需要開 VS Code，也不需要執行：

```powershell
git add .
git commit
git push
```

---

## 三、本機開始重大修改前

例如要修改：

- Quartz 設定
- 網站版型
- CSS
- JavaScript
- 網站功能
- 小遊戲
- 導覽列
- 自訂元件
- 大量文章

先進入網站目錄：

```powershell
cd C:\Users\howar\Documents\MyWebsite\site
```

接著先同步 GitHub 最新版本：

```powershell
git pull --rebase origin v5
```

這一步的目的，是先把 Pages CMS 或其他 GitHub 修改同步到本機。

---

## 四、本機進行修改

同步完成後，再進行本機開發。

例如啟動本機預覽：

```powershell
dev
```

完成 CSS、Quartz、JavaScript、文章或其他功能修改後，再進入提交流程。

---

## 五、本機修改完成後

先檢查修改內容：

```powershell
git status
```

確認沒有不該提交的檔案後：

```powershell
git add .
```

建立本機 commit：

```powershell
git commit -m "Update website features"
```

或中文：

```powershell
git commit -m "網站功能更新"
```

這一步相當於先把本機成果封存成一個版本。

---

## 六、Push 前再次同步 GitHub

即使開始開發前已經執行過：

```powershell
git pull --rebase origin v5
```

在真正 push 前仍建議再執行一次：

```powershell
git pull --rebase origin v5
```

原因是：

```text
開始開發
↓
你在本機修改 1～2 小時
↓
期間可能又用 Pages CMS 修改文章
↓
GitHub 已經比本機更新
```

第二次 `pull --rebase` 可以把這段期間 GitHub 新增的內容同步回本機。

---

## 七、最後發布

同步完成且沒有衝突後：

```powershell
git push origin v5
```

之後：

```text
本機修改
↓
GitHub v5
↓
GitHub Actions
↓
Quartz Build
↓
網站更新
```

---

# 八、完整重大修改流程

日後可以固定使用以下流程。

## 開始網站開發前

```powershell
git pull --rebase origin v5
```

## 進行網站修改

```powershell
dev
```

完成修改後：

```powershell
git status
```

## 建立本機版本

```powershell
git add .

git commit -m "網站功能更新"
```

## 再次同步 Pages CMS / GitHub 期間產生的新修改

```powershell
git pull --rebase origin v5
```

## 發布

```powershell
git push origin v5
```

---

## 九、為什麼使用 `git pull --rebase`

假設 GitHub 與本機已經各自有新的 commit。

例如：

```text
A ── B ── C    GitHub
     \
      D ── E   本機
```

其中：

- `C` 可能是 Pages CMS 建立的文章修改
- `D、E` 是本機網站修改

執行：

```powershell
git pull --rebase origin v5
```

Git 會整理成：

```text
A ── B ── C ── D' ── E'
```

也就是：

1. 先保留 GitHub 最新內容
2. 再把本機修改接到後面
3. 最後形成一條較乾淨的 commit 歷史

---

## 十、不同檔案通常會自動合併

例如 GitHub 上 Pages CMS 修改：

```text
content/5. 網站建置/Pages CMS筆記.md
```

而本機修改：

```text
quartz/styles/custom.scss
```

這兩者通常不會衝突。

執行：

```powershell
git pull --rebase origin v5
```

Git 通常可以自動合併。

最後本機同時保留：

```text
✓ GitHub 最新文章
✓ Pages CMS 修改
✓ 本機 CSS
✓ 本機 Quartz 設定
```

---

# 十一、發生 Git 衝突時

如果 Pages CMS 與本機同時修改了：

```text
同一個檔案
```

而且修改了：

```text
同一段內容
```

Git 可能無法自動判斷要保留哪一版。

此時會看到：

```text
CONFLICT
```

先執行：

```powershell
git status
```

Git 會列出衝突檔案。

---

## 十二、衝突檔案的樣子

打開衝突檔案後，可能看到：

```text
<<<<<<< HEAD
GitHub / Pages CMS 的內容
=======
本機修改的內容
>>>>>>> 本機 commit
```

例如：

```markdown
<<<<<<< HEAD
# Pages CMS 教學

這是 GitHub 上的新內容。
=======
# Pages CMS 使用方法

這是本機修改的內容。
>>>>>>> 本機 commit
```

你需要人工決定最後內容。

例如整理成：

```markdown
# Pages CMS 使用方法

這是最後整理完成的正式內容。
```

並刪掉：

```text
<<<<<<<
=======
>>>>>>>
```

---

## 十三、處理完衝突後

先把解決完成的檔案加入 Git：

```powershell
git add "content/5. 網站建置/Pages CMS筆記.md"
```

接著：

```powershell
git rebase --continue
```

如果還有其他衝突，就繼續處理。

全部完成後：

```powershell
git push origin v5
```

---

# 十四、如果不想繼續處理衝突

如果衝突太多，或不確定自己是否處理正確，可以取消這次 rebase：

```powershell
git rebase --abort
```

Git 會回到執行 rebase 前的狀態。

此時可以重新確認本機與 GitHub 的差異後，再決定如何處理。

---

# 十五、不要使用強制 Push

現在 Pages CMS 會直接建立 GitHub commit，因此不建議使用：

```powershell
git push --force
```

或：

```powershell
git push -f
```

因為這可能直接覆蓋 GitHub 上 Pages CMS 新增或修改的文章。

原則是：

> **先把 GitHub 的修改合併到本機，再把本機修改推回 GitHub。**

不要用本機版本強制覆蓋 GitHub。

---

# 十六、最簡單的使用原則

## 平常寫文章

```text
Pages CMS
→ Save
→ 完成
```

## 重大網站修改

```text
git pull --rebase
↓
本機修改
↓
git add .
↓
git commit
↓
git pull --rebase
↓
git push
```

---

# 十七、日常速查

## 開始重大修改前

```powershell
git pull --rebase origin v5
```

## 修改完成

```powershell
git status

git add .

git commit -m "網站功能更新"
```

## 發布前再次同步

```powershell
git pull --rebase origin v5
```

## 發布

```powershell
git push origin v5
```

## 發生衝突

```powershell
git status
```

人工修改衝突檔案後：

```powershell
git add "衝突檔案路徑"

git rebase --continue
```

如果想放棄：

```powershell
git rebase --abort
```

---

# 十八、最後記住一句話

```text
Pages CMS 改文章
        ↓
      GitHub
        ↑
本機重大修改
```

因此：

> **GitHub 是中央版本。先同步，再修改；Push 前再同步一次。**
