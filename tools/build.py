#!/usr/bin/env python3
"""Build the LCC website (v2) from data/content.json.

    python3 tools/build.py

Every fact comes from content.json, where sources are recorded. Items with "verified": false render as
"to be confirmed". Photo slots stay on LCC's own YouTube stills until a slot is marked "approved": true.
"""
import json, html, datetime, pathlib, re

ROOT = pathlib.Path(__file__).resolve().parent.parent
C = json.loads((ROOT / "data/content.json").read_text(encoding="utf-8"))
S, CT, SO, CF = C["site"], C["contact"], C["social"], C["conference"]
BASE = S["url"].rstrip("/") + "/"
TODAY = datetime.date.today()
e = lambda s: html.escape(str(s or ""), quote=True)
VID = {v["id"]: v for v in C["videos"]}
import sys  # noqa: E402
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from photolib import Photos, pick, picks, stamp, BY, CATNAME, LIB  # noqa: E402  (v2.1 photography layer)
PH = Photos("")

NAV = [("about.html", "About"), ("services.html", "Services"), ("ministries.html", "Ministries"),
       ("sermons.html", "Sermons"), ("events.html", "Events"), ("gallery.html", "Gallery"), ("give.html", "Give"), ("contact.html", "Contact")]
SECTION_OF = {"leadership.html": "about.html", "visit.html": "visit.html",
              "conference.html": "events.html", "watch.html": "sermons.html", "news.html": "about.html"}

MARK = ('<svg class="brand-mark" viewBox="0 0 48 48" aria-hidden="true"><circle cx="24" cy="24" r="23" fill="#1E1A16"/>'
        '<path d="M24 9v30M15 18h18" stroke="#F6F1E8" stroke-width="3" stroke-linecap="round"/>'
        '<path d="M9 35c5-4 10-6 15-6s10 2 15 6" stroke="#D49A2F" stroke-width="2.5" fill="none" stroke-linecap="round"/></svg>')
CONTOUR = ('<svg viewBox="0 0 400 500" preserveAspectRatio="none" aria-hidden="true"><g fill="none" stroke="#FFF5E8" stroke-width="1.2">'
           + "".join(f'<path d="M-20 {300+i*18} C 80 {250+i*14}, 160 {330+i*10}, 240 {280+i*16} S 380 {300+i*12}, 430 {270+i*18}"/>' for i in range(10))
           + '<circle cx="300" cy="120" r="46"/><circle cx="300" cy="120" r="30"/></g></svg>')
# Original linework divider inspired by kiondo/kitenge weaving geometry (not a copy of any pattern).
KENTE = ('<svg class="kente" viewBox="0 0 240 18" preserveAspectRatio="none" aria-hidden="true" focusable="false"><g fill="none" stroke="currentColor" stroke-width="1.5">'
         '<path d="M0 9 L10 2 L20 9 L30 16 L40 9 L50 2 L60 9 L70 16 L80 9 L90 2 L100 9 L110 16 L120 9 L130 2 L140 9 L150 16 L160 9 L170 2 L180 9 L190 16 L200 9 L210 2 L220 9 L230 16 L240 9"/>'
         '<path d="M0 9 H240" stroke-dasharray="2 8"/></g></svg>')


def kente():
    return f'<div class="wrap" aria-hidden="true">{KENTE}</div>'


def yt_img(vid, alt="", lazy=True, cls="", frame=None):
    """frame=None: the video's own thumbnail (for video cards). frame=1..3: a real frame captured inside the video (for photography)."""
    vid = e(vid)
    hi, lo = (f"maxres{frame}", f"hq{frame}") if frame else ("maxresdefault", "hqdefault")
    return (f'<img src="https://i.ytimg.com/vi/{vid}/{hi}.jpg" data-fallback="https://i.ytimg.com/vi/{vid}/{lo}.jpg" '
            f'alt="{e(alt)}" width="1280" height="720" loading="{"lazy" if lazy else "eager"}" decoding="async"{f" class={cls}" if cls else ""}>')


def ph(caption="Awaiting LCC-approved photo", cls=""):
    return f'<div class="ph {cls}" role="img" aria-label="Placeholder image: {e(caption)}">{CONTOUR}<span class="cap" aria-hidden="true">{e(caption)}</span></div>'


def vmeta(v):
    lab = {"sermon": "Message", "service": "Sunday service", "praise": "Praise Express", "worship": "Worship",
           "conference": "Conference", "story": "Story", "special": "Special service"}.get(v.get("category"), "")
    return " · ".join(x for x in [v.get("speaker"), lab, v.get("published", "").replace(" ago (as of 25 Nov 2026)", " ago")] if x)


def video_card(v, lazy=True):
    vid = e(v["id"])
    return (f'<figure class="video" data-cat="{e(v.get("category"))}" data-speaker="{e(v.get("speaker",""))}" data-title="{e((v["title"]+" "+v.get("speaker","")).lower())}">'
            f'<div class="frame">{yt_img(v["id"], "", lazy)}'
            f'<button class="play" type="button" data-yt="{vid}" aria-label="Play video: {e(v["title"])}"></button></div>'
            f'<figcaption><b>{e(v["title"])}</b><small>{e(vmeta(v))}</small></figcaption></figure>')


def vids(ids):
    return [VID[i] for i in ids if i in VID]


def share_btn(label="Share"):
    return f'<button class="share" type="button" data-share>{e(label)} <span aria-hidden="true">↗</span></button>'


def photo_slot(slot):
    """Approved church photo if available; otherwise LCC's own YouTube still linked to its video."""
    p = next((x for x in C.get("photos", []) if x["slot"] == slot), None)
    if p and p.get("approved") and p.get("slug") in BY:
        return PH.img(p["slug"], 1280, alt=p["desc"], sizes="(max-width:860px) 100vw, 60vw"), ""
    if p and p.get("approved") and p.get("src"):
        return f'<img src="{e(p["src"])}" alt="{e(p["desc"])}" loading="lazy">', ""
    v = VID.get((p or {}).get("fallback_video", ""), None)
    if not v:
        return "", ""
    return yt_img(v["id"], p["desc"] + " (frame from LCC's YouTube stream)", frame=p.get("frame", 2)), f'https://www.youtube.com/watch?v={v["id"]}'


def rail(title, items, rid, eyebrow="", more=None):
    nav = (f'<div class="row-nav"><button type="button" data-rail="{rid}" data-dir="-1" aria-label="Scroll {e(title)} left">←</button>'
           f'<button type="button" data-rail="{rid}" data-dir="1" aria-label="Scroll {e(title)} right">→</button></div>')
    mo = f' <a href="{e(more[0])}">{e(more[1])}</a>' if more else ""
    return (f'<section class="row" aria-labelledby="{rid}-h"><div class="row-head"><div>{f"<span class=eyebrow>{e(eyebrow)}</span>" if eyebrow else ""}'
            f'<h2 id="{rid}-h">{e(title)}</h2>{mo}</div>{nav}</div><div class="rail" id="{rid}" tabindex="0" aria-label="{e(title)} videos">{"".join(video_card(v) for v in items)}</div></section>')


def fmt_range(a, b):
    da, db = datetime.date.fromisoformat(a), datetime.date.fromisoformat(b)
    return f"{da.day} {da:%b} – {db.day} {db:%b %Y}"


def notice_html():
    n = C.get("notice", {})
    if not n.get("show"):
        return ""
    return f'<aside class="noticebar" aria-label="Announcement" data-cms="notice"><a href="{e(n["link"])}">{e(n["text"])} →</a></aside>'


def giving_html():
    g = C["giving"]
    if g.get("verified") and g.get("mpesa_paybill"):
        return (f'<div class="give-card" data-cms="giving"><span class="eyebrow">M-Pesa</span><h3>Paybill {e(g["mpesa_paybill"])}</h3>'
                f'<p>Account: <b>{e(g["mpesa_account"])}</b></p><p class="muted">Confirmed by the LCC church office.</p></div>')
    return (f'<div class="notice" data-cms="giving"><b>Giving details are being confirmed</b>{e(g["note"])}'
            f' <a href="tel:{e(CT["phone_intl"])}">Call {e(CT["phone"])}</a></div>')


def maps_url():
    return "https://www.google.com/maps/search/?api=1&amp;query=" + e(CT["maps_query"]).replace(" ", "+")


def jsonld_org():
    return {"@context": "https://schema.org", "@type": ["Church", "PlaceOfWorship"], "@id": BASE + "#church",
            "name": S["org"], "alternateName": [S["name"], S["short"]], "url": BASE, "telephone": CT["phone_intl"],
            "email": CT["email"], "slogan": S["vision"], "description": S["mission"],
            "address": {"@type": "PostalAddress", "streetAddress": CT["street"], "addressLocality": CT["city"], "addressCountry": CT["country"], "postOfficeBoxNumber": "2758-20100"},
            "sameAs": [SO["youtube"], SO["facebook"], SO["instagram"]],
            "employee": [{"@type": "Person", "name": "Rev. Elijah Mwangi", "jobTitle": "Lead Pastor"}]}


