#!/usr/bin/env bash
# bash sheet.sh file.mp4  → file.sheet.jpg (frame every 2 s, 6 columns), plus duration/size printout
f="$1"; out="${f%.*}.sheet.jpg"
ffprobe -v error -show_entries format=duration:stream=width,height -of default=nw=1 "$f"
ffmpeg -v error -y -i "$f" -vf "fps=1/2,scale=320:-1,tile=6x1000:padding=4:margin=4" -frames:v 1 -q:v 4 "$out"
echo "wrote $out"
