#!/usr/bin/env python3
"""List all registered clients and their video cache status."""

import json
import sys
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
CLIENTS_FILE = SKILL_DIR / "data" / "clients.json"
VIDEOS_DIR = SKILL_DIR / "data" / "videos"


def main() -> int:
    clients = json.loads(CLIENTS_FILE.read_text()) if CLIENTS_FILE.exists() else {}
    if not clients:
        print("No clients registered. Use add_client.py to add one.")
        return 0

    print(f"{'SLUG':<24} {'VIDEOS':>7}  {'LAST UPDATED':<27} NAME / URL")
    print("-" * 100)
    for slug, c in clients.items():
        vf = VIDEOS_DIR / f"{slug}.json"
        count = "-"
        if vf.exists():
            try:
                count = str(len(json.loads(vf.read_text())))
            except Exception:
                count = "err"
        last = c.get("last_updated") or "never"
        print(f"{slug:<24} {count:>7}  {last:<27} {c.get('name','?')}  {c.get('channel_url','?')}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
