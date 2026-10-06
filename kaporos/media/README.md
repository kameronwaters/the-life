# Media intake (Parts 1 & 2, interviews, pickups)

Drop files here from the laptop; commit the small ones, keep the big ones out of git (see .gitignore) but
run `sheet.sh` and `transcribe.sh` so the cloud session can "see" and "hear" them through the sheets and text.

```
kaporos/media/
  part1.mp4   part1.sheet.jpg   part1.srt   part1.md      the Part 1 short as exported (vertical master)
  part2.mp4   part2.sheet.jpg   part2.srt   part2.md
  interviews/<slug>.mp4 (+ .sheet.jpg, .srt, .txt)         full interviews, one file each — 1080p H.264 PROXIES (6 Mb/s), not the
                                                            4K masters: the masters total 71 GB and the laptop had 38 GB free. Each
                                                            ../transcripts/<slug>.md names the master path on /Volumes/Jan 2025/Kapparot.
                                                            Joined files (vanessa, joseph, practitioner-lions) list the join offsets there.
  pickups/                                                  sticker wall, desk, hen, books, drive-in
  links.md                                                  IG / X / YT URLs of Parts 1 and 2, with view counts and date
```

- `sheet.sh <file.mp4>` → one JPG, a frame every 2 s, 6 across (every 3 s+ and smaller frames past ~24 min so the JPEG stays
  under its 65,500 px height limit and a few MB). Lets a session without video playback read the cut.
- `transcribe.sh <file.mp4>` → .srt and .txt with timecodes. Uses whisper.cpp (`whisper-cli`, large-v3-turbo at
  `~/moby_work/ggml-large-v3-turbo.bin`, override with `WHISPER_CPP_MODEL=`) when present, else `whisper`, else faster-whisper
  medium (decoded through ffmpeg, so it works with any PyAV). Parts 1 and 2 were done with faster-whisper medium before the
  whisper.cpp branch existed; the interviews with whisper.cpp.
- Glasses HEVC clips do not survive `-f concat` straight into one encode (garbled picture): transcode each clip first, then
  concat the proxies with `-c copy`.
- Interview transcripts then go to `../transcripts/<slug>.md` with the header in that folder's README.
