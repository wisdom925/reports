# reports

Wisdom 的互動式 HTML 報告站，部署到 GitHub Pages：

- 首頁：<https://wisdom925.github.io/reports/>
- 報告目錄：`reports/`
- 報告索引：`reports/manifest.json`
- Hermes 技能：`.hermes/skills/html-report/`
- Claude Code 相容技能：`.claude/skills/html-report/`

這個 repo 是從 `voidful/claude-html-report-skill` 改成 Hermes 可直接使用的版本，同時保留 Claude Code 相容目錄。

## 一次性安裝到 Hermes

在這台 Mac mini 上執行：

```bash
mkdir -p ~/.hermes/skills
ln -sfn /Users/wisdom/reports/.hermes/skills/html-report ~/.hermes/skills/html-report
```

驗證：

```bash
hermes skills list | grep html-report
```

之後在 Hermes 對話中只要說「用 html-report 產生報告」，Hermes 會讀取這個 skill。

## 使用方式

1. 產生一個單檔 HTML：
   `reports/<YYYY-MM-DD>-<slug>.html`
2. 使用 `.hermes/skills/html-report/templates/base.html` 作為起點。
3. 發布：

```bash
python3 .hermes/skills/html-report/scripts/publish.py \
  reports/<YYYY-MM-DD>-<slug>.html \
  "報告標題" \
  "一句話摘要"
```

腳本會：

- 更新 `reports/manifest.json`
- `git add -A`
- `git commit -m "report: <報告標題>"`
- `git push`
- 印出公開網址

## 草稿模式

不想推送時：

```bash
python3 .hermes/skills/html-report/scripts/publish.py \
  reports/<YYYY-MM-DD>-<slug>.html \
  "報告標題" \
  "一句話摘要" \
  --draft
```

草稿模式只更新本機 manifest，不 commit、不 push。

## 報告品質要求

每份報告至少要使用三種 HTML 互動能力，例如：

- 圖表
- 可排序或可篩選表格
- tabs
- collapsible sections
- Mermaid 圖
- KaTeX 公式
- sticky TOC
- dark mode
- 搜尋或篩選輸入框

中文報告一律使用正體中文與台灣用語。投資、新聞、公司與人名資訊發布前要核對，不要混淆實體關係。

## 更新 upstream skill

若要同步原作者更新，只更新技能檔，不覆蓋既有報告：

```bash
git remote add upstream https://github.com/voidful/claude-html-report-skill.git 2>/dev/null || true
git fetch upstream
git checkout upstream/main -- .claude/skills/html-report/scripts .claude/skills/html-report/templates
cp -R .claude/skills/html-report/scripts .hermes/skills/html-report/
cp -R .claude/skills/html-report/templates .hermes/skills/html-report/
```
