#!/usr/bin/env python3
"""Design laboratory for the LCC photography + motion upgrade.
Writes docs/lab/*.html. Uses real LCC photos from assets/photos/library.json (roles assigned there).
usage: python3 tools/lab.py"""
import json, pathlib, html, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from photolib import Photos, LIB, BY, CATNAME, stamp as _stamp  # noqa: E402
OUT = ROOT / "docs/lab"; OUT.mkdir(parents=True, exist_ok=True)
e = lambda s: html.escape(str(s or ""), quote=True)
PHL = Photos("../../")
CAT = {}
for p in LIB:
    CAT.setdefault(p["cat"], []).append(p)
src = lambda slug, w=1280, base=None: PHL.src(slug, w)
img = lambda slug, w=960, eager=False, sizes="(max-width:860px) 100vw, 50vw", base=None: PHL.img(slug, w, eager, sizes)
def pic(slug, cls="", reveal=None, d=0, w=960, extra="", tag=None, **k):
    return PHL.pic(slug, cls, reveal, d, w, extra, tag, **{x: y for x, y in k.items() if x in ("eager", "sizes", "alt")})
def roles(cat, n):
    xs = [p["slug"] for p in CAT.get(cat, [])]
    return (xs * 3)[:n] if xs else [LIB[i % len(LIB)]["slug"] for i in range(n)]
# map lab roles onto the curated library categories
_MAP = {"worship": "worship", "fellowship": "team", "congregation": "worship", "teaching": "teaching", "baptism": "conference",
        "outreach": "events", "youth": "youth", "building": "team", "events": "events", "conference": "conference"}
R = {k: roles(v, 8) for k, v in _MAP.items()}
ALL = [p["slug"] for p in LIB]
for k in list(R):
    R[k] = list(dict.fromkeys(R[k] + ALL))[:8]


def shell(title, body, intro="", base="../../", wide=False):
    return f"""<!doctype html><html lang="en-KE"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(title)} · LCC Design Lab</title><meta name="robots" content="noindex">
<link rel="stylesheet" href="{base}assets/css/site.css"><link rel="stylesheet" href="{base}assets/css/enhance.css">
<script>document.documentElement.classList.add('js')</script>
<style>
.lab-top{{position:sticky;top:0;z-index:60;background:var(--ink);color:var(--bone);font:500 14px var(--sans)}}
.lab-top .wrap{{display:flex;gap:6px 18px;align-items:center;min-height:52px;flex-wrap:wrap}}
.lab-top a{{color:var(--bone);text-decoration:none;opacity:.75}}.lab-top a:hover,.lab-top a[aria-current]{{opacity:1;color:var(--sun)}}
.lab-top b{{font:500 16px var(--serif);margin-right:auto;color:var(--bone)}}
.exp{{padding:clamp(48px,7vw,96px) 0;border-top:1px solid var(--line)}}
.exp-h{{display:flex;justify-content:space-between;gap:20px;align-items:baseline;margin-bottom:clamp(24px,4vw,44px);flex-wrap:wrap}}
.exp-h .no{{font:600 12px var(--sans);letter-spacing:.2em;color:var(--clay)}}
.exp-h h2{{font-size:clamp(26px,3vw,40px);margin:4px 0 0}}
.exp-h p{{max-width:52ch;color:var(--muted);margin:0;font-size:15px}}
.verdict{{display:inline-block;font:700 11px var(--sans);letter-spacing:.14em;text-transform:uppercase;padding:4px 10px;border-radius:999px;background:var(--sand);color:var(--ink)}}
.verdict.keep{{background:#2E4A12;color:#E6EFD9}}.verdict.maybe{{background:var(--ochre)}}.verdict.no{{background:#7A1F12;color:#F7E0DA}}
.band-night .exp-h p{{color:#C9BDAF}}
</style></head><body>
<div class="lab-top"><div class="wrap"><b>LCC Design Lab</b>
<a href="index.html">Overview</a><a href="compositions.html">Photo compositions</a><a href="galleries.html">Galleries</a><a href="slideshows.html">Slideshows</a><a href="motion.html">Motion showcase</a><a href="mobile.html">Mobile</a><a href="photo-library.html">Photo library</a></div></div>
{intro}
{body}
<script src="{base}assets/js/motion.js" defer></script></body></html>"""