def page(slug, title, desc, body, current=None, extra_ld=None):
    canon = BASE if slug == "index.html" else BASE + slug
    full_title = title if slug == "index.html" else f"{title} | {S['name']} (LCC) Nakuru"
    cur = current or SECTION_OF.get(slug)
    nav = "".join(f'<a href="{h}"{" aria-current=page" if h == cur else ""}>{t}</a>' for h, t in NAV)
    lds = [jsonld_org()] + (extra_ld or [])
    ld = "\n".join(f'<script type="application/ld+json">{json.dumps(x, ensure_ascii=False)}</script>' for x in lds)
    return f"""<!doctype html>
<html lang="en-KE">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(full_title)}</title>
<meta name="description" content="{e(desc)}">
<link rel="canonical" href="{canon}">
<meta name="theme-color" content="#F6F1E8">
<meta property="og:type" content="website">
<meta property="og:site_name" content="{e(S['org'])}">
<meta property="og:title" content="{e(full_title)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:url" content="{canon}">
<meta property="og:image" content="{BASE}assets/img/og-image.png">
<meta property="og:locale" content="{S['locale']}">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="assets/img/favicon.svg" type="image/svg+xml">
<link rel="preconnect" href="https://i.ytimg.com">
<link rel="preload" href="assets/fonts/fraunces-latin-wght-normal.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="assets/fonts/inter-tight-latin-wght-normal.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="assets/css/site.css">
<link rel="stylesheet" href="assets/css/enhance.css">
<script>document.documentElement.classList.add('js')</script>
{ld}
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
{notice_html()}
<header class="site-header">
 <div class="wrap">
  <a class="brand" href="./" aria-label="{e(S['name'])} — home">{MARK}<span><b>{e(S['name'])}</b><small>Deliverance Church · Nakuru</small></span></a>
  <button class="menu-toggle" type="button" aria-expanded="false" aria-controls="site-nav">Menu</button>
  <nav class="nav" id="site-nav" aria-label="Main">
   <a class="watch" href="watch.html"{" aria-current=page" if slug == "watch.html" else ""}>Watch online</a>
   {nav}
   <a class="btn btn-solid" href="visit.html"{" aria-current=page" if slug == "visit.html" else ""}>Plan your visit</a>
  </nav>
 </div>
</header>
<main id="main" tabindex="-1">
{body}
</main>
<footer class="site-footer">
 <div class="wrap">
  <div class="foot-top">
   <div><h2>{e(S['vision'])}.</h2><p style="color:#C9BDAF;max-width:36ch">{e(S['org'])}</p><p>{share_btn("Share this page")}</p></div>
   <div><h3>Visit</h3><ul><li>{e(CT['street'])}</li><li>{e(CT['city'])}, Kenya</li><li><a href="visit.html">Plan your visit</a></li><li><a href="services.html">Service times</a></li><li><a href="{maps_url()}" rel="noopener" target="_blank">Open in Google Maps</a></li></ul></div>
   <div><h3>Explore</h3><ul><li><a href="about.html">About LCC</a></li><li><a href="leadership.html">Leadership</a></li><li><a href="gallery.html">LCC Moments</a></li><li><a href="news.html">Announcements</a></li><li><a href="conference.html">Cutting Edge Conference</a></li></ul></div>
   <div><h3>Connect</h3><ul><li><a href="tel:{e(CT['phone_intl'])}">{e(CT['phone'])}</a></li><li><a href="mailto:{e(CT['email'])}">{e(CT['email'])}</a></li><li><a href="contact.html#prayer">Prayer request</a></li><li><a href="{e(SO['youtube'])}" rel="noopener" target="_blank">YouTube</a> · <a href="{e(SO['facebook'])}" rel="noopener" target="_blank">Facebook</a> · <a href="{e(SO['instagram'])}" rel="noopener" target="_blank">Instagram</a></li></ul></div>
  </div>
  <div class="foot-bottom"><span>© {TODAY.year} {e(S['org'])}</span><span><a href="privacy.html">Privacy</a> · <a href="give.html">Give</a> · <a href="contact.html">Contact</a></span></div>
 </div>
</footer>
<dialog class="lightbox" id="lightbox" aria-label="Media viewer"><div class="lb-frame" id="lb-frame"></div><div class="lb-bar"><span id="lb-title"></span><span><button type="button" data-lb="prev" aria-label="Previous">←</button> <button type="button" data-lb="next" aria-label="Next">→</button> <button type="button" data-lb="close">Close</button></span></div></dialog>
<script src="assets/js/site.js" defer></script>
<script src="assets/js/motion.js" defer></script>
</body>
</html>
"""


# ================================================================ shared blocks
SV = C["services"]
latest_services = [v for v in C["videos"] if v["category"] == "service"]
sermons_older = [v for v in C["videos"] if v["category"] == "sermon"]
praise = [v for v in C["videos"] if v["category"] == "praise"]
conf26 = vids(CF["archive_2026"])
special = [v for v in C["videos"] if v["category"] == "special"]
worship = [v for v in C["videos"] if v["category"] == "worship"]
conf_old = [v for v in C["videos"] if v["category"] == "conference" and v["id"] not in CF["archive_2026"]]
up_ev = [ev for ev in C["events"] if datetime.date.fromisoformat(ev["end"]) >= TODAY]
PAST = C["past_events"]


def ev_slug(ev):
    return "event-" + re.sub(r"[^a-z0-9]+", "-", ev["title"].lower()).strip("-") + ".html"


def tbc_badge(item):
    return '<span class="badge">Confirmed</span>' if item.get("status") == "confirmed" else '<span class="badge tbc">Reported</span>'


def this_sunday():
    s1, s2 = SV["items"][0], SV["items"][1]
    return (f'<div class="this-sunday">'
            f'<div><small>In person</small><b>First &amp; Second Service</b><p>Every Sunday at LCC, General Kariba Street, Freehold: First Service 7:30–9:00 am, Second Service 10:00 am–12 noon.</p><a class="btn btn-sun" href="visit.html">Plan your visit</a></div>'
            f'<div><small>Online</small><b>Streamed live on YouTube</b><p>Both Sunday services are streamed every week on the LCC channel.</p><a class="btn btn-ghost-light" href="watch.html">Watch online</a></div>'
            f'<div><small>Catch up</small><b>{e(latest_services[0]["title"])}</b><p>{e(latest_services[0]["published"])}</p><a class="btn btn-ghost-light" href="sermons.html">Latest services</a></div></div>')


def ecard(ev, past=True, href=None):
    v = VID.get(ev.get("video"))
    img = yt_img(v["id"], "", frame=2) if v else ""
    href = href or ev_slug(ev)
    return (f'<article class="ecard"><div class="frame">{img}<span class="vdate">{e(ev["when"])}</span>{"<span class=past>Past event</span>" if past else ""}</div>'
            f'<div class="body"><span class="cat">{e(ev["category"])}</span><h3><a href="{e(href)}">{e(ev["title"])}</a></h3><p>{e(ev["summary"])}</p>'
            f'<a href="{e(href)}">View event →</a></div></article>')


def upnext():
    """Upcoming one-day services/events (from official church posters): typographic date, no image."""
    xs = sorted([ev for ev in up_ev if not ev.get("featured")], key=lambda x: x["start"])
    if not xs:
        return ""
    def row(ev):
        d = datetime.date.fromisoformat(ev["start"])
        return (f'<article class="upnext"><div class="un-date" aria-hidden="true"><b>{d.day}</b><small>{d:%b %Y}</small></div>'
                f'<div><span class="cat">{e(ev["category"])} · {d:%A} {d.day} {d:%B} · {e(ev.get("time", ""))}</span><h3>{e(ev["title"])}</h3><p>{e(ev["summary"])}</p></div></article>')
    return '<div class="upnexts" data-stagger>' + "".join(row(x) for x in xs) + '</div>'


def feature_conf(compact=False):
    ev = up_ev[0] if up_ev else None
    if not ev:
        return ""
    d = datetime.date.fromisoformat(ev["start"])
    return (f'<article class="feature-event"><div class="fe-media"><div class="bignum">{d.day}–4<small>{d:%B} – April {d.year}</small></div></div>'
            f'<div class="fe-body"><span class="eyebrow">Next major event · {e(ev["category"])}</span><h2>{e(ev["title"])}</h2>'
            f'<p class="lead" style="color:#C9BDAF">{e(CF["theme"])} · Anchor scripture {e(CF["anchor"])}</p>'
            f'<div class="countdown" data-countdown="{e(CF["start_iso"])}" aria-label="Time until the conference starts"></div>'
            f'<p style="display:flex;gap:12px;flex-wrap:wrap"><a class="btn btn-sun" href="{e(CF["register"])}" rel="noopener" target="_blank">Register on the official site</a><a class="btn btn-ghost-light" href="conference.html">Explore the conference</a></p></div></article>')


def mission_band():
    return (f'<section class="sec band-night" id="mission" aria-labelledby="mv-h"><div class="wrap">'
            f'<span class="eyebrow">Our vision</span><h2 id="mv-h" class="statement" data-split="lines" data-lines="Transforming|<em>Nations</em> for Christ.">Transforming <em>Nations</em> for Christ.</h2>'
            f'<div class="split mt4"><div><span class="eyebrow">Our mission</span><p class="ink" style="font:350 clamp(24px,2.8vw,36px)/1.3 var(--serif);color:var(--bone);margin:0">“{e(S["mission"])}”</p></div>'
            f'<div class="speakers" style="align-self:end" data-stagger><div class="speaker"><b>Reconcile</b><small>people to God</small></div><div class="speaker"><b>Equip</b><small>for ministry to God and people</small></div><div class="speaker"><b>Transform</b><small>with a transformative agenda</small></div><div class="speaker"><b>Nations</b><small>Nakuru and the world</small></div></div></div>'
            f'<p class="credit mt2">Source: LCC YouTube channel and cuttingedgeconference.co.ke/about</p></div></section>')


def values_block():
    return ('<div class="values" data-stagger>' + "".join(f'<div class="value"><span class="n">0{i+1}</span><b>{e(v)}</b></div>' for i, v in enumerate(S["values"])) + '</div>'
            f'<p class="credit">Core values as published at cuttingedgeconference.co.ke/about</p>')


