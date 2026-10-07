#!/usr/bin/env bash
# bash transcribe.sh file.mp4  → file.srt + file.txt   (pip install openai-whisper, or: pip install faster-whisper)
# The faster-whisper path decodes audio through ffmpeg (not PyAV), so it works regardless of the installed av version.
f="$1"
WHISPER_CPP_MODEL="${WHISPER_CPP_MODEL:-$HOME/moby_work/ggml-large-v3-turbo.bin}"
if command -v whisper-cli >/dev/null && [ -s "$WHISPER_CPP_MODEL" ]; then
  # whisper.cpp (large-v3-turbo) is installed on the Mac: faster and more accurate than medium, same output files.
  base="${f%.*}"; wav="$(mktemp -t kaporos).wav"
  ffmpeg -nostdin -v error -y -i "$f" -vn -ac 1 -ar 16000 "$wav"
  whisper-cli -m "$WHISPER_CPP_MODEL" -l en -osrt -of "$base" "$wav" >/dev/null 2>&1
  python3 - "$base.srt" "$base.txt" <<'PY'
import sys, re
srt, txt = sys.argv[1], sys.argv[2]
blocks = open(srt).read().strip().split("\n\n")
with open(txt, "w") as out:
    for b in blocks:
        lines = b.split("\n")
        if len(lines) < 3: continue
        h, m, s = lines[1].split(" --> ")[0].split(",")[0].split(":")
        out.write(f"[{int(h)*60+int(m):02}:{int(s):02}] {' '.join(l.strip() for l in lines[2:])}\n")
PY
  rm -f "$wav"; echo "wrote $base.srt $base.txt"
elif command -v whisper >/dev/null; then
  whisper "$f" --model medium --language en --output_format srt --output_format txt --output_dir "$(dirname "$f")"
else
  python3 - "$f" <<'PY'
import sys, os, subprocess
import numpy as np
from faster_whisper import WhisperModel
f = sys.argv[1]; base = os.path.splitext(f)[0]
raw = subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-i", f, "-vn", "-ac", "1", "-ar", "16000", "-f", "f32le", "-"],
                     capture_output=True, check=True).stdout
audio = np.frombuffer(raw, dtype=np.float32)
model = WhisperModel("medium", compute_type="int8")
segs, _ = model.transcribe(audio, language="en", vad_filter=True)
def ts(t): h=int(t//3600); m=int(t%3600//60); s=t%60; return f"{h:02}:{m:02}:{s:06.3f}".replace(".",",")
with open(base+".srt","w") as srt, open(base+".txt","w") as txt:
    for i, s in enumerate(segs, 1):
        srt.write(f"{i}\n{ts(s.start)} --> {ts(s.end)}\n{s.text.strip()}\n\n")
        txt.write(f"[{int(s.start//60):02}:{int(s.start%60):02}] {s.text.strip()}\n")
print("wrote", base+".srt", base+".txt")
PY
fi