def exp(no, title, note, inner, verdict="", cls=""):
    v = {"keep": '<span class="verdict keep">Selected</span>', "maybe": '<span class="verdict maybe">Use sparingly</span>', "no": '<span class="verdict no">Not used</span>'}.get(verdict, "")
    return f'<section class="exp {cls}"><div class="wrap"><div class="exp-h"><div><span class="no">{e(no)}</span><h2>{title}</h2></div><p>{note} {v}</p></div>{inner}</div></section>'


ARROW_L = '<svg viewBox="0 0 24 24" width="18" height="18" aria-hidden="true"><path d="M15 5l-7 7 7 7" fill="none" stroke="currentColor" stroke-width="2"/></svg>'
ARROW_R = '<svg viewBox="0 0 24 24" width="18" height="18" aria-hidden="true"><path d="M9 5l7 7-7 7" fill="none" stroke="currentColor" stroke-width="2"/></svg>'


def stamp(text="TRANSFORMING NATIONS FOR CHRIST · "):
    return _stamp(text)


def slideshow(slugs, fx="kenburns", cls="", label="LCC photographs", autoplay=True, thumbs=False, metas=None, interval=6000):
    return PHL.slideshow(slugs, fx, cls, label, autoplay, thumbs, bool(metas), interval)


def lb_btn(slug, group, w=960, cls="", extra=""):
    return PHL.lb_btn(slug, group, w, cls)


# =====================================================================
# PAGE: Photo compositions (circles, organic, layered, geometric)
# =====================================================================
W, F, C_, T, O, B, Y = R["worship"], R["fellowship"], R["congregation"], R["teaching"], R["outreach"], R["baptism"], R["youth"]

comp = []
comp.append(exp("C1", "Arch hero with orbiting circle", "Homepage hero. One dominant arch (the sanctuary shape), a circular inset that overlaps it, and a rotating type seal carrying the verified vision. The text column on the left stays unchanged.",
 f'''<div class="hero" style="padding:0"><div><span class="eyebrow">Transforming Nations for Christ</span><h1 data-split="words">A place to <em>celebrate</em> life in Christ.</h1><p class="lead">Life Celebration Centre exists to reconcile people to God and equip them for ministry — right here on General Kariba Street, Nakuru.</p><div class="actions"><a class="btn btn-solid" href="#">Plan your visit</a><a class="btn" href="#">Watch a message</a></div></div>
 <div class="hero-photo">{pic(W[0], "main", "arch", w=1600, eager=True)}{pic(F[0], "orbit f-circle", "circle", d=.5)}{stamp()}</div></div>''', "keep"))

comp.append(exp("C2", "Three overlapping circles", "Community moments in three sizes, overlapping like a conversation. Faces are kept clear of the overlaps by setting a focus point for each photo.",
 f'''<div class="duo"><div class="trio">{pic(F[1],"a","circle")}{pic(C_[0],"b","circle",d=.25)}{pic(F[2],"c","circle",d=.5)}</div>
 <div><span class="eyebrow">Life together</span><h2 data-split="lines" data-lines="Church is a family|before it is|a building.">Church is a family before it is a building.</h2><p class="lead">After every service the courtyard fills with greetings, catch-ups and prayer.</p></div></div>''', "keep"))

comp.append(exp("C3", "Ringed portrait", "Leadership. A circular portrait inside two hairline rings (clay and line colour). Calm and dignified, with no heavy shadow.",
 f'''<div class="duo"><div style="max-width:420px;margin:12% auto">{pic(T[0],"f-circle ringed","circle")}</div>
 <div><span class="eyebrow">Lead Pastor</span><h2>Rev. Elijah Mwangi</h2><p class="lead">Leads Life Celebration Centre and convenes the annual Cutting Edge Conference.</p></div></div>''', "keep"))

comp.append(exp("C4", "Organic masks", "Two soft, hand-drawn blob masks for the youth and fellowship pages. Used once per page at most, so it stays special.",
 f'''<div class="duo flip"><div style="display:grid;grid-template-columns:1.2fr .8fr;gap:18px;align-items:end">{pic(Y[0],"f-organic","organic",extra=' style="aspect-ratio:1"')}{pic(F[3],"f-organic-2","organic",d=.3,extra=' style="aspect-ratio:.85"')}</div>
 <div><span class="eyebrow">Youth Ablaze</span><h2 data-split="chars">Set on fire.</h2><p class="lead">Worship nights, mentorship and bonfires for LCC teens and young adults.</p></div></div>''', "maybe"))

