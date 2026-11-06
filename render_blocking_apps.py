#!/usr/bin/env python3
"""render_blocking_apps: toon blokkerende scripts en stylesheets in de <head> van een pagina.

Gebruik:
    python3 render_blocking_apps.py https://jouwwinkel.nl
    python3 render_blocking_apps.py pagina.html
    python3 render_blocking_apps.py https://jouwwinkel.nl --json

Leest de HTML zoals de server die levert. Scripts die later via JavaScript worden
toegevoegd zie je hier niet. Alleen standaardbibliotheek.
Gemaakt door Joepify (https://www.joepify.nl), MIT-licentie.
"""
import argparse, json, os, sys, urllib.parse, urllib.request
from collections import Counter
from html.parser import HTMLParser

KNOWN = {
    "cdn.shopify.com": "Shopify (thema of app-extensie)",
    "www.googletagmanager.com": "Google Tag Manager / GA4",
    "www.google-analytics.com": "Google Analytics",
    "connect.facebook.net": "Meta pixel",
    "static.klaviyo.com": "Klaviyo",
    "static.hotjar.com": "Hotjar",
    "script.hotjar.com": "Hotjar",
    "widget.trustpilot.com": "Trustpilot",
    "js.stripe.com": "Stripe",
    "cdn.judge.me": "Judge.me",
    "static.zdassets.com": "Zendesk",
    "code.tidio.co": "Tidio",
    "fonts.googleapis.com": "Google Fonts",
    "analytics.tiktok.com": "TikTok pixel",
}


class Head(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.in_head, self.scripts, self.styles, self.inline = False, [], [], []
        self._inline_buf, self._in_script = "", False

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "head":
            self.in_head = True
        elif tag == "body":
            self.in_head = False
        if not self.in_head:
            return
        if tag == "script":
            if a.get("src"):
                blocking = not any(k in a for k in ("async", "defer")) and (a.get("type") or "").lower() != "module"
                self.scripts.append({"src": a["src"], "blocking": blocking})
            else:
                self._in_script, self._inline_buf = True, ""
        elif tag == "link" and "stylesheet" in (a.get("rel") or "").lower().split():
            media = (a.get("media") or "all").strip().lower()
            self.styles.append({"href": a.get("href", ""), "blocking": media in ("all", "screen", "")})

    def handle_data(self, data):
        if self._in_script:
            self._inline_buf += data

    def handle_endtag(self, tag):
        if tag == "script" and self._in_script:
            self.inline.append(len(self._inline_buf.encode("utf-8")))
            self._in_script = False
        elif tag == "head":
            self.in_head = False


def load(src):
    if os.path.isfile(src):
        return open(src, encoding="utf-8", errors="replace").read(), "file:" + src
    if not src.startswith("http"):
        src = "https://" + src
    req = urllib.request.Request(src, headers={"User-Agent": "render-blocking-apps/1.0"})
    r = urllib.request.urlopen(req, timeout=20)
    return r.read(3_000_000).decode(r.headers.get_content_charset() or "utf-8", "replace"), r.geturl()


def host_path(url, base):
    full = urllib.parse.urljoin(base if base.startswith("http") else "https://local/", url)
    p = urllib.parse.urlsplit(full)
    return (p.netloc if base.startswith("http") or url.startswith(("http", "//")) else "(eigen domein)"), p.path


def analyse(html, base):
    h = Head()
    h.feed(html)
    own = urllib.parse.urlsplit(base).netloc if base.startswith("http") else ""
    def row(u):
        host, path = host_path(u, base)
        return {"domein": "(eigen domein)" if host == own else host, "pad": path}
    bs = [dict(row(s["src"])) for s in h.scripts if s["blocking"]]
    bc = [dict(row(s["href"])) for s in h.styles if s["blocking"]]
    ext = Counter(row(x["src"])["domein"] for x in h.scripts)
    ext.update(row(x["href"])["domein"] for x in h.styles)
    return {
        "blokkerende_scripts": bs,
        "blokkerende_stylesheets": bc,
        "externe_domeinen": dict(ext.most_common()),
        "inline_scripts": {"aantal": len(h.inline), "bytes": sum(h.inline)},
        "bekend": {d: KNOWN[d] for d in ext if d in KNOWN},
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("source", help="URL of HTML-bestand")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    try:
        html, base = load(a.source)
    except Exception as e:
        print(f"Kon niet laden: {e}", file=sys.stderr)
        sys.exit(2)
    r = analyse(html, base)
    if a.json:
        print(json.dumps(r, indent=2, ensure_ascii=False))
        return
    print(f"Blokkerende scripts in <head>: {len(r['blokkerende_scripts'])}")
    for s in r["blokkerende_scripts"]:
        print(f"  {s['domein']}   {s['pad']}")
    print(f"\nBlokkerende stylesheets in <head>: {len(r['blokkerende_stylesheets'])}")
    for s in r["blokkerende_stylesheets"]:
        print(f"  {s['domein']}   {s['pad']}")
    print("\nExterne domeinen en eigen bestanden (scripts + stylesheets):")
    for d, n in r["externe_domeinen"].items():
        print(f"  {n}x  {d}" + (f"   <- {r['bekend'][d]}" if d in r["bekend"] else ""))
    i = r["inline_scripts"]
    print(f"\nInline scripts in <head>: {i['aantal']} ({i['bytes']} bytes)")


if __name__ == "__main__":
    main()
