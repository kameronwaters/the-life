"""
Layer-based renderer. A spec is:

    {
      "name": "kaporos-part3-a",
      "size": "yt" | [w, h],
      "extends": "a.json",                # optional: deep-merge over another spec in the same folder
      "layers": [ {"type": ..., "id": ...}, ... ],
      "grade": { overrides of brand.grade_defaults },
      "text": { ... }                     # drawn last, after the grade
    }

Layer types (in the order you list them):
    plate    {src, scale?, x?, shift?, fit?: "cover"|"width"}   base photograph
    image    {src, x, y, w?, h?, rot?, opacity?, blur?}          any image / logo / prop
    sticker  {src, x, y, w, rot?, brightness?, blur?, shadow?}  flat printed thing pasted into the scene
    cutout   {src, crop?, height, cx, bottom?, brightness?, flip?, lightwrap?}   RGBA person/object
    fade     {top?, bottom?, left?, right?, strength?}          black fades for type
    gradient {color, from, to, alpha}                           full-frame tint
    vignette {amount}                                           extra vignette before grade

Everything is composited first, then ONE global grade (clarity, contrast,
lifted blacks, split tone, bloom, vignette, grain), then type.
"""
import json, os
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance, ImageOps, ImageChops
from .brand import BRAND, rp, font, color, size_of


# ------------------------------------------------------------------ helpers

def _open(path, base):
    path = path if os.path.isabs(path) else os.path.join(base, path)
    if not os.path.exists(path):
        path = rp(path)
    if not os.path.exists(path):
        raise SystemExit(f"missing asset: {path}\n  drop it into videos/<slug>/assets/ (or change 'src' in the spec)")
    return Image.open(path)


def scene_mean(canvas, box):
    box = (max(0, box[0]), max(0, box[1]), min(canvas.size[0], box[2]), min(canvas.size[1], box[3]))
    if box[2] <= box[0] or box[3] <= box[1]:
        return (128, 128, 128)
    reg = canvas.crop(box).resize((8, 8))
    px = list(reg.getdata())
    return tuple(sum(c[i] for c in px) / len(px) for i in range(3))


def tint_to_scene(rgb, mean, strength=0.5):
    r, g, b = rgb.split()
    lm = sum(mean) / 3 or 1
    fr, fg, fb = [1 + strength * (c / lm - 1) for c in mean]
    return Image.merge("RGB", (r.point(lambda v: min(255, int(v * fr))),
                               g.point(lambda v: min(255, int(v * fg))),
                               b.point(lambda v: min(255, int(v * fb)))))


def _resize_to(im, w=None, h=None):
    if w and not h:
        h = int(w * im.size[1] / im.size[0])
    elif h and not w:
        w = int(h * im.size[0] / im.size[1])
    elif not w and not h:
        return im
    return im.resize((int(w), int(h)), Image.LANCZOS)


# ------------------------------------------------------------------ layers

