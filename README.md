# claude-html-report-skill

A Claude Code skill that makes Claude generate **rich, interactive HTML reports** instead of markdown — and publishes them to your own GitHub Pages site so you can share a public URL.

> **This is a GitHub template.** Click ▸ **Use this template** at the top of the page to create your own copy. Forking is the wrong choice here (forks are for upstream PRs; templates are for "clone and diverge", which is what reports are).

---

## Why?

Claude defaults to markdown for everything. Markdown is fine for plain text, but the moment your output has data, comparisons, code, or detail readers want to navigate, you want HTML:

- interactive **charts** (Chart.js / Plotly)
- **sortable / searchable / filterable tables**
- **tabs** for comparing alternatives without scrolling
- **collapsible** sections for optional depth
- syntax-highlighted **code** with copy buttons
- **Mermaid** diagrams, **KaTeX** math
- **dark mode**, **print stylesheets**, **mobile responsive**, **OG link previews**

This skill nudges Claude to lean into all of that — and gives you a one-line publish flow.

See [the live example report](./reports/2026-05-10-example-showcase.html) for what you get.

---

## Setup (≈ 3 minutes, one-time)

### 1. Create your repo from this template

Click ▸ **Use this template → Create a new repository** at the top of this page. Name it whatever you like (e.g. `reports`).

### 2. Clone it locally

```bash
git clone git@github.com:<your-username>/<your-repo>.git ~/reports
cd ~/reports
```

### 3. Install the skill into Claude Code

Symlink the skill directory into Claude's global skills folder. The symlink means future updates to the skill (yours or upstream) are picked up automatically.

```bash
mkdir -p ~/.claude/skills
ln -s "$(pwd)/.claude/skills/html-report" ~/.claude/skills/html-report
```

> Prefer not to symlink? Just `cp -r .claude/skills/html-report ~/.claude/skills/` instead. Re-copy when the skill changes.

### 4. Enable GitHub Pages on your new repo

GitHub → your repo → **Settings → Pages** → **Source: Deploy from a branch** → **Branch: `main` / `(root)`** → Save. Wait ~1 min for the first deploy.

### 5. (Optional) Edit `config.json`

You usually **don't need to edit anything** — the publish script auto-detects:
- the local repo path (from where the script lives on disk, even via symlink)
- the GitHub Pages URL (from `git remote origin`)

Edit [`.claude/skills/html-report/config.json`](.claude/skills/html-report/config.json) only if:
- you cloned to a path the auto-detect can't find (e.g. you copied the skill dir somewhere else and the repo lives elsewhere)
- you use a custom domain (set `base_url`)

That's the entire setup.

---

## Use it

In Claude Code, ask Claude to generate any report and mention the skill:

```
use the html-report skill to write up the results from runs/exp-42
```

```
make an html-report comparing these three checkpoints
```

```
/html-report   # if Claude exposes it as a slash command in your version
```

Claude will:
1. Plan the report (which sections benefit from charts vs tables vs tabs vs collapsibles).
2. Generate a self-contained HTML file at `reports/<YYYY-MM-DD>-<slug>.html` using [`templates/base.html`](.claude/skills/html-report/templates/base.html) as a starting point.
3. Run [`scripts/publish.py`](.claude/skills/html-report/scripts/publish.py), which updates the manifest, commits, pushes, and prints the URL.
4. Hand you back something like `https://<you>.github.io/<repo>/reports/2026-05-10-my-report.html`.

The landing page at `https://<you>.github.io/<repo>/` lists every report (with a filter input).

---

## Requirements

- `git`, `python3` (≥ 3.8), `bash`
- A GitHub account with push access to your new repo (SSH key or credential helper configured)

No `jq`, no node, no build step. The publish script is pure Python stdlib.

---

## How it's wired

```
your-repo/
├── index.html                ← landing page; reads reports/manifest.json
├── reports/
│   ├── manifest.json         ← list of {file, title, date, description}
│   └── *.html                ← one self-contained file per report
└── .claude/
    └── skills/
        └── html-report/      ← symlink target
            ├── SKILL.md      ← what Claude reads to know how to behave
            ├── config.json   ← optional path / base_url overrides
            ├── templates/
            │   └── base.html ← starter template Claude copies & enriches
            └── scripts/
                └── publish.py
```

The skill lives **inside the same repo** as the reports it produces. That's deliberate:
- you only manage one repo
- the skill source ships with the published example, so you can see exactly what you're getting before you fork
- if you ever open the repo in Claude Code, the skill auto-loads as a project skill (no symlink needed for that case)

---

## Customizing the look

- Edit [`templates/base.html`](.claude/skills/html-report/templates/base.html) to change default fonts, colors, libraries, or chrome. Claude copies this file as the starting point for every new report.
- Edit [`index.html`](index.html) to restyle the landing page.
- Edit [`SKILL.md`](.claude/skills/html-report/SKILL.md) to change Claude's behavior (which libraries to prefer, what counts as the "quality bar", etc.). The skill instructions are the most powerful lever — tweak them to suit your taste.

---

## Pulling upstream updates

If you want to track improvements to this skill over time:

```bash
git remote add upstream https://github.com/<original-owner>/claude-html-report-skill.git
git fetch upstream
# update only the skill files; leave your reports/ alone
git checkout upstream/main -- .claude/ index.html
```

---

## Why a template, not a fork?

| | Fork | Template |
|---|---|---|
| Tracks upstream by default | yes | no |
| Designed for sending PRs back | yes | no |
| Your commit history is yours | shared | yours |
| Good for "clone and diverge" | no | **yes** |

You're going to fill this repo with **your** reports. You don't want a fork relationship cluttering the GitHub UI with "this branch is 47 commits ahead of upstream" warnings forever. Templates are the right primitive.

---

## Draft mode

If you ask Claude *"just draft it, don't push yet"*, Claude will pass `--draft` to the publish script. Manifest still updates locally; nothing is committed or pushed. You get the local file path back instead of a URL.

---

## Troubleshooting

- **`ERROR: ... is not a git repository`** — your `local_repo_path` (or auto-detected path) doesn't point at a git repo. Either clone the repo to that path, or set `local_repo_path` in `config.json` explicitly.
- **`git push` failed** — check your SSH/HTTPS auth. The report file is committed locally; just `git push` manually once auth is fixed.
- **Pages URL 404s for ~1 minute** — GitHub Pages takes a moment after first enable. Wait, then refresh.
- **Mermaid / KaTeX not rendering** — they're loaded from jsdelivr; check browser console for CSP / network issues.

---

## License

MIT. See [LICENSE](LICENSE).