def discover_grid():
    out = []
    for m in C["ministries"]:
        href = m.get("link") or f'ministries.html#{m["slug"]}'
        img = yt_img(m["video"], "", frame=2) if m.get("video") else ""
        out.append(f'<a href="{e(href)}">{img}<small>{e(m["kind"])}</small><b>{e(m["name"])}</b><span>Discover →</span></a>')
    return '<div class="discover" data-stagger>' + "".join(out) + '</div>'


def collage(items, group=None):
    out = []
    for v, cat in items:
        out.append(f'<figure data-cat="{e(cat)}"><button type="button" data-lightbox="{e(v["id"])}" data-group="{e(group or "all")}" data-title="{e(v["title"])}" aria-label="Open: {e(v["title"])}">'
                   f'{yt_img(v["id"], "", frame=2)}<figcaption>{e(v["title"])}<small>{e(cat)} · {e(v.get("published",""))}</small></figcaption></button></figure>')
    return '<div class="collage">' + "".join(out) + '</div>'


MOMENTS = ([(v, "Sunday services") for v in latest_services[:4]] + [(v, "Praise & worship") for v in praise[:3]] + [(v, "Conferences") for v in conf26[:3]]
           + [(v, "Special nights") for v in special[:4]] + [(v, "Praise & worship") for v in worship[:2]])


# ================================================================ pages
P = {}

# ---------------- HOME
hero_v = latest_services[1] if len(latest_services) > 1 else latest_services[0]
HERO = "praise-express-worshipper" if "praise-express-worshipper" in BY else (LIB[0]["slug"] if LIB else None)
_h = BY.get(HERO, {})
_mv = latest_services[2]
P["index.html"] = page("index.html", f"{S['name']} (LCC) Nakuru — Deliverance Church International",
    "Deliverance Church International – Life Celebration Centre (LCC), General Kariba Street, Freehold, Nakuru. Transforming Nations for Christ. Sunday services, sermons, ministries and the Cutting Edge Conference.",
f"""
<section class="hx" aria-labelledby="hx-h"><div class="wrap hx-grid">
 <div class="hx-text">
  <span class="eyebrow" data-reveal="fade">Deliverance Church International · Nakuru</span>
  <h1 id="hx-h" data-split="words">A place to <em>celebrate</em> life in Christ.</h1>
  <p class="lead" data-reveal="rise" style="--d:.45s">Every Sunday on General Kariba Street, Freehold — a church family reconciling people to God and equipping them for ministry.</p>
  <div class="actions" data-reveal="rise" style="--d:.6s"><a class="btn btn-solid" href="visit.html">Plan your visit <span class="arrow" aria-hidden="true">→</span></a><a class="btn" href="watch.html">Watch online</a></div>
  <p class="hx-links" data-reveal="fade" style="--d:.8s"><a href="contact.html#prayer">Ask for prayer</a><a href="ministries.html">Find a ministry</a><a href="sermons.html">Latest messages</a></p>
 </div>
 <figure class="hx-photo" data-reveal="arch" style="--fb:url('{PH.src(HERO, 640).replace("assets/", "../", 1)}')">
  {PH.img(HERO, 1280, eager=True, sizes="(max-width:860px) 100vw, 44vw") if HERO else ''}
  <figcaption>{e(_h.get('short',''))}</figcaption>
 </figure>
</div></section>

<div class="wrap"><div class="facts" data-stagger>
 <div><small>Sundays</small><b>7:30 am &amp; 10:00 am</b><a href="services.html">Services →</a></div>
 <div><small>Where</small><b>Kariba Street, Freehold</b><a href="visit.html#find-us">Directions →</a></div>
 <div><small>Online</small><b>Streamed every Sunday</b><a href="watch.html">Watch online →</a></div>
 <div><small>30 Mar – 4 Apr 2027</small><b>Cutting Edge</b><a href="conference.html">Conference →</a></div>
</div></div>

<section class="sec who has-bigword" aria-labelledby="who-h"><span class="bigword" aria-hidden="true">LCC</span><div class="wrap who-grid">
 <div>
  <span class="eyebrow">Who we are</span>
  <h2 id="who-h" class="statement" data-split="lines" data-lines="Transforming|<em>nations</em> for Christ.">Transforming <em>nations</em> for Christ.</h2>
 </div>
 <div>
  <p class="ink who-mission">{e(S['mission'])}</p>
  <p class="values-line">{' <span aria-hidden="true">·</span> '.join(e(v) for v in S['values'])}</p>
  <p class="who-lead">Led by <a href="leadership.html">{e(C['leadership'][0]['name'])}</a>, Lead Pastor — <a href="about.html">read our story →</a></p>
 </div>
</div></section>

<section class="sec band-night" aria-labelledby="sun-h"><div class="wrap">
 <div class="sec-head"><div><span class="eyebrow">This Sunday at LCC</span><h2 id="sun-h" data-split="words">Join us in person or <em style="color:var(--sun)">online</em></h2></div></div>
 {this_sunday()}
 <div class="feature-video mt4"><div>{video_card(_mv)}</div><div><span class="eyebrow">Message of the week</span><h3 style="font-size:clamp(28px,3vw,40px);color:var(--bone)">{e(_mv["title"].split(" · ")[0])}</h3><p class="lead">Streamed on {e(_mv["published"])}. Catch up here or on YouTube.</p><p><a class="btn btn-ghost-light" href="sermons.html">Sermon library</a></p></div></div>
</div></section>

<section class="sec" aria-labelledby="min-h"><div class="wrap duo">
 <div style="max-width:460px;width:100%;margin:auto">{PH.pic("worship-team-cross", "f-arch", "arch", sizes="(max-width:860px) 90vw, 34vw")}</div>
 <div>
  <span class="eyebrow">Ministries &amp; community</span>
  <h2 id="min-h" data-split="words">Find your place to <em>belong.</em></h2>
  <ul class="mini-list" data-stagger>{''.join(f'<li><a href="{e(m.get("link") or "ministries.html#" + m["slug"])}"><b>{e(m["name"])}</b><span>{e(m["kind"])}</span></a></li>' for m in C["ministries"])}</ul>
 </div>
</div></section>

<section class="sec" aria-labelledby="ev-h" style="padding-top:0"><div class="wrap">
 <h2 class="sr-only" id="ev-h">Coming up at LCC</h2>
 {upnext()}
 {feature_conf()}
 <p class="mt2" style="text-align:right"><a href="events.html">All events &amp; past gatherings →</a></p>
</div></section>

<section class="sec" style="padding-top:0"><div class="wrap">
 <div class="invite" style="--fb:url('{PH.src("conquerors-entrance", 640).replace("assets/", "../", 1)}')">{PH.img("conquerors-entrance", 1920, sizes="100vw", alt="")}
  <span class="eyebrow">Come and experience LCC</span><h2>There's a seat for you this Sunday.</h2>
  <p class="lead" style="color:#E6DCCF">General Kariba Street, Freehold, Nakuru · First Service 7:30 am · Second Service 10:00 am</p>
  <p style="display:flex;gap:12px;flex-wrap:wrap"><a class="btn btn-sun" href="visit.html">Plan your visit</a><a class="btn btn-ghost-light" href="{maps_url()}" rel="noopener" target="_blank">Get directions</a></p>
 </div>
</div></section>
""")

# ---------------- ABOUT (13 sections)
slides = []
for i, sl in enumerate([p for p in C["photos"] if p["slot"].startswith("about-hero")]):
    img, link = photo_slot(sl["slot"])
    v = VID.get(sl["fallback_video"])
    cap = f'<a href="{e(link)}" rel="noopener" target="_blank">{e(sl["desc"])} · watch ↗</a>' if link else e(sl["desc"])
    slides.append(f'<figure class="slide{" on" if i == 0 else ""}" data-cap="{e(cap)}" aria-hidden="{"false" if i == 0 else "true"}">{img}</figure>')
caps0 = slides and re.search(r'data-cap="([^"]*)"', slides[0]).group(1)

