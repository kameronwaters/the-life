# Thumbnail system

Spec-driven, reproducible thumbnails for every video. One brand file, one renderer, one folder per video,
A/B/C variants as tiny JSON overrides, and previews at the sizes YouTube actually shows them.

```
brand/thumbnails/
  thumb               CLI  (./thumb -h)
  brand.json          palette, font roles, sizes, grade defaults, house rules
  fonts/              brand fonts by role (see fonts/README.md)
  templates/          doc/ (16:9 a,b,c)  short/ (9:16)  NOTES.md
  thumbkit/           render.py (layers + grade + type) · tools.py (cutout, flatten, fonts, previews) · figma.py · cli.py
  videos/<slug>/      assets/  specs/a.json b.json c.json  out/  NOTES.md
```

## Per-video procedure

```
cd brand/thumbnails
pip install -r requirements.txt                 # once per machine

thumb new my-video                               # scaffold from templates/doc
thumb cutout ~/Desktop/selfie.jpg -o videos/my-video/assets/presenter_cutout.png
thumb flatten ~/Desktop/sticker.jpg 412,388 1180,402 1166,990 398,966 -o videos/my-video/assets/prop.jpg
cp "<best frame>.jpg" videos/my-video/assets/plate.jpg

$EDITOR videos/my-video/specs/a.json             # positions, words, red word
thumb render my-video                            # out/a.jpg b.jpg c.jpg + _contact.jpg + *_preview.jpg
thumb watch  my-video                            # live re-render while you nudge numbers
thumb open   my-video                            # contact sheet in Preview
```

Then upload the three to YouTube's native A/B test ("Test & compare"). Keep the winner's spec; it is the record.

## Spec format

A spec is a list of layers composited in order, then ONE global grade, then `post` fades, then type.

```json
{
  "title": "the locked title (previews show it under the thumb)",
  "size": "yt",                                      // or "short", "ig", "square", or [w,h]
  "layers": [
    { "id": "plate",     "type": "plate",   "src": "assets/plate.jpg", "fit": "cover" },
    { "id": "prop",      "type": "sticker", "src": "assets/prop.jpg", "x": 940, "y": 470, "w": 330, "rot": -3 },
    { "id": "presenter", "type": "cutout",  "src": "assets/presenter_cutout.png", "height": 560, "cx": 0.66 },
    { "id": "logo",      "type": "image",   "src": "assets/logo.png", "x": 20, "y": 640, "w": 160, "opacity": 0.9 }
  ],
  "grade": { "contrast": 1.14, "saturation": 0.82 },  // overrides brand.grade_defaults; false = no grade
  "post":  [ { "type": "fade", "top": 330 } ],
  "text":  { "font": "condensed", "size": 168, "x": 40, "y": 22,
             "lines": [ { "t": "HE'S THE", "color": "white" }, { "t": "MESSIAH!?", "color": "red" } ] }
}
```

Variants extend the lead and override by layer `id`:

```json
{ "extends": "a.json",
  "layers": [ { "id": "presenter", "cx": 0.77 }, { "id": "logo", "remove": true } ],
  "text": { "lines": [ { "t": "HE'S THE", "color": "white" }, { "t": "Messiah!?", "color": "red", "font": "serif-italic", "stroke": 0 } ] } }
```

Layer reference is at the top of `thumbkit/render.py`. Every cutout and sticker is exposure- and colour-matched
to the scene behind it, gets a light wrap and a contact shadow, and then the single grade (clarity, contrast,
lifted blacks, split tone, bloom, vignette, grain) goes over everything so it reads as one photograph.

## Figma

Two ways in:

1. **Claude with the Figma connector** (claude.ai → connectors → Figma): Claude reads the file, pulls colour /
   type variables into `brand.json`, screenshots frames and drops them into `assets/`. Just paste a figma.com link.
2. **Terminal, no Claude**: `export FIGMA_TOKEN=figd_…` then
   `thumb figma export <file_key> <node-id> … --slug my-video` (PNG @2x into that video's assets) or
   `thumb figma vars <file_key>` (colour variables as JSON to paste into `brand.json`).

## Remote Control (work on it from your phone / claude.ai with the laptop's files)

On the laptop, in the repo:

```
cd ~/the-life && claude remote-control
```

(`claude --help` lists the exact subcommand if your version differs.) The session then shows up in the Claude
app / claude.ai/code and runs **on the laptop**, so Claude can open the XSPIRACY FONTS folder, raw stills, the
Premiere export folder, run `thumb cutout`, `thumb render`, and commit. A cloud session (like the one that built
this) only sees what is in the repo, which is why the fonts and plates must be committed.

## House rules (also in brand.json)

- One idea. One hero (face or object). Max 2 lines, max 3 words a line, one red word.
- Title and thumbnail complement each other, never say the same thing.
- One global grade over every composite. No pasted-on look.
- If the hero and the red word don't read at 168px (`*_preview.jpg`), it fails.
- Three real variants, not three crops. Let YouTube's test pick.

## Current projects

`thumb list`. First one is `kaporos-part3` (specs a/b/c, renders in its `out/`).
