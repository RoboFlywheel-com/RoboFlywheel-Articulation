# SPDX-License-Identifier: Apache-2.0

"""Gates on the authoring-doc corpus itself — the anti-codification ratchet.

Two failure modes of a rules-as-prose corpus, made machine-checkable:

1. **Symbol drift** — a doc teaches an API/check that no longer exists in code
   (the `allow_disconnected_islands` class of staleness). Every backticked
   python-ish identifier in the authoring docs must occur somewhere in the
   repo's Python source, or be explicitly allowlisted.

2. **Size ratchet** — the small active authoring corpus may only shrink. Each
   doc's line count is capped by `authoring_doc_budget.json`. Enforcing a rule
   in code (gate/API raise) and demoting its prose to a short "why" note frees
   budget; adding prose without shrinking elsewhere fails here. Raising a
   budget number is allowed but must be a conscious, reviewable act in the
   same commit — that is the whole point.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
DOCS_DIR = REPO_ROOT / "articraft_template_authoring"
BUDGET_FILE = Path(__file__).with_name("authoring_doc_budget.json")
ALLOWLIST_FILE = Path(__file__).with_name("doc_symbol_allowlist.txt")

_CODE_DIRS = ("agent", "sdk", "cli", "scripts", "tests")
_ACTIVE_AUTHORING_DOCS = (
    "README.md",
    "AUTHORING.md",
    "MECHANICAL_PRIORS.md",
    "VISUAL_DIVERSITY_MODEL.md",
)

# Backticked spans that look like python identifiers: lowercase, >=4 chars,
# at least one underscore (skips plain words), optional trailing "()".
_SYMBOL_RE = re.compile(r"`([a-z_][a-z0-9_]{3,})(?:\(\))?`")

# Fenced code blocks are pedagogical examples — invented helper names in a
# ```python fence are fine; drift only matters for inline references to what
# is claimed to be a real API/check.
_FENCE_RE = re.compile(r"^```.*?^```", re.MULTILINE | re.DOTALL)


def _authoring_docs() -> list[Path]:
    """Return the explicitly small current corpus, excluding historical specs."""

    return [DOCS_DIR / name for name in _ACTIVE_AUTHORING_DOCS]


def _code_corpus() -> str:
    chunks: list[str] = []
    for d in _CODE_DIRS:
        for py in sorted((REPO_ROOT / d).rglob("*.py")):
            chunks.append(py.read_text(encoding="utf-8", errors="ignore"))
    return "\n".join(chunks)


def _allowlist() -> set[str]:
    if not ALLOWLIST_FILE.exists():
        return set()
    lines = ALLOWLIST_FILE.read_text(encoding="utf-8").splitlines()
    return {ln.strip() for ln in lines if ln.strip() and not ln.startswith("#")}


def test_doc_symbols_exist_in_code() -> None:
    corpus = _code_corpus()
    allow = _allowlist()
    stale: dict[str, list[str]] = {}
    for doc in _authoring_docs():
        text = _FENCE_RE.sub("", doc.read_text(encoding="utf-8"))
        for sym in sorted({m.group(1) for m in _SYMBOL_RE.finditer(text)}):
            if sym in allow or sym in corpus:
                continue
            stale.setdefault(doc.name, []).append(sym)
    assert not stale, (
        "Authoring docs reference identifiers that do not occur anywhere in "
        f"{_CODE_DIRS} — either the doc is stale (fix the doc), the symbol was "
        "renamed (fix the doc), or it is a legitimate doc-only term (add it to "
        f"{ALLOWLIST_FILE.name} with a comment):\n"
        + "\n".join(f"  {doc}: {', '.join(syms)}" for doc, syms in sorted(stale.items()))
    )


def test_authoring_doc_size_ratchet() -> None:
    budget: dict[str, int] = json.loads(BUDGET_FILE.read_text(encoding="utf-8"))
    over: list[str] = []
    unbudgeted: list[str] = []
    for doc in _authoring_docs():
        lines = len(doc.read_text(encoding="utf-8").splitlines())
        cap = budget.get(doc.name)
        if cap is None:
            unbudgeted.append(f"{doc.name} ({lines} lines)")
        elif lines > cap:
            over.append(f"{doc.name}: {lines} > budget {cap}")
    assert not unbudgeted, (
        "New authoring doc(s) without a size budget — add them to "
        f"{BUDGET_FILE.name} with a consciously chosen cap:\n  " + "\n  ".join(unbudgeted)
    )
    assert not over, (
        "Authoring docs grew past their ratchet budget. Prefer enforcing the "
        "new rule in code (gate/API raise) and demoting prose to a short "
        "'why' note; if prose truly must grow, shrink elsewhere or raise the "
        f"budget in {BUDGET_FILE.name} in this same commit (reviewable):\n  " + "\n  ".join(over)
    )
