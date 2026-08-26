# Joey + Kam Episode — Export → QC → FCP → Thumbnail Runbook

A re-shareable prompt + operating manual for running the full post-production
pipeline autonomously overnight.

---

## 0. Read this first — where it has to run

This pipeline touches **Riverside in a logged-in Chrome profile**, the **local
filesystem**, and **Final Cut Pro**. All three live on the Mac. A cloud agent
(Claude Code on the web) has none of them and cannot do this job.

Run it from **Claude Code installed on the laptop** — the desktop app, or the
CLI in Terminal. That session can drive Chrome, read the Downloads folder, run
`ffmpeg`, and script Final Cut Pro via AppleScript.

### One-time setup before an unattended run

```bash
brew install ffmpeg          # audio QC + frame extraction
brew install --cask chromium # only if driving a separate browser profile
pip install openai-whisper   # transcript for title/hook mining (or use whisper.cpp)
```

Confirm before sleeping:
- Riverside is **already logged in** in the Chrome profile the agent will drive.
  An agent cannot pass an emailed magic link or 2FA at 3am.
- The edit is **already open** and is the correct one (Joey + Kam).
- Final Cut Pro has been **launched at least once** and its library is chosen.
- The Mac will **not sleep**: `caffeinate -dimsu` for the duration, or
  Settings → Lock Screen → never.
- Enough free disk for a multi-GB master export.

Unattended means the agent runs without approving each step. That is a real
grant — it can delete files and overwrite projects. Scope it to a working
directory and let it touch nothing else.

---

## 1. One deliberate change from the original plan

The original ask was: *watch the Riverside edit play through the whole episode,
confirm the audio is clean and Magic Audio is on, and only then export.*

**Do it the other way around: export first, then QC the exported file.**

Reasons:
- An agent "watching" a 50-minute browser playback is the least reliable check
  available. It cannot hear anything. It would be reading a waveform in a
  canvas element and guessing.
- The exported file is the artifact that actually ships. QC on the export is
  deterministic, measurable, and catches problems the preview player hides
  (render-stage dropouts, channel collapse, A/V drift).
- `ffmpeg` gives hard numbers — LUFS, true peak, silence spans, per-track
  levels — instead of a vibe.

So: verify Magic Audio is **toggled on** in the UI (a visual check, which is
what a browser agent is genuinely good at), export, then interrogate the file.
If QC fails, re-export rather than shipping a file nobody verified.

---

## 2. The prompt to paste

Copy everything in the block below into Claude Code **on the laptop**.

