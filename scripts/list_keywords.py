#!/usr/bin/env python3
"""Show all keywords previously used for a client (to avoid overlap when proposing new ones).

Usage:
    list_keywords.py <client_slug>             # one client
    list_keywords.py --all                     # every client
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
KEYWORDS_FILE = SKILL_DIR / "data" / "keywords.json"


def load() -> dict:
    if not KEYWORDS_FILE.exists():
        return {}
    return json.loads(KEYWORDS_FILE.read_text())


def print_client(slug: str, entries: dict) -> None:
    if not entries:
        print(f"[{slug}] no keywords recorded yet.")
        return
    print(f"\n=== {slug} ===")
    print(f"{'KEYWORD':<14} {'PLATFORM':<11} {'DATE':<11} VIDEO")
    print("-" * 90)
    for kw, meta in sorted(entries.items()):
        date = (meta.get("created") or "")[:10]
        plat = meta.get("platform", "?")
        title = (meta.get("video_title") or "?")[:55]
        print(f"{kw:<14} {plat:<11} {date:<11} {title}")


def main() -> int:
    if len(sys.argv) != 2:
        print(__doc__, file=sys.stderr)
        return 2

    data = load()
    arg = sys.argv[1]
    if arg == "--all":
        if not data:
            print("No keywords recorded.")
            return 0
        for slug, entries in data.items():
            print_client(slug, entries)
    else:
        print_client(arg, data.get(arg, {}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
