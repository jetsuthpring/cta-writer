---
name: cta-writer
description: Write Manychat-style CTAs that route short-form viewers to a specific long-form YouTube video. Use when given a short-form script (TikTok, Reels, Shorts) that needs a comment-keyword CTA pointing to a client's existing YouTube video.
---

# CTA Writer

Turns a short-form script into 3–5 Manychat CTA options that push viewers to comment a keyword, triggering a ManyChat DM that links to the most relevant long-form YouTube video from the client's channel.

## Data layout

```
data/
  clients.json                        # {slug: {name, channel_url, last_updated}}
  videos/<slug>.json                  # cached video list per client (newest first)
  transcripts/<slug>/<video_id>.txt   # auto-caption transcript per video
  keywords.json                       # {slug: {KEYWORD: {cta, video, platform, ...}}}
references/
  cta-templates.csv                   # the user's proven CTA patterns
scripts/
  add_client.py                       # register a client
  update_videos.py                    # scrape/refresh videos + transcripts via yt-dlp
  list_clients.py                     # show registry + cache status
  list_keywords.py                    # show keywords already used per client
  save_keyword.py                     # record chosen CTA + print ManyChat setup block
```

Each entry in `videos/<slug>.json` has a `has_transcript` flag. Transcripts live in separate files so the index JSON stays small — only load the transcripts for the videos you're actually evaluating.

## Commands

All scripts live in `~/.claude/skills/cta-writer/scripts/` and are self-contained (stdlib + yt-dlp on PATH).

### Register a client

```bash
python3 ~/.claude/skills/cta-writer/scripts/add_client.py "<Client Name>" <youtube_channel_url>
```

Accepts channel URLs in any form: `youtube.com/@handle`, `youtube.com/channel/UC...`, or with `/videos` suffix.

### Refresh videos

```bash
python3 ~/.claude/skills/cta-writer/scripts/update_videos.py <slug>   # one client
python3 ~/.claude/skills/cta-writer/scripts/update_videos.py --all    # every client
```

Incremental: only fetches full metadata for videos not already cached. Safe to run on every invocation.

### List registered clients

```bash
python3 ~/.claude/skills/cta-writer/scripts/list_clients.py
```

## Workflow when the user pastes a script

1. **Identify the client.** If the user didn't name one, ask. Then check `data/clients.json` for the slug. If not registered, ask for the YouTube channel URL and run `add_client.py` + `update_videos.py`.
2. **Refresh videos + transcripts.** Always run `update_videos.py <slug>` before picking videos — catches new uploads AND backfills any missing transcripts. Fast when nothing changed.
3. **Shortlist with metadata.** Read `data/videos/<slug>.json`. Skim titles + descriptions to pick 3–5 candidate videos whose topic could plausibly match the short-form script. This is the cheap pass — don't load transcripts yet.
4. **Confirm with transcripts.** For each shortlisted candidate, read `data/transcripts/<slug>/<video_id>.txt` (only the shortlisted ones, not all 27+ videos). Use the actual spoken content to confirm the video genuinely covers the script's topic — titles/descriptions often mislead. Pick the single best primary video, plus an alt if the script spans two topics.
5. **Pull concrete references.** Skim the chosen transcript(s) for specific stories, names, numbers, frameworks the long-form video actually covers. CTAs land harder when they promise something specific the viewer can verify exists (e.g. "the 3-step framework he breaks down at minute 8").
6. **Check used keywords.** Run `list_keywords.py <slug>` (or read `data/keywords.json`) to see every keyword already taken for this client. Never propose one that's listed there — ManyChat conflicts if two automations on the same IG account share a keyword.
7. **Draft 3–5 CTAs.** Each CTA must:
   - Use a **short comment keyword** that is NOT in the used list for this client (one word, alphanumeric, ALL CAPS in the CTA text). The user wires the keyword into ManyChat; ManyChat DMs the YouTube link.
   - Reference the **value** the long-form video delivers, not just "watch my YouTube" — the keyword must feel worth commenting for.
   - Vary the angle: mix "full breakdown" / "free course" / "step-by-step" / "save this" / "I should be charging for this" framings pulled from `references/cta-templates.csv`.
   - Stay natural in short-form voice — conversational, under ~30 words each.
8. **Output format** — always this exact shape:

```
Matched long-form: <title> — <url>
(If 2nd pick) Alt: <title> — <url>

Suggested keyword: <KEYWORD>  (not previously used for this client)

CTA options:
1. <option 1>
2. <option 2>
3. <option 3>
4. <option 4>
5. <option 5>
```

9. **After the user picks a CTA**, run `save_keyword.py` with that CTA's details — it records the keyword (so future runs avoid it) and prints a paste-ready ManyChat setup block. Example:

```bash
python3 ~/.claude/skills/cta-writer/scripts/save_keyword.py <slug> \
  --keyword <KEYWORD> --video-id <video_id> \
  --cta "<the exact CTA text the user chose>" \
  --platform instagram
```

Optional flags: `--post-url <instagram-post-url>`, `--comment-reply "..."`, `--dm-opener "..."`. If the post URL isn't ready yet, omit it — the output block shows a placeholder the user can fill in later.

## CTA-writing rules

- **Always Manychat-style**: the viewer must comment a keyword. No "link in bio" only options — the whole point is triggering ManyChat.
- **Keyword requirements**: one word, 4–8 letters ideally, ALL CAPS in the CTA text (Manychat is case-insensitive but caps read cleanly). Must relate to the topic so the commenter remembers why they're commenting.
- **Do not invent videos**. If no video in the cache matches, say so and suggest either (a) a generic "follow for more" CTA or (b) that the client should make a long-form on this topic.
- **Match script tone**. If the short-form is blunt/sweary, the CTA can be too. If it's polished, keep it polished.
- **Templates are patterns, not scripts**. Use `references/cta-templates.csv` for structure/angles, but rewrite to fit the specific script and video.

## When to update video cache vs. skip

- **Always run `update_videos.py`** before drafting CTAs — it's the "built-in update" the user asked for.
- If the run shows "No new videos" and was done <24h ago, it's a no-op and near-instant.
- If the channel is huge (>100 videos) and this is the first scrape, warn the user that the initial cache build will take a few minutes.