comp.append(exp("C5", "Layered editorial collage", "One dominant photograph, a second overlapping from below right, a small detail shot and a sand disc behind. Good for About and the conference recap.",
 f'''<div class="xcollage"><span class="shape" aria-hidden="true"></span>{pic(W[1],"c1","left")}{pic(C_[1],"c2","up",d=.35)}{pic(W[2],"c3 f-circle","circle",d=.7)}<span class="label">Sunday at LCC · Freehold, Nakuru</span></div>''', "keep"))

comp.append(exp("C6", "Double-line arch frame", "Architectural frame for the church building and the 'Plan your visit' page: two hairlines echo a doorway.",
 f'''<div class="duo"><div class="arch-frame" style="max-width:460px">{pic(R["building"][0],"f-arch","arch")}</div><div><span class="eyebrow">Find us</span><h2>General Kariba Street, Freehold</h2><p class="lead">Ushers meet you at the gate and help you find a seat.</p></div></div>''', "keep"))

comp.append(exp("C7", "Offset frame", "A hairline rectangle offset behind the photo. Quiet and editorial; for ministry and event pages.",
 f'''<div class="duo flip"><div class="offset" style="margin:0 24px 24px 0">{pic(O[0],"","right",extra=' style="aspect-ratio:4/3"')}</div><div><span class="eyebrow">Outreach</span><h2>Into the streets of Nakuru</h2><p class="lead">Open-air ministry brings worship and the gospel to the city centre.</p></div></div>''', "keep"))

comp.append(exp("C8", "Pill and oval portraits", "Tall pill frames for people-led stories (testimonies, ministry leaders). Avoid for groups.",
 f'''<div style="display:grid;grid-template-columns:repeat(4,1fr);gap:clamp(10px,2vw,24px);align-items:end" data-stagger>{pic(W[3],"f-pill")}{pic(F[4],"f-oval")}{pic(T[1],"f-pill")}{pic(C_[2],"f-oval")}</div>''', "maybe"))

(OUT / "compositions.html").write_text(shell("Photo compositions", "".join(comp),
 '<div class="wrap"><header class="page-hero"><span class="eyebrow">Lab · 01</span><h1>Photographs as <em>design</em>.</h1><p class="lead">Eight composition techniques using authentic LCC photographs. Each is marked Selected, Use sparingly or Not used.</p></header></div>'), encoding="utf-8")


# =====================================================================
# PAGE: Galleries (editorial spread, frames, film strip, wall, collage)
# =====================================================================
g = []
g.append(exp("G0", "The existing gallery", "There is no gallery page in the current build, and every photo slot is a placeholder gradient. This is the baseline we are improving on.",
 '<div class="ph wide" role="img" aria-label="Current placeholder image"><span class="cap">Awaiting LCC-approved photo</span></div>'))

sp = ALL[:]
g.append(exp("G1", "Editorial asymmetric spread", "A magazine spread: one dominant image, five supporting images in different proportions, and an editorial note in the whitespace. Every image opens full screen.",
 f'''<div class="spread">{pic(W[0],"s1","scale")}{pic(F[0],"s2","right",d=.15)}{pic(C_[0],"s3","up",d=.3)}{pic(B[0],"s4","up",d=.45)}{pic(O[0],"s5","left",d=.2)}{pic(Y[0],"s6","left",d=.35)}
 <div class="note"><span class="eyebrow">November 2026</span><h3>A season of celebration</h3><p class="muted">Worship nights, baptisms, the Leaders' Summit and Sundays in the courtyard.</p><span class="cap-line"><b>Photos</b>LCC media team</span></div></div>''', "keep"))

g.append(exp("G3", "Creative frame gallery", "Circles, arches, an organic mask and a tall pill, arranged on a loose 12-column grid. Sizes vary; nothing crops a face.",
 f'''<div class="frames">{pic(W[1],"k1 f-arch","arch")}{pic(F[1],"k2 f-circle","circle",d=.2)}{pic(B[1] if len(B)>1 else B[0],"k3 f-pill","up",d=.35)}{pic(C_[1],"k4 f-organic","organic",d=.15,extra=' style="aspect-ratio:1"')}{pic(O[1] if len(O)>1 else O[0],"k5","left",d=.3,extra=' style="aspect-ratio:16/9;border-radius:var(--r)"')}</div>''', "keep"))