```
You are running an unattended overnight post-production pipeline. Work in
~/Episodes/joey-kam/ and create it if needed. Do not modify files outside it
except the Final Cut Pro library named in step 4.

Log every step with timestamps to ~/Episodes/joey-kam/run.log. If a step fails,
write the failure to the log, complete every step that does not depend on it,
and leave a clear STATUS.md at the end saying what succeeded and what did not.
Never report a step as done that you did not verify.

STEP 1 — RIVERSIDE PRE-FLIGHT (browser)
Open the Riverside project for the Joey + Kam episode in Chrome. Confirm and
screenshot each of these, saving screenshots to ./qc/:
  a. The correct edit is open (episode title, both speakers present).
  b. Magic Audio is toggled ON.
  c. Every speaker track is present and none is muted or soloed.
  d. The timeline end time matches the expected full episode length.
If Magic Audio is off, turn it on and wait for reprocessing to finish.
If anything else looks wrong, STOP, screenshot it, and write it to STATUS.md.
Do not attempt to fix an edit decision yourself.

STEP 2 — EXPORT
Trigger the highest-quality export available (separate audio tracks if the
option exists — it makes QC and any fix far easier). Renders can take 30-90+
minutes. Poll the export status roughly every 5 minutes; do not busy-wait.
When it completes, download it to ~/Episodes/joey-kam/master/.
Verify the download finished: no .crdownload file remains, and the file size
is stable across two checks 30 seconds apart.

STEP 3 — AUDIO QC ON THE EXPORTED FILE
Run the commands in Appendix A of this runbook against the downloaded master.
Write results to ./qc/audio-report.md. Flag as problems:
  - Integrated loudness outside -16 to -14 LUFS
  - True peak above -1.0 dBTP
  - Any silence span longer than 2s that is not an intentional beat
  - A dead or near-silent channel on either speaker
  - Duration mismatch vs. the Riverside timeline
  - A/V drift greater than 2 frames at the end of the file
If a defect is clearly a render fault (dropout, dead channel, truncation),
re-export once from Riverside and re-run QC. Note it in STATUS.md either way.

STEP 4 — FINAL CUT PRO
Do NOT drive the FCP GUI by clicking. Generate an FCPXML instead:
  - Build an .fcpxml (v1.11+) referencing the master file, with a project
    named "Joey + Kam — <date>", frame rate and audio rate matching the
    master exactly (read them from ffprobe, do not assume 23.98 or 29.97).
  - Validate it, then: open -a "Final Cut Pro" <path>.fcpxml
  - Confirm via AppleScript or a screenshot that the project opened with the
    clip present and the timeline length matching the master.
Leave FCP open on that project so it is ready in the morning.

STEP 5 — CLEANUP NOTES
Transcribe the master with whisper to ./transcript.txt (with timestamps).
From the transcript plus the audio report, write ./cleanup-notes.md listing
concrete, timestamped suggested fixes ONLY. Do not edit the video. Cover:
  - Filler-word clusters and long dead-air worth trimming (with timecodes)
  - False starts and repeated sentences
  - Cross-talk sections that may need ducking
  - Loudness inconsistencies between the two speakers
  - Any moment where a speaker is clipped, plosive, or off-mic
Rank by impact. Keep it to the 15 highest-value fixes, not an exhaustive list.

STEP 6 — SCREENSHOT EXTRACTION
Extract candidate frames of each speaker:
  ffmpeg -i master.mp4 -vf fps=1/5 ./frames/f_%05d.png
Then review the frames visually and select, for EACH of Joey and Kam:
  - 3 candidates with a strong, readable facial expression
  - Eyes open, face large in frame, sharp focus, clean separation from
    background (matters for cutout)
  - Prefer high-emotion moments: laughing, shocked, leaning in, pointing
Save the picks to ./thumbnail/picks/ named joey-1.png, kam-1.png, etc.
Delete the rest of ./frames/ afterward — it is thousands of files.

STEP 7 — TITLE + THUMBNAIL
Read Appendix B of this runbook for the channel's proven style before starting.
  a. Pull the 5 strongest hooks from the transcript — the most surprising,
     contentious, or quotable moments, with timecodes.
  b. Generate 12 title candidates using the channel's proven formula. Score
     each one, keep the top 3.
  c. Generate thumbnail concepts using the selected frames of Joey and Kam.
     Score each concept, refine the best, and iterate until the score stops
     improving or you have run 4 rounds.
  d. Output 3 finished 1280x720 thumbnails to ./thumbnail/final/ plus a
     THUMBNAILS.md explaining the reasoning and pairing each with a title.
Thumbnail text: 3-5 words maximum, readable at 168px wide. Never repeat the
title verbatim — the text must add a second hook, not echo the first.

STEP 8 — WRAP
Write ./STATUS.md: what completed, what failed and why, where every artifact
lives, and the single most important thing to check in the morning.
```

---

## Appendix A — Audio QC commands

```bash
M=~/Episodes/joey-kam/master/master.mp4

# Stream inventory, duration, sample rate, channel layout
ffprobe -v error -show_streams -show_format "$M"

# Broadcast loudness: integrated LUFS, LRA, true peak
ffmpeg -i "$M" -af ebur128=peak=true -f null - 2>&1 | tail -20

# Per-channel statistics — catches a dead or collapsed channel
ffmpeg -i "$M" -af astats=metadata=1:reset=0 -f null - 2>&1 | \
  grep -E "Channel|RMS level|Peak level|Flat factor"

# Silence detection: anything over 2s below -50dB
ffmpeg -i "$M" -af silencedetect=noise=-50dB:d=2 -f null - 2>&1 | \
  grep silence_

# Clipping check
ffmpeg -i "$M" -af astats=metadata=1 -f null - 2>&1 | grep -i "clipped"

# If exported with separate tracks, QC each independently
ffprobe -v error -select_streams a -show_entries stream=index,channels,codec_name "$M"
```

