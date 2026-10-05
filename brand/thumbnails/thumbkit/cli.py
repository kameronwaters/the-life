"""thumb — thumbnail production CLI. Run `thumb -h`."""
import argparse, os, sys, json, glob, shutil, subprocess
from .brand import ROOT, BRAND
from . import render as R, tools as T

VIDEOS = os.path.join(ROOT, "videos")
TEMPLATES = os.path.join(ROOT, "templates")


def video_dir(slug):
    d = os.path.join(VIDEOS, slug)
    if not os.path.isdir(d):
        raise SystemExit(f"no video folder {d}  (thumb new {slug})")
    return d


def cmd_new(a):
    d = os.path.join(VIDEOS, a.slug)
    if os.path.exists(d) and not a.force:
        raise SystemExit(f"{d} exists")
    for sub in ("assets", "specs", "out"):
        os.makedirs(os.path.join(d, sub), exist_ok=True)
    tpl = os.path.join(TEMPLATES, a.template)
    for f in glob.glob(os.path.join(tpl, "*.json")):
        shutil.copy2(f, os.path.join(d, "specs", os.path.basename(f)))
    shutil.copy2(os.path.join(TEMPLATES, "NOTES.md"), os.path.join(d, "NOTES.md"))
    print("created", d)
    print("next: drop plate + cutouts into assets/, edit specs/a.json, then: thumb render", a.slug)


def cmd_render(a):
    d = video_dir(a.slug)
    specs = sorted(glob.glob(os.path.join(d, "specs", f"{a.variant or '*'}.json")))
    if not specs:
        raise SystemExit("no specs")
    outs = []
    for sp in specs:
        out, _ = R.render_file(sp)
        print("wrote", os.path.relpath(out, ROOT)); outs.append(out)
    if len(outs) > 1:
        sheet = T.contact_sheet(outs, os.path.join(d, "out", "_contact.jpg"))
        print("wrote", os.path.relpath(sheet, ROOT))
    for out in outs:
        pv = T.youtube_preview(out, out.replace(".jpg", "_preview.jpg"), title=a.title or json.load(open(specs[0])).get("title", ""))
        print("wrote", os.path.relpath(pv, ROOT))
    for role, name, st in T.font_status():
        if st != "ok":
            print(f"WARNING font role '{role}' is {st} ({name}) — see fonts/README.md")


def cmd_watch(a):
    """Re-render whenever a spec or asset changes (poll, no deps)."""
    import time
    d = video_dir(a.slug)
    def stamp():
        return max(os.path.getmtime(f) for f in glob.glob(os.path.join(d, "specs", "*.json")) + glob.glob(os.path.join(d, "assets", "*")))
    last = 0
    print("watching", d, "(ctrl-c to stop)")
    while True:
        s = stamp()
        if s != last:
            last = s
            try:
                cmd_render(a)
            except SystemExit as e:
                print("render failed:", e)
        time.sleep(1)


def cmd_cutout(a):
    for src in a.images:
        print("wrote", T.cutout(src, a.out if len(a.images) == 1 else None, a.model))


def cmd_flatten(a):
    pts = [tuple(int(v) for v in p.split(",")) for p in a.points]
    print("wrote", T.flatten(a.image, pts, a.out, a.width))


def cmd_fonts(a):
    if a.action == "import":
        m = T.import_fonts(a.path, link=not a.no_link)
        print(f"copied {len(m['fonts'])} fonts; roles linked: {m['roles'] or 'none (link by hand, see fonts/README.md)'}")
        print("specimen:", T.specimen())
    elif a.action == "specimen":
        print("wrote", T.specimen())
    elif a.action == "link":
        src = os.path.join(ROOT, "fonts", a.path)
        ext = os.path.splitext(src)[1].lower()
        shutil.copy2(src, os.path.join(ROOT, "fonts", f"{a.role}{ext}"))
        print(f"{a.role} -> {a.path}")
    else:
        for role, name, st in T.font_status():
            print(f"{role:14} {st:9} {name}")