leader = C["leadership"][0]
P["about.html"] = page("about.html", "About LCC — More than a church", "Discover Life Celebration Centre, Nakuru: our story, journey since 2018, mission, vision, core values, church family, leadership, ministries, worship and the Cutting Edge Conference.",
f"""
<section class="slides" aria-roledescription="carousel" aria-label="Life at LCC" data-slides>
 {''.join(slides)}
 <p class="slide-cap" data-slide-cap>{html.unescape(caps0) if caps0 else ''}</p>
 <div class="wrap inner">
  <span class="eyebrow">Discover LCC</span>
  <h1 data-split="words">More than a church. A place to <em style="color:var(--sun)">belong.</em></h1>
  <p class="lead">A Deliverance Church International family in Freehold, Nakuru — celebrating life in Christ and transforming nations for Him.</p>
  <div class="actions" style="display:flex;gap:12px;flex-wrap:wrap;margin-top:24px"><a class="btn btn-sun" href="#story">Explore our story</a><a class="btn btn-ghost-light" href="visit.html">Plan your visit</a></div>
  <div class="slide-ui"><button type="button" data-slide-prev aria-label="Previous slide">←</button><div class="dots" role="group" aria-label="Choose slide">{''.join(f'<button type="button" data-slide-to="{i}" aria-label="Slide {i+1}"{" aria-current=true" if i==0 else ""}></button>' for i in range(len(slides)))}</div><button type="button" data-slide-next aria-label="Next slide">→</button><button type="button" data-slide-pause aria-pressed="false">Pause</button></div>
 </div>
</section>
<nav class="subnav" aria-label="On this page"><div class="wrap">
 <a href="#story">Our story</a><a href="#journey">Journey</a><a href="#mission">Mission &amp; vision</a><a href="#values">Values</a><a href="#family">Church family</a><a href="#leadership">Leadership</a><a href="#worship">Worship</a><a href="#conference">Cutting Edge</a><a href="#visit">Visit</a>
</div></nav>

<section class="sec" id="story" aria-labelledby="story-h"><div class="wrap split">
 <div class="layered"><div class="a" data-reveal="left">{photo_slot("story-a")[0]}</div><div class="b" data-reveal="up" style="--d:.35s">{photo_slot("story-b")[0]}</div></div>
 <div>
  <span class="num">01 — The story of LCC</span>
  <h2 id="story-h" class="mt2">A Nakuru church with a <em>global</em> heart.</h2>
  <p class="lead" style="max-width:none">{e(C['about']['intro'])}</p>
  <p>LCC exists to reconcile people to God and equip them for ministry — to God and to people — with a transformative agenda. Its vision reaches far beyond Nakuru: <b>Transforming Nations for Christ</b>.</p>
  <details class="more"><summary>Read our story</summary>
   <p>LCC is part of Deliverance Church International, a Kenyan church family with congregations across the country. Every year since 2018 the LCC family has hosted the Cutting Edge Conference, whose goal is to “equip the saints for the work of the ministry” (Ephesians 4:12) — reaching not only the local congregation but the wider body of Christ in Nakuru and beyond through television and social media.</p>
   <p>On Sundays the church gathers for two services that are also streamed online. Throughout the year LCC comes together for Praise Express services, nights of prayer (Kesha), leaders' summits and worship experiences for students.</p>
   <p class="credit">Founding date and early history are being prepared with the church office and will be added once confirmed.</p>
  </details>
  <p class="mt2"><b>What to expect when you visit:</b> heartfelt worship, prayer, a message from the Bible and time to connect with the church family.</p>
 </div>
</div></section>
{kente()}
<section class="sec" id="journey" aria-labelledby="journey-h"><div class="wrap">
 <span class="num">02 — Our journey through time</span>
 <h2 id="journey-h" class="mt2">Milestones we can show you</h2>
 <p class="muted" style="max-width:60ch">Only documented milestones appear here, each with its source. Earlier history will be added with the church office.</p>
 <ol class="timeline mt4">{''.join(f'<li><span class="yr">{e(t["year"])}</span><h3>{e(t["title"])}</h3><p>{e(t["text"])}</p><span class="src">Source: {e(t["source"])}</span></li>' for t in C['about']['timeline'])}</ol>
</div></section>

{mission_band()}

<section class="sec" id="values" aria-labelledby="values-h"><div class="wrap">
 <span class="num">04 — Our core values</span>
 <h2 id="values-h" class="mt2">Six values that shape our life together</h2>
 <div class="mt4">{values_block()}</div>
</div></section>

<section class="sec bg-sand" id="family" aria-labelledby="family-h"><div class="wrap">
 <div class="sec-head"><div><span class="num">05 — Our church family</span><h2 id="family-h" class="mt2">Worship, fellowship and <em>connection</em></h2></div><a class="btn" href="gallery.html">Explore LCC Moments</a></div>
 <p class="lead" style="max-width:60ch">{e(C['about']['family'])}</p>
 <div class="mt4">{collage([MOMENTS[i] for i in (0, 4, 7, 10, 12) if i < len(MOMENTS)], "family")}</div>
 <p class="credit">Moments captured from LCC's own YouTube streams — select any to watch. Church photography (Facebook albums) awaits the church office's approval.</p>
</div></section>

<section class="sec" id="leadership" aria-labelledby="lead-h"><div class="wrap portrait">
 {PH.pic(C["leadership"][0].get("portrait"), "f-circle ringed lead-portrait", "circle", sizes="(max-width:860px) 72vw, 380px") if C["leadership"][0].get("portrait") in BY else '<div class="medal ringed" role="img" aria-label="Lead Pastor"><span aria-hidden="true">EM</span></div>'}
 <div>
  <span class="num">06 — Leadership</span>
  <h2 id="lead-h" class="mt2">{e(leader['name'])}</h2>
  <span class="eyebrow">{e(leader['role'])}</span>
  <p class="lead" style="max-width:none">{e(leader['bio'])}</p>
  <p><a class="btn" href="leadership.html">Full profile &amp; leadership</a></p>
  <p class="credit">Biography as published at cuttingedgeconference.co.ke/about</p>
 </div>
</div></section>

<section class="sec band-night" id="worship" aria-labelledby="w-h"><div class="wrap">
 <span class="eyebrow">07 — Our worship experience</span>
 <h2 id="w-h">Worship at LCC</h2>
 <div class="feature-video mt2"><div>{video_card(praise[0], lazy=True)}</div><div><p class="lead">Praise Express services fill the sanctuary with a full service of praise and worship, alongside recordings by LCC's worship ministers, One Accord Ministers.</p><ul class="meta-list"><li><b>Praise Express</b> — held every few months</li><li><b>One Accord Ministers</b> — worship recordings</li><li><b>Live at LCC</b> — guest worship moments</li></ul></div></div>
</div></section>

<section class="cu" id="conference" aria-labelledby="c-h"><div class="wrap cu-hero">
 <span class="eyebrow">08 — Cutting Edge Conference</span>
 <div class="yr" aria-hidden="true">2027</div>
 <h2 id="c-h" class="statement" style="color:var(--bone);font-size:clamp(36px,5vw,72px)">{e(CF['theme'])}</h2>
 <div class="cu-grid mt4"><div><small>Dates</small><b>{e(CF['dates'])}</b></div><div><small>Venue</small><b>LCC, Freehold, Nakuru</b></div><div><small>Anchor scripture</small><b>{e(CF['anchor'])}</b></div><div><small>Since</small><b>2018 · every April</b></div></div>
 <p class="mt2" style="display:flex;gap:12px;flex-wrap:wrap"><a class="btn btn-sun" href="conference.html">View the conference</a><a class="btn btn-ghost-light" href="{e(CF['register'])}" rel="noopener" target="_blank">Register (official site)</a></p>
</div></section>

<section class="sec" id="visit"><div class="wrap">
 <div class="invite">{yt_img("GOjZxrPfljE", "", frame=2)}
  <span class="eyebrow">09 — Come and experience LCC</span><h2>Celebrate life with us this Sunday.</h2>
  <p class="lead" style="color:#E6DCCF">First Service 7:30 am · Second Service 10:00 am · General Kariba Street, Freehold, Nakuru</p>
  <p style="display:flex;gap:12px;flex-wrap:wrap"><a class="btn btn-sun" href="visit.html">Plan your visit</a><a class="btn btn-ghost-light" href="watch.html">Watch online</a><a class="btn btn-ghost-light" href="contact.html">Contact LCC</a><a class="btn btn-ghost-light" href="{maps_url()}" rel="noopener" target="_blank">Map</a></p>
 </div>
</div></section>
""")

# ---------------- LEADERSHIP
P["leadership.html"] = page("leadership.html", "Leadership", "Leadership at Life Celebration Centre (LCC) Nakuru: Lead Pastor Rev. Elijah Mwangi — official biography.",
f"""
<div class="wrap"><header class="page-hero"><span class="eyebrow">Leadership</span><h1 data-split="words">Shepherds who <em>serve.</em></h1></header></div>
<section class="sec"><div class="wrap portrait">
 {PH.pic(C["leadership"][0].get("portrait"), "f-circle ringed lead-portrait", "circle", sizes="(max-width:860px) 72vw, 380px") if C["leadership"][0].get("portrait") in BY else '<div class="medal ringed" role="img" aria-label="Lead Pastor"><span aria-hidden="true">EM</span></div>'}
 <div><span class="eyebrow">{e(leader['role'])}</span><h2>{e(leader['name'])}</h2>
 <p class="lead" style="max-width:none">{e(leader['bio'])}</p><p>{e(leader['bio_more'])}</p>
 <p class="credit">Source: official biography at cuttingedgeconference.co.ke/about</p>
 <p class="mt2" style="display:flex;gap:12px;flex-wrap:wrap"><a class="btn" href="sermons.html">Watch his messages</a><a class="btn" href="conference.html">Cutting Edge Conference</a></p></div>
</div></section>
<section class="sec bg-sand"><div class="wrap split">
 <div><span class="eyebrow">From our pulpit</span><h2>Voices you'll hear at LCC</h2><p class="muted">Names as they appear in LCC's own service and conference recordings. Formal pastoral-team roles will be added once confirmed by the church office.</p></div>
 <ul class="pulpit" data-stagger>{''.join(f'<li><b>{e(p["name"])}</b><span>{e(p["note"])}</span></li>' for p in C['pulpit'])}</ul>
</div></section>
""")

