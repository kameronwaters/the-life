import json, os
from PIL import ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))   # brand/thumbnails
BRAND = json.load(open(os.path.join(ROOT, "brand.json")))


def rp(path):
    """Resolve a path relative to the toolkit root."""
    return path if os.path.isabs(path) else os.path.join(ROOT, path)


def font_path(role):
    for cand in BRAND["fonts"].get(role, []):
        if os.path.exists(rp(cand)):
            return rp(cand)
    # allow a direct file path as a role
    if os.path.exists(rp(role)):
        return rp(role)
    raise SystemExit(f"no font found for role '{role}' (see fonts/README.md)")


def font(role, size):
    return ImageFont.truetype(font_path(role), size)


def font_is_fallback(role):
    return "fallback-" in os.path.basename(font_path(role))


def color(name):
    if isinstance(name, (list, tuple)):
        return tuple(name)
    if isinstance(name, str) and name.startswith("#"):
        h = name.lstrip("#")
        return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))
    return tuple(BRAND["palette"][name])


def size_of(spec):
    s = spec.get("size", "yt")
    if isinstance(s, str):
        return tuple(BRAND["sizes"][s])
    return tuple(s)
