#!/usr/bin/env bash
# Archive every source the film cites. RUN ON THE LAPTOP (the cloud session has no outbound web).
#   brew install yt-dlp        (once)
#   bash kaporos/sources/pull.sh
# Output: articles/<n>-<slug>.pdf (+ .html)   video/<title> [id].mp4 (+ .info.json, subs)
set -u
cd "$(dirname "$0")"
mkdir -p articles html video
CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
[ -x "$CHROME" ] || CHROME="$(command -v chromium || command -v google-chrome || true)"

n=0
while IFS= read -r url; do
  [ -z "$url" ] && continue
  n=$((n+1))
  slug=$(echo "$url" | sed -E 's#https?://(www\.)?##; s#[^A-Za-z0-9]+#-#g' | cut -c1-80)
  pdf="articles/$(printf '%03d' $n)-$slug.pdf"
  if [ ! -s "$pdf" ] && [ -n "$CHROME" ]; then
    "$CHROME" --headless --disable-gpu --no-pdf-header-footer --virtual-time-budget=8000 \
      --print-to-pdf="$pdf" "$url" >/dev/null 2>&1 || echo "PDF failed: $url"
  fi
  [ -s "html/$slug.html" ] || curl -sL -A "Mozilla/5.0" -m 30 -o "html/$slug.html" "$url" || echo "HTML failed: $url"
done < urls.txt
echo "articles: $(ls articles | wc -l) pdfs"

# videos: 1080p max, keep metadata and any English subs for the transcript folder
grep -v '^#' videos.txt | grep -v '^\s*$' | while IFS= read -r item; do
  yt-dlp --no-overwrites -f "bv*[height<=1080]+ba/b" --merge-output-format mp4 \
    --write-info-json --write-auto-subs --sub-langs en --convert-subs srt \
    -o "video/%(title).80s [%(id)s].%(ext)s" "$item" || echo "video failed: $item"
done
echo "video: $(ls video/*.mp4 2>/dev/null | wc -l) files"