# ---------------- SERVICES
P["services.html"] = page("services.html", "Services & weekly programme", "Sunday First and Second Services, Praise Express, Kesha nights and connection time at LCC Nakuru — First Service 7:30 am, Second Service 10:00 am, streamed online every Sunday.",
f"""
<div class="wrap"><header class="page-hero"><span class="eyebrow">Services</span><h1 data-split="words">When we <em>gather.</em></h1><p class="lead">LCC meets every Sunday for two services, streamed live on YouTube, plus special services and nights of prayer through the year.</p></header></div>
<section class="sec band-night"><div class="wrap"><span class="eyebrow">This Sunday at LCC</span><h2>In person, online, or catch up</h2>{this_sunday()}</div></section>
<section class="sec"><div class="wrap">
 <div class="sec-head"><div><span class="eyebrow">Timetable</span><h2>Services &amp; programmes</h2></div></div>
 <div class="timetable" data-cms="services">{''.join(f'<div class="tt"><div><span class="day">{e(i["day"])}</span><div class="time">{e(i["time"])}</div></div><div><h3>{e(i["name"])} {tbc_badge(i)}</h3><p>{e(i["detail"])}</p></div><div>{f"<a class=btn href={e(i[chr(119)+chr(97)+chr(116)+chr(99)+chr(104)])} rel=noopener target=_blank>Watch</a>" if i.get("watch") else ""}</div></div>' for i in SV['items'])}</div>
 <p class="credit">{e(SV['times_note'])}</p>
 <p class="credit">“Confirmed” means the programme is shown in LCC's own recent YouTube streams or Facebook posts. “Reported” means it appears in social media highlights but needs confirmation.</p>
</div></section>
<section class="sec bg-sand"><div class="wrap split"><div><span class="eyebrow">Online church</span><h2>Can't make it in person?</h2><p>Both Sunday services stream live on the LCC YouTube channel every week, and past services stay available to watch.</p></div><div style="align-self:center"><a class="btn btn-solid" href="watch.html">Watch online</a> <a class="btn" href="visit.html">Plan your first visit</a></div></div></section>
""")

# ---------------- VISIT
faqs = [("What time are services?", "Every Sunday: First Service 7:30–9:00 am and Second Service 10:00 am–12 noon (as published on the church's Sunday Services posters). Special services may differ — check Facebook or call " + CT["phone"] + "."),
        ("Where is the church?", "General Kariba Street (Kariba Road), Freehold, Nakuru. Use the map on this page or search “Deliverance Church Nakuru” in Google Maps."),
        ("Where do I park?", "Parking details will be added once confirmed by the church office. Ushers are happy to help when you arrive."),
        ("What should I wear?", "Come as you are."),
        ("Is there something for my children?", "Please ask the welcome team on arrival about children's ministry during the service; details will be published once confirmed."),
        ("Can I watch online first?", "Yes — both Sunday services are streamed live on YouTube every week.")]
P["visit.html"] = page("visit.html", "Plan your visit", "Plan your first visit to Life Celebration Centre on General Kariba Street, Freehold, Nakuru: services, map, directions, what to expect and a visitor enquiry form.",
f"""
<div class="wrap"><header class="page-hero"><span class="eyebrow">New here?</span><h1 data-split="words">We'd love to <em>welcome</em> you.</h1><p class="lead">Everything you need for your first Sunday at LCC.</p></header></div>
<section class="sec"><div class="wrap">
 <span class="eyebrow">Your first visit, step by step</span><h2>The first-time visitor journey</h2>
 <ol class="journey-x mt2" data-stagger>
  <li><span class="num">01</span><h3>Pick a service</h3><p>Choose the First or Second Service on Sunday. Call {e(CT['phone'])} to confirm times.</p></li>
  <li><span class="num">02</span><h3>Find us</h3><p>General Kariba Street, Freehold, Nakuru — <a href="#find-us">map below</a>.</p></li>
  <li><span class="num">03</span><h3>Arrive &amp; say hello</h3><p>Ushers will welcome you and help you find a seat.</p></li>
  <li><span class="num">04</span><h3>Stay &amp; connect</h3><p>Stay for connection time and meet the church family.</p></li>
 </ol>
</div></section>
<section class="sec bg-sand" id="find-us"><div class="wrap split">
 <div><span class="eyebrow">Find us</span><h2>General Kariba Street, Freehold, Nakuru</h2><p>{e(CT['postal'])}</p>
 <p class="mt2" style="display:flex;gap:12px;flex-wrap:wrap"><a class="btn btn-solid" href="{maps_url()}" rel="noopener" target="_blank">Open in Google Maps</a><a class="btn" href="tel:{e(CT['phone_intl'])}">Call {e(CT['phone'])}</a></p></div>
 <div class="map" data-map="https://www.google.com/maps?q={e(CT['maps_query']).replace(' ','+')}&amp;output=embed"><div><p><b>Interactive map</b></p><p class="muted">Loads Google Maps (Google's privacy policy applies).</p><button class="btn" type="button" data-map-load>Show map</button></div></div>
</div></section>
<div class="expand"><div class="sticky">{PH.pic("courtyard-after-service", "", w=1920, sizes="100vw")}<div class="over"><span class="eyebrow" style="color:var(--sun)">Sundays at LCC</span><h2>Come as you are.</h2></div></div></div>
<section class="sec"><div class="wrap split">
 <div><span class="eyebrow">What to expect</span><h2>Your first Sunday</h2><p>Expect heartfelt worship, prayer and a message from the Bible. There's no pressure to give or to stand up — simply come and be with us.</p>
  <form class="form mt4" id="enquiry" action="api/submit.php" method="post" data-form="visit" novalidate>
   <h3 style="font-size:28px">Planning to visit? Tell us</h3>
   <input type="hidden" name="type" value="visit">
   <div class="field"><label for="v-name">Your name</label><input id="v-name" name="name" autocomplete="name" required maxlength="100"></div>
   <div class="field"><label for="v-reply">Email or phone</label><input id="v-reply" name="reply" required maxlength="120"></div>
   <div class="field"><label for="v-msg">Questions or when you plan to come</label><textarea id="v-msg" name="message" required maxlength="3000"></textarea></div>
   <div class="hp" aria-hidden="true"><label for="v-web">Website</label><input id="v-web" name="website" tabindex="-1" autocomplete="off"></div>
   <button class="btn btn-solid" type="submit">Send</button>
   <div class="form-status" role="status" aria-live="polite"></div>
  </form></div>
 <div>{''.join(f'<details><summary>{e(q)}</summary><p>{e(a)}</p></details>' for q, a in faqs)}</div>
</div></section>
""", extra_ld=[{"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faqs]}])

# ---------------- MINISTRIES
MFRAME = ["offset", "m-arch", "m-orb", "m-pill"]  # a different photographic frame for each ministry
MREV = ["left", "arch", "up", "right"]
MCAT = {"worship": "team", "youth": "youth", "prayer": "worship", "leaders": "events", "fellowship": "fellowship", "outreach": "outreach", "conference": "conference"}
P["ministries.html"] = page("ministries.html", "Ministries", "Ministries at LCC Nakuru: Praise & Worship (One Accord Ministers), Youth & Students, Prayer (Kesha), Leadership Development, Fellowship and the Cutting Edge Conference.",
f"""
<div class="wrap"><header class="page-hero"><span class="eyebrow">Ministries</span><h1 data-split="words">Discover your <em>ministry.</em></h1><p class="lead">Every ministry listed here is documented in LCC's own recordings and posts. Ask the welcome team on Sunday how to join.</p></header></div>
<section class="sec" style="padding-top:clamp(20px,3vw,40px)"><div class="wrap"><nav aria-label="Ministries on this page"><ul class="mini-list" data-stagger>{''.join(f'<li><a href="#{e(m["slug"])}"><b>{e(m["name"])}</b><span>{e(m["kind"])}</span></a></li>' for m in C["ministries"])}</ul></nav><p class="credit">{e(C['ministries_note'])}</p></div></section>
<section class="sec"><div class="wrap mlist">
{''.join(f'<article class="mitem" id="{e(m["slug"])}"><div class="mmedia {MFRAME[i % len(MFRAME)]}" data-reveal="{MREV[i % len(MREV)]}">' + (video_card(VID[m["video"]]) if m.get("video") in VID else PH.pic(pick(MCAT.get(m["slug"], "worship"), 1), "f-arch" if i % 2 else "f-circle ringed")) + (PH.pic(pick(MCAT.get(m["slug"], "worship"), 0), "m-orbit f-circle", "circle", d=.5, sizes="20vw") if MFRAME[i % len(MFRAME)] == "m-orb" and m.get("video") in VID else "") + f'</div><div><span class="eyebrow">{e(m["kind"])} · {e(m["tag"])}</span><h2>{e(m["name"])}</h2><p class="lead" style="max-width:none">{e(m["text"])}</p><ul>' + ''.join(f'<li>{e(a)}</li>' for a in m.get("activities", [])) + f'</ul>' + (f'<a class="btn" href="{e(m["link"])}">Discover</a>' if m.get("link") else '<a class="btn" href="contact.html#message">Ask about joining</a>') + '</div></article>' for i, m in enumerate(C['ministries']))}
</div></section>
<section class="sec band-night"><div class="wrap split"><div><span class="eyebrow">Serve &amp; volunteer</span><h2>Want to serve?</h2><p class="lead">Tell us where you'd like to serve and the church office will connect you with the right ministry. Conference volunteers sign up on the official Cutting Edge site.</p></div><div style="align-self:center;display:flex;gap:12px;flex-wrap:wrap"><a class="btn btn-sun" href="contact.html#message">I want to serve</a><a class="btn btn-ghost-light" href="{e(CF['volunteer'])}" rel="noopener" target="_blank">Volunteer at the conference</a></div></div></section>
""")

# ---------------- SERMONS
speakers = sorted({v["speaker"] for v in C["videos"] if v.get("speaker")})
feat = latest_services[0]
P["sermons.html"] = page("sermons.html", "Sermons & media", "Watch LCC Sunday services, messages by Rev. Elijah Mwangi, Praise Express, Kesha nights, Cutting Edge Conference sessions and worship — all from the official LCC YouTube channel.",
f"""
<section class="band-night"><div class="wrap" style="padding-top:clamp(40px,7vw,96px);padding-bottom:clamp(40px,6vw,72px)">
 <span class="eyebrow">Latest service · {e(feat['published'])}</span>
 <div class="feature-video"><div>{video_card(feat, lazy=False)}</div><div><h1 style="color:var(--bone);font-size:clamp(36px,5vw,72px)">{e(feat['title'])}</h1><ul class="meta-list"><li><b>Streamed:</b> {e(feat['published'])}</li><li><b>Where:</b> LCC, Freehold, Nakuru</li></ul><p style="display:flex;gap:12px;flex-wrap:wrap"><a class="btn btn-sun" href="watch.html">Watch online</a>{share_btn()}</p></div></div>
</div></section>
<section class="sec"><div class="wrap">
 {rail("Latest Sunday services", latest_services, "rail-latest", "Every Sunday")}
 {rail("Praise Express", praise, "rail-praise", "Praise &amp; worship".replace("&amp;","&"))}
 {rail("Cutting Edge Conference 2026", conf26, "rail-conf", "Conference", ("conference.html","Conference page →"))}
 {rail("Special services & nights", special, "rail-special", "Kesha · Summits · Students")}
 {rail("Worship & music", worship, "rail-worship2", "One Accord Ministers")}
 {rail("Messages archive", sermons_older + conf_old, "rail-archive", "Earlier messages")}
</div></section>
<section class="sec bg-sand" aria-labelledby="lib-h"><div class="wrap">
 <h2 id="lib-h">Search the library</h2>
 <div class="filters" role="group" aria-label="Filter videos">
  <button class="chip" type="button" data-filter="all" aria-pressed="true">All</button>
  <button class="chip" type="button" data-filter="service" aria-pressed="false">Sunday services</button>
  <button class="chip" type="button" data-filter="sermon" aria-pressed="false">Messages</button>
  <button class="chip" type="button" data-filter="praise" aria-pressed="false">Praise Express</button>
  <button class="chip" type="button" data-filter="conference" aria-pressed="false">Conference</button>
  <button class="chip" type="button" data-filter="special" aria-pressed="false">Special</button>
  <button class="chip" type="button" data-filter="worship" aria-pressed="false">Worship</button>
  <label class="sr-only" for="speaker">Speaker</label><select class="search" id="speaker"><option value="">All speakers</option>{''.join(f'<option>{e(s)}</option>' for s in speakers)}</select>
  <label class="sr-only" for="q">Search videos</label><input class="search" id="q" type="search" placeholder="Search by title or speaker">
 </div>
 <p class="sr-only" aria-live="polite" id="count"></p>
 <div class="videos" id="library" data-cms="videos">{''.join(video_card(v) for v in C['videos'])}</div>
 <p class="empty" id="empty" hidden>No videos match that search.</p>
 <p class="mt4 center"><a class="btn" href="{e(SO['youtube'])}" rel="noopener" target="_blank">Everything on YouTube</a></p>
</div></section>
""", extra_ld=[{"@context": "https://schema.org", "@type": "ItemList", "itemListElement": [
    {"@type": "ListItem", "position": i + 1, "item": {"@type": "VideoObject", "name": v["full_title"], "thumbnailUrl": f"https://i.ytimg.com/vi/{v['id']}/hqdefault.jpg", "embedUrl": f"https://www.youtube-nocookie.com/embed/{v['id']}", "description": v["full_title"] + " — Life Celebration Centre, Nakuru"}} for i, v in enumerate(C["videos"][:12])]}])

# ---------------- WATCH
P["watch.html"] = page("watch.html", "Watch online", "Watch Life Celebration Centre (LCC) Nakuru online: both Sunday services stream live on YouTube every week. Watch the latest service now.",
f"""
<section class="band-night"><div class="wrap" style="padding-top:clamp(40px,7vw,96px);padding-bottom:clamp(40px,6vw,80px)">
 <span class="eyebrow">Online church</span>
 <h1 style="color:var(--bone);max-width:14ch">Worship with LCC <em style="color:var(--sun)">wherever</em> you are.</h1>
 <p class="lead">Both Sunday services — First and Second Service — stream live on the official LCC YouTube channel. When a service is live, you'll find it at the top of the channel's live page.</p>
 <p style="display:flex;gap:12px;flex-wrap:wrap"><a class="btn btn-sun" href="{e(SO['youtube_live'])}" rel="noopener" target="_blank">Open live streams on YouTube</a><a class="btn btn-ghost-light" href="{e(SO['facebook'])}" rel="noopener" target="_blank">Facebook</a></p>
 <p class="credit">We don't show a “live now” badge here because this website can't check the channel's live status — the YouTube link always shows what's live.</p>
 <div class="mt4"><span class="eyebrow">Latest service · {e(feat['published'])}</span>{video_card(feat)}</div>
</div></section>
<section class="sec"><div class="wrap">{rail("Recent services", latest_services[1:], "rail-recent")}{rail("Praise Express", praise, "rail-pe")}<p class="center"><a class="btn" href="sermons.html">Full sermon library</a></p></div></section>
""")

# ---------------- EVENTS
ev_ld = [{"@context": "https://schema.org", "@type": "Event", "name": ev["title"], "startDate": ev["start"], "endDate": ev["end"],
          "eventStatus": "https://schema.org/EventScheduled", "eventAttendanceMode": "https://schema.org/OfflineEventAttendanceMode",
          "location": {"@type": "Place", "name": "Deliverance Church LCC", "address": {"@type": "PostalAddress", "streetAddress": "Kariba Road, Freehold", "addressLocality": "Nakuru", "addressCountry": "KE"}},
          "organizer": {"@type": "Organization", "name": S["org"], "url": BASE}, "description": ev["summary"], "url": ev.get("external") or BASE + "conference.html"} for ev in up_ev]
cats = sorted({p["category"] for p in PAST})
P["events.html"] = page("events.html", "Events", "Events at LCC Nakuru: Cutting Edge Conference 2027 (30 Mar – 4 Apr) and an archive of past events — Leaders' Summit, Praise Express, Pastors' and Spouses Conference, Kesha and more.",
f"""
<div class="wrap"><header class="page-hero"><span class="eyebrow">Events</span><h1 data-split="words">What's <em>coming up.</em></h1><p class="lead">Major events are listed here; weekly announcements are on our <a href="{e(SO['facebook'])}" rel="noopener" target="_blank">Facebook page</a>.</p></header></div>
<section class="sec"><div class="wrap">
 <span class="eyebrow">Upcoming</span>
 {upnext()}
 {feature_conf()}
 <div class="sec-head mt4"><div><span class="eyebrow">Recurring</span><h2>Throughout the year</h2></div></div>
 <div class="cards" data-stagger>
  <div class="card"><span class="kind">Every Sunday</span><h3>First &amp; Second Service</h3><p class="muted">Streamed live on YouTube. <a href="services.html">Times &amp; details</a></p></div>
  <div class="card"><span class="kind">Every few months</span><h3>Praise Express Service</h3><p class="muted">Next date to be announced on Facebook.</p></div>
  <div class="card"><span class="kind">Special nights</span><h3>Kesha</h3><p class="muted">Including the annual Crossover Kesha on 31 December — date to be announced.</p></div>
 </div>
</div></section>
<section class="sec bg-sand" aria-labelledby="arc-h"><div class="wrap">
 <div class="sec-head"><div><span class="eyebrow">Archive</span><h2 id="arc-h">Past events</h2></div></div>
 <div class="filters gallery-f" role="group" aria-label="Filter past events"><button class="chip" type="button" data-efilter="all" aria-pressed="true">All</button>{''.join(f'<button class="chip" type="button" data-efilter="{e(c)}" aria-pressed="false">{e(c)}</button>' for c in cats)}</div>
 <div class="ecards" id="past">{''.join(ecard(ev).replace('<article class="ecard">', f'<article class="ecard" data-cat="{e(ev["category"])}">') for ev in PAST)}</div>
</div></section>
""", extra_ld=ev_ld)

# event detail pages
for ev in PAST:
    v = VID.get(ev["video"])
    related = [x for x in C["videos"] if x["id"] != ev["video"] and (x["title"].split(" · ")[0] in ev["title"] or ev["title"].split(" 20")[0] in x["title"])][:6]
    P[ev_slug(ev)] = page(ev_slug(ev), ev["title"], f'{ev["title"]} at Life Celebration Centre (LCC) Nakuru — {ev["when"]}. {ev["summary"]}',
f"""
<section class="band-night"><div class="wrap" style="padding-top:clamp(40px,7vw,96px);padding-bottom:clamp(40px,6vw,80px)">
 <p><a href="events.html">← All events</a></p>
 <span class="eyebrow">Past event · {e(ev['category'])} · {e(ev['when'])}</span>
 <h1 style="color:var(--bone);max-width:16ch">{e(ev['title'])}</h1>
 <p class="lead">{e(ev['summary'])}</p>
 <p style="display:flex;gap:12px;flex-wrap:wrap">{share_btn()}<a class="btn btn-ghost-light" href="events.html">Upcoming events</a></p>
 <div class="mt4">{video_card(v) if v else ''}</div>
 <ul class="meta-list"><li><b>When:</b> {e(ev['when'])} (date from the LCC YouTube stream)</li><li><b>Where:</b> LCC, Freehold, Nakuru</li></ul>
</div></section>
<section class="sec"><div class="wrap">{rail("More from this event", related, "rail-rel") if related else '<p class="muted">More recordings are on the <a href="sermons.html">sermon library</a>.</p>'}</div></section>
""", current="events.html")

# ---------------- CONFERENCE (universe)
P["conference.html"] = page("conference.html", "Cutting Edge Conference 2027", "Cutting Edge Conference 2027, 30 March – 4 April 2027 at LCC Nakuru. Theme: Commissioning for the Global Mission (John 4:35). Speakers, six-day programme, registration and past editions.",
f"""
<div class="cu">
<section class="wrap cu-hero">
 <span class="eyebrow">The Cutting Edge Conference · Nakuru</span>
 <div class="yr" aria-hidden="true">2027</div>
 <h1>{e(CF['theme'])}</h1>
 <div class="countdown" data-countdown="{e(CF['start_iso'])}" aria-label="Time until the conference starts"></div>
 <div class="cu-grid"><div><small>Dates</small><b>{e(CF['dates'])}</b></div><div><small>Venue</small><b>Deliverance Church LCC, Freehold along Kariba Road</b></div><div><small>Anchor scripture</small><b>{e(CF['anchor'])}</b></div><div><small>Convener</small><b>Rev. Elijah Mwangi</b></div></div>
 <p class="mt2" style="display:flex;gap:12px;flex-wrap:wrap"><a class="btn btn-sun" href="{e(CF['register'])}" rel="noopener" target="_blank">Register as a delegate</a><a class="btn btn-ghost-light" href="{e(CF['volunteer'])}" rel="noopener" target="_blank">Volunteer</a><a class="btn btn-ghost-light" href="{e(CF['partner'])}" rel="noopener" target="_blank">Partner</a>{share_btn()}</p>
 <p class="credit">Registration, volunteering and partnership are handled on the official site, cuttingedgeconference.co.ke.</p>
</section>
<section class="sec"><div class="wrap split">
 <blockquote class="scripture" style="margin:0">“Say not ye, There are yet four months, and then cometh harvest? behold, I say unto you, Lift up your eyes, and look on the fields; for they are white already to harvest.”<cite>John 4:35 (KJV) · 2027 anchor scripture</cite></blockquote>
 <div><span class="eyebrow">Our purpose</span><h2 style="color:var(--bone)">Equipping the saints</h2><p class="lead">The conference takes its theme from Ephesians 4:12 — equipping the saints for the work of the ministry. It serves the LCC congregation and the wider body of Christ in Nakuru and beyond, and is held every April. {e(CF['edition_note'])}</p></div>
</div></section>
<section class="sec"><div class="wrap split">
 <div><span class="eyebrow">Programme</span><h2 style="color:var(--bone)">Six days</h2>
 <table class="programme"><thead><tr><th scope="col">Day</th><th scope="col">Time</th><th scope="col">Focus</th></tr></thead><tbody>
 {''.join(f'<tr><td>{e(p["day"])}</td><td>{e(p["time"])}</td><td>{e(p["what"])}</td></tr>' for p in CF['programme'])}
 </tbody></table>
 <p class="credit">Delegate options: Day delegate (lunch included) · Boarding delegate (bed, breakfast and lunch). Fees on the official site.</p></div>
 <div><span class="eyebrow">2027 speakers</span><h2 style="color:var(--bone)">Ministering</h2>
 <div class="speakers">{''.join(f'<div class="speaker"><div class="initials" aria-hidden="true">{e("".join(w[0] for w in s["name"].replace("Rev. ","").replace("Bishop ","").split()[:2]))}</div><b>{e(s["name"])}</b><small>{e(s["from"])}</small></div>' for s in CF['speakers'])}</div>
 <h3 class="mt4" style="color:var(--bone)">Featured speakers across editions</h3>
 <div class="speaker-cloud mt2">{''.join(f'<span>{e(s)}</span>' for s in CF['all_speakers'])}</div>
 <p class="credit">As listed at cuttingedgeconference.co.ke/speakers</p></div>
</div></section>
<section class="sec" aria-labelledby="c26-h"><div class="wrap duo">
 <div><span class="eyebrow">Last edition · April 2026</span><h2 id="c26-h" style="color:var(--bone)" data-split="words">Cutting Edge <em style="color:var(--sun)">2026</em> in pictures</h2><p class="lead">Six days of worship, teaching and preaching at LCC. These frames come from the 2026 conference streams, not the 2027 edition.</p></div>
 <div class="xcollage cu-collage"><span class="shape" aria-hidden="true"></span>{PH.pic(pick("conference", 0), "c1", "left")}{PH.pic(pick("conference", 3), "c2", "up", d=.35)}{PH.pic(pick("conference", 1), "c3 f-circle", "circle", d=.7)}<span class="label">Cutting Edge Conference 2026 · LCC Nakuru</span></div>
</div></section>
<section class="sec"><div class="wrap">
 {rail("Cutting Edge Conference 2026", conf26, "rail-c26", "Previous edition · April 2026")}
 {rail("Earlier editions", conf_old, "rail-cold", "2024 and before")}
</div></section>
<section class="sec"><div class="wrap prose"><span class="eyebrow">Questions</span><h2 style="color:var(--bone)">Contact the conference team</h2>
<p>Email <a href="mailto:{e(CF['email'])}">{e(CF['email'])}</a> or call <a href="tel:+254722864864">{e(CF['phone'])}</a>.</p></div></section>
</div>
""", current="events.html", extra_ld=ev_ld[:1])

# ---------------- GALLERY
gcats = []
for v, c in MOMENTS + [(x, "Conferences") for x in conf26[3:]] + [(x, "Sunday services") for x in latest_services[4:]]:
    if (v, c) not in gcats:
        gcats.append((v, c))
_ALL = [p["slug"] for p in LIB]
_gcats = [c for c in CATNAME if c in {p["cat"] for p in LIB}]
_feat = [x for x in ["fellowship-circle", "worship-gold", "baptism", "worship-open-hands", "handshake-welcome", "outreach-stage"] if x in BY]
_strip = [x for x in dict.fromkeys(["youth-group", "courtyard-greeting", "conquerors-entrance", pick("conference", 0), pick("conference", 3), "worship-team-cross", pick("team", 6), pick("teaching", 0), pick("events", 0), pick("events", 2), pick("conference", 6)]) if x and x in BY]
P["gallery.html"] = page("gallery.html", "LCC Moments — gallery", "LCC Moments: Sunday services, praise and worship, conferences and special nights at Life Celebration Centre, Nakuru.",
f"""
<div class="wrap"><header class="page-hero"><span class="eyebrow">LCC Moments</span><h1 data-split="words">Church life, <em>captured.</em></h1><p class="lead" data-reveal="rise" style="--d:.4s">Moments from Sundays, Praise Express, fellowship days, baptisms and the Cutting Edge Conference. Select a photograph in the film strip to view it full screen.</p></header></div>

<section class="sec" aria-labelledby="g1-h" style="padding-top:clamp(24px,3vw,40px)"><div class="wrap">
 <h2 class="sr-only" id="g1-h">Featured moments</h2>
 <div class="spread">
  {PH.pic(_feat[0], "s1", "scale", eager=True, sizes="(max-width:860px) 100vw, 58vw")}{PH.pic(_feat[1], "s2", "right", d=.15)}{PH.pic(_feat[2], "s3", "up", d=.3, sizes="25vw")}{PH.pic(_feat[3], "s4", "up", d=.45, sizes="18vw")}{PH.pic(_feat[4], "s5", "left", d=.2, sizes="25vw")}{PH.pic(_feat[5], "s6", "left", d=.35, sizes="40vw")}
  <div class="note"><span class="eyebrow">Life at LCC</span><h3>Fellowship, worship &amp; new life</h3><p class="muted">Fellowship days, Praise Express, baptisms and outreach across Nakuru.</p><span class="cap-line"><b>Photos</b>LCC media team</span></div>
 </div>
</div></section>

<section aria-labelledby="g4-h" style="padding-bottom:clamp(48px,6vw,88px)">
 <div class="wrap"><div class="sec-head"><div><span class="eyebrow">Film strip</span><h2 id="g4-h">Drag through the year</h2></div></div></div>
 <div class="strip"><div class="xrail" tabindex="0" role="region" aria-label="Film strip of LCC moments (scrollable)">{''.join(f'<figure>{PH.lb_btn(x, "strip", sizes="(max-width:600px) 70vw, 28vw")}<figcaption><b>{e(CATNAME.get(BY[x]["cat"]))}</b>{e(BY[x]["short"])}</figcaption></figure>' for x in _strip)}</div>
 <div class="nav-btns"><button class="chip" type="button" data-strip="prev" aria-label="Scroll film strip back">←</button><button class="chip" type="button" data-strip="next" aria-label="Scroll film strip forward">→</button></div></div>
</section>

<section class="sec bg-sand" aria-labelledby="g7-h"><div class="wrap">
 <div class="sec-head"><div><span class="eyebrow">Watch the moments</span><h2 id="g7-h">Moments from the streams</h2></div></div>
 <div class="filters gallery-f" role="group" aria-label="Filter moments"><button class="chip" type="button" data-gfilter="all" aria-pressed="true">All</button>{''.join(f'<button class="chip" type="button" data-gfilter="{e(c)}" aria-pressed="false">{e(c)}</button>' for c in ["Sunday services","Praise & worship","Conferences","Special nights"])}</div>
 {collage(gcats[:12], "gallery")}
 <p class="credit mt4">Photographs by the LCC media team, published with the church's approval; stream frames come from LCC's own YouTube services. If you appear in a photograph and would like it removed, please <a href="contact.html">contact the church office</a>.</p>
</div></section>
""", current="gallery.html")

# ---------------- NEWS
P["news.html"] = page("news.html", "Announcements", "Announcements and stories from Life Celebration Centre (LCC) Nakuru, with dates clearly marked.",
f"""
<div class="wrap"><header class="page-hero"><span class="eyebrow">Announcements</span><h1>News from <em>LCC.</em></h1><p class="lead">Current notices first; older items are marked with their dates. Weekly updates are posted on Facebook.</p></header></div>
<section class="sec"><div class="wrap">
 <span class="eyebrow">Current</span>
 <article class="split wide-left" style="padding:28px 0;border-top:1px solid var(--line)"><div><h2 style="font-size:clamp(28px,3vw,40px)">Cutting Edge Conference 2027 — registration open</h2><p class="muted">30 March – 4 April 2027 · “Commissioning for the Global Mission” · Register on the official conference website.</p><a href="conference.html">Conference details →</a></div><div></div></article>
 <span class="eyebrow mt4" style="display:block">Recent &amp; archive</span>
 {''.join(f'<article class="split wide-left" style="padding:32px 0;border-top:1px solid var(--line)" id="{e(n["slug"])}"><div><span class="kind" style="font:600 12px var(--sans);letter-spacing:.16em;color:var(--clay)">{e(n["date"])}</span><h2 style="font-size:clamp(28px,3vw,40px)">{e(n["title"])}</h2><p class="muted">{e(n["summary"])}</p>' + (f'<a href="{e(n["link"])}">Read more →</a>' if n.get("link") else '') + '</div><div>' + (video_card(VID[n["video"]]) if n.get("video") in VID else '') + '</div></article>' for n in C['news'] if n["slug"] != "cutting-edge-2027-announced")}
 {''.join(f'<article class="split wide-left" style="padding:32px 0;border-top:1px solid var(--line)"><div><span class="kind" style="font:600 12px var(--sans);letter-spacing:.16em;color:var(--clay)">{e(ev["when"])}</span><h2 style="font-size:clamp(28px,3vw,40px)">{e(ev["title"])}</h2><p class="muted">{e(ev["summary"])}</p><a href="{ev_slug(ev)}">View event →</a></div><div></div></article>' for ev in PAST[:2])}
</div></section>
""")

# ---------------- GIVE
P["give.html"] = page("give.html", "Give", "Give to Life Celebration Centre (LCC) Nakuru. Verified giving details are published only after confirmation by the church office.",
f"""
<div class="wrap"><header class="page-hero"><span class="eyebrow">Give</span><h1>Generosity that <em>transforms.</em></h1><p class="lead">Your giving supports worship, outreach, discipleship and the work of transforming nations for Christ.</p></header></div>
<section class="sec"><div class="wrap">
 <h2 class="sr-only">Ways to give</h2>
 <div class="give-grid">
  <div class="give-card"><span class="eyebrow">In person</span><h3>During any service</h3><p class="muted">Give your tithes and offerings during our Sunday services.</p></div>
  <div class="give-card"><span class="eyebrow">M-Pesa</span><h3>Mobile giving</h3>{giving_html()}</div>
  <div class="give-card"><span class="eyebrow">Questions</span><h3>Talk to the office</h3><p class="muted">For pledges, projects or receipts, call <a href="tel:{e(CT['phone_intl'])}">{e(CT['phone'])}</a>.</p></div>
 </div>
 <div class="notice mt4"><b>Stay safe</b>LCC publishes giving numbers only on this page and through the church office. If anyone sends you a different number claiming to be LCC, call the office to confirm before sending money.</div>
</div></section>
""")

# ---------------- CONTACT (unchanged forms, refreshed layout)
P["contact.html"] = page("contact.html", "Contact & prayer", "Contact Life Celebration Centre (LCC) Nakuru: 0722 864 864, lccnakuru@yahoo.com, General Kariba Street, Freehold. Send a message or a private prayer request.",
f"""
<div class="wrap"><header class="page-hero"><span class="eyebrow">Contact</span><h1>We're <em>here</em> for you.</h1></header></div>
<section class="sec"><div class="wrap split">
 <div>
  <span class="eyebrow">Church office</span><h2>Get in touch</h2>
  <p><b>Phone</b><br><a href="tel:{e(CT['phone_intl'])}">{e(CT['phone'])}</a></p>
  <p><b>Email</b><br><a href="mailto:{e(CT['email'])}">{e(CT['email'])}</a></p>
  <p><b>Visit</b><br>{e(CT['street'])}, {e(CT['city'])}<br>{e(CT['postal'])}<br><a href="{maps_url()}" rel="noopener" target="_blank">Open in Google Maps</a></p>
  <p><b>Online</b><br><a href="{e(SO['facebook'])}" rel="noopener" target="_blank">Facebook</a> · <a href="{e(SO['youtube'])}" rel="noopener" target="_blank">YouTube</a> · <a href="{e(SO['instagram'])}" rel="noopener" target="_blank">Instagram</a></p>
  <p class="credit">WhatsApp: no official WhatsApp number has been published, so none is listed.</p>
  <div class="invite mt4" style="padding:28px">{yt_img("I-Zw0aavDF4", "", frame=2)}<span class="eyebrow">Prayer corner</span><h2 style="font-size:32px">You don't have to carry it alone.</h2><p style="color:#E6DCCF">Send a private prayer request — it is never published and is read only by the LCC pastoral team.</p><a class="btn btn-sun" href="#prayer">Send a prayer request</a></div>
 </div>
 <div>
  <form class="form" id="message" action="api/submit.php" method="post" data-form="contact" novalidate>
   <h2 style="font-size:32px">Send a message</h2>
   <input type="hidden" name="type" value="contact">
   <div class="field"><label for="c-name">Your name</label><input id="c-name" name="name" autocomplete="name" required maxlength="100"></div>
   <div class="field"><label for="c-email">Email or phone</label><input id="c-email" name="reply" autocomplete="email" required maxlength="120"></div>
   <div class="field"><label for="c-msg">Message</label><textarea id="c-msg" name="message" required maxlength="3000"></textarea></div>
   <div class="hp" aria-hidden="true"><label for="c-web">Website</label><input id="c-web" name="website" tabindex="-1" autocomplete="off"></div>
   <button class="btn btn-solid" type="submit">Send message</button>
   <div class="form-status" role="status" aria-live="polite"></div>
  </form>
  <form class="form mt4" id="prayer" action="api/submit.php" method="post" data-form="prayer" novalidate>
   <h2 style="font-size:32px">Prayer request</h2>
   <p class="muted mt0">Your request is private. It is never published on this website and is seen only by the LCC pastoral team.</p>
   <input type="hidden" name="type" value="prayer">
   <div class="field"><label for="p-name">Your name <span class="muted">(optional)</span></label><input id="p-name" name="name" autocomplete="name" maxlength="100"></div>
   <div class="field"><label for="p-reply">Email or phone <span class="muted">(optional, for a call back)</span></label><input id="p-reply" name="reply" maxlength="120"></div>
   <div class="field"><label for="p-msg">How can we pray for you?</label><textarea id="p-msg" name="message" required maxlength="3000"></textarea></div>
   <div class="check"><input type="checkbox" id="p-ok" name="consent" value="1" required><label for="p-ok">I agree that the LCC pastoral team may read this request and contact me if I gave my details.</label></div>
   <div class="hp" aria-hidden="true"><label for="p-web">Website</label><input id="p-web" name="website" tabindex="-1" autocomplete="off"></div>
   <button class="btn btn-clay" type="submit">Send prayer request</button>
   <div class="form-status" role="status" aria-live="polite"></div>
  </form>
 </div>
</div></section>
""")

P["privacy.html"] = page("privacy.html", "Privacy notice", "How the LCC Nakuru website handles your information, prayer requests, cookies, maps and YouTube embeds.",
f"""
<div class="wrap"><header class="page-hero"><span class="eyebrow">Privacy</span><h1>Your privacy.</h1></header></div>
<section class="sec"><div class="wrap prose">
<h2>What we collect</h2><p>Only what you send through our contact, visitor and prayer forms: your name (optional for prayer), how to reach you, and your message. Prayer requests are never published and are read only by the LCC pastoral team.</p>
<h2>Cookies, video and maps</h2><p>This site sets no tracking cookies. Videos use YouTube's privacy-enhanced mode and load only when you press play; YouTube's policy applies when you do. Video stills are loaded from YouTube's image servers. The map loads Google Maps only when you choose “Show map”.</p>
<h2>Fonts</h2><p>Fonts are served from this website, not a third party.</p>
<h2>Your rights</h2><p>Under Kenya's Data Protection Act, 2019, you may ask to see or delete information you sent us. Contact <a href="mailto:{e(CT['email'])}">{e(CT['email'])}</a> or call {e(CT['phone'])}.</p>
<p class="muted">Last updated {TODAY.isoformat()}.</p>
</div></section>
""")

P["404.html"] = page("404.html", "Page not found", "This page could not be found.",
"""<div class="wrap"><header class="page-hero"><span class="eyebrow">404</span><h1>This page has <em>wandered</em> off.</h1><p class="lead">Let's get you home.</p><p class="mt2"><a class="btn btn-solid" href="./">Go to the homepage</a></p></header></div>""")


def main():
    for name, src in P.items():
        (ROOT / name).write_text(src, encoding="utf-8")
    urls = [n for n in P if n != "404.html"]
    sm = "".join(f"<url><loc>{BASE if u == 'index.html' else BASE + u}</loc><lastmod>{TODAY.isoformat()}</lastmod></url>" for u in urls)
    (ROOT / "sitemap.xml").write_text(f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{sm}</urlset>\n')
    (ROOT / "robots.txt").write_text(f"User-agent: *\nAllow: /\nDisallow: /admin/\nDisallow: /api/\nDisallow: /private/\n\nSitemap: {BASE}sitemap.xml\n")
    print("built", len(P), "pages")


if __name__ == "__main__":
    main()
