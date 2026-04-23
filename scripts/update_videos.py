#!/usr/bin/env python3
"""Scrape (or refresh) a client's YouTube videos + auto-generated transcripts.

Usage:
    update_videos.py <client_slug>           # refresh one client
    update_videos.py --all                   # refresh every registered client

Stores:
    data/videos/<slug>.json
        [{"video_id", "title", "url", "description", "duration",
          "upload_date", "has_transcript"}, ...]
    data/transcripts/<slug>/<video_id>.txt
        Plain-text auto-caption transcript (English). Missing if YouTube had
        no captions for that video.

Incremental: skips metadata fetch for already-cached videos, and skips
transcript fetch when the .txt already exists. Safe to run on every CTA job.
"""

from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

try:
    from youtube_transcript_api import YouTubeTranscriptApi
except ImportError:
    YouTubeTranscriptApi = None  # transcripts will be skipped with a clear message

SKILL_DIR = Path(__file__).resolve().parent.parent
CLIENTS_FILE = SKILL_DIR / "data" / "clients.json"
VIDEOS_DIR = SKILL_DIR / "data" / "videos"
TRANSCRIPTS_DIR = SKILL_DIR / "data" / "transcripts"


def run_ytdlp(args: list[str]) -> str:
    proc = subprocess.run(
        ["yt-dlp", *args],
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.returncode != 0:
        print(proc.stderr, file=sys.stderr)
        raise RuntimeError(f"yt-dlp failed (exit {proc.returncode})")
    return proc.stdout


def list_video_ids(channel_url: str) -> list[str]:
    url = channel_url.rstrip("/")
    if "/videos" not in url and "/channel/" not in url and "/@" in url:
        url = url + "/videos"
    elif "/channel/" in url and "/videos" not in url:
        url = url + "/videos"

    out = run_ytdlp([
        "--flat-playlist",
        "--print", "%(id)s\t%(title)s",
        "--skip-download",
        url,
    ])
    ids = []
    for line in out.splitlines():
        line = line.strip()
        if not line:
            continue
        parts = line.split("\t", 1)
        if parts and parts[0]:
            ids.append(parts[0])
    return ids


def fetch_video_metadata(video_id: str) -> dict:
    out = run_ytdlp([
        "--skip-download",
        "--dump-single-json",
        f"https://www.youtube.com/watch?v={video_id}",
    ])
    data = json.loads(out)
    return {
        "video_id": data.get("id"),
        "title": data.get("title"),
        "url": data.get("webpage_url") or f"https://www.youtube.com/watch?v={video_id}",
        "description": data.get("description") or "",
        "duration": data.get("duration"),
        "upload_date": data.get("upload_date"),
    }


def fetch_transcript(video_id: str) -> str | None:
    """Fetch a YouTube transcript via youtube-transcript-api (bypasses yt-dlp's PO-token limitation)."""
    if YouTubeTranscriptApi is None:
        return None
    try:
        api = YouTubeTranscriptApi()
        data = api.fetch(video_id)
    except Exception:
        return None
    text = " ".join(s.text for s in data if getattr(s, "text", "").strip()).strip()
    return text or None


def refresh_client(slug: str, clients: dict) -> None:
    client = clients.get(slug)
    if not client:
        print(f"Error: no client with slug '{slug}'. Register it first with add_client.py.", file=sys.stderr)
        sys.exit(2)

    out_file = VIDEOS_DIR / f"{slug}.json"
    transcript_dir = TRANSCRIPTS_DIR / slug
    transcript_dir.mkdir(parents=True, exist_ok=True)

    existing = json.loads(out_file.read_text()) if out_file.exists() else []
    existing_by_id = {v["video_id"]: v for v in existing if v.get("video_id")}

    print(f"[{slug}] Listing videos from {client['channel_url']} ...")
    current_ids = list_video_ids(client["channel_url"])
    print(f"[{slug}] Channel has {len(current_ids)} videos; {len(existing_by_id)} cached.")

    new_ids = [vid for vid in current_ids if vid not in existing_by_id]
    stale_ids = [vid for vid in existing_by_id if vid not in current_ids]

    if stale_ids:
        print(f"[{slug}] Removing {len(stale_ids)} stale entries (deleted/private).")
        for vid in stale_ids:
            existing_by_id.pop(vid, None)
            (transcript_dir / f"{vid}.txt").unlink(missing_ok=True)

    if new_ids:
        print(f"[{slug}] Fetching metadata for {len(new_ids)} new videos...")
        for i, vid in enumerate(new_ids, 1):
            try:
                meta = fetch_video_metadata(vid)
                existing_by_id[vid] = meta
                print(f"  [{i}/{len(new_ids)}] meta: {meta.get('title','?')[:70]}")
            except Exception as e:
                print(f"  [{i}/{len(new_ids)}] {vid} FAILED: {e}", file=sys.stderr)

    # Backfill transcripts for every video that doesn't have one cached yet.
    needs_transcript = [
        vid for vid in current_ids
        if vid in existing_by_id and not (transcript_dir / f"{vid}.txt").exists()
    ]
    if needs_transcript:
        print(f"[{slug}] Fetching transcripts for {len(needs_transcript)} videos...")
        for i, vid in enumerate(needs_transcript, 1):
            title = existing_by_id[vid].get("title", "?")[:70]
            try:
                text = fetch_transcript(vid)
                if text:
                    (transcript_dir / f"{vid}.txt").write_text(text + "\n")
                    existing_by_id[vid]["has_transcript"] = True
                    print(f"  [{i}/{len(needs_transcript)}] transcript: {title}")
                else:
                    existing_by_id[vid]["has_transcript"] = False
                    print(f"  [{i}/{len(needs_transcript)}] no captions: {title}")
            except Exception as e:
                existing_by_id[vid]["has_transcript"] = False
                print(f"  [{i}/{len(needs_transcript)}] {vid} FAILED: {e}", file=sys.stderr)
    else:
        print(f"[{slug}] All transcripts cached.")

    # Sync has_transcript flag on every entry (in case file was deleted externally).
    for vid, meta in existing_by_id.items():
        meta["has_transcript"] = (transcript_dir / f"{vid}.txt").exists()

    ordered = [existing_by_id[vid] for vid in current_ids if vid in existing_by_id]
    out_file.write_text(json.dumps(ordered, indent=2, ensure_ascii=False) + "\n")

    clients[slug]["last_updated"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
    CLIENTS_FILE.write_text(json.dumps(clients, indent=2) + "\n")
    with_tx = sum(1 for v in ordered if v.get("has_transcript"))
    print(f"[{slug}] Saved {len(ordered)} videos ({with_tx} with transcripts) -> {out_file}")


def main() -> int:
    if len(sys.argv) != 2:
        print(__doc__, file=sys.stderr)
        return 2

    VIDEOS_DIR.mkdir(parents=True, exist_ok=True)
    TRANSCRIPTS_DIR.mkdir(parents=True, exist_ok=True)
    clients = json.loads(CLIENTS_FILE.read_text()) if CLIENTS_FILE.exists() else {}

    arg = sys.argv[1]
    if arg == "--all":
        if not clients:
            print("No clients registered yet.", file=sys.stderr)
            return 1
        for slug in clients:
            refresh_client(slug, clients)
    else:
        refresh_client(arg, clients)
    return 0


if __name__ == "__main__":
    sys.exit(main())
