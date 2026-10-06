# Media intake (Parts 1 & 2, interviews, pickups)

Drop files here from the laptop; commit the small ones, keep the big ones out of git (see .gitignore) but
run `sheet.sh` and `transcribe.sh` so the cloud session can "see" and "hear" them through the sheets and text.

```
kaporos/media/
  part1.mp4   part1.sheet.jpg   part1.srt   part1.md      the Part 1 short as exported (vertical master)
  part2.mp4   part2.sheet.jpg   part2.srt   part2.md
  interviews/<slug>.mp4 (+ .sheet.jpg, .srt)               full interviews, one file each
  pickups/                                                  sticker wall, desk, hen, books, drive-in
  links.md                                                  IG / X / YT URLs of Parts 1 and 2, with view counts and date
```

- `sheet.sh <file.mp4>` → one JPG, a frame every 2 s, 6 across. Lets a session without video playback read the cut.
- `transcribe.sh <file.mp4>` → .srt and .txt with timecodes (whisper, medium model, runs on the Mac).
- Interview transcripts then go to `../transcripts/<slug>.md` with the header in that folder's README.
