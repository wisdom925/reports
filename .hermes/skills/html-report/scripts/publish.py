#!/usr/bin/env python3
"""Publish a generated HTML report.

Updates reports/manifest.json, commits, pushes, and prints the public URL.

Usage:
    publish.py <html-file> "<title>" ["<description>"] [--no-push] [--draft]

<html-file> may be absolute, or relative to the repo root, or relative to CWD.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from datetime import date
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
CONFIG_PATH = SKILL_DIR / "config.json"


def main() -> int:
    args = _parse_args()
    cfg = _load_config()
    repo_path = _resolve_repo_path(cfg)
    reports_dir = cfg.get("reports_dir") or "reports"
    base_url = (cfg.get("base_url") or "").rstrip("/") or _derive_base_url(repo_path)

    html_path = _resolve_html_path(args.html_file, repo_path)
    rel = html_path.relative_to(repo_path)
    filename = html_path.name

    report_date = _date_from_filename(filename)
    _update_manifest(repo_path / reports_dir / "manifest.json", filename, args.title, report_date, args.description)

    if args.draft:
        print(f"DRAFT: {html_path}")
        return 0

    _git(repo_path, ["add", "-A"])
    if _git(repo_path, ["diff", "--cached", "--quiet"], check=False).returncode == 0:
        print("No changes to commit.", file=sys.stderr)
    else:
        try:
            _git(repo_path, ["commit", "-m", f"report: {args.title}"])
        except subprocess.CalledProcessError:
            print(
                "WARN: git commit failed. Files are staged; resolve the issue (e.g. set "
                "git user.name/email) and commit manually.",
                file=sys.stderr,
            )
            return 1
        if not args.no_push:
            try:
                _git(repo_path, ["push"])
            except subprocess.CalledProcessError:
                print(
                    "WARN: git push failed. Report is committed locally; push manually when ready.",
                    file=sys.stderr,
                )

    if base_url:
        url = f"{base_url}/{rel.as_posix()}"
    else:
        url = f"(no base_url; set it in {CONFIG_PATH} or push to GitHub) local: {html_path}"
    print(url)
    return 0


def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("html_file", help="path to the generated HTML file")
    p.add_argument("title", help="report title (used in manifest + commit message)")
    p.add_argument("description", nargs="?", default="", help="one-line summary")
    p.add_argument("--no-push", action="store_true", help="commit but do not push")
    p.add_argument("--draft", action="store_true", help="update manifest only; no commit, no push")
    return p.parse_args()


def _load_config() -> dict:
    if not CONFIG_PATH.exists():
        sys.exit(f"ERROR: missing config file at {CONFIG_PATH}")
    try:
        return json.loads(CONFIG_PATH.read_text())
    except json.JSONDecodeError as e:
        sys.exit(f"ERROR: invalid JSON in {CONFIG_PATH}: {e}")


def _resolve_repo_path(cfg: dict) -> Path:
    raw = (cfg.get("local_repo_path") or "").strip()
    if raw:
        repo = Path(os.path.expanduser(raw)).resolve()
    else:
        # Auto-detect: this script lives at <repo>/.claude/skills/html-report/scripts/publish.py.
        # SCRIPT_DIR.parents[0..3] = scripts, html-report, skills, .claude. parents[3] = <repo>.
        repo = SCRIPT_DIR.resolve().parents[3]
    if not (repo / ".git").exists():
        sys.exit(
            f"ERROR: {repo} is not a git repository. "
            f"Set local_repo_path in {CONFIG_PATH} to the clone of your reports repo."
        )
    return repo


def _resolve_html_path(arg: str, repo_path: Path) -> Path:
    p = Path(arg)
    if not p.is_absolute():
        # Try repo-relative first, then CWD-relative.
        cand = (repo_path / p).resolve()
        if cand.exists():
            p = cand
        else:
            p = (Path.cwd() / p).resolve()
    else:
        p = p.resolve()
    if not p.exists():
        sys.exit(f"ERROR: HTML file not found: {arg}")
    if not str(p).startswith(str(repo_path) + os.sep) and p != repo_path:
        sys.exit(f"ERROR: {p} is outside the repo at {repo_path}")
    return p


def _date_from_filename(filename: str) -> str:
    m = re.match(r"^(\d{4}-\d{2}-\d{2})", filename)
    return m.group(1) if m else date.today().isoformat()


def _update_manifest(path: Path, filename: str, title: str, report_date: str, description: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        try:
            items = json.loads(path.read_text())
            if not isinstance(items, list):
                items = []
        except json.JSONDecodeError:
            items = []
    else:
        items = []
    items = [it for it in items if isinstance(it, dict) and it.get("file") != filename]
    items.insert(0, {
        "file": filename,
        "title": title,
        "date": report_date,
        "description": description,
    })
    path.write_text(json.dumps(items, indent=2) + "\n")


def _derive_base_url(repo_path: Path) -> str:
    try:
        out = subprocess.run(
            ["git", "-C", str(repo_path), "config", "--get", "remote.origin.url"],
            capture_output=True, text=True, check=True,
        ).stdout.strip()
    except subprocess.CalledProcessError:
        return ""
    m = re.search(r"github\.com[:/]+([^/]+)/([^/]+?)(?:\.git)?/?$", out)
    if not m:
        return ""
    owner, repo = m.group(1), m.group(2)
    return f"https://{owner}.github.io/{repo}"


def _git(repo_path: Path, args: list[str], check: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(["git", "-C", str(repo_path), *args], check=check)


if __name__ == "__main__":
    sys.exit(main())
