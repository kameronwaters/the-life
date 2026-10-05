"""Pull assets out of Figma with a personal access token (Settings → Security → Personal access tokens).

    export FIGMA_TOKEN=figd_...
    thumb figma export <file_key> <node_id> [<node_id>...] --out videos/<slug>/assets --scale 2
    thumb figma vars   <file_key>          # dump colour variables → prints palette JSON

file_key is the part of the URL after /design/ or /file/. node_id is the "node-id" query param (use ':' or '-').
No extra dependencies: urllib only.
"""
import os, json, urllib.request, urllib.parse

API = "https://api.figma.com/v1"


def _get(path, params=None):
    tok = os.environ.get("FIGMA_TOKEN")
    if not tok:
        raise SystemExit("set FIGMA_TOKEN (Figma → Settings → Security → Personal access tokens)")
    url = API + path + ("?" + urllib.parse.urlencode(params) if params else "")
    req = urllib.request.Request(url, headers={"X-Figma-Token": tok})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.load(r)


def export_nodes(file_key, node_ids, out_dir, scale=2, fmt="png"):
    ids = [n.replace("-", ":") for n in node_ids]
    res = _get(f"/images/{file_key}", {"ids": ",".join(ids), "scale": scale, "format": fmt})
    os.makedirs(out_dir, exist_ok=True)
    written = []
    meta = _get(f"/files/{file_key}/nodes", {"ids": ",".join(ids)})
    for nid, url in res.get("images", {}).items():
        if not url:
            print("no render for", nid); continue
        name = meta["nodes"].get(nid, {}).get("document", {}).get("name", nid)
        safe = "".join(c if c.isalnum() or c in "-_" else "_" for c in name).strip("_").lower() or nid.replace(":", "-")
        dst = os.path.join(out_dir, f"{safe}.{fmt}")
        urllib.request.urlretrieve(url, dst)
        written.append(dst)
    return written


def variables(file_key):
    """Local colour variables → {name: [r,g,b]} (needs an Enterprise/Full seat for the variables endpoint;
    falls back to styles)."""
    out = {}
    try:
        res = _get(f"/files/{file_key}/variables/local")
        for v in res["meta"]["variables"].values():
            if v["resolvedType"] == "COLOR":
                mode = next(iter(v["valuesByMode"].values()))
                if isinstance(mode, dict) and "r" in mode:
                    out[v["name"]] = [round(mode[k] * 255) for k in "rgb"]
    except Exception as e:
        print("variables endpoint unavailable:", e)
        res = _get(f"/files/{file_key}/styles")
        for s in res["meta"]["styles"]:
            if s["style_type"] == "FILL":
                out[s["name"]] = None
    return out
