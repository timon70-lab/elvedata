#!/usr/bin/env python3
"""Validering av Elvesona-HTML før commit.

Bruk:  python scripts/valider.py <fil.html> [<fil2.html> ...] [--mot REF] [--uten-jsdom]

Sjekker i rekkefølge:
 1. Git-konfliktmarkører
 2. node --check på hvert inline <script> (uten src)
 3. div-balanse (<div vs </div>)
 4. HTML-nesting (stakkbasert)
 5. Toppnivå let/const/var/function-deklarasjoner mot git-referanse (standard HEAD)
 6. jsdom-røyktest (scripts/jsdom_smoke.js) — hoppes over hvis jsdom ikke er installert
Avslutter med kode 1 hvis noe feiler.
"""
import re, subprocess, sys, tempfile, os
from html.parser import HTMLParser

VOID = {"area","base","br","col","embed","hr","img","input","link","meta","param",
        "source","track","wbr","path","circle","rect","line","polyline","polygon",
        "ellipse","stop","use"}
OPTIONAL_CLOSE = {"p","li","td","th","tr","thead","tbody","tfoot","option","dt","dd"}
DECL = re.compile(r"^(?:let|const|var|function|async function|class)\s+([A-Za-z_$][\w$]*)", re.M)

def scripts(html):
    return [m.group(2) for m in re.finditer(
        r"<script(?![^>]*\bsrc=)([^>]*)>(.*?)</script>", html, re.S | re.I)
        if not re.search(r"type=[\"'](?:application/(?:ld\+)?json|text/template)", m.group(1), re.I)]

class Nest(HTMLParser):
    def __init__(s):
        super().__init__(); s.stack=[]; s.errors=[]
    def handle_starttag(s, tag, attrs):
        if tag not in VOID: s.stack.append((tag, s.getpos()[0]))
    def handle_startendtag(s, tag, attrs): pass
    def handle_endtag(s, tag):
        if tag in VOID: return
        while s.stack and s.stack[-1][0] != tag and s.stack[-1][0] in OPTIONAL_CLOSE:
            s.stack.pop()
        if s.stack and s.stack[-1][0] == tag: s.stack.pop()
        else:
            s.errors.append(f"linje {s.getpos()[0]}: </{tag}> uten matchende åpning"
                            + (f" (åpen: <{s.stack[-1][0]}> fra linje {s.stack[-1][1]})" if s.stack else ""))

def _toplevel(js):
    """Returnerer JS-kode på klammedybde 0, med strenger/kommentarer/regex-lignende maler fjernet."""
    out=[]; depth=0; i=0; n=len(js)
    while i<n:
        c=js[i]
        if js.startswith("//",i): j=js.find("\n",i); i=n if j<0 else j; continue
        if js.startswith("/*",i): j=js.find("*/",i+2); i=n if j<0 else j+2; continue
        if c in "'\"`":
            q=c; i+=1
            while i<n and js[i]!=q:
                i+=2 if js[i]=="\\" else 1
            i+=1; out.append(" ") if depth==0 else None; continue
        if c=="{": depth+=1
        elif c=="}": depth=max(0,depth-1)
        elif depth==0: out.append(c)
        if c in "{}" and depth<=1: out.append(" ")
        i+=1
    return "".join(out)

TOP=re.compile(r"(?:^|[;\s])(?:let|const|var|function\*?|class)\s+([A-Za-z_$][\w$]*)")
def decls(html):
    names=set()
    for sc in scripts(html): names |= set(TOP.findall(_toplevel(sc)))
    return names

def main():
    args=[a for a in sys.argv[1:]]
    ref="HEAD"; jsdom=True
    if "--mot" in args:
        i=args.index("--mot"); ref=args[i+1]; del args[i:i+2]
    if "--uten-jsdom" in args:
        args.remove("--uten-jsdom"); jsdom=False
    if not args: print(__doc__); sys.exit(2)
    ok=True
    for path in args:
        print(f"\n=== {path}")
        html=open(path, encoding="utf-8").read()
        # 1
        cm=[i+1 for i,l in enumerate(html.splitlines()) if re.match(r"^(<{7}|={7}|>{7})( |$)", l)]
        if cm: ok=False; print(f"  FEIL konfliktmarkører på linje {cm[:10]}")
        else: print("  ok  ingen konfliktmarkører")
        # 2
        js_ok=True
        for n, sc in enumerate(scripts(html), 1):
            with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False, encoding="utf-8") as f:
                f.write(sc); tmp=f.name
            r=subprocess.run(["node","--check",tmp],capture_output=True,text=True); os.unlink(tmp)
            if r.returncode: ok=js_ok=False; print(f"  FEIL node --check, script #{n}:\n{r.stderr.strip()}")
        if js_ok: print(f"  ok  node --check på {len(scripts(html))} inline-script")
        # 3
        o=len(re.findall(r"<div\b", html, re.I)); c=len(re.findall(r"</div>", html, re.I))
        # tell ikke div-strenger inne i JS-maler dobbelt: rapporter bare
        if o!=c: ok=False; print(f"  FEIL div-balanse: {o} <div vs {c} </div>")
        else: print(f"  ok  div-balanse {o}/{c}")
        # 4
        stripped=re.sub(r"<script\b.*?</script>|<style\b.*?</style>", "", html, flags=re.S|re.I)
        p=Nest(); p.feed(stripped)
        rest=[t for t in p.stack if t[0] not in OPTIONAL_CLOSE and t[0] not in ("html","body","head")]
        if p.errors or rest:
            ok=False
            for e in p.errors[:10]: print("  FEIL nesting:", e)
            for t,l in rest[:10]: print(f"  FEIL nesting: <{t}> fra linje {l} lukkes aldri")
        else: print("  ok  HTML-nesting")
        # 5
        r=subprocess.run(["git","show",f"{ref}:{os.path.relpath(path)}"],capture_output=True,text=True)
        if r.returncode==0:
            before, after = decls(r.stdout), decls(html)
            gone=sorted(before-after); new=sorted(after-before)
            if gone: ok=False; print(f"  FEIL deklarasjoner borte vs {ref}: {gone}")
            else: print(f"  ok  ingen toppnivå-deklarasjoner forsvunnet vs {ref}")
            if new: print(f"  info nye deklarasjoner: {new}")
        else: print(f"  info finnes ikke i {ref} (ny fil) — deklarasjonsdiff hoppet over")
        # 6
        if jsdom:
            here=os.path.dirname(os.path.abspath(__file__))
            r=subprocess.run(["node",os.path.join(here,"jsdom_smoke.js"),path],capture_output=True,text=True)
            if r.returncode==3: print("  info jsdom ikke installert (npm i -D jsdom) — røyktest hoppet over")
            elif r.returncode: ok=False; print("  FEIL jsdom:\n" + (r.stdout+r.stderr).strip())
            else: print("  ok  " + r.stdout.strip())
    print("\nRESULTAT:", "OK" if ok else "FEIL — ikke commit")
    sys.exit(0 if ok else 1)

if __name__=="__main__": main()
