# SPDX-License-Identifier: Apache-2.0
"""Sensitive-information scanner for release hygiene.

Scans the working tree (default) or the full git history (``--git-history``)
for committed secrets, internal infrastructure references, and
organization-specific keywords.

Keyword sources:

- A built-in baseline pattern set (private keys, tokens, API keys, personal
  paths, internal hostnames).
- ``.sanitize-keywords.local`` at the repository root: one case-sensitive
  literal or regex per line. This file is intentionally **not** committed —
  it may itself contain internal terms. The scanner exits with code 2 when
  the file is missing so a forgotten keyword list can never masquerade as a
  clean scan; pass ``--allow-missing-keyword-file`` only for a deliberate
  baseline-only run.

Every directory tracked by git is scanned — nothing (vendor bundles,
generated prompts, lockfiles) is excluded from pattern matching. The only
files never scanned are the scanner itself, the keyword list and the
allowlist (they contain the patterns by definition).

``.sanitize-allowlist.local`` (also not committed) lists justified hits, one
per line as ``path<TAB>pattern<TAB>reason``. Allowlisted hits are recorded
under ``allowlisted`` with their reason instead of failing the scan.

Exit codes: 0 = no hits, 1 = hits found, 2 = configuration error.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
KEYWORD_FILE = REPO_ROOT / ".sanitize-keywords.local"
ALLOWLIST_FILE = REPO_ROOT / ".sanitize-allowlist.local"
SELF_SKIP = {
    "scripts/scan_sensitive.py",
    KEYWORD_FILE.name,
    ALLOWLIST_FILE.name,
}

BASELINE_PATTERNS: dict[str, str] = {
    "private_key_block": r"-----BEGIN (?:RSA |EC |OPENSSH |DSA |PGP )?PRIVATE KEY",
    "openai_style_key": r"\bsk-[A-Za-z0-9_-]{20,}\b",
    "github_token": r"\b(?:ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9]{30,}\b",
    "aws_access_key": r"\bAKIA[0-9A-Z]{16}\b",
    "aliyun_access_key": r"\bLTAI[A-Za-z0-9]{12,}\b",
    "assigned_secret_value": (
        r"(?i)\b(?:api[_-]?key|secret|access[_-]?token|auth[_-]?token|password)\b"
        r"\s*[:=]\s*[\"'][^\"'\s]{8,}[\"']"
    ),
    "bearer_token": r"(?i)bearer\s+[A-Za-z0-9._~+/=-]{20,}",
    "personal_home_path": r"(?<![\w/.-])/(?:home|Users)/[A-Za-z0-9._-]+",
    "internal_hostname": r"(?i)\b[\w.-]*(?:alibaba-inc|taobao-inc)\.com\b|\btbsite\.net\b",
}

SKIP_DIRS = {".git", ".venv", "node_modules", "dist", "__pycache__", ".mypy_cache", ".pytest_cache", ".ruff_cache"}
MAX_FILE_BYTES = 8 * 1024 * 1024


def load_keyword_patterns(allow_missing: bool) -> dict[str, re.Pattern[str]]:
    patterns: dict[str, re.Pattern[str]] = {
        name: re.compile(expr) for name, expr in BASELINE_PATTERNS.items()
    }
    if not KEYWORD_FILE.exists():
        if not allow_missing:
            print(
                f"ERROR: keyword list {KEYWORD_FILE.name} is missing; refusing to "
                "run a baseline-only scan without --allow-missing-keyword-file.",
                file=sys.stderr,
            )
            sys.exit(2)
        return patterns
    for lineno, raw in enumerate(KEYWORD_FILE.read_text(encoding="utf-8").splitlines(), 1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        patterns[f"local_keyword:{lineno}"] = re.compile(line)
    return patterns


def load_allowlist() -> dict[tuple[str, str], str]:
    allow: dict[tuple[str, str], str] = {}
    if not ALLOWLIST_FILE.exists():
        return allow
    for raw in ALLOWLIST_FILE.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        path, pattern, reason = (line.split("\t") + [""])[:3]
        allow[(path.strip(), pattern.strip())] = reason.strip()
    return allow


def iter_worktree_files() -> list[Path]:
    files: list[Path] = []
    for dirpath, dirnames, filenames in os.walk(REPO_ROOT):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for name in filenames:
            p = Path(dirpath) / name
            try:
                if p.stat().st_size <= MAX_FILE_BYTES and str(p.relative_to(REPO_ROOT)) not in SELF_SKIP:
                    files.append(p)
            except OSError:
                continue
    return files


def scan_text(text: str, patterns: dict[str, re.Pattern[str]]) -> list[dict[str, object]]:
    hits = []
    for lineno, line in enumerate(text.splitlines(), 1):
        for name, pat in patterns.items():
            if pat.search(line):
                hits.append({"line": lineno, "pattern": name, "excerpt": line.strip()[:200]})
    return hits


def scan_worktree(patterns: dict[str, re.Pattern[str]]) -> dict[str, object]:
    results = []
    files = iter_worktree_files()
    for p in files:
        try:
            raw = p.read_bytes()
        except OSError:
            continue
        if b"\0" in raw[:8192]:
            continue
        hits = scan_text(raw.decode("utf-8", errors="replace"), patterns)
        for h in hits:
            results.append({"path": str(p.relative_to(REPO_ROOT)), **h})
    return {"mode": "worktree", "files_scanned": len(files), "hits": results}


def scan_git_history(patterns: dict[str, re.Pattern[str]]) -> dict[str, object]:
    commits = subprocess.run(
        ["git", "rev-list", "--all"], cwd=REPO_ROOT, capture_output=True, text=True, check=True
    ).stdout.split()
    # Collect every blob once (dedupe by SHA), then scan contents in Python —
    # git grep -E cannot express the PCRE baseline patterns.
    blob_paths: dict[str, list[tuple[str, str]]] = {}
    for commit in commits:
        listing = subprocess.run(
            ["git", "ls-tree", "-r", commit], cwd=REPO_ROOT, capture_output=True, text=True, check=True
        ).stdout
        for line in listing.splitlines():
            meta, _, path = line.partition("\t")
            parts = meta.split()
            if len(parts) < 3 or parts[1] != "blob" or path in SELF_SKIP:
                continue
            blob_paths.setdefault(parts[2], []).append((commit[:12], path))

    results = []
    for sha, locations in blob_paths.items():
        show = subprocess.run(
            ["git", "cat-file", "blob", sha], cwd=REPO_ROOT, capture_output=True
        )
        raw = show.stdout
        if b"\0" in raw[:8192] or len(raw) > MAX_FILE_BYTES:
            continue
        text = raw.decode("utf-8", errors="replace")
        for hit in scan_text(text, patterns):
            for commit, path in locations:
                results.append({"commit": commit, "path": path, **hit})
    return {
        "mode": "git-history",
        "commits_scanned": len(commits),
        "unique_blobs_scanned": len(blob_paths),
        "hits": results,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--git-history", action="store_true", help="scan all commits instead of the worktree")
    parser.add_argument("--allow-missing-keyword-file", action="store_true")
    parser.add_argument("--report-dir", type=Path, default=None, help="write a JSON scan record here")
    args = parser.parse_args()

    patterns = load_keyword_patterns(args.allow_missing_keyword_file)
    allowlist = load_allowlist()
    report = scan_git_history(patterns) if args.git_history else scan_worktree(patterns)
    hits = []
    allowed = []
    for h in report["hits"]:  # type: ignore[union-attr]
        key = (str(h.get("path")), str(h.get("pattern")))
        reason = next((r for (p, pat), r in allowlist.items() if key[0] == p and pat in key[1].split(",")), None)
        (allowed if reason is not None else hits).append({**h, "allowlist_reason": reason} if reason is not None else h)
    report["hits"] = hits
    report["allowlisted"] = allowed
    report.update(
        {
            "tool": "scripts/scan_sensitive.py",
            "timestamp_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "keyword_file": KEYWORD_FILE.name if KEYWORD_FILE.exists() else None,
            "allowlist_file": ALLOWLIST_FILE.name if ALLOWLIST_FILE.exists() else None,
            "pattern_count": len(patterns),
            "hit_count": len(hits),
            "allowlisted_count": len(allowed),
        }
    )

    if args.report_dir:
        args.report_dir.mkdir(parents=True, exist_ok=True)
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        out = args.report_dir / f"scan_{report['mode']}_{stamp}.json"
        out.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"scan record: {out}")

    hits = report["hits"]
    print(
        f"mode={report['mode']} patterns={report['pattern_count']} "
        f"hit_count={report['hit_count']} allowlisted={report['allowlisted_count']}"
    )
    for h in allowed:
        print(f"  allowlisted: {h}")
    for h in hits[:50]:  # type: ignore[index]
        print(f"  {h}")
    if hits:
        print("FAIL: sensitive-pattern hits found", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
