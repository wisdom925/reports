---
name: html-report
description: Generate a rich, interactive HTML report and publish it to Wisdom's GitHub Pages reports site. Use when the user asks for a report, writeup, summary page, dashboard, share link, investment analysis page, or anything that benefits from charts, sortable tables, tabs, search, syntax highlighting, math, diagrams, or visual polish that markdown cannot deliver. Returns a public URL.
---

# html-report

Generate a self-contained, polished, interactive HTML report and publish it to the GitHub Pages site in this repo.

## Default target

- Local repo: auto-detected from this skill path when installed as a symlink from `/Users/wisdom/reports/.hermes/skills/html-report`.
- Report output directory: `reports/`.
- Public base URL: auto-detected from Git remote, normally `https://wisdom925.github.io/reports`.
- Publish command: `python3 <skill-dir>/scripts/publish.py <html-path-relative-to-repo> "<title>" "<one-line description>"`.

## Why this skill exists

Markdown is fine for plain text. For reports with data, comparisons, source material, code, or details readers need to navigate, use HTML.

HTML should add real value through at least three of these:

- Interactive charts: Chart.js, Plotly, or ApexCharts for trends, distributions, comparisons.
- Sortable, filterable, searchable tables for tabular data with more than five rows.
- Tabs for comparing alternatives or multiple views of the same data.
- Collapsible `<details>` sections for raw material, appendices, methods, or deep dives.
- Syntax-highlighted code with copy buttons.
- Mermaid diagrams for architecture, flows, state machines, or dependency graphs.
- KaTeX math when equations are present.
- Hover tooltips, popovers, footnotes, citations.
- Dark mode toggle.
- Sticky table of contents with scroll-spy for reports longer than two sections.
- Mobile responsive layout.
- Print stylesheet for PDF export.
- Search or filter inputs for long lists, FAQs, glossaries, or source catalogs.

If none of these fit, write a normal answer instead of forcing an HTML page.

## Workflow

1. Plan the report before writing HTML.
   - Put the headline finding at the top.
   - Decide the major sections.
   - Assign the right interactive element to each section.
   - Use a table of contents when there are more than two sections.

2. Generate one self-contained HTML file at:
   - `reports/<YYYY-MM-DD>-<short-kebab-slug>.html`
   - Use `templates/base.html` as the starting point.
   - Use CDN libraries only. No build step.
   - Put custom CSS in one `<style>` block.
   - Put custom JavaScript in one `<script>` block at the bottom.
   - Set `<title>`, `<meta name="description">`, viewport, and Open Graph tags.

3. Publish.
   ```bash
   python3 /Users/wisdom/reports/.hermes/skills/html-report/scripts/publish.py reports/<YYYY-MM-DD>-<slug>.html "<title>" "<one-line description>"
   ```

   The script updates `reports/manifest.json`, commits, pushes, and prints the public URL.

4. Return the printed URL verbatim. Do not fabricate the URL.

## Draft mode

If the user says the report is a draft, should not be pushed, or needs local review first, pass `--draft`:

```bash
python3 /Users/wisdom/reports/.hermes/skills/html-report/scripts/publish.py reports/<YYYY-MM-DD>-<slug>.html "<title>" "<one-line description>" --draft
```

Draft mode updates the manifest locally and prints the local file path. Revert or commit the draft intentionally afterward.

## Quality bar

Every report must satisfy these requirements:

- Single HTML file, no build step, CDN-only dependencies.
- Mobile responsive at a 375 px viewport.
- Dark mode toggle persisted to `localStorage`.
- Title, description, viewport, and Open Graph metadata.
- `prefers-reduced-motion` respected.
- Sticky table of contents for reports with more than two top-level sections.
- Anchor links on all section headings.
- No inline `style=""`; use a single style block.
- No hardcoded light-mode-only colors.
- Use Traditional Chinese and Taiwan terminology for Chinese reports unless the user asks otherwise.
- Verify company names, person names, and relationships before publishing investment or news reports.

## Recommended elements

- Tables: DataTables.js or a small custom sorter/filter.
- Numeric data: Chart.js with responsive charts and `maintainAspectRatio: false`.
- Code: highlight.js plus copy buttons.
- Comparisons: tabs or segmented controls.
- Long detail: `<details>` sections with clear summaries.
- Flows: Mermaid.
- Math: KaTeX auto-render.
- Citations: hover popovers or linked source cards.

## Anti-patterns

Do not ship these:

- Markdown disguised as HTML.
- Static chart images when live chart data is small enough to render in the page.
- Tables over ten rows with no sort or filter.
- Walls of code without syntax highlighting.
- Light-only color choices.
- Vague link text like "click here".
- Charts that overflow on mobile.
- Unverified financial claims or mixed-up entity names.

## Troubleshooting

- If the script says the repo is not a git repository, install this skill as a symlink from the repo, or set `local_repo_path` in `config.json`.
- If push fails, the report may already be committed locally. Fix GitHub authentication, then run `git push` from `/Users/wisdom/reports`.
- If GitHub Pages returns 404 right after publishing, wait for Pages deployment and refresh.
- If the new report stays 404, check GitHub Pages deployment status before guessing the URL:
  ```bash
  python3 - <<'PY'
  import requests
  runs=requests.get('https://api.github.com/repos/wisdom925/reports/actions/runs?per_page=3',headers={'User-Agent':'Mozilla/5.0'}).json()
  print(runs)
  PY
  ```
  Public API rate limits may apply; the browser Actions page also shows the latest Pages run.
- If Pages deployment fails during the build step, inspect for tracked symlinks or Jekyll-sensitive files in the repo root. A bad absolute symlink can block Pages publication. Check and remove only accidental tracked symlinks:
  ```bash
  python3 - <<'PY'
  import os
  root='/Users/wisdom/reports'
  for dirpath, dirs, files in os.walk(root):
      if '/.git' in dirpath: continue
      for name in dirs+files:
          p=os.path.join(dirpath,name)
          if os.path.islink(p): print(os.path.relpath(p,root),'->',os.readlink(p))
  PY
  git ls-files -s | awk '$1 ~ /^120/ {print}'
  ```
  Adding a repo-root `.nojekyll` file can also reduce Jekyll build fragility for static HTML reports.
