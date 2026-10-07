---
name: thumbnail
description: Build or revise a YouTube/Shorts thumbnail for a video using the brand thumbnail system in brand/thumbnails (spec-driven, Christspiracy house style). Use when the user asks for a thumbnail, a thumbnail variant, a cutout, or to re-render thumbnails.
---

# Thumbnail skill

The system lives in `brand/thumbnails/` (read its README first). Never hand-build a thumbnail in a one-off
script; add or edit a spec so it is reproducible.

## Procedure

1. `cd brand/thumbnails && ./thumb list`. If the video has no folder: `./thumb new <slug>` (`--template short` for 9:16).
2. Read `videos/<slug>/NOTES.md`. Lock the title first; the thumbnail must complement it, not repeat it.
3. Assets into `videos/<slug>/assets/`:
   - plate: the single strongest frame (hero face or object, clean edge for type). Ask for a full-res export if you only have a screenshot.
   - presenter / objects: `./thumb cutout <photo> -o assets/<name>_cutout.png`
   - printed things (stickers, signs, pages): `./thumb flatten <photo> TL TR BR BL -o assets/<name>.jpg`
   - Figma assets: with the Figma connector, screenshot the node and save it; or `./thumb figma export`.
4. Edit `specs/a.json` (lead), then `b.json`/`c.json` as `extends` overrides. Three *different* ideas, not three crops.
5. `./thumb render <slug>`; look at `out/_contact.jpg` and `out/a_preview.jpg` (168px legibility is the gate).
6. Iterate on numbers, not on new scripts. Keep the grade global. Type goes last.
7. Record the choice and why in NOTES.md. Commit specs, assets and renders.

## Style (do not drift)

- Heavy condensed caps, white, ONE key word in brand red `#E45428`. Optional serif-italic accent word. Nothing else: no eyebrows, straplines, arrows, emoji, circles.
- Hard shadow under type. Max 2 lines, max 3 words a line.
- Everything composited takes the same single grade so it reads as one photograph.
- Fonts: `./thumb fonts` must say `ok` for `condensed` and `serif-italic`. If it says FALLBACK, say so in the hand-off; sizes may shift slightly with the real fonts.

## Checking

- vidIQ: `vidiq_score_thumbnail` on the render and `vidiq_score_title` on the title, if the connector is available.
- Galloway checks: one idea; promise delivered in first 10 s of the video; title+thumb complement; curiosity without lying.