strip_items = (W[:3] + F[:3] + B[:2] + O[:2] + Y[:2] + T[:2])
STRIP = "".join(f'<figure class="">{lb_btn(s,"strip")}<figcaption><b>{e(CATNAME.get(BY[s]["cat"]))}</b>{e(BY[s]["short"])}</figcaption></figure>' for s in dict.fromkeys(strip_items))
g.append(exp("G4", "Film strip", "Drag, swipe or use the arrows. Sprocket marks along the edges, captions under each frame, and a tap opens the photo full screen.",
 f'''</div><div class="strip"><div class="xrail" tabindex="0" aria-label="Moments from the life of LCC (scrollable)">{STRIP}</div><div class="nav-btns"><button class="chip" type="button" data-strip="prev" aria-label="Scroll back">{ARROW_L}</button><button class="chip" type="button" data-strip="next" aria-label="Scroll forward">{ARROW_R}</button></div></div><div class="wrap">''', "keep"))

cats = sorted({BY[s]["cat"] for s in ALL})
chips = '<button class="chip" type="button" data-f="all" aria-pressed="true">All</button>' + "".join(f'<button class="chip" type="button" data-f="{c}" aria-pressed="false">{e(CATNAME.get(c,c))}</button>' for c in cats)
WALL = "".join(lb_btn(s, "wall", w=480) for s in ALL)
g.append(exp("G5", "Immersive photo wall", "A masonry wall that keeps each photo's natural proportions, with category filters, a hover label and a full-screen viewer (arrow keys, swipe, Esc).",
 f'''<div class="filters" data-gallery-filter="wall1" role="group" aria-label="Filter photographs">{chips}<span role="status" class="muted" style="font-size:14px"></span></div><div class="wall" id="wall1" data-stagger>{WALL}</div>''', "keep"))

g.append(exp("G6", "Layered visual collage", "For conference and worship highlights: photos at slight angles over a ringed disc, with small labels. Kept to one per page.",
 f'''<div style="position:relative;min-height:560px;max-width:980px;margin:auto" class="has-bigword"><span class="bigword" aria-hidden="true">Worship</span>
 <div style="position:absolute;left:50%;top:50%;width:420px;aspect-ratio:1;translate:-50% -50%" class="ringed"><div class="f-circle" style="background:var(--sand);width:100%;height:100%;border-radius:50%"></div></div>
 {pic(W[0],"tilt","scale",extra=' style="position:absolute;left:4%;top:6%;width:46%;aspect-ratio:4/3;rotate:-3deg;box-shadow:0 30px 60px -30px rgba(0,0,0,.5);border-radius:3px"')}
 {pic(W[1],"tilt","scale",d=.25,extra=' style="position:absolute;right:4%;top:22%;width:40%;aspect-ratio:3/4;rotate:2.5deg;box-shadow:0 30px 60px -30px rgba(0,0,0,.5);border-radius:3px"')}
 {pic(W[2],"f-circle","circle",d=.5,extra=' style="position:absolute;left:30%;bottom:0;width:26%;border:6px solid var(--paper)"')}
 <span class="cap-line" style="position:absolute;left:4%;bottom:4%"><b>Worship</b>One Accord Ministers</span></div>''', "maybe"))

(OUT / "galleries.html").write_text(shell("Galleries", "".join(g),
 '<div class="wrap"><header class="page-hero"><span class="eyebrow">Lab · 02</span><h1>Galleries that feel <em>curated</em>.</h1><p class="lead">The gallery structures you asked for, built with real LCC photography. G2 (the cinematic slideshow) has its own page.</p></header></div>'), encoding="utf-8")


# =====================================================================
# PAGE: Slideshows
# =====================================================================
hl = (W[:2] + F[:1] + B[:1] + O[:1] + C_[:1])
hl = list(dict.fromkeys(hl))
metas = [(CATNAME.get(BY[s]["cat"]), BY[s]["short"]) for s in hl]
s = []
s.append(exp("S1", "Full-bleed cinematic · crossfade + Ken Burns", "Home and gallery. A 1.2s crossfade with a slow 1.08→1.0 push-in, captions on a soft gradient, a progress bar on the active dot, and pause, keyboard, swipe and full-screen controls.",
 slideshow(hl, "kenburns", label="Highlights from LCC", metas=metas, thumbs=True), "keep", "band-night"))
