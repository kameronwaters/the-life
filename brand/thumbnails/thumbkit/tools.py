"""Asset prep: cutouts, flattening printed things, font import, previews."""
import os, shutil, json, glob
from PIL import Image, ImageDraw, ImageFont
from .brand import ROOT, BRAND, rp, font_path

FONT_EXT = (".ttf", ".otf", ".TTF", ".OTF")


# ---------------------------------------------------------------- cutout

def cutout(src, dst=None, model="bria-rmbg"):
    """Remove the background from a photo → RGBA PNG. Uses rembg (pip install rembg[cpu])."""
    try:
        from rembg import remove, new_session
    except ImportError:
        raise SystemExit("pip install 'rembg[cpu]' onnxruntime")
    try:
        sess = new_session(model)
    except Exception:
        sess = new_session("isnet-general-use")
    im = Image.open(src).convert("RGB")
    out = remove(im, session=sess)
    dst = dst or os.path.splitext(src)[0] + "_cutout.png"
    out.save(dst)
    return dst


# ---------------------------------------------------------------- flatten (4-point)

def _persp_coeffs(src_pts, dst_pts):
    import numpy as np
    A = []
    for (x, y), (u, v) in zip(dst_pts, src_pts):
        A.append([x, y, 1, 0, 0, 0, -u * x, -u * y])
        A.append([0, 0, 0, x, y, 1, -v * x, -v * y])
    A = np.array(A, dtype=float)
    B = np.array([c for pt in src_pts for c in pt], dtype=float)
    return tuple(np.linalg.solve(A, B))


def flatten(src, points, dst=None, width=1200):
    """Square up a sticker / sign / page photographed at an angle.
    points: 4 (x,y) corners in the photo, order TL, TR, BR, BL."""
    im = Image.open(src).convert("RGB")
    (x0, y0), (x1, y1), (x2, y2), (x3, y3) = points
    import math
    wpx = max(math.dist((x0, y0), (x1, y1)), math.dist((x3, y3), (x2, y2)))
    hpx = max(math.dist((x0, y0), (x3, y3)), math.dist((x1, y1), (x2, y2)))
    W = width; H = int(width * hpx / wpx)
    coeffs = _persp_coeffs(points, [(0, 0), (W, 0), (W, H), (0, H)])
    out = im.transform((W, H), Image.PERSPECTIVE, coeffs, Image.BICUBIC)
    dst = dst or os.path.splitext(src)[0] + "_flat.jpg"
    out.save(dst, quality=95)
    return dst


# ---------------------------------------------------------------- fonts

ROLE_HINTS = {
    "condensed":    (["condensed", "compressed", "narrow", "cond", "anton", "bebas", "druk", "tungsten", "knockout", "impact"],
                     ["black", "heavy", "bold", "extrabold", "ultra", "super", "wide"]),
    "serif-italic": (["italic", "ital", "oblique"], ["serif", "garamond", "playfair", "caslon", "didot", "bodoni", "times", "tiempos", "canela", "freight"]),
}


def _score(name, role):
    n = name.lower()
    primary, secondary = ROLE_HINTS[role]
    s = sum(3 for k in primary if k in n) + sum(1 for k in secondary if k in n)
    if role == "serif-italic" and "italic" not in n:
        s = 0
    return s


def import_fonts(src_dir, link=True):
    """Copy every .ttf/.otf under src_dir into fonts/, write fonts/manifest.json,
    and (best effort) link the brand roles condensed / serif-italic by filename."""
    dst = os.path.join(ROOT, "fonts")
    found = []
    for f in sorted(glob.glob(os.path.join(src_dir, "**", "*"), recursive=True)):
        if f.endswith(FONT_EXT) and os.path.isfile(f):
            name = os.path.basename(f)
            shutil.copy2(f, os.path.join(dst, name))
            found.append(name)
    manifest = {"source": src_dir, "fonts": found, "roles": {}}
    if link:
        for role in ROLE_HINTS:
            best = max(found, key=lambda n: _score(n, role), default=None)
            if best and _score(best, role) > 0:
                ext = os.path.splitext(best)[1].lower()
                target = os.path.join(dst, f"{role}{ext}")
                shutil.copy2(os.path.join(dst, best), target)
                manifest["roles"][role] = best
    json.dump(manifest, open(os.path.join(dst, "manifest.json"), "w"), indent=2)
    return manifest