def l_plate(canvas, s, base):
    W, H = canvas.size
    im = _open(s["src"], base).convert("RGB")
    fit = s.get("fit", "width")
    if "scale" in s:
        scale = s["scale"]
    elif fit == "cover":
        scale = max(W / im.size[0], H / im.size[1])
    else:
        scale = W / im.size[0]
    im = im.resize((int(im.size[0] * scale), int(im.size[1] * scale)), Image.LANCZOS)
    if s.get("flip"):
        im = ImageOps.mirror(im)
    x = s.get("x", (W - im.size[0]) // 2 if fit == "cover" else 0)
    y = s.get("shift", s.get("y", (H - im.size[1]) // 2 if fit == "cover" else 0))
    canvas.paste(im, (x, y))
    return canvas


def l_image(canvas, s, base):
    im = _open(s["src"], base).convert("RGBA")
    im = _resize_to(im, s.get("w"), s.get("h"))
    if s.get("flip"):
        im = ImageOps.mirror(im)
    if s.get("blur"):
        im = im.filter(ImageFilter.GaussianBlur(s["blur"]))
    if s.get("rot"):
        im = im.rotate(s["rot"], expand=True, resample=Image.BICUBIC)
    if s.get("opacity", 1) < 1:
        a = im.split()[3].point(lambda v: int(v * s["opacity"]))
        im.putalpha(a)
    out = canvas.convert("RGBA")
    out.paste(im, (s["x"], s["y"]), im)
    return out.convert("RGB")


def l_sticker(canvas, s, base):
    W, H = canvas.size
    flat = _open(s["src"], base).convert("RGB")
    st = _resize_to(flat, s["w"])
    w, h = st.size
    st = ImageEnhance.Brightness(st).enhance(s.get("brightness", 0.8))
    st = ImageEnhance.Color(st).enhance(0.85)
    st = tint_to_scene(st, scene_mean(canvas, (s["x"], s["y"], s["x"] + w, s["y"] + h)), s.get("match", 0.45))
    st = st.filter(ImageFilter.GaussianBlur(s.get("blur", 0.5)))
    st = st.convert("RGBA").rotate(s.get("rot", 0), expand=True, resample=Image.BICUBIC)
    out = canvas.convert("RGBA")
    if s.get("shadow", True):
        sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        shl = Image.new("RGBA", st.size, (0, 0, 0, 0))
        shl.putalpha(st.split()[3].point(lambda v: int(v * 0.6)))
        sh.paste(shl, (s["x"] + 6, s["y"] + 8), shl)
        out = Image.alpha_composite(out, sh.filter(ImageFilter.GaussianBlur(7)))
    out.paste(st, (s["x"], s["y"]), st)
    return out.convert("RGB")


def l_cutout(canvas, s, base):
    W, H = canvas.size
    cut = _open(s["src"], base).convert("RGBA")
    if "crop" in s:
        cut = cut.crop(tuple(s["crop"]))
    if s.get("flip"):
        cut = ImageOps.mirror(cut)
    cut = _resize_to(cut, h=s["height"]) if "height" in s else _resize_to(cut, w=s["width"])
    x0 = int(W * s["cx"]) - cut.size[0] // 2 if "cx" in s else s["x"]
    y0 = s.get("bottom", H + 10) - cut.size[1] if "y" not in s else s["y"]
    rgb = cut.convert("RGB"); a = cut.split()[3]
    box = (x0, y0, x0 + cut.size[0], y0 + cut.size[1])
    mean = scene_mean(canvas, box)
    rgb = ImageEnhance.Brightness(rgb).enhance(s.get("brightness", 0.74))
    rgb = ImageEnhance.Contrast(rgb).enhance(s.get("contrast", 1.12))
    rgb = ImageEnhance.Color(rgb).enhance(s.get("saturation", 0.88))
    rgb = tint_to_scene(rgb, mean, s.get("match", 0.55))
    if s.get("lightwrap", True):
        cb = (max(box[0], 0), max(box[1], 0), min(box[2], W), min(box[3], H))
        if cb[2] > cb[0] and cb[3] > cb[1]:
            bg = canvas.crop(cb).resize(cut.size).filter(ImageFilter.GaussianBlur(18))
            edge = ImageChops.subtract(a, a.filter(ImageFilter.MinFilter(9)))
            edge = edge.filter(ImageFilter.GaussianBlur(4)).point(lambda v: int(v * 0.7))
            rgb = Image.composite(bg, rgb, edge)
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    c2 = rgb.copy(); c2.putalpha(a)
    layer.paste(c2, (x0, y0), c2)
    out = canvas.convert("RGBA")
    if s.get("shadow", True):
        shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        shadow.putalpha(layer.split()[3].filter(ImageFilter.GaussianBlur(26)).point(lambda v: int(v * 0.85)))
        out = Image.alpha_composite(out, shadow)
    out = Image.alpha_composite(out, layer)
    return out.convert("RGB")


def l_fade(canvas, s, base=None):
    W, H = canvas.size
    k = s.get("strength", 205)
    c = canvas.convert("RGBA")
    m = Image.new("L", (W, H), 0); d = ImageDraw.Draw(m)
    for side in ("top", "bottom", "left", "right"):
        px = s.get(side)
        if not px:
            continue
        for i in range(px):
            v = int(k * (1 - i / px) ** 1.3)
            if side == "top":    d.line([(0, i), (W, i)], fill=v)
            if side == "bottom": d.line([(0, H - 1 - i), (W, H - 1 - i)], fill=v)
            if side == "left":   d.line([(i, 0), (i, H)], fill=v)
            if side == "right":  d.line([(W - 1 - i, 0), (W - 1 - i, H)], fill=v)
    return Image.composite(Image.new("RGBA", (W, H), (0, 0, 0, 255)), c, m).convert("RGB")


def l_gradient(canvas, s, base=None):
    W, H = canvas.size
    col = color(s.get("color", "black"))
    m = Image.linear_gradient("L").resize((W, H))
    if s.get("from", "top") == "bottom":
        m = ImageOps.flip(m)
    m = m.point(lambda v: int(v * s.get("alpha", 0.5)))
    return Image.composite(Image.new("RGB", (W, H), col), canvas, m)


LAYERS = {"plate": l_plate, "image": l_image, "sticker": l_sticker, "cutout": l_cutout,
          "fade": l_fade, "gradient": l_gradient}


# ------------------------------------------------------------------ grade

def grade(im, g):
    W, H = im.size
    if g.get("clarity"):
        im = im.filter(ImageFilter.UnsharpMask(radius=22, percent=int(100 * g["clarity"]), threshold=2))
    im = ImageEnhance.Contrast(im).enhance(g["contrast"])
    im = ImageEnhance.Color(im).enhance(g["saturation"])
    lift = g["lift_blacks"]
    im = im.point([min(255, int(lift + v * (255 - lift) / 255)) for v in range(256)] * 3)
    lum = ImageOps.grayscale(im)
    sh_mask = lum.point(lambda v: max(0, 255 - v * 2))
    hi_mask = lum.point(lambda v: max(0, (v - 128) * 2))

    def tone(img, shift, mask):
        ch = [c.point(lambda v, d=d: max(0, min(255, v + d))) for c, d in zip(img.split(), shift)]
        return Image.composite(Image.merge("RGB", ch), img, mask)
    im = tone(im, g["split_shadows"], sh_mask)
    im = tone(im, [int(c * g["warmth"]) for c in g["split_highlights"]], hi_mask)
    if g.get("bloom"):
        glow = im.point(lambda v: max(0, (v - 150) * 2)).filter(ImageFilter.GaussianBlur(28))
        im = ImageChops.add(im, glow.point(lambda v: int(v * g["bloom"])))
    if g.get("vignette"):
        m = Image.new("L", (W, H), 0); d = ImageDraw.Draw(m)
        d.ellipse((-int(W * 0.25), -int(H * 0.45), int(W * 1.25), int(H * 1.45)), fill=255)
        m = m.filter(ImageFilter.GaussianBlur(220)).point(lambda v: int(255 - (255 - v) * g["vignette"]))
        im = Image.composite(im, Image.new("RGB", (W, H), (6, 5, 5)), m)
    if g.get("grain"):
        n = ImageOps.autocontrast(Image.effect_noise((W, H), 14).convert("L"))
        im = Image.blend(im, Image.merge("RGB", (n, n, n)), g["grain"])
    return im


# ------------------------------------------------------------------ type

def draw_text(canvas, t):
    if not t:
        return canvas
    W, H = canvas.size
    td = BRAND["text_defaults"]
    out = canvas.convert("RGBA")
    y = t.get("y", 22)
    for line in t["lines"]:
        f = font(line.get("font", t.get("font", "condensed")), line.get("size", t["size"]))
        txt = line["t"]
        tw = ImageDraw.Draw(out).textlength(txt, font=f)
        align = line.get("align", t.get("align", "left"))
        x = line.get("x", t.get("x", 40))
        if align == "center": x = (W - tw) // 2
        if align == "right":  x = W - tw - t.get("x", 40)
        stroke = line.get("stroke", td["stroke"])
        if t.get("shadow", True):
            sh = Image.new("RGBA", (W, H), (0, 0, 0, 0)); sd = ImageDraw.Draw(sh)
            ox, oy = td["shadow_offset"]
            sd.text((x + ox, y + oy), txt, font=f, fill=(0, 0, 0, td["shadow_alpha"]),
                    stroke_width=stroke + 2, stroke_fill=(0, 0, 0, td["shadow_alpha"]))
            out = Image.alpha_composite(out, sh.filter(ImageFilter.GaussianBlur(td["shadow_blur"])))
        ImageDraw.Draw(out).text((x, y), txt, font=f, fill=color(line.get("color", "white")),
                                 stroke_width=stroke, stroke_fill=tuple(td["stroke_color"]))
        y += line.get("advance", int(line.get("size", t["size"]) * 1.0))
    return out.convert("RGB")


# ------------------------------------------------------------------ spec loading

def _merge(a, b):
    """deep merge b over a; layers are merged by id."""
    out = dict(a)
    for k, v in b.items():
        if k == "layers":
            byid = {l.get("id"): i for i, l in enumerate(out.get("layers", []))}
            layers = [dict(l) for l in out.get("layers", [])]
            for l in v:
                if l.get("id") in byid:
                    if l.get("remove"):
                        layers[byid[l["id"]]] = None
                    else:
                        layers[byid[l["id"]]].update(l)
                else:
                    layers.append(l)
            out["layers"] = [l for l in layers if l]
        elif isinstance(v, dict) and isinstance(out.get(k), dict):
            out[k] = _merge(out[k], v)
        else:
            out[k] = v
    return out


def load_spec(path):
    spec = json.load(open(path))
    if "extends" in spec:
        parent = load_spec(os.path.join(os.path.dirname(path), spec["extends"]))
        parent.pop("name", None)
        spec = _merge(parent, {k: v for k, v in spec.items() if k != "extends"})
    spec["name"] = os.path.splitext(os.path.basename(path))[0]
    spec["_dir"] = os.path.dirname(os.path.abspath(path))
    return spec


def render(spec):
    W, H = size_of(spec)
    base = os.path.dirname(spec["_dir"])        # videos/<slug>/
    canvas = Image.new("RGB", (W, H), color(spec.get("bg", "black")))
    for layer in spec.get("layers", []):
        fn = LAYERS.get(layer["type"])
        if not fn:
            raise SystemExit(f"unknown layer type {layer['type']}")
        canvas = fn(canvas, layer, base)
    g = dict(BRAND["grade_defaults"]); g.update(spec.get("grade", {}))
    if spec.get("grade") is not False:
        canvas = grade(canvas, g)
    for layer in spec.get("post", []):            # fades drawn after the grade, before type
        canvas = LAYERS[layer["type"]](canvas, layer, base)
    canvas = draw_text(canvas, spec.get("text"))
    return canvas


def render_file(path, out_dir=None):
    spec = load_spec(path)
    im = render(spec)
    out_dir = out_dir or os.path.join(os.path.dirname(spec["_dir"]), "out")
    os.makedirs(out_dir, exist_ok=True)
    out = os.path.join(out_dir, spec["name"] + ".jpg")
    im.save(out, quality=95)
    return out, im
