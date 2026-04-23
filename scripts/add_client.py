#!/usr/bin/env python3
"""Add or update a client in the cta-writer registry.

Usage:
    add_client.py "<client name>" <youtube_channel_url>

Examples:
    add_client.py "Acme Co" https://www.youtube.com/@acmeco
    add_client.py "Jane Doe" https://www.youtube.com/channel/UCxxxxxxx
"""

import json
import re
import sys
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
CLIENTS_FILE = SKILL_DIR / "data" / "clients.json"


def slugify(name: str) -> str:
    s = name.lower().strip()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return s.strip("-")


def main() -> int:
    if len(sys.argv) != 3:
        print(__doc__, file=sys.stderr)
        return 2

    name, url = sys.argv[1], sys.argv[2]
    if "youtube.com" not in url and "youtu.be" not in url:
        print(f"Error: URL does not look like a YouTube URL: {url}", file=sys.stderr)
        return 2

    slug = slugify(name)
    if not slug:
        print("Error: could not derive a slug from the client name", file=sys.stderr)
        return 2

    clients = json.loads(CLIENTS_FILE.read_text()) if CLIENTS_FILE.exists() else {}
    existed = slug in clients
    clients[slug] = {
        "name": name,
        "channel_url": url,
        "last_updated": clients.get(slug, {}).get("last_updated"),
    }
    CLIENTS_FILE.write_text(json.dumps(clients, indent=2) + "\n")

    action = "Updated" if existed else "Added"
    print(f"{action} client: {name} ({slug}) -> {url}")
    print(f"Next: run update_videos.py {slug}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
