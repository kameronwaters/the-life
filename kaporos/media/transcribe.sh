#!/usr/bin/env bash
# bash transcribe.sh file.mp4  → file.srt + file.txt   (pip install openai-whisper, or: pip install mlx-whisper on Apple Silicon)
f="$1"
if command -v whisper >/dev/null; then
  whisper "$f" --model medium --language en --output_format srt --output_format txt --output_dir "$(dirname "$f")"
else
  python3 - "$f" <<'PY'
import sys, os
from faster_whisper import WhisperModel
f = sys.argv[1]; base = os.path.splitext(f)[0]
model = WhisperModel("medium", compute_type="int8")
segs, _ = model.transcribe(f, language="en", vad_filter=True)
def ts(t): h=int(t//3600); m=int(t%3600//60); s=t%60; return f"{h:02}:{m:02}:{s:06.3f}".replace(".",",")
with open(base+".srt","w") as srt, open(base+".txt","w") as txt:
    for i, s in enumerate(segs, 1):
        srt.write(f"{i}\n{ts(s.start)} --> {ts(s.end)}\n{s.text.strip()}\n\n")
        txt.write(f"[{int(s.start//60):02}:{int(s.start%60):02}] {s.text.strip()}\n")
print("wrote", base+".srt", base+".txt")
PY
fi
