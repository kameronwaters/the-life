import os, sys, re, glob
from pypdf import PdfReader
A=os.path.expanduser("~/Documents/the-life/kaporos/sources/articles")
urls=[l.strip() for l in open(os.path.expanduser("~/Documents/the-life/kaporos/sources/urls.txt")) if l.strip()]
PAY=re.compile(r"subscribe to continue|subscription|sign in to read|paywall|premium article|log in to continue|create a free account|already a subscriber|access denied|403 forbidden|404|page not found|enable javascript|verify you are human|just a moment|cloudflare|are you a robot|unusual traffic|Please turn on JavaScript", re.I)
rows=[]
for i,u in enumerate(urls,1):
    pre=f"{i:03d}-"; m=[p for p in glob.glob(f"{A}/{pre}*.pdf")]
    if not m: rows.append((i,u,"MISSING","no pdf")); continue
    p=m[0]; sz=os.path.getsize(p)
    try:
        r=PdfReader(p); n=len(r.pages); txt="".join((r.pages[k].extract_text() or "") for k in range(min(n,3)))
    except Exception as e:
        rows.append((i,u,"BROKEN",str(e)[:60])); continue
    words=len(txt.split()); hit=PAY.search(txt)
    flag="ok"
    if words<120: flag="EMPTY/THIN"
    if hit: flag=f"PAYWALL? ({hit.group(0)})"
    rows.append((i,u,flag,f"{n}p {sz//1024}KB {words}w"))
for r in rows:
    if r[2]!="ok": print(*r, sep="\t")
print("total",len(rows),"ok",sum(1 for r in rows if r[2]=="ok"))