Targets for YouTube: **integrated -14 LUFS**, **true peak ≤ -1.0 dBTP**.
YouTube normalizes down but not up, so landing hot wastes headroom and landing
quiet loses to every video next to it in the sidebar.

---

## Appendix B — Channel style ground truth

Pulled from the live channel, not from memory.

**Channel:** Christspiracy — `UC12AQA6VyDa_vwTKm9a06FA`, ~15,000 subscribers.

**The Moby reference episode:**
`Moby: "How Would Jesus Kill An Animal?"` — published 2026-08-02, 49:40 runtime.
4,677 views, 435 likes, 171 comments. Views-per-hour of **5.74** — the highest
of any recent upload on the channel. Like rate ~9.3%, which is very high; the
audience that arrives is strongly engaged. The constraint is reach, not
retention. **The thumbnail's job is to widen the top of the funnel.**

**Top performers, long-form:**

| Title | Views | Note |
|---|---|---|
| The Gospel Catch: Something Fishy About Jesus' Dinner? | 26,124 | best long-form |
| Oxford Theologian Criticized Christspiracy… Then Changed His Mind? | 14,454 | breakout 2.79 |
| The $100B Meat Myth: If Meat Has Everything, Why Sell Supplements? | 7,175 | number hook |
| I'm Facing 12.5 Years in Prison for Rescuing a Beagle | 5,648 | personal stakes |
| Moby: "How Would Jesus Kill An Animal?" | 4,677 | highest VPH |

**The formula that actually works on this channel** — every top performer uses
at least two of these:

1. **A named authority put under pressure.** "Oxford Theologian", "Moby".
   The guest's name is a credential the viewer borrows.
2. **A question the viewer cannot answer but feels they should.** Note how
   many titles end in "?". This channel's audience clicks to resolve doubt,
   not to be told.
3. **A reversal.** "…Then Changed His Mind?" — the setup implies one outcome
   and the payoff implies another.
4. **A hard number.** "$100B", "12.5 Years", "46 Million".
5. **Moral stakes made concrete.** Not "animal ethics" — a beagle, a lamb,
   a dinner.

**What to avoid:** the channel's weakest videos are branded and abstract —
"Christspiracy | Sizzle Reel", "THANKSPIRACY: Cultural Myth Kills 46 Million!?".
Institutional voice underperforms personal voice consistently here.

**Thumbnail direction for a two-hander:** Joey and Kam facing each other or
split-frame, both with high-emotion expressions, is the strongest structural
choice — it reads as confrontation even before the text is parsed. Overlay text
should carry the *reversal*, while the title carries the *question*. Do not let
them say the same thing.

**Calibration:** this is a 15k-subscriber channel with excellent engagement.
A realistic ceiling for a great thumbnail here is the 25-30k range that "The
Gospel Catch" hit, not a million. Optimize for beating 26k, not for a fantasy.

---

## Appendix C — Known failure modes

- **Riverside session expires mid-render.** Verify login before sleeping.
  There is no recovery path at 3am.
- **Export silently fails or produces a truncated file.** This is why Step 3
  checks duration against the timeline, not just that a file exists.
- **The browser agent clicks the wrong export preset.** Screenshot the export
  dialog before confirming, so the morning review can catch it.
- **FCPXML frame-rate mismatch** causes FCP to conform the clip and drift the
  audio. Always read the real rate from `ffprobe`.
- **Frame extraction fills the disk.** A 50-minute file at 1 frame per 5
  seconds is ~600 PNGs, which is fine — at `fps=1` it is 3,000+. Delete after
  selection.
