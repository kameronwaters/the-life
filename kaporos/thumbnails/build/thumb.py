#!/usr/bin/env python3
"""
Christspiracy thumbnail builder.

    python thumb.py specs/kaporos_part3.json          # renders to out/<spec name>.jpg
    python thumb.py specs/*.json                      # renders them all

Every layer (plate, sticker, presenter) is composited first, then ONE grade,
ONE grain, ONE vignette and ONE bloom are applied over everything so the
result reads as a single photograph instead of pasted parts. Type goes on
last, after the grade, so it stays clean.

Fonts: see fonts/README.md. Colors and defaults: style.json.
"""
import json, sys, os, math
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance, ImageOps, ImageChops

HERE = os.path.dirname(os.path.abspath(__file__))
STYLE = json.load(open(os.path.join(HERE, "style.json")))


def p(path):
    return path if os.path.isabs(path) else os.path.join(HERE, path)


def font(role, size):
    for cand in STYLE["fonts"][role]:
        if os.path.exists(p(cand)):
            return ImageFont.truetype(p(cand), size)
    raise SystemExit(f"no font found for role {role}")


def color(name):
    if isinstance(name, list):
        return tuple(name)
    return tuple(STYLE["palette"][name])


# ---------------------------------------------------------------- layers

def load_plate(spec, W, H):
    s = spec["plate"]
    im = Image.open(p(s["src"])).convert("RGB")
    scale = s.get("scale", W / im.size[0])
    im = im.resize((int(im.size[0] * scale), int(im.size[1] * scale)), Image.LANCZOS)
    canvas = Image.new("RGB", (W, H), (0, 0, 0))
    canvas.paste(im, (s.get("x", 0), s.get("shift", 0)))
    return canvas


def tint_to_scene(rgb, scene_mean, strength=0.5):
    """Push a layer's colour balance toward the scene's mean colour so it sits in the same light."""
    r, g, b = rgb.split()
    lm = sum(scene_mean) / 3 or 1
    fr, fg, fb = [1 + strength * (c / lm - 1) for c in scene_mean]
    r = r.point(lambda v: min(255, int(v * fr)))
    g = g.point(lambda v: min(255, int(v * fg)))
    b = b.point(lambda v: min(255, int(v * fb)))
    return Image.merge("RGB", (r, g, b))


def scene_mean(canvas, box):
    reg = canvas.crop(box).resize((8, 8))
    px = list(reg.getdata())
    return tuple(sum(c[i] for c in px) / len(px) for i in range(3))


def add_sticker(canvas, spec):
    s = spec.get("sticker")
    if not s:
        return canvas
    W, H = canvas.size
    flat = Image.open(p(s["src"])).convert("RGB")
    w = s["w"]; h = int(w * flat.size[1] / flat.size[0])
    st = flat.resize((w, h), Image.LANCZOS)
    st = ImageEnhance.Brightness(st).enhance(s.get("brightness", 0.8))
    st = ImageEnhance.Color(st).enhance(0.85)
    st = tint_to_scene(st, scene_mean(canvas, (s["x"], s["y"], s["x"] + w, s["y"] + h)), 0.45)
    st = st.filter(ImageFilter.GaussianBlur(s.get("blur", 0.5)))
    st = st.convert("RGBA").rotate(s.get("rot", -3.5), expand=True, resample=Image.BICUBIC)
    # cast shadow
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    a = st.split()[3].point(lambda v: int(v * 0.6))
    shl = Image.new("RGBA", st.size, (0, 0, 0, 0)); shl.putalpha(a)
    sh.paste(shl, (s["x"] + 6, s["y"] + 8), shl)
    sh = sh.filter(ImageFilter.GaussianBlur(7))
    out = Image.alpha_composite(canvas.convert("RGBA"), sh)
    out.paste(st, (s["x"], s["y"]), st)
    return out.convert("RGB")


def add_presenter(canvas, spec):
    s = spec.get("presenter")
    if not s:
        return canvas
    W, H = canvas.size
    cut = Image.open(p(s["src"])).convert("RGBA")
    if "crop" in s:
        cut = cut.crop(tuple(s["crop"]))
    scale = s["height"] / cut.size[1]
    cut = cut.resize((int(cut.size[0] * scale), int(cut.size[1] * scale)), Image.LANCZOS)
    x0 = int(W * s["cx"]) - cut.size[0] // 2
    y0 = s.get("bottom", H + 10) - cut.size[1]

    rgb = cut.convert("RGB"); a = cut.split()[3]
    # match exposure + colour to the scene region behind the presenter
    box = (max(x0, 0), max(y0, 0), min(x0 + cut.size[0], W), min(y0 + cut.size[1], H))
    mean = scene_mean(canvas, box)
    rgb = ImageEnhance.Brightness(rgb).enhance(s.get("brightness", 0.74))
    rgb = ImageEnhance.Contrast(rgb).enhance(1.12)
    rgb = ImageEnhance.Color(rgb).enhance(0.88)
    rgb = tint_to_scene(rgb, mean, 0.55)
    # light wrap: let the background bleed into the edge of the cutout
    bg = canvas.crop(box).resize(cut.size) if box[2] > box[0] and box[3] > box[1] else None
    if bg is not None and s.get("lightwrap", True):
        bgb = bg.filter(ImageFilter.GaussianBlur(18))
        edge = ImageChops.subtract(a, a.filter(ImageFilter.MinFilter(9)))  # outer rim of the alpha
        edge = edge.filter(ImageFilter.GaussianBlur(4)).point(lambda v: int(v * 0.7))
        rgb = Image.composite(bgb, rgb, edge)
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    cut2 = rgb.copy(); cut2.putalpha(a)
    layer.paste(cut2, (x0, y0), cut2)
    # contact shadow + ambient occlusion
    shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sa = layer.split()[3].filter(ImageFilter.GaussianBlur(26)).point(lambda v: int(v * 0.85))
    shadow.putalpha(sa)
    out = Image.alpha_composite(canvas.convert("RGBA"), shadow)
    out = Image.alpha_composite(out, layer)
    return out.convert("RGB")


