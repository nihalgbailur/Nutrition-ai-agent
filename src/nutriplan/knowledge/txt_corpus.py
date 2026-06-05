from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from nutriplan.config import TXT_CORPUS_DIR


@lru_cache(maxsize=1)
def load_txt_lines() -> list[str]:
    """Load non-comment lines from synthetic TXT corpora (for search / future RAG)."""
    lines: list[str] = []
    if not TXT_CORPUS_DIR.exists():
        return lines
    for path in sorted(TXT_CORPUS_DIR.glob("*.txt")):
        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#"):
                lines.append(line)
    return lines


def search_txt_corpus(query: str, limit: int = 5) -> list[str]:
    """Simple keyword search over TXT corpus."""
    q = query.lower()
    hits = [ln for ln in load_txt_lines() if q in ln.lower()]
    return hits[:limit]