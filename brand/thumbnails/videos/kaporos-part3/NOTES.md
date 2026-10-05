# kaporos-part3

- Title (locked): I Exposed the Doomsday Cult Behind America's Biggest Sacrifice...
- Promise the thumbnail makes: the man swinging the chicken is tied to a "Messiah" claim; Kameron is there, on the ground.
- Hero: the swinging man (plate). Secondary: real "MESSIAH IS HERE" sticker (Reade St), Kameron on-site cutout.
- Red word: MESSIAH!?
- Plate source: assets/swing_frame_real.jpg = 4K frame at 28.67s of `/Volumes/Jan 2025/Kapparot/Final Day/camera/C9304.MP4` (Sony log, converted with a levels stretch + gamma 1.2 + saturation 1.3 before the house grade). Found by sheeting all 103 camera clips at 1 frame / 2 s; the only overhead swings in the whole night are C9304 ~27-30s, C9355 ~120-124s (wide) and C9320 ~2-4s (blurred, child in frame). The old swing_frame.jpg was a supplied 640x400 press-style still and is kept only for reference.
- Cutouts: kameron_onsite_cutout.png (2160x3840, rembg bria-rmbg) from assets/kameron_onsite_selfie.jpg = frame at 19.10s of `/Volumes/Jan 2025/Kapparot/Day 3/Teleprompter-2026-16-09_18-30-48.MP4` (template-match score 0.995 vs the old 1320px cutout).
- Variants: a = lead (condensed, presenter lower-left, sticker on the fence between him and the rabbi), b = serif-italic accent, c = no presenter, plate shifted left, sticker covers the bystander lower-left
- Fonts: real brand fonts since 2026-10-05 (condensed = PPFormula-CondensedBlack, serif-italic = PPEiko-BlackItalic). Text sizes re-tuned: a 176/advance 172, b 156 + Eiko 122, so nothing touches the chicken.

## AI-plate variants (2026-10-05)
- d = Artlist / Nano Banana Pro 2K plate (assets/artlist_plate_4_notext_v2.jpg: 770 Eastern Parkway night, Chabad crowd, rabbi + bird from C9304, sticker on the pole) + the REAL studio cutout (assets/kameron_studio_cutout.png) over the AI version of Kameron, type set in PP Formula Condensed Black. Nano Banana's "remove the title" edit also erased the cap twice, hence the cutout.
- e = Artlist plate 1 (assets/artlist_plate_1_notext.jpg, AI Kameron kept, cap intact) + PP Eiko Black Italic accent.
- Grok v1 (old press still) and v2 (new brief) screenshots in out/_grok_designs*.png; comparison sheets out/_vs_grok.jpg and out/_vs_grok_artlist.jpg. Grok v1 repainted both faces; v2 is close but only available as screenshots (no download taken).
- Artlist refs: assetIds 69316504 (studio selfie), 5635d446 (C9304 frame), 4f7a4919 (sticker); generations 01a10e0f (4 designs), 01a10e11-dbe4/dbe6 (text-free 4 and 1), 01a10e13 (text-free 4, cap still lost). ~1,120 credits total.

## Relight pass (2026-10-05, later)
- Pipeline that finally kept both likenesses: build the collage in-house with REAL pixels (assets/composite_d2_notext.jpg = Artlist scene plate + rabbi_cutout.png from C9304 + kameron_studio_cutout.png), upload it, and ask Nano Banana Pro only to relight/integrate ("do not repaint... pixel-identical"). Results assets/relit_1..4.jpg (1-2 subtle, 3-4 chiaroscuro/A24). relit_2 kept cap text + shirt + sticker; relit_4 blanked the sticker (patched with the sticker layer in e.json).
- d = relit_2 + PP Formula; e = relit_4 + PP Eiko accent + real sticker patch. relit_2/relit_4 are the text-free plates if the type is placed by hand.
- Artlist generations 01a10e27-53ff / 01a10e27-5417 (640 credits).
