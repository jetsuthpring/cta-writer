# ManyChat CTA Workflow — Client Setup Guide

This is the full process, end to end, for turning your short-form videos into a comment-to-DM machine that pushes viewers into your long-form YouTube content.

You'll be doing this with me (Jet) on the content side, and ManyChat on the automation side. Here's how the whole loop works.

## Overview of the loop

1. You send me your YouTube channel link (one time only).
2. For each new short-form video, I write the script and pick the matching long-form YouTube video from your channel.
3. I send you back: a **CTA line** to put in the video, a **keyword** for viewers to comment, and a **ManyChat setup block** with all the DM copy ready to paste.
4. You set up ManyChat for that specific post (~5 minutes).
5. You post the video.
6. Viewers comment the keyword → ManyChat auto-DMs them the YouTube link → they watch your long-form.

---

## Step 1 — Send me your YouTube channel link (one time)

Just paste me the URL of your YouTube channel. Any of these formats work:

- `youtube.com/@yourhandle`
- `youtube.com/channel/UCxxxxxx`
- `youtube.com/c/yourname`

I'll register your channel on my end and pull your videos + transcripts so I can match the right long-form video to each short-form script we make.

You only do this once.

---

## Step 2 — Send me your short-form script (or let me write it)

Either:
- Paste me the script you've already written, OR
- Tell me the topic and I'll write it.

I'll then pick the long-form YouTube video on your channel that best matches the topic of the short-form. This is what the keyword in the CTA will lead viewers to.

---

## Step 3 — What I'll send back

For each video, you'll get a block that looks like this:

```
Matched long-form: [Video title] — [YouTube URL]

Suggested keyword: THINK

CTA options:
1. [option 1]
2. [option 2]
3. [option 3]

→ pick one and tell me

── MANYCHAT SETUP BLOCK ──
Client:         [Your Name]
Platform:       instagram
🔑 Keyword:      THINK
💬 Public comment reply: "Sent! Check your DMs 👀"

── DM STAGE 1 — Opening DM ──
Message: Hey! Saw you commented THINK 🙌 Want me to send the video?
Button label: Yes, send it

── DM STAGE 2 — Follow-gate DM ──
Message: One small thing — make sure you're following so this works 🙏
Button label: I'm following

── DM STAGE 3 — Link DM ──
Message: Here it is — full breakdown 👇
Link card: Watch on YouTube
URL: https://youtube.com/watch?v=...
```

You'll plug those exact values into ManyChat in the steps below.

---

## Step 4 — One-time ManyChat + Instagram setup

Do this once. After this, every new video only takes ~5 minutes.

1. Go to **manychat.com** and sign up (the free plan is enough to start).
2. Switch your Instagram to a **Business** or **Creator** account:
   - Open Instagram → **Settings** → **Account type and tools** → **Switch to professional account**.
3. Link your Instagram to a **Facebook Page** (Meta requires this for ManyChat to work):
   - Instagram → **Settings** → **Accounts Center** → **Connect a Facebook account**.
   - If you don't have a Facebook Page yet, create a basic one — it doesn't need to be active.
4. In ManyChat → **Settings** → **Channels** → **Instagram** → click **Connect** and approve.

That's it for the one-time stuff.

---

## Step 5 — Per-video ManyChat setup (do this BEFORE posting)

Time: ~5 minutes per video.

### 5a. Create a new automation

- ManyChat dashboard → **Automation** → **+ New Automation**.
- Pick **Instagram → Comments → Specific Post**.
- If you haven't published yet, choose **Any Post** for now — you'll switch it to the specific post in Step 5f.

### 5b. Set the keyword trigger

- **Keyword**: paste the keyword I sent you (e.g. `THINK`).
- **Match type**: **Contains**.
- Case-insensitive should be on by default.

### 5c. Public comment reply

- Enable "Reply to comment publicly".
- Paste the **public comment reply** text from the block (e.g. "Sent! Check your DMs 👀").

### 5d. Build the DM flow (3 messages in order)

**Message 1 — Opening DM**
- Text: paste the **Opening DM** message.
- Add a **button** → label = the Stage 1 button text → action = "Go to next message".

**Message 2 — Follow-gate DM**
- Text: paste the **Follow-gate DM** message.
- Add a **button** → label = the Stage 2 button text → action = "Go to next message".

**Message 3 — Link DM**
- Text: paste the **Link DM** message.
- Add a **link card / URL button**:
  - Label = the **Link card** text (e.g. "Watch on YouTube")
  - URL = the YouTube **URL** from the block.

### 5e. Turn the automation ON

- Top right → toggle **Active**.

### 5f. After you post the video

- Copy the URL of the post you just published.
- Go back into the automation → change the trigger from "Any Post" to **that specific post**.
- Save.

---

## Step 6 — Test it before relying on it

1. From a **second Instagram account** (not your own), comment the keyword on the live post.
2. Within ~30 seconds you should see:
   - The public reply appear under the comment.
   - A DM arrive in the second account, walking through all 3 stages.
3. If nothing happens, check:
   - The automation is **Active**.
   - The **post URL** is set correctly.
   - Your IG is **Business/Creator** and connected to ManyChat.

---

## Step 7 — Post the video

- In your caption (or as a pinned comment), include the **CTA line** I sent you. That's what tells viewers what keyword to comment.
- Don't change the keyword wording — it has to match exactly what's in ManyChat for the trigger to fire.

---

## Reusing keywords

Each keyword can only point to **one** YouTube video at a time per IG account. If you want to reuse a keyword later for a different video, either:
- Pause the old automation first, or
- Use a fresh keyword (I'll always send you one that hasn't been used yet).

---

That's the whole loop. The first time takes a bit of setup, but every video after that is just: receive the block → 5 minutes in ManyChat → post.
