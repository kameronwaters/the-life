#!/usr/bin/env bash
# bash sheet.sh file.mp4  → file.sheet.jpg (frame every 2 s, 6 columns; every 3+ s past 24 min), plus duration/size printout
# Rows are computed from the duration: a fixed 6x1000 grid overflows the JPEG size limit on vertical masters.
f="$1"; out="${f%.*}.sheet.jpg"
ffprobe -v error -show_entries format=duration:stream=width,height -of default=nw=1 "$f"
dur=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$f")
# Long files: widen the interval so the sheet stays under the 65,500 px JPEG height limit (~120 rows of vertical frames).
step=$(python3 -c "import math,sys; print(max(2, math.ceil(float(sys.argv[1])/720)))" "$dur")
frames=$(python3 -c "import math,sys; print(max(1, math.ceil(float(sys.argv[1])/float(sys.argv[2]))))" "$dur" "$step")
rows=$(( (frames + 5) / 6 ))
q=4; w=320; [ "$step" -gt 2 ] && { q=8; w=240; }   # long files: smaller frames and JPEG so the sheet stays a few MB in git
ffmpeg -v error -y -i "$f" -vf "fps=1/${step},scale=${w}:-1,tile=6x${rows}:padding=4:margin=4" -frames:v 1 -update 1 -q:v $q "$out"
echo "wrote $out ($frames frames every ${step}s, 6x$rows)"
