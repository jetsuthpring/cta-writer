#!/usr/bin/env python3
"""Record a chosen CTA + keyword and print a paste-ready ManyChat setup block.

Usage:
    save_keyword.py <client_slug> --keyword THINK --video-id <yt_id> \
        --cta "The CTA text the user chose" \
        [--platform instagram] [--post-url https://instagram.com/p/...]

All DM/button/reply text defaults to a random pick from
references/manychat-variations.json so viewers don't see the same automation
twice. Override any slot with the matching flag:
    --comment-reply "..."
    --opening-dm "..."         --opening-button "..."
    --gate-dm "..."            --gate-button "..."
    --link-dm "..."            --link-label "..."

Platforms: instagram (default), facebook, tiktok.
  - instagram / facebook: full ManyChat 3-stage DM block (opener → follow-gate → link).
  - tiktok: manual-reply block (ManyChat doesn't support TikTok).

Fails if the keyword is already used for this client.
"""

from __future__ import annotations

import argparse
import json
import random
import sys
from datetime import datetime, timezone
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
CLIENTS_FILE = SKILL_DIR / "data" / "clients.json"
VIDEOS_DIR = SKILL_DIR / "data" / "videos"
KEYWORDS_FILE = SKILL_DIR / "data" / "keywords.json"
VARIATIONS_FILE = SKILL_DIR / "references" / "manychat-variations.json"

SUPPORTED_PLATFORMS = {"instagram", "facebook", "tiktok"}


def load_json(path: Path, default):
    if not path.exists():
        return default
    return json.loads(path.read_text())


def pick(pool: list[str], override: str | None) -> str:
    if override:
        return override
    return random.choice(pool)


def find_video(slug: str, video_id: str) -> dict:
    path = VIDEOS_DIR / f"{slug}.json"
    videos = load_json(path, [])
    for v in videos:
        if v.get("video_id") == video_id:
            return v
    sys.exit(f"Error: video_id '{video_id}' not found in {path}. Run update_videos.py.")


def print_lines(prefix: str, text: str, width: int = 72) -> None:
    words = text.split()
    line = ""
    first = True
    for w in words:
        if len(line) + len(w) + 1 > width:
            print(f"{prefix if first else ' ' * len(prefix)}{line}")
            first = False
            line = w
        else:
            line = (line + " " + w).strip()
    if line:
        print(f"{prefix if first else ' ' * len(prefix)}{line}")


def print_manychat_block(client_name: str, slug: str, keyword: str, platform: str,
                         video: dict, cta: str, post_url: str | None,
                         comment_reply: str, opening_dm: str, opening_button: str,
                         gate_dm: str, gate_button: str, link_dm: str,
                         link_label: str) -> None:
    line = "━" * 60
    print(f"\n{line}")
    print(f" MANYCHAT SETUP — {platform.title()} Comments → DM")
    print(f"{line}\n")
    print(f"Client:         {client_name} ({slug})")
    print(f"Platform:       {platform}")
    print(f"Trigger:        Comments on Post\n")
    print(f"📌 Post:         {post_url or '[paste post URL after publishing]'}")
    print(f"🔑 Keyword:      {keyword}   (match: contains, case-insensitive)\n")
    print(f"💬 Public comment reply:")
    print_lines("   ", f'"{comment_reply}"')
    print()
    print("── DM STAGE 1 — Opening DM ──────────────────────────────────")
    print(f"Message:")
    print_lines("   ", opening_dm)
    print(f"Button label:   {opening_button}\n")
    print("── DM STAGE 2 — Follow-gate DM ───────────────────────────────")
    print(f"Message:")
    print_lines("   ", gate_dm)
    print(f"Button label:   {gate_button}\n")
    print("── DM STAGE 3 — Link DM ──────────────────────────────────────")
    print(f"Message:")
    print_lines("   ", link_dm)
    print(f"Link card:      {link_label}")
    print(f"URL:            {video.get('url','?')}")
    print(f"Video title:    {video.get('title','?')}\n")
    print(f"📝 CTA in the short-form:")
    print_lines("   ", cta)
    print()
    path_hint = {
        "instagram": "Instagram → Automation → New Automation → Comments → Instagram Post",
        "facebook":  "Facebook → Automation → New Automation → Comments on Page Post",
    }[platform]
    print(f"ManyChat path:  {path_hint}")
    print(line)


