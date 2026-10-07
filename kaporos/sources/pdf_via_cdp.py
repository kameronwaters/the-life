"""Print a URL to PDF through a real (non-virtual-time) headless Chrome via CDP, waiting for Cloudflare-style challenges.
usage: python cdp_pdf.py <url> <out.pdf> [wait_seconds]"""
import sys, json, time, base64, subprocess, tempfile, urllib.request, shutil, os
url, out = sys.argv[1], sys.argv[2]; wait = float(sys.argv[3]) if len(sys.argv) > 3 else 12
import websocket
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
prof = tempfile.mkdtemp(prefix="cdpprof"); port = 9337
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36"
p = subprocess.Popen([CHROME, "--headless=new", "--disable-gpu", f"--remote-debugging-port={port}", f"--user-data-dir={prof}",
                      f"--user-agent={UA}", "--window-size=1280,2000", "about:blank"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
try:
    for _ in range(50):
        try:
            tabs = json.load(urllib.request.urlopen(f"http://127.0.0.1:{port}/json")); break
        except Exception: time.sleep(0.2)
    page = [t for t in tabs if t.get("type") == "page"][0]
    ws = websocket.create_connection(page["webSocketDebuggerUrl"], suppress_origin=True)
    mid = 0
    def send(method, params=None):
        global mid; mid += 1
        ws.send(json.dumps({"id": mid, "method": method, "params": params or {}}))
        while True:
            r = json.loads(ws.recv())
            if r.get("id") == mid: return r
    send("Page.enable"); send("Page.navigate", {"url": url})
    time.sleep(wait)
    # if still on a challenge page, wait more
    t = send("Runtime.evaluate", {"expression": "document.title + '|' + document.body.innerText.slice(0,200)", "returnByValue": True})
    title = t.get("result", {}).get("result", {}).get("value", "")
    if "Just a moment" in title or "verify you are human" in title.lower():
        time.sleep(wait)
    r = send("Page.printToPDF", {"printBackground": True, "preferCSSPageSize": False, "displayHeaderFooter": False})
    data = r.get("result", {}).get("data")
    if not data: print("NO PDF", r.get("error")); sys.exit(1)
    open(out, "wb").write(base64.b64decode(data)); print("wrote", out, os.path.getsize(out), "|", title[:80].replace("\n", " "))
finally:
    p.kill(); shutil.rmtree(prof, ignore_errors=True)
