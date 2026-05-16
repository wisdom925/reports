---
name: html-report
description: Generate a rich, INTERACTIVE HTML report (not markdown!) and publish it to GitHub Pages. Use when the user asks for a "report", "writeup", "summary page", "dashboard", "share link", or anything that benefits from interactivity, charts, sortable tables, tabs, search, syntax highlighting, math, diagrams, or visual polish that markdown cannot deliver. Returns a public URL the user can share.
---

# html-report

Generate a self-contained, polished, **interactive** HTML report and publish it to the user's GitHub Pages site.

## Why this skill exists (read this first)

Claude defaults to markdown for everything. Markdown is fine for plain text, but it's a **failure mode** for any output that has data, comparisons, code, or detail that the reader will want to navigate. This skill exists to push you toward HTML's strengths. If you generate a wall of `<p>` tags and `<h2>` headings, **you have wasted this skill** — markdown would have done the same job.

Concretely, HTML can do all of these and markdown cannot:

| Capability | Use it for |
|---|---|
| **Interactive charts** (Chart.js / Plotly / ApexCharts) | any numeric data, trends, distributions |
| **Sortable / filterable / searchable tables** (DataTables, grid.js) | any tabular data with >5 rows |
| **Tabs** | comparing alternatives, before/after, multiple views of same data |
| **Collapsible `<details>` sections** | proofs, raw output, optional deep-dives, long appendices |
| **Syntax-highlighted code with copy buttons** (highlight.js / Prism) | any code snippet |
| **Mermaid / Graphviz diagrams** | architecture, flows, state machines, dependency graphs |
| **KaTeX / MathJax** | any equation |
| **Hover tooltips, popovers, modals** | term definitions, footnotes, citations |
| **Animations / transitions** | state changes, reveals, focus shifts |
| **Dark mode toggle** | every report |
| **Sticky table-of-contents with scroll-spy** | any report >2 sections |
| **Responsive layout** | mobile reading |
| **Print stylesheet** (`@media print`) | shareable PDFs |
| **Embedded video / audio** | media-heavy work |
| **Search / filter inputs** over content | long lists, FAQs, glossaries |

Every report you produce should use **at least three** of these. If you can't find three that apply, the user probably wanted markdown — push back and ask.

## Configuration

Read `config.json` next to this file. Fields:
- `local_repo_path` — local clone of the GitHub Pages repo. **Optional** — if empty, the script auto-detects it from where this skill lives on disk (works whether installed in-place or symlinked).
- `reports_dir` — subdirectory for reports (default: `reports`).
- `base_url` — GitHub Pages base URL. **Optional** — auto-detected from `git remote origin` if empty.

The user should normally not need to edit anything.

## Workflow

1. **Plan the report.** Before writing HTML, decide:
   - What's the headline finding? (Goes at the top, big.)
   - What sections does it have?
   - For each section, which interactive element fits? (data → chart, comparison → tabs, code → highlighted block, long → collapsible, etc.)
   - Will it have a TOC? (Yes if >2 sections.)

2. **Generate ONE self-contained HTML file** at `<repo>/<reports_dir>/<YYYY-MM-DD>-<slug>.html`.
   - Slug should be short, kebab-case, descriptive (`gpt5-vs-claude-benchmark`, not `report-1`).
   - Start from `templates/base.html` — it already wires up Tailwind, highlight.js, Chart.js, Mermaid, KaTeX, dark mode, sticky TOC, and print styles.
   - All libraries via CDN (no build step).
   - Custom CSS in a single `<style>` block; custom JS in a single `<script>` block at the bottom.
   - Set `<title>`, `<meta name="description">`, `<meta name="viewport">`, and Open Graph tags (the report will be shared as a link — OG tags make link previews work).

3. **Publish.** Run the publish script from anywhere:
   ```bash
   python3 <skill-dir>/scripts/publish.py <html-path-relative-to-repo> "<title>" "<one-line description>"
   ```
   The script:
   - Updates `reports/manifest.json` (which the index page reads).
   - `git add -A`, `git commit -m "report: <title>"`, `git push`.
   - Prints the public URL.

4. **Return the URL** to the user. Don't fabricate it — use the script's output.

## Quality bar — required for every report

- **Single file**, no build step, CDN-only deps.
- **Mobile-responsive** — test in your head: does it work on a 375px viewport?
- **Dark mode** with a toggle, persisted to localStorage.
- **Title + description + OG tags** in `<head>`.
- **Prefers-reduced-motion respected** — no jarring animations for users who opted out.
- **Sticky TOC** for any report with >2 top-level sections.
- **Anchor links** on all section headings (`id="..."`).
- **No inline `style=""`** — use a single `<style>` block.
- **No hardcoded light-mode colors** — use Tailwind's `dark:` variants or CSS variables.

## Strongly recommended (pick what fits the content)

- **Tables → DataTables.js** (sort, filter, paginate). Drop-in: load `datatables.net` CDN, wrap with `$('table').DataTable()`.
- **Numeric data → Chart.js** (bar/line/pie/scatter/radar). Always set `responsive: true, maintainAspectRatio: false`.
- **Code → highlight.js**, plus a "copy" button per block.
- **Comparisons (3+ alternatives) → tabs**. Hand-roll with `<input type="radio">` + CSS or use the snippet in `templates/base.html`.
- **Long detail → `<details>` collapsibles** with descriptive `<summary>`.
- **Architecture / flow → Mermaid**. `<pre class="mermaid">graph TD; A-->B</pre>`.
- **Math → KaTeX** auto-render (faster than MathJax). Inline: `$x^2$`. Display: `$$\int...$$`.
- **Multiple views of same data → segmented control / toggle**.
- **Long lists (>20 items) → search/filter input** at the top.
- **Citations / footnotes → popovers** that show the source on hover, not at the bottom of the page.

## Anti-patterns (do not ship these)

- ❌ Markdown disguised as HTML — paragraphs and bullets only.
- ❌ Static images of charts when the data is small enough to render live.
- ❌ Tables of >10 rows with no sort or filter.
- ❌ Walls of code with no syntax highlighting.
- ❌ 5MB of JS for a 200-word report. Pick libraries that fit the content.
- ❌ Light-only color choices.
- ❌ "Click here" links — use descriptive link text.
- ❌ Charts that overflow on mobile.

## Example: planning a "model benchmark" report

| Element | Choice |
|---|---|
| Headline number | Big number at the top, with sparkline trend |
| Per-task results | DataTable, sortable by score |
| Two models compared head-to-head | Bar chart |
| Three configs compared | Tabs |
| Per-task example outputs | Collapsibles |
| Methodology | Collapsible at the bottom |
| Math (eg. ELO formula) | KaTeX |

## Draft mode

If the user says "just draft it" or "don't push yet", pass `--draft` to the publish script. It updates the manifest locally, skips commit + push, and prints the local file path instead of the URL.

## After publishing

The script prints the URL. Pass it through verbatim. If the script printed a warning about a failed push, surface that to the user — don't bury it.

## When NOT to use this skill

- One-line answers.
- Throwaway debug output.
- Anything the user explicitly asked for as markdown / plain text.
- Code that goes into a file in the user's project.