def print_tiktok_block(client_name: str, slug: str, keyword: str,
                      video: dict, cta: str, post_url: str | None) -> None:
    line = "━" * 60
    print(f"\n{line}")
    print(f" TIKTOK — manual reply (ManyChat does not support TikTok)")
    print(f"{line}\n")
    print(f"Client:         {client_name} ({slug})")
    print(f"📌 Post:         {post_url or '[paste post URL after publishing]'}")
    print(f"🔑 Keyword:      {keyword}")
    print(f"🔗 Long-form:    {video.get('url','?')}")
    print(f"                {video.get('title','?')}\n")
    print(f"📝 CTA in the short-form:")
    print_lines("   ", cta)
    print("\nManual workflow (or use a 3rd-party TikTok comment tool):")
    print(f'  1. Watch the post for comments containing "{keyword}" (case-insensitive).')
    print( "  2. Reply publicly: \"Sent! Check your DMs 👀\"")
    print(f'  3. DM them: "Here\'s what I promised: {video.get("url","?")}"')
    print(line)


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("slug")
    p.add_argument("--keyword", required=True)
    p.add_argument("--video-id", required=True)
    p.add_argument("--cta", required=True, help="The exact CTA text used in the short-form script")
    p.add_argument("--platform", default="instagram", choices=sorted(SUPPORTED_PLATFORMS))
    p.add_argument("--post-url", default=None)
    # overrides — if unset, a random variation is picked
    p.add_argument("--comment-reply", default=None)
    p.add_argument("--opening-dm", default=None)
    p.add_argument("--opening-button", default=None)
    p.add_argument("--gate-dm", default=None)
    p.add_argument("--gate-button", default=None)
    p.add_argument("--link-dm", default=None)
    p.add_argument("--link-label", default=None)
    args = p.parse_args()

    clients = load_json(CLIENTS_FILE, {})
    if args.slug not in clients:
        sys.exit(f"Error: client '{args.slug}' not registered. Run add_client.py first.")

    keyword = args.keyword.strip().upper()
    if not keyword.isalnum():
        sys.exit("Error: keyword must be alphanumeric only (no spaces or punctuation).")

    all_kw = load_json(KEYWORDS_FILE, {})
    client_kw = all_kw.setdefault(args.slug, {})
    if keyword in client_kw:
        existing = client_kw[keyword]
        sys.exit(
            f"Error: keyword '{keyword}' already used for {args.slug} "
            f"(created {existing.get('created','?')[:10]}, "
            f"video: {(existing.get('video_title') or '?')[:50]}). "
            "Pick a different keyword."
        )

    video = find_video(args.slug, args.video_id)
    variations = load_json(VARIATIONS_FILE, {})

    comment_reply  = pick(variations.get("comment_reply", []),  args.comment_reply)
    opening_dm     = pick(variations.get("opening_dm", []),     args.opening_dm)
    opening_button = pick(variations.get("opening_button", []), args.opening_button)
    gate_dm        = pick(variations.get("follow_gate_dm", []), args.gate_dm)
    gate_button    = pick(variations.get("follow_gate_button", []), args.gate_button)
    link_dm        = pick(variations.get("link_dm", []),        args.link_dm)
    link_label     = pick(variations.get("link_card_label", []), args.link_label)

    entry = {
        "created": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "platform": args.platform,
        "video_id": args.video_id,
        "video_title": video.get("title"),
        "video_url": video.get("url"),
        "cta": args.cta,
        "post_url": args.post_url,
        "manychat": {
            "comment_reply":  comment_reply,
            "opening_dm":     opening_dm,
            "opening_button": opening_button,
            "gate_dm":        gate_dm,
            "gate_button":    gate_button,
            "link_dm":        link_dm,
            "link_label":     link_label,
        },
        "manychat_flow_id": None,
    }
    client_kw[keyword] = entry
    KEYWORDS_FILE.write_text(json.dumps(all_kw, indent=2, ensure_ascii=False) + "\n")

    client_name = clients[args.slug].get("name", args.slug)
    print(f"✅ Saved keyword '{keyword}' for {client_name}.")

    if args.platform == "tiktok":
        print_tiktok_block(client_name, args.slug, keyword, video, args.cta, args.post_url)
    else:
        print_manychat_block(client_name, args.slug, keyword, args.platform,
                             video, args.cta, args.post_url,
                             comment_reply, opening_dm, opening_button,
                             gate_dm, gate_button, link_dm, link_label)
    return 0


if __name__ == "__main__":
    sys.exit(main())
