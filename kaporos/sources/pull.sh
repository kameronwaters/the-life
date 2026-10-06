#!/usr/bin/env bash
# Archive every source the film cites. RUN ON THE LAPTOP (the cloud session has no outbound web).
#   brew install yt-dlp        (once)
#   bash kaporos/sources/pull.sh
# Output: articles/<n>-<slug>.pdf (+ .html)   video/<title> [id].mp4 (+ .info.json, subs)
# Afterwards: `.venv/bin/python -I review_pdfs.py` (needs pypdf) lists empty / paywalled / Cloudflare-challenge PDFs, and
# `python pdf_via_cdp.py <url> <out.pdf> 12` (needs websocket-client) re-prints one through a real headless Chrome that waits
# out the Cloudflare "Just a moment" page; that cleared chabad.org, forward.com, congress.gov on 2026-10-06.
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
    # Chrome writes the PDF and then sometimes never exits (seen on Chrome 154); run it under a timeout.
    "$CHROME" --headless --disable-gpu --no-pdf-header-footer --virtual-time-budget=8000 \
      --print-to-pdf="$pdf" "$url" >/dev/null 2>&1 &
    cpid=$!; for i in $(seq 1 60); do kill -0 $cpid 2>/dev/null || break; [ -s "$pdf" ] && { sleep 2; break; }; sleep 1; done
    kill -0 $cpid 2>/dev/null && kill -9 $cpid 2>/dev/null; wait $cpid 2>/dev/null
    [ -s "$pdf" ] || echo "PDF failed: $url"
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
