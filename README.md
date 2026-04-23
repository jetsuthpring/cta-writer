# cta-writer

A Claude Code skill that turns short-form scripts (TikTok, Reels, Shorts) into ManyChat comment-to-DM setups that route viewers to the most relevant long-form video on a client's YouTube channel.

## What it does

1. You paste a short-form script.
2. Claude picks the best matching long-form YouTube video from the client's channel (reads actual transcripts, not just titles).
3. Returns 3–5 CTA options with a suggested keyword that hasn't been used for this client before.
4. You pick one → Claude prints a paste-ready ManyChat setup block (public comment reply + 3-stage DM sequence with rotated variations so viewers don't see the same text twice).

## Prerequisites

- [Claude Code](https://claude.com/claude-code)
- Python 3.9+
- `yt-dlp` on PATH — `brew install yt-dlp` or `pip3 install --user yt-dlp`
- `youtube-transcript-api` — `pip3 install --user youtube-transcript-api`

## Install

```bash
git clone <this-repo-url> ~/.claude/skills/cta-writer
```

That's it. Claude Code auto-loads any skill under `~/.claude/skills/`.

## Quick start

### 1. Register a client

```bash
python3 ~/.claude/skills/cta-writer/scripts/add_client.py "<Client Name>" <youtube-channel-url>
```

Example:
```bash
python3 ~/.claude/skills/cta-writer/scripts/add_client.py "Acme" https://www.youtube.com/@acmechannel
```

### 2. Scrape videos + transcripts

```bash
python3 ~/.claude/skills/cta-writer/scripts/update_videos.py <slug>
```

First run on a large channel takes a few minutes (one metadata + transcript fetch per video). After that, future runs are incremental — only new uploads get fetched.

### 3. Generate CTAs

In Claude Code, invoke `/cta-writer`, tell Claude which client, and paste the short-form script. You'll get 3–5 CTA options and a suggested keyword.

### 4. Lock in a CTA + get the ManyChat setup block

```bash
python3 ~/.claude/skills/cta-writer/scripts/save_keyword.py <slug> \
  --keyword <KEYWORD> \
  --video-id <yt-id> \
  --cta "<the chosen CTA text>" \
  --platform instagram
```

Output is a paste-ready block you copy into ManyChat → Instagram → Automation → New Automation → Comments.

## Other useful commands

```bash
# See all registered clients + their cache status
python3 ~/.claude/skills/cta-writer/scripts/list_clients.py

# See every keyword already used for a client (so you don't reuse)
python3 ~/.claude/skills/cta-writer/scripts/list_keywords.py <slug>

# Refresh every client's videos at once
python3 ~/.claude/skills/cta-writer/scripts/update_videos.py --all
```

## Customizing the ManyChat variations

The comment-reply and DM-sequence variations live in `references/manychat-variations.json`. Edit freely — `save_keyword.py` picks one at random per run. Every slot (comment reply, opening DM, buttons, follow-gate DM, link DM, link card label) has its own pool.

## Data layout

```
data/                              # all per-user state, gitignored
  clients.json                     # client registry
  videos/<slug>.json               # cached video list per client
  transcripts/<slug>/<id>.txt      # per-video transcript
  keywords.json                    # keywords used per client (prevents reuse)
references/
  cta-templates.csv                # proven CTA patterns (pool for Claude to pull from)
  manychat-variations.json         # rotated text for ManyChat setup
scripts/
  add_client.py                    # register client
  update_videos.py                 # scrape/refresh videos + transcripts
  list_clients.py                  # list registered clients
  list_keywords.py                 # list used keywords per client
  save_keyword.py                  # lock a keyword + print ManyChat block
SKILL.md                           # skill definition + workflow rules
```

## Notes

- **Keyword scope is per-client** — the same keyword can be reused across different clients, just not twice for the same one (ManyChat conflicts if two automations on the same IG account share a keyword).
- **Platform support:** Instagram (full), Facebook (full), TikTok (manual-reply block only — ManyChat doesn't support TikTok).
- **Transcript fetching** uses `youtube-transcript-api` because `yt-dlp` now requires a PO token for auto-captions.