def cmd_list(a):
    for d in sorted(glob.glob(os.path.join(VIDEOS, "*"))):
        specs = glob.glob(os.path.join(d, "specs", "*.json")); outs = glob.glob(os.path.join(d, "out", "*.jpg"))
        print(f"{os.path.basename(d):30} {len(specs)} specs  {len(outs)} renders")


def cmd_figma(a):
    from . import figma
    if a.action == "export":
        out = a.out or os.path.join(VIDEOS, a.slug, "assets") if a.slug else os.path.join(ROOT, "assets")
        for f in figma.export_nodes(a.file_key, a.nodes, out, scale=a.scale, fmt=a.format):
            print("wrote", f)
    elif a.action == "vars":
        print(json.dumps(figma.variables(a.file_key), indent=2))


def cmd_open(a):
    d = video_dir(a.slug)
    target = os.path.join(d, "out", "_contact.jpg") if a.variant is None else os.path.join(d, "out", a.variant + ".jpg")
    opener = "open" if sys.platform == "darwin" else "xdg-open"
    subprocess.call([opener, target])


def main(argv=None):
    ap = argparse.ArgumentParser(prog="thumb", description="Christspiracy thumbnail production")
    sp = ap.add_subparsers(dest="cmd", required=True)

    s = sp.add_parser("new", help="scaffold videos/<slug>/ from a template"); s.add_argument("slug")
    s.add_argument("--template", default="doc"); s.add_argument("--force", action="store_true"); s.set_defaults(fn=cmd_new)

    s = sp.add_parser("render", help="render specs → out/, contact sheet, UI previews"); s.add_argument("slug")
    s.add_argument("variant", nargs="?"); s.add_argument("--title", default=None); s.set_defaults(fn=cmd_render)

    s = sp.add_parser("watch", help="re-render on every spec/asset change"); s.add_argument("slug")
    s.add_argument("variant", nargs="?"); s.add_argument("--title", default=None); s.set_defaults(fn=cmd_watch)

    s = sp.add_parser("cutout", help="remove background → RGBA png"); s.add_argument("images", nargs="+")
    s.add_argument("-o", "--out"); s.add_argument("--model", default="bria-rmbg"); s.set_defaults(fn=cmd_cutout)

    s = sp.add_parser("flatten", help="square up a sticker/sign: 4 corners TL TR BR BL as x,y"); s.add_argument("image")
    s.add_argument("points", nargs=4); s.add_argument("-o", "--out"); s.add_argument("--width", type=int, default=1200); s.set_defaults(fn=cmd_flatten)

    s = sp.add_parser("fonts", help="status | import <dir> | link <role> <file> | specimen")
    s.add_argument("action", nargs="?", default="status", choices=["status", "import", "link", "specimen"])
    s.add_argument("role", nargs="?"); s.add_argument("path", nargs="?"); s.add_argument("--no-link", action="store_true"); s.set_defaults(fn=cmd_fonts)

    s = sp.add_parser("list", help="all video projects"); s.set_defaults(fn=cmd_list)

    s = sp.add_parser("figma", help="export <file_key> <node>... | vars <file_key>  (needs FIGMA_TOKEN)")
    s.add_argument("action", choices=["export", "vars"]); s.add_argument("file_key"); s.add_argument("nodes", nargs="*")
    s.add_argument("--slug"); s.add_argument("--out"); s.add_argument("--scale", type=int, default=2); s.add_argument("--format", default="png"); s.set_defaults(fn=cmd_figma)

    s = sp.add_parser("open", help="open the contact sheet (or a variant) in the OS viewer"); s.add_argument("slug"); s.add_argument("variant", nargs="?"); s.set_defaults(fn=cmd_open)

    a = ap.parse_args(argv)
    # `thumb fonts import <dir>` → role slot holds the dir
    if a.cmd == "fonts" and a.action == "import" and a.path is None:
        a.path = a.role
    a.fn(a)


if __name__ == "__main__":
    main()