s.append(exp("S2", "Rounded architectural frame · directional wipe", "About page storytelling. A left-to-right wipe inside an arch-topped frame.",
 f'<div class="duo"><div>{slideshow(F[:4], "wipe", "arch", label="Life at LCC", autoplay=True)}</div><div><span class="eyebrow">Our story in pictures</span><h2>Reconcile. Equip. <em>Transform.</em></h2><p class="lead">A small visual story of a church family on Kariba Street.</p></div></div>', "keep"))
s.append(exp("S3", "Circular mask · iris transition", "Worship section. Each photo opens through a circle (the iris). Captions stay outside the circle so the frame stays clean.",
 f'<div class="duo flip"><div style="max-width:520px">{slideshow(W[:4], "iris", "circle", label="Worship at LCC", interval=5000)}</div><div><span class="eyebrow">Worship</span><h2>Come, let us <em>worship.</em></h2><p class="lead">Praise and worship led by One Accord Ministers.</p></div></div>', "keep"))
s.append(exp("S4", "Asymmetric split · horizontal slide", "Events. Large slide on the left with the event text on the right; the outgoing photo drifts 30% as the next one slides in.",
 f'<div class="duo"><div>{slideshow((O[:2]+Y[:2]), "slide", label="Event photographs", autoplay=False)}</div><div><span class="eyebrow">Events</span><h2>Leaders’ Summit · Coming of Age · Outreach</h2><p class="lead">Recent gatherings captured by the LCC media team.</p></div></div>', "maybe"))
(OUT / "slideshows.html").write_text(shell("Slideshows", "".join(s),
 '<div class="wrap"><header class="page-hero"><span class="eyebrow">Lab · 03</span><h1>Slideshows with a <em>frame</em>.</h1><p class="lead">Four presentations, each matched to its section. All pause on hover or focus and work with the keyboard; swipe works on touch. Reduced motion turns autoplay and zoom off.</p></header></div>'), encoding="utf-8")


# =====================================================================
# PAGE: Motion showcase (12 experiments)
# =====================================================================
m = []
m.append(exp("M1", "Word-by-word headline", "Words rise one by one with a 70 ms stagger. Used for page H1s.",
 '<h2 data-split="words" style="font-size:clamp(40px,6vw,88px);max-width:14ch">A place to <em>celebrate</em> life in Christ.</h2>', "keep"))
m.append(exp("M2", "Character-by-character", "Letters rise with a 2° tilt. Reserved for short display words (2–3 per site).",
 '<h2 data-split="chars" style="font-size:clamp(56px,11vw,170px);line-height:.9">Ablaze.</h2>', "maybe"))
m.append(exp("M3", "Line-by-line mask", "Each line slides up from behind its own mask. For the vision statement and quotes.",
 '<h2 data-split="lines" data-lines="Transforming|<em>nations</em>|for Christ." style="font-size:clamp(48px,8vw,128px);line-height:.95">Transforming nations for Christ.</h2>', "keep"))
m.append(exp("M4", "Circular image reveal", "The photo opens from a point to a full circle while the image settles from 1.12 to 1.",
 f'<div style="max-width:520px;margin:auto">{pic(W[0],"f-circle","circle")}</div>', "keep"))
m.append(exp("M5", "Organic image reveal", "An ellipse grows from off-centre, like light spreading. Used for the youth and fellowship pages.",
 f'<div style="max-width:620px;margin:auto">{pic(Y[0],"f-organic","organic",extra=" style=aspect-ratio:1")}</div>', "maybe"))
m.append(exp("M6", "Cinematic entrance", "Three entrances side by side: a scale-in (1.08→1), blur-to-sharp, and a bottom-up wipe.",
 f'<div style="display:grid;grid-template-columns:repeat(3,1fr);gap:18px">{pic(F[0],"","scale",extra=" style=aspect-ratio:3/4")}{pic(F[1],"","blur",d=.2,extra=" style=aspect-ratio:3/4")}{pic(F[2],"","up",d=.4,extra=" style=aspect-ratio:3/4")}</div>', "keep"))
m.append(exp("M7", "Layered parallax", "The back photo moves at 0.06× and the front at -0.08×, so the layers separate gently. Desktop only; off on mobile and with reduced motion.",
 f'<div style="position:relative;height:620px"><figure class="pic" data-parallax="0.06" style="position:absolute;left:0;top:0;width:62%;height:82%;border-radius:var(--r)">{img(W[1],1600)}</figure><figure class="pic f-arch" data-parallax="-0.08" style="position:absolute;right:4%;bottom:0;width:34%;border:8px solid var(--paper)">{img(C_[0])}</figure></div>', "keep"))