# ---------------------------------------------------------------- global grade

def grade(canvas, g):
    W, H = canvas.size
    im = canvas
    # clarity (local contrast)
    if g["clarity"]:
        im = im.filter(ImageFilter.UnsharpMask(radius=22, percent=int(100 * g["clarity"]), threshold=2))
    im = ImageEnhance.Contrast(im).enhance(g["contrast"])
    im = ImageEnhance.Color(im).enhance(g["saturation"])
    # lift blacks (film look) then split tone
    lift = g["lift_blacks"]
    lut = [min(255, int(lift + v * (255 - lift) / 255)) for v in range(256)]
    im = im.point(lut * 3)
    lum = ImageOps.grayscale(im)
    sh_mask = lum.point(lambda v: max(0, 255 - v * 2))        # strong in shadows
    hi_mask = lum.point(lambda v: max(0, (v - 128) * 2))       # strong in highlights
    def tone(img, rgb_shift, mask):
        r, gg, b = img.split()
        r2 = r.point(lambda v: max(0, min(255, v + rgb_shift[0])))
        g2 = gg.point(lambda v: max(0, min(255, v + rgb_shift[1])))
        b2 = b.point(lambda v: max(0, min(255, v + rgb_shift[2])))
        return Image.composite(Image.merge("RGB", (r2, g2, b2)), img, mask)
    im = tone(im, g["split_shadows"], sh_mask)
    im = tone(im, [int(c * g["warmth"]) for c in g["split_highlights"]], hi_mask)
    # bloom: soft glow on highlights
    if g["bloom"]:
        glow = im.point(lambda v: max(0, (v - 150) * 2)).filter(ImageFilter.GaussianBlur(28))
        im = ImageChops.add(im, glow.point(lambda v: int(v * g["bloom"])))
    # vignette
    if g["vignette"]:
        m = Image.new("L", (W, H), 0); d = ImageDraw.Draw(m)
        d.ellipse((-int(W * 0.25), -int(H * 0.45), int(W * 1.25), int(H * 1.45)), fill=255)
        m = m.filter(ImageFilter.GaussianBlur(220)).point(lambda v: int(255 - (255 - v) * g["vignette"]))
        im = Image.composite(im, Image.new("RGB", (W, H), (6, 5, 5)), m)
    # grain
    if g["grain"]:
        n = ImageOps.autocontrast(Image.effect_noise((W, H), 14).convert("L"))
        im = Image.blend(im, Image.merge("RGB", (n, n, n)), g["grain"])
    return im


def top_fade(canvas, px):
    if not px:
        return canvas
    W, H = canvas.size
    c = canvas.convert("RGBA"); m = Image.new("L", (W, H), 0); d = ImageDraw.Draw(m)
    for y in range(px):
        d.line([(0, y), (W, y)], fill=int(205 * (1 - y / px) ** 1.3))
    return Image.composite(Image.new("RGBA", (W, H), (0, 0, 0, 255)), c, m).convert("RGB")


# ---------------------------------------------------------------- type

def draw_text(canvas, spec):
    t = spec.get("text")
    if not t:
        return canvas
    W, H = canvas.size
    td = STYLE["text_defaults"]
    out = canvas.convert("RGBA")
    y = t["y"]
    for line in t["lines"]:
        f = font(line.get("font", t.get("font", "condensed")), line.get("size", t["size"]))
        x = line.get("x", t["x"])
        txt = line["t"]
        d0 = ImageDraw.Draw(out)
        tw = d0.textlength(txt, font=f)
        if t.get("align") == "center":
            x = (W - tw) // 2
        stroke = line.get("stroke", td["stroke"])
        if t.get("shadow", True):
            sh = Image.new("RGBA", (W, H), (0, 0, 0, 0)); sd = ImageDraw.Draw(sh)
            ox, oy = td["shadow_offset"]
            sd.text((x + ox, y + oy), txt, font=f, fill=(0, 0, 0, td["shadow_alpha"]),
                    stroke_width=stroke + 2, stroke_fill=(0, 0, 0, td["shadow_alpha"]))
            out = Image.alpha_composite(out, sh.filter(ImageFilter.GaussianBlur(td["shadow_blur"])))
        d = ImageDraw.Draw(out)
        d.text((x, y), txt, font=f, fill=color(line.get("color", "white")),
               stroke_width=stroke, stroke_fill=(10, 8, 8))
        y += line.get("advance", int(line.get("size", t["size"]) * 1.0))
    return out.convert("RGB")


# ---------------------------------------------------------------- main

def build(spec_path):
    spec = json.load(open(spec_path))
    W, H = spec.get("size", [1280, 720])
    c = load_plate(spec, W, H)
    c = add_sticker(c, spec)
    c = add_presenter(c, spec)
    g = dict(STYLE["grade_defaults"]); g.update(spec.get("grade", {}))
    c = grade(c, g)
    c = top_fade(c, spec.get("top_fade", 0))
    c = draw_text(c, spec)
    name = spec.get("name") or os.path.splitext(os.path.basename(spec_path))[0]
    out = os.path.join(HERE, "out", name + ".jpg")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    c.save(out, quality=95)
    print("wrote", out)
    return out


if __name__ == "__main__":
    for sp in sys.argv[1:]:
        build(sp)