def font_status():
    rows = []
    for role in BRAND["fonts"]:
        try:
            path = font_path(role)
            rows.append((role, os.path.basename(path), "FALLBACK" if "fallback-" in path else "ok"))
        except SystemExit:
            rows.append((role, "-", "MISSING"))
    return rows


def specimen(dst=None, sample="MESSIAH!? Blood 1234"):
    """Render every font in fonts/ with its filename so you can see what's what."""
    files = sorted(f for f in os.listdir(os.path.join(ROOT, "fonts")) if f.endswith(FONT_EXT))
    rowh = 120
    im = Image.new("RGB", (1600, 40 + rowh * max(1, len(files))), (20, 20, 20))
    d = ImageDraw.Draw(im)
    label = ImageFont.load_default()
    for i, f in enumerate(files):
        y = 20 + i * rowh
        d.text((20, y), f, font=label, fill=(160, 160, 160))
        try:
            d.text((20, y + 18), sample, font=ImageFont.truetype(os.path.join(ROOT, "fonts", f), 72), fill=(255, 255, 255))
        except Exception as e:
            d.text((20, y + 30), f"cannot load: {e}", font=label, fill=(228, 84, 40))
    dst = dst or os.path.join(ROOT, "fonts", "specimen.png")
    im.save(dst)
    return dst


# ---------------------------------------------------------------- previews

def contact_sheet(images, dst, cols=3, w=640, labels=True):
    """Side-by-side sheet of variants."""
    thumbs = []
    for path in images:
        im = Image.open(path).convert("RGB")
        im = im.resize((w, int(w * im.size[1] / im.size[0])), Image.LANCZOS)
        thumbs.append((os.path.basename(path), im))
    rows = (len(thumbs) + cols - 1) // cols
    th = max(t.size[1] for _, t in thumbs) + (28 if labels else 0)
    sheet = Image.new("RGB", (cols * (w + 20) + 20, rows * (th + 20) + 20), (24, 24, 24))
    d = ImageDraw.Draw(sheet)
    for i, (name, t) in enumerate(thumbs):
        x = 20 + (i % cols) * (w + 20); y = 20 + (i // cols) * (th + 20)
        sheet.paste(t, (x, y))
        if labels:
            d.text((x, y + t.size[1] + 8), name, fill=(200, 200, 200), font=ImageFont.load_default())
    sheet.save(dst)
    return dst


def youtube_preview(image, dst, title="Title goes here"):
    """How the thumbnail reads in the real UI: home grid (336px), search (360px), sidebar (168px), phone (~390px)."""
    src = Image.open(image).convert("RGB")
    sheet = Image.new("RGB", (1400, 560), (15, 15, 15))
    d = ImageDraw.Draw(sheet)
    lab = ImageFont.load_default()
    slots = [("home / desktop 336px", 336, 20, 20), ("search 360px", 360, 400, 20),
             ("sidebar 168px", 168, 800, 20), ("phone feed 390px", 390, 20, 290)]
    for name, w, x, y in slots:
        t = src.resize((w, int(w * src.size[1] / src.size[0])), Image.LANCZOS)
        sheet.paste(t, (x, y))
        d.text((x, y + t.size[1] + 6), title[:60], fill=(240, 240, 240), font=lab)
        d.text((x, y + t.size[1] + 20), name, fill=(130, 130, 130), font=lab)
    sheet.save(dst)
    return dst