steps = [("01", "Reconcile", "Reconcile people to God through worship, prayer and the preaching of the Word.", W[0]),
         ("02", "Equip", "Equip believers for ministry to God and to people.", T[0]),
         ("03", "Transform", "Carry a transformative agenda into families, Nakuru and the nations.", O[0])]
m.append(exp("M8", "Pinned image-and-text story", "The arch photo stays pinned while three statements scroll past, and the photo crossfades on each step. On mobile this becomes a simple stacked list.",
 '<div class="pinstory"><div class="visual">' + "".join(f'<figure class="pic">{img(sl,1600)}</figure>' for *_, sl in steps) + '</div><div class="steps">'
 + "".join(f'<div class="step"><span class="num">{n}</span><h2 style="font-size:clamp(40px,5vw,72px)">{t}</h2><p class="lead">{d}</p></div>' for n, t, d, _ in steps) + '</div></div>', "keep"))
m.append(exp("M9", "Expanding photograph", "The frame starts inset with rounded corners and grows to full-bleed as you scroll; the heading fades in over it. Desktop only.",
 f'</div><div class="expand"><div class="sticky"><figure class="pic">{img(W[2],1600,sizes="100vw")}</figure><div class="over"><span class="eyebrow" style="color:var(--sun)">Sundays at LCC</span><h2>Come as you are.</h2></div></div></div><div class="wrap">', "keep"))
m.append(exp("M10", "Marquee typography", "A slow horizontal band of words and the verified vision. Pauses on hover; with reduced motion it becomes static, wrapped text.",
 '</div><div class="marquee" aria-label="Transforming Nations for Christ"><div class="track" aria-hidden="true">' + "<span>Transforming Nations for Christ</span><i>✦</i><span>Reconcile</span><i>✦</i><span>Equip</span><i>✦</i><span>Transform</span><i>✦</i>" * 2 + '</div></div><div class="wrap">', "keep"))
m.append(exp("M11", "Scroll-triggered background scene", "The page background eases from paper to night when this band reaches mid-screen, then back afterwards. Used once, before the conference feature.",
 f'<div data-scene="night" style="padding:12vh 0;color:var(--bone)"><p class="ink" style="font:300 clamp(28px,3.6vw,52px)/1.2 var(--serif);max-width:24ch;color:var(--ink);mix-blend-mode:difference">Life Celebration Centre exists to reconcile people to God, equip them for ministry to God and the people, with a transformative agenda.</p></div>', "keep"))
m.append(exp("M12", "Staggered gallery reveal", "Grid items rise in sequence (90 ms apart) as the group enters the viewport.",
 '<div style="display:grid;grid-template-columns:repeat(4,1fr);gap:12px" data-stagger>' + "".join(pic(sl, "", extra=' style="aspect-ratio:1;border-radius:3px"', w=480) for sl in ALL[:8]) + '</div>', "keep"))
m.append(exp("+", "Bonus: scroll-ink statement (Tabor technique)", "Muted words darken as you read, one by one. This is the circles+co Tabor technique, adapted for the mission statement. Readable without JavaScript.",
 '<p class="ink" style="font:300 clamp(30px,4vw,60px)/1.18 var(--serif);letter-spacing:-.02em;max-width:22ch">Life Celebration Centre exists to <em style="color:var(--clay)">reconcile</em> people to God, <em style="color:var(--clay)">equip</em> them for ministry to God and the people, with a <span class="hl">transformative</span> agenda.</p>', "keep"))

(OUT / "motion.html").write_text(shell("Motion showcase", "".join(m),
 '<div class="wrap"><header class="page-hero"><span class="eyebrow">Lab · 04</span><h1 data-split="words">Motion with a <em>purpose</em>.</h1><p class="lead">The 12 requested experiments, plus the Tabor scroll-ink technique. Scroll slowly. With “reduce motion” switched on in your device settings, everything appears instantly and nothing moves.</p></header></div>'), encoding="utf-8")


