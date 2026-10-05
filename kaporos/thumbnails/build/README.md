# thumbnail build

Thumbnails as code. One spec file per thumbnail, one script, one style file. Re-render anything with:

```bash
cd kaporos/thumbnails/build
pip install pillow          # once
python thumb.py specs/kaporos_part3_tyler_a24.json
python thumb.py specs/*.json
```

Output lands in `out/<spec name>.jpg` at 1280x720.

## Why this reads as one image
`thumb.py` composites every layer first (plate, sticker, presenter), with each layer colour-matched to the scene behind it and light-wrapped at its edges, and only then applies ONE grade over everything: clarity, contrast, lifted blacks, split toning (cool shadows, warm highlights), bloom, vignette, grain. Type goes on last so it stays clean. Nothing is graded on its own.

## Files
- `style.json` — palette (white, brand red #E45428, cream, black), font roles, text and grade defaults. Change the brand here once.
- `fonts/` — drop `condensed.ttf` and `serif-italic.ttf` from the brand library here. Until then the OFL fallbacks (Anton, Playfair Display Black Italic) are used. See `fonts/README.md`.
- `assets/` — the real photographs: the swing frame (Artlist-upscaled), Kameron's cutout from the street selfie, the squared-up Messiah sticker from Reade St.
- `specs/` — one JSON per thumbnail: plate, sticker placement, presenter placement, grade overrides, type.
- `out/` — renders.

## Specs
- `kaporos_part3_tyler_a24.json` — the Tyler Oliveira grammar (presenter reacting, the scene, three words) with the Christspiracy treatment. **Lead.**
- `kaporos_part3_serif.json` — same with the serif-italic accent word, the Thug Rose layout.
- `kaporos_part3_poster_only.json` — no presenter, sticker on the wall. A/B variant.

## Making a new one
Copy a spec, change `plate.src`, the presenter cutout, the text lines. Cutouts: `rembg` produces the alpha PNG (`pip install rembg`). Stickers and signs: photograph them flat-on or square them with a four-point transform first.

This folder could move to `the-way/core/brand/` once that repo has its brand system; nothing here depends on this repo.
