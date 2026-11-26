"""Shared photo helpers for build.py and lab.py (LCC v2.1 photography layer).

Photo library: data/content.json -> "library" (curated list). Two kinds of entry:
  * {"yt": "<videoId>", "frame": 1|2|3, ...}  a real frame captured inside one of LCC's own YouTube
    streams, served by YouTube's image service (the same images YouTube shows for the video).
  * {"src": "assets/photos/<file>.jpg", "approved": true, ...}  a church photograph that the LCC media
    team has approved for the website. Unapproved local photos are never rendered.
Pages ask for photos by category (pick("worship", 0)); swapping a photo is a data edit, not a code edit."""
import json, pathlib, html, re

ROOT = pathlib.Path(__file__).resolve().parent.parent
_C = json.loads((ROOT / "data/content.json").read_text(encoding="utf-8"))
LIB = [p for p in _C.get("library", []) if p.get("yt") or (p.get("src") and p.get("approved"))]
BY = {p["slug"]: p for p in LIB}
CAT = {}
for _p in LIB:
    CAT.setdefault(_p["cat"], []).append(_p["slug"])
CATNAME = {"worship": "Worship", "team": "Worship team", "conference": "Cutting Edge 2026", "teaching": "The Word",
           "events": "Gatherings", "youth": "Students", "fellowship": "Fellowship", "congregation": "Congregation"}
e = lambda s: html.escape(str(s or ""), quote=True)


def pick(cat, i=0):
    xs = CAT.get(cat, [])
    return xs[i % len(xs)] if xs else None


def picks(cat, n, start=0):
    xs = CAT.get(cat, [])
    return [xs[(start + k) % len(xs)] for k in range(min(n, len(xs)))] if xs else []


class Photos:
    def __init__(self, base=""):
        self.base = base

    def src(self, slug, w=1280):
        p = BY[slug]
        if p.get("yt"):
            return f'https://i.ytimg.com/vi/{p["yt"]}/{"maxres" if w > 320 else "mq"}{p["frame"]}.jpg'
        return self.base + p["src"]

    def img(self, slug, w=960, eager=False, sizes="(max-width:860px) 100vw, 50vw", alt=None):
        p = BY[slug]
        a = e(p["alt"] if alt is None else alt)
        pos = p.get("focus", "50% 40%")
        if p.get("yt"):
            yt, f = e(p["yt"]), int(p["frame"])
            ss = f'https://i.ytimg.com/vi/{yt}/mq{f}.jpg 320w, https://i.ytimg.com/vi/{yt}/maxres{f}.jpg 1280w'
            return (f'<img src="https://i.ytimg.com/vi/{yt}/maxres{f}.jpg" srcset="{ss}" sizes="{sizes}" data-fallback="https://i.ytimg.com/vi/{yt}/hq{f}.jpg" '
                    f'alt="{a}" width="1280" height="720" loading="{"eager" if eager else "lazy"}"{" fetchpriority=high" if eager else ""} decoding="async" style="object-position:{pos}">')
        return (f'<img src="{self.base}{e(p["src"])}" alt="{a}" width="{p.get("w", 1600)}" height="{p.get("h", 1067)}" '
                f'loading="{"eager" if eager else "lazy"}" decoding="async" style="object-position:{pos}">')

    def pic(self, slug, cls="", reveal=None, d=0, w=960, extra="", tag=None, **k):
        if not slug:
            return ""
        r = f' data-reveal="{reveal}"' if reveal else ""
        style = f"--d:{d}s;" if d else ""
        m = re.search(r'style="([^"]*)"', extra) or re.search(r"style=(\S+)", extra)
        if m:
            style += m.group(1); extra = extra.replace(m.group(0), "")
        st = f' style="{style}"' if style else ""
        t = f'<span class="tag">{e(tag)}</span>' if tag else ""
        return f'<figure class="pic {cls}"{r}{st}{extra}>{self.img(slug, w, **k)}{t}</figure>'

    def credit(self, slug):
        p = BY[slug]
        return p.get("source", "")

    def slideshow(self, slugs, fx="kenburns", cls="", label="LCC photographs", autoplay=True, thumbs=False, metas=True, interval=6000):
        slugs = [s for s in dict.fromkeys(slugs) if s]
        if not slugs:
            return ""
        def meta(s):
            p = BY[s]
            return f'<figcaption class="meta"><small>{e(CATNAME.get(p["cat"], p["cat"]))}</small><b>{e(p.get("short", p["alt"]))}</b></figcaption>'
        sl = "".join(f'<figure class="slide">{self.img(s, 1280, eager=(i == 0), sizes="(max-width:860px) 100vw, 70vw")}{meta(s) if metas else ""}</figure>' for i, s in enumerate(slugs))
        th = ('<div class="thumbs">' + "".join(f'<button type="button" aria-label="Show photo {i + 1}">{self.img(s, 320, sizes="96px", alt="")}</button>' for i, s in enumerate(slugs)) + '</div>') if thumbs else ""
        return (f'<div class="xshow {cls}" data-fx="{fx}" aria-label="{e(label)}" data-interval="{interval}"{" data-autoplay" if autoplay else ""} tabindex="0">'
                f'<div class="stage">{sl}{"<div class=shade></div>" if metas else ""}</div>{th}</div>')

    def lb_btn(self, slug, group, w=960, cls="", sizes="(max-width:600px) 50vw, 25vw"):
        p = BY[slug]
        cap = p.get("short", p["alt"]) + (f' · {p["source"]}' if p.get("source") else "")
        return (f'<button type="button" class="{cls}" data-lb="{group}" data-full="{self.src(slug)}" data-caption="{e(cap)}" '
                f'data-cat="{e(CATNAME.get(p["cat"], p["cat"]))}" data-cat-key="{e(p["cat"])}" aria-label="View photo: {e(p["alt"])}">{self.img(slug, w, sizes=sizes)}</button>')


def stamp(text="TRANSFORMING NATIONS FOR CHRIST · "):
    return (f'<svg class="stamp" viewBox="0 0 120 120" aria-hidden="true" focusable="false"><defs><path id="sc" d="M60 60m-46 0a46 46 0 1 1 92 0a46 46 0 1 1 -92 0"/></defs>'
            f'<circle cx="60" cy="60" r="58" fill="var(--paper)"/><text><textPath href="#sc">{e(text)}</textPath></text>'
            f'<path d="M60 44v32M50 54h20" stroke="var(--clay)" stroke-width="2.5" stroke-linecap="round"/></svg>')