# =====================================================================
# PAGE: Mobile previews
# =====================================================================
frames = [("compositions.html", "Compositions"), ("galleries.html", "Galleries"), ("slideshows.html", "Slideshows"), ("motion.html", "Motion")]
mob = '<div class="wrap" style="display:flex;gap:28px;overflow-x:auto;padding-bottom:40px">' + "".join(
    f'<div style="flex:0 0 auto"><p class="eyebrow">{t} · 390 px</p><iframe src="{h}" title="{t} at 390 pixels" style="width:390px;height:780px;border:10px solid var(--ink);border-radius:36px;background:var(--paper)" loading="lazy"></iframe></div>' for h, t in frames) + '</div>'
(OUT / "mobile.html").write_text(shell("Mobile", mob,
 '<div class="wrap"><header class="page-hero"><span class="eyebrow">Lab · 05</span><h1>Built for the <em>phone</em> first.</h1><p class="lead">Live pages at 390 px. Mobile gets shorter reveals, no parallax, no pinned sections, and stacked compositions with faces kept in frame.</p></header></div>'), encoding="utf-8")


# =====================================================================
# PAGE: Photo library (register)
# =====================================================================
rows = "".join(f'<tr><td style="width:120px">{img(p["slug"],480,sizes="120px")}</td><td><b>{e(p["slug"])}</b><br><small class="muted">{e(p["alt"])}</small></td><td>{e(CATNAME.get(p["cat"],p["cat"]))}</td><td>16:9</td><td>1280×720 frame</td><td>{e(p["short"])}</td><td>{e(p["source"])}</td><td><a href="{e(p["video"])}" rel="noopener" target="_blank">Video</a></td></tr>' for p in LIB)
lib = f'<section class="sec"><div class="wrap"><div style="overflow-x:auto"><table class="programme" style="min-width:960px"><thead><tr><th>Photo</th><th>File · description</th><th>Category</th><th>Original</th><th>Quality</th><th>Placement</th><th>Source</th><th>Watch</th></tr></thead><tbody>{rows}</tbody></table></div></div></section>'
(OUT / "photo-library.html").write_text(shell("Photo library", lib,
 f'<div class="wrap"><header class="page-hero"><span class="eyebrow">Lab · 06</span><h1>The photo <em>library</em>.</h1><p class="lead">{len(LIB)} photographs curated from LCC’s own YouTube streams (three frames per video, 65 videos reviewed). Each is linked to its video. The 154 Facebook photographs stay out until the LCC media team approves them.</p></header></div>'), encoding="utf-8")
print("lab written:", sorted(x.name for x in OUT.glob("*.html")))

# =====================================================================
# PAGE: Lab overview
# =====================================================================
rows = [("Compositions", "compositions.html", "Arch hero, overlapping circles, ringed portrait, organic masks, layered collage, double-line arch, offset frame, pill/oval",
         "Used: arch hero (Home), arch (Home ministries), ringed medallion (Leadership), offset/arch/pill frames (Ministries), layered collage (Conference 2026)"),
        ("Galleries", "galleries.html", "Editorial spread, frame gallery, film strip, photo wall + lightbox, layered collage",
         "Used on Gallery: editorial spread, film strip with full-screen viewer, stream-moments collage. Others stay in the lab (the brief asks for fewer images)."),
        ("Slideshows", "slideshows.html", "Ken Burns crossfade, arch wipe, circular iris, split slide",
         "Used: About hero slideshow (existing v2). Others kept as options."),
        ("Motion", "motion.html", "12 experiments + scroll-ink",
         "Used: word/line reveals on headings, clip/arch/circle image reveals, scroll-ink mission, expanding photo (Visit), staggered lists. Marquee, parallax and pinned story kept in the lab only."),
        ("Mobile", "mobile.html", "390 px live previews", "Mobile gets shorter reveals, no parallax or pinning, and photo-first heroes.")]
ov = '<section class="sec"><div class="wrap"><table class="programme"><thead><tr><th>Area</th><th>What you can inspect</th><th>Production decision</th></tr></thead><tbody>' + "".join(
    f'<tr><td><a href="{h}"><b>{t}</b></a></td><td>{d}</td><td>{u}</td></tr>' for t, h, d, u in rows) + '</tbody></table></div></section>'
(OUT / "index.html").write_text(shell("Overview", ov,
 '<div class="wrap"><header class="page-hero"><span class="eyebrow">LCC Design Lab</span><h1 data-split="words">Every technique, <em>tested.</em></h1><p class="lead">Working experiments with LCC’s own photography. The live site uses only the strongest few, so pages stay calm and fast.</p></header></div>'), encoding="utf-8")
print("lab index written")
