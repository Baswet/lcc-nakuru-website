#!/usr/bin/env python3
"""Build the LCC static site from data/content.json.

Usage:  python3 tools/build.py            (writes *.html, sitemap.xml, robots.txt in the site root)
Only facts in content.json are published. Unverified items carry "verified": false and render as "to be confirmed".
"""
import json, html, datetime, pathlib, re

ROOT = pathlib.Path(__file__).resolve().parent.parent
C = json.loads((ROOT / "data/content.json").read_text(encoding="utf-8"))
S, CT, SO = C["site"], C["contact"], C["social"]
BASE = S["url"].rstrip("/") + "/"
TODAY = datetime.date.today().isoformat()
e = lambda s: html.escape(str(s or ""), quote=True)

NAV = [("about.html", "About"), ("ministries.html", "Ministries"), ("sermons.html", "Sermons"),
       ("events.html", "Events"), ("give.html", "Give"), ("contact.html", "Contact")]

MARK = ('<svg class="brand-mark" viewBox="0 0 48 48" aria-hidden="true"><circle cx="24" cy="24" r="23" fill="#1E1A16"/>'
        '<path d="M24 9v30M15 18h18" stroke="#F6F1E8" stroke-width="3" stroke-linecap="round"/>'
        '<path d="M9 35c5-4 10-6 15-6s10 2 15 6" stroke="#D49A2F" stroke-width="2.5" fill="none" stroke-linecap="round"/></svg>')

CONTOUR = ('<svg viewBox="0 0 400 500" preserveAspectRatio="none" aria-hidden="true"><g fill="none" stroke="#FFF5E8" stroke-width="1.2">'
           + "".join(f'<path d="M-20 {300+i*18} C 80 {250+i*14}, 160 {330+i*10}, 240 {280+i*16} S 380 {300+i*12}, 430 {270+i*18}"/>' for i in range(10))
           + '<circle cx="300" cy="120" r="46"/><circle cx="300" cy="120" r="30"/></g></svg>')


def ph(caption="Awaiting LCC-approved photo", cls=""):
    return f'<div class="ph {cls}" role="img" aria-label="Placeholder image: {e(caption)}">{CONTOUR}<span class="cap" aria-hidden="true">{e(caption)}</span></div>'


def video_card(v, lazy=True, h="h3"):
    vid = e(v["id"])
    meta = " · ".join(x for x in [v.get("speaker"), {"sermon": "Message", "worship": "Worship", "conference": "Conference", "story": "Story"}.get(v.get("category"), "")] if x)
    return (f'<figure class="video" data-cat="{e(v.get("category"))}" data-title="{e((v["title"]+" "+v.get("speaker","")).lower())}">'
            f'<div class="frame"><img src="https://i.ytimg.com/vi/{vid}/hqdefault.jpg" alt="" width="480" height="360" loading="{"lazy" if lazy else "eager"}" decoding="async">'
            f'<button class="play" type="button" data-yt="{vid}" aria-label="Play video: {e(v["title"])}"></button></div>'
            f'<figcaption><b>{e(v["title"])}</b><small>{e(meta)}</small></figcaption></figure>')


def vids(ids):
    by = {v["id"]: v for v in C["videos"]}
    return [by[i] for i in ids if i in by]


def fmt_range(a, b):
    da, db = datetime.date.fromisoformat(a), datetime.date.fromisoformat(b)
    return f"{da.day} {da:%b} – {db.day} {db:%b %Y}"


def event_row(ev):
    d = datetime.date.fromisoformat(ev["start"])
    ext = f' <a class="btn btn-clay" href="{e(ev["external"])}" rel="noopener" target="_blank">Register<span class="sr-only"> (opens official conference site)</span></a>' if ev.get("external") else ""
    return (f'<article class="event"><div class="date">{d.day}<small>{d:%b %Y}</small></div>'
            f'<div><h3><a href="{e(ev.get("url","#"))}">{e(ev["title"])}</a></h3><p class="muted mt0">{e(fmt_range(ev["start"], ev["end"]))} · {e(ev["place"])}</p><p class="mt0">{e(ev["summary"])}</p></div>'
            f'<div>{ext}</div></article>')


def services_html():
    sv = C["services"]
    items = "".join(f'<div class="card"><span class="kind">{e(i["day"])}</span><h3>{e(i["name"])}</h3><p class="mt0"><b>{e(i["time"])}</b>{" <span class=tbc>To be confirmed</span>" if not sv["verified"] else ""}</p><p class="muted">{e(i["detail"])}</p></div>' for i in sv["items"])
    note = "" if sv["verified"] else f'<div class="notice"><b>Service times are being confirmed</b>{e(sv["note"])}</div>'
    return f'<div class="cards" data-cms="services">{items}</div>{note}'


def giving_html():
    g = C["giving"]
    if g.get("verified") and g.get("mpesa_paybill"):
        return (f'<div class="give-card" data-cms="giving"><span class="eyebrow">M-Pesa</span><h3>Paybill {e(g["mpesa_paybill"])}</h3>'
                f'<p>Account: <b>{e(g["mpesa_account"])}</b></p><p class="muted">Confirmed by the LCC church office.</p></div>')
    return (f'<div class="notice" data-cms="giving"><b>Giving details are being confirmed</b>{e(g["note"])}'
            f' <a href="tel:{e(CT["phone_intl"])}">Call {e(CT["phone"])}</a></div>')


def notice_html():
    n = C.get("notice", {})
    if not n.get("show"):
        return ""
    return f'<aside class="noticebar" aria-label="Announcement" data-cms="notice"><a href="{e(n["link"])}">{e(n["text"])} →</a></aside>'


def jsonld_org():
    return {"@context": "https://schema.org", "@type": ["Church", "PlaceOfWorship"], "@id": BASE + "#church",
            "name": S["org"], "alternateName": [S["name"], S["short"]], "url": BASE, "telephone": CT["phone_intl"],
            "email": CT["email"], "slogan": S["vision"], "description": S["mission"],
            "address": {"@type": "PostalAddress", "streetAddress": CT["street"], "addressLocality": CT["city"], "addressCountry": CT["country"], "postOfficeBoxNumber": "2758-20100"},
            "sameAs": [SO["youtube"], SO["facebook"], SO["instagram"]],
            "employee": [{"@type": "Person", "name": "Rev. Elijah Mwangi", "jobTitle": "Lead Pastor"}]}


def page(slug, title, desc, body, current=None, extra_ld=None, hero_img=None):
    canon = BASE if slug == "index.html" else BASE + slug
    full_title = title if slug == "index.html" else f"{title} | {S['name']} (LCC) Nakuru"
    nav = "".join(f'<a href="{h}"{" aria-current=page" if h == current else ""}>{t}</a>' for h, t in NAV)
    lds = [jsonld_org()] + (extra_ld or [])
    ld = "\n".join(f'<script type="application/ld+json">{json.dumps(x, ensure_ascii=False)}</script>' for x in lds)
    og_img = hero_img or BASE + "assets/img/og-image.png"
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
<meta property="og:image" content="{og_img}">
<meta property="og:locale" content="{S['locale']}">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="assets/img/favicon.svg" type="image/svg+xml">
<link rel="preload" href="assets/fonts/fraunces-latin-wght-normal.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="assets/fonts/inter-tight-latin-wght-normal.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="assets/css/site.css">
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
   <a class="watch" href="{e(SO['youtube_live'])}" rel="noopener" target="_blank">Watch online<span class="sr-only"> (opens YouTube)</span></a>
   {nav}
   <a class="btn btn-solid" href="visit.html"{" aria-current=page" if current == "visit.html" else ""}>Plan your visit</a>
  </nav>
 </div>
</header>
<main id="main" tabindex="-1">
{body}
</main>
<footer class="site-footer">
 <div class="wrap">
  <div class="foot-top">
   <div><h2>{e(S['vision'])}.</h2><p style="color:#C9BDAF;max-width:36ch">{e(S['org'])}</p></div>
   <div><h3>Visit</h3><ul><li>{e(CT['street'])}</li><li>{e(CT['city'])}, Kenya</li><li>{e(CT['postal'])}</li><li><a href="https://www.google.com/maps/search/?api=1&amp;query={e(CT['maps_query']).replace(' ','+')}" rel="noopener" target="_blank">Open in Google Maps</a></li></ul></div>
   <div><h3>Contact</h3><ul><li><a href="tel:{e(CT['phone_intl'])}">{e(CT['phone'])}</a></li><li><a href="mailto:{e(CT['email'])}">{e(CT['email'])}</a></li><li><a href="contact.html#prayer">Send a prayer request</a></li></ul></div>
   <div><h3>Follow</h3><ul><li><a href="{e(SO['youtube'])}" rel="noopener" target="_blank">YouTube</a></li><li><a href="{e(SO['facebook'])}" rel="noopener" target="_blank">Facebook</a></li><li><a href="{e(SO['instagram'])}" rel="noopener" target="_blank">Instagram</a></li><li><a href="{e(C['conference']['site'])}" rel="noopener" target="_blank">Cutting Edge Conference</a></li></ul></div>
  </div>
  <div class="foot-bottom"><span>© {datetime.date.today().year} {e(S['org'])}</span><span><a href="privacy.html">Privacy</a> · <a href="news.html">News</a> · <a href="leadership.html">Leadership</a></span></div>
 </div>
</footer>
<script src="assets/js/site.js" defer></script>
</body>
</html>
"""


# ---------------------------------------------------------------- pages
P = {}
latest = [v for v in C["videos"] if v["category"] == "sermon"][:5]
conf = C["conference"]

P["index.html"] = page("index.html", f"{S['name']} (LCC) Nakuru — Deliverance Church International",
    "Deliverance Church International – Life Celebration Centre (LCC) on General Kariba Street, Nakuru. Transforming Nations for Christ. Plan your visit, watch sermons and join the Cutting Edge Conference.",
f"""
<div class="wrap">
 <section class="hero">
  <div>
   <span class="eyebrow">{e(S['vision'])}</span>
   <h1>A place to <em>celebrate</em> life in Christ.</h1>
   <p class="lead">Life Celebration Centre exists to reconcile people to God and equip them for ministry — right here on General Kariba Street, Nakuru.</p>
   <div class="actions"><a class="btn btn-solid" href="visit.html">Plan your visit</a><a class="btn" href="sermons.html">Watch a message</a></div>
  </div>
  {ph()}
 </section>
 <div class="facts">
  <div><small>Sundays</small><b>Worship services</b><a href="visit.html">Service times →</a></div>
  <div><small>Where</small><b>Kariba Street, Freehold</b><a href="visit.html#find-us">Directions →</a></div>
  <div><small>Online</small><b>YouTube &amp; Facebook</b><a href="{e(SO['youtube_live'])}" rel="noopener" target="_blank">Watch online →</a></div>
  <div><small>30 Mar – 4 Apr 2027</small><b>Cutting Edge</b><a href="conference.html">Conference →</a></div>
 </div>
</div>

<section class="sec">
 <div class="wrap">
  <div class="sec-head"><div><span class="eyebrow">Next steps</span><h2>Where would you like to <em>begin?</em></h2></div></div>
  <div class="intents">
   <a class="intent t-ochre" href="visit.html"><b>I'm new and want to visit</b><span>Plan your visit →</span></a>
   <a class="intent t-flamingo" href="contact.html#prayer"><b>I'd like someone to pray with me</b><span>Send a private request →</span></a>
   <a class="intent" href="ministries.html"><b>I want to serve and belong</b><span>Explore ministries →</span></a>
   <a class="intent t-sand" href="give.html"><b>I want to give</b><span>Ways to give →</span></a>
  </div>
 </div>
</section>

<section class="sec band-night" aria-labelledby="watch-h">
 <div class="wrap">
  <div class="sec-head"><div><span class="eyebrow">Watch &amp; worship</span><h2 id="watch-h">Latest messages from LCC</h2></div><a class="btn btn-ghost-light" href="sermons.html">All sermons &amp; worship</a></div>
  <div class="videos feature">{video_card(latest[0], lazy=False)}{video_card(latest[1])}{video_card(latest[2])}</div>
 </div>
</section>

<section class="sec" aria-labelledby="about-h">
 <div class="wrap split wide-left">
  <div>
   <span class="eyebrow">Who we are</span>
   <h2 id="about-h">Reconcile. Equip. <em>Transform.</em></h2>
   <p class="lead" style="max-width:52ch">“{e(S['mission'])}”</p>
   <p class="mt2"><a class="btn" href="about.html">About LCC</a></p>
  </div>
  <div class="card"><span class="kind">Lead Pastor</span><h3>Rev. Elijah Mwangi</h3><p class="muted">Leads Life Celebration Centre and convenes the annual Cutting Edge Conference.</p><a href="leadership.html">Meet our leadership →</a></div>
 </div>
</section>

<section class="sec band-night" aria-labelledby="conf-h">
 <div class="wrap conf">
  <div>
   <span class="eyebrow">Featured event</span>
   <h2 id="conf-h">Cutting Edge Conference <em style="color:var(--sun)">2027</em></h2>
   <p class="lead">Theme: <b style="color:var(--bone)">{e(conf['theme'])}</b>. Six days of evangelism, teaching and preaching in Nakuru.</p>
   <div class="conf-dates"><div><small>Dates</small><b>{e(conf['dates'])}</b></div><div><small>Venue</small><b>LCC, Freehold, Nakuru</b></div></div>
   <p class="mt2" style="display:flex;gap:12px;flex-wrap:wrap"><a class="btn btn-sun" href="{e(conf['register'])}" rel="noopener" target="_blank">Register on the official site</a><a class="btn btn-ghost-light" href="conference.html">Programme &amp; speakers</a></p>
  </div>
  <div class="speakers">{''.join(f'<div class="speaker"><div class="initials" aria-hidden="true">{e("".join(w[0] for w in s["name"].replace("Rev. ","").replace("Bishop ","").split()[:2]))}</div><b>{e(s["name"])}</b><small>{e(s["from"])}</small></div>' for s in conf['speakers'])}</div>
 </div>
</section>

<section class="sec" aria-labelledby="news-h">
 <div class="wrap">
  <div class="sec-head"><div><span class="eyebrow">News &amp; stories</span><h2 id="news-h">Life together at LCC</h2></div><a class="btn" href="news.html">All news</a></div>
  <div class="cards" data-cms="news-home">{''.join(f'<article class="card"><span class="kind">{e(n["date"])}</span><h3>{e(n["title"])}</h3><p class="muted">{e(n["summary"])}</p></article>' for n in C['news'][:3])}</div>
 </div>
</section>
""", current=None)

P["about.html"] = page("about.html", "About LCC", "About Deliverance Church International – Life Celebration Centre, Nakuru: our vision, mission and what we believe.",
f"""
<div class="wrap"><header class="page-hero"><span class="eyebrow">About LCC</span><h1>{e(S['vision'])}.</h1><p class="lead">Life Celebration Centre (LCC) is a congregation of Deliverance Church International on General Kariba Street in Freehold, Nakuru.</p></header></div>
<section class="sec"><div class="wrap split">
 <div><span class="eyebrow">Our vision</span><h2>{e(S['vision'])}</h2><p class="muted">Our vision is shared on our official YouTube and Facebook pages.</p></div>
 <div><span class="eyebrow">Our mission</span><p style="font:400 clamp(22px,2.4vw,30px)/1.35 var(--serif)">“{e(S['mission'])}”</p></div>
</div></section>
<section class="sec bg-sand"><div class="wrap">
 <span class="eyebrow">What that looks like</span><h2>Three movements</h2>
 <div class="cards mt2">
  <div class="card"><span class="kind">01</span><h3>Reconcile people to God</h3><p class="muted">Through worship, the preaching of the Word and evangelism in Nakuru and beyond.</p></div>
  <div class="card"><span class="kind">02</span><h3>Equip for ministry</h3><p class="muted">Raising believers who minister to God and to people, including through the annual Cutting Edge Conference.</p></div>
  <div class="card"><span class="kind">03</span><h3>A transformative agenda</h3><p class="muted">Faith that shapes families, the city and the nations.</p></div>
 </div>
</div></section>
<section class="sec"><div class="wrap split">
 <div><span class="eyebrow">Our story</span><h2>A story still being written</h2>
 <div class="notice"><b>History being prepared with the church office</b>We will publish LCC's history — its founding, milestones and the journey to Freehold — once the church office has confirmed the details. We would rather wait than get it wrong.</div>
 <p>LCC is part of <b>Deliverance Church International</b>, a Kenyan church family with congregations across the country.</p></div>
 {ph("Awaiting LCC-approved photo of the sanctuary", "wide")}
</div></section>
""", current="about.html")

lead = C["leadership"][0]
P["leadership.html"] = page("leadership.html", "Leadership", "Leadership at Life Celebration Centre (LCC) Nakuru, led by Lead Pastor Rev. Elijah Mwangi.",
f"""
<div class="wrap"><header class="page-hero"><span class="eyebrow">Leadership</span><h1>Shepherds who serve.</h1></header></div>
<section class="sec"><div class="wrap split">
 {ph("Awaiting approved portrait of Rev. Elijah Mwangi")}
 <div><span class="eyebrow">{e(lead['role'])}</span><h2>{e(lead['name'])}</h2><p class="lead" style="max-width:none">{e(lead['bio'])}</p>
 <p class="mt2"><a class="btn" href="sermons.html">Watch his messages</a></p></div>
</div></section>
<section class="sec bg-sand"><div class="wrap prose">
 <span class="eyebrow">Pastoral team</span><h2>More of our team, coming soon</h2>
 <p>Profiles of LCC's pastors, elders and ministry leaders will be added once confirmed by the church office. For pastoral care today, please <a href="contact.html">contact the church office</a>.</p>
</div></section>
""", current="about.html")

P["ministries.html"] = page("ministries.html", "Ministries", "Ministries at LCC Nakuru: One Accord Ministers worship, Youth Ablaze, Morning Devotion, CityAnnex and the Cutting Edge Conference.",
f"""
<div class="wrap"><header class="page-hero"><span class="eyebrow">Ministries</span><h1>Find your place to <em>belong</em> and serve.</h1><p class="lead">These are ministries we share publicly in our life together. Full details and contacts for each are being confirmed with the church office.</p></header></div>
<section class="sec"><div class="wrap"><h2 class="sr-only">Our ministries</h2><div class="cards">
{''.join(f'<article class="card"><span class="kind">{e(m["kind"])}</span><h3>{e(m["name"])}</h3><p class="muted">{e(m["text"])}</p>' + (f'<a href="{e(m["link"])}">Learn more →</a>' if m.get("link") else '') + '</article>' for m in C['ministries'])}
</div>
<div class="notice mt4"><b>Want to get involved?</b>Ask at the welcome desk on Sunday, or <a href="contact.html">send us a message</a> telling us where you'd like to serve.</div>
</div></section>
<section class="sec band-night"><div class="wrap"><div class="sec-head"><div><span class="eyebrow">One Accord Ministers</span><h2>Worship from LCC</h2></div></div>
<div class="videos">{''.join(video_card(v) for v in [x for x in C['videos'] if x['category']=='worship'][:3])}</div></div></section>
""", current="ministries.html")

faqs = [("What time are services?", "Sunday service times are being confirmed for this website. Please call the church office on " + CT["phone"] + " before your first visit, or check our Facebook page for the latest announcements."),
        ("Where do I park?", "Parking details will be added once confirmed by the church office. Our ushers are happy to help when you arrive."),
        ("What should I wear?", "Come as you are. You'll see everything from Sunday best to casual wear."),
        ("Is there something for my children?", "Please ask the welcome team on arrival about children's ministry during the service."),
        ("Can I watch online first?", "Yes. Services and messages are shared on our YouTube channel and Facebook page.")]
P["visit.html"] = page("visit.html", "Plan your visit", "Plan your first visit to Life Celebration Centre, General Kariba Street, Freehold, Nakuru: service times, directions and what to expect.",
f"""
<div class="wrap"><header class="page-hero"><span class="eyebrow">Plan your visit</span><h1>We'd love to <em>welcome</em> you.</h1><p class="lead">Here's everything you need for your first Sunday at LCC.</p></header></div>
<section class="sec"><div class="wrap"><span class="eyebrow">Gatherings</span><h2>When we meet</h2>{services_html()}</div></section>
<section class="sec bg-sand" id="find-us"><div class="wrap split">
 <div><span class="eyebrow">Find us</span><h2>General Kariba Street, Freehold, Nakuru</h2><p>{e(CT['postal'])}</p>
 <p class="mt2" style="display:flex;gap:12px;flex-wrap:wrap"><a class="btn btn-solid" href="https://www.google.com/maps/search/?api=1&amp;query={e(CT['maps_query']).replace(' ','+')}" rel="noopener" target="_blank">Open in Google Maps</a><a class="btn" href="tel:{e(CT['phone_intl'])}">Call {e(CT['phone'])}</a></p></div>
 {ph("Awaiting approved photo of the LCC entrance", "wide ochre")}
</div></section>
<section class="sec"><div class="wrap split">
 <div><span class="eyebrow">What to expect</span><h2>Your first Sunday</h2><p>Expect heartfelt worship, prayer and a message from the Bible. Our ushers will help you find a seat. There's no pressure to give or to stand up — simply come and be with us.</p></div>
 <div>{''.join(f'<details><summary>{e(q)}</summary><p>{e(a)}</p></details>' for q, a in faqs)}</div>
</div></section>
""", current="visit.html", extra_ld=[{"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faqs]}])

P["sermons.html"] = page("sermons.html", "Sermons & media", "Watch sermons by Rev. Elijah Mwangi, worship by One Accord Ministers and Cutting Edge Conference sessions from LCC Nakuru.",
f"""
<div class="wrap"><header class="page-hero"><span class="eyebrow">Sermons &amp; media</span><h1>Watch, listen and <em>grow.</em></h1><p class="lead">Messages, worship and conference sessions from our YouTube channel. Videos load only when you press play, which saves your data.</p>
<p><a class="btn btn-clay" href="{e(SO['youtube_live'])}" rel="noopener" target="_blank">Watch live services on YouTube</a></p></header></div>
<section class="sec"><div class="wrap">
 <div class="filters" role="group" aria-label="Filter videos">
  <button class="chip" type="button" data-filter="all" aria-pressed="true">All</button>
  <button class="chip" type="button" data-filter="sermon" aria-pressed="false">Messages</button>
  <button class="chip" type="button" data-filter="worship" aria-pressed="false">Worship</button>
  <button class="chip" type="button" data-filter="conference" aria-pressed="false">Conference</button>
  <label class="sr-only" for="q">Search videos</label><input class="search" id="q" type="search" placeholder="Search by title or speaker">
 </div>
 <p class="sr-only" aria-live="polite" id="count"></p>
 <div class="videos" id="library" data-cms="videos">{''.join(video_card(v) for v in C['videos'])}</div>
 <p class="empty" id="empty" hidden>No videos match that search.</p>
 <p class="mt4 center"><a class="btn" href="{e(SO['youtube'])}" rel="noopener" target="_blank">See everything on YouTube</a></p>
</div></section>
""", current="sermons.html", extra_ld=[{"@context": "https://schema.org", "@type": "ItemList", "itemListElement": [
    {"@type": "ListItem", "position": i + 1, "item": {"@type": "VideoObject", "name": v["full_title"], "thumbnailUrl": f"https://i.ytimg.com/vi/{v['id']}/hqdefault.jpg", "embedUrl": f"https://www.youtube-nocookie.com/embed/{v['id']}", "contentUrl": f"https://www.youtube.com/watch?v={v['id']}", "description": v["full_title"] + " — Life Celebration Centre, Nakuru", "uploadDate": "2026-01-01" if False else None}} for i, v in enumerate(C["videos"][:10])]}])

ev_ld = [{"@context": "https://schema.org", "@type": "Event", "name": ev["title"], "startDate": ev["start"], "endDate": ev["end"],
          "eventStatus": "https://schema.org/EventScheduled", "eventAttendanceMode": "https://schema.org/OfflineEventAttendanceMode",
          "location": {"@type": "Place", "name": "Deliverance Church LCC", "address": {"@type": "PostalAddress", "streetAddress": "Kariba Road, Freehold", "addressLocality": "Nakuru", "addressCountry": "KE"}},
          "organizer": {"@type": "Organization", "name": S["org"], "url": BASE}, "description": ev["summary"], "url": ev.get("external") or BASE + ev["url"]} for ev in C["events"]]

P["events.html"] = page("events.html", "Events", "Upcoming events at Life Celebration Centre (LCC) Nakuru, including the Cutting Edge Conference 2027.",
f"""
<div class="wrap"><header class="page-hero"><span class="eyebrow">Events</span><h1>What's <em>coming up.</em></h1><p class="lead">Weekly announcements are shared on our <a href="{e(SO['facebook'])}" rel="noopener" target="_blank">Facebook page</a>. Major events are listed here.</p></header></div>
<section class="sec"><div class="wrap" data-cms="events"><h2 class="sr-only">Upcoming events</h2>{''.join(event_row(ev) for ev in sorted(C['events'], key=lambda x: x['start']))}</div></section>
""", current="events.html", extra_ld=ev_ld)

P["conference.html"] = page("conference.html", "Cutting Edge Conference 2027", "Cutting Edge Conference 2027, 30 March – 4 April 2027 at LCC Nakuru. Theme: Commissioning for the Global Mission. Speakers, programme and official registration.",
f"""
<section class="band-night"><div class="wrap" style="padding-top:clamp(48px,8vw,110px);padding-bottom:clamp(48px,7vw,90px)">
 <span class="eyebrow">{e(conf['dates'])} · Nakuru</span>
 <h1 style="color:var(--bone);max-width:14ch">Cutting Edge Conference <em style="color:var(--sun)">2027</em></h1>
 <p class="lead" style="max-width:48ch">Theme: <b style="color:var(--bone)">{e(conf['theme'])}</b>. Hosted by Deliverance Church – Life Celebration Centre and convened by Rev. Elijah Mwangi.</p>
 <p class="mt2" style="display:flex;gap:12px;flex-wrap:wrap"><a class="btn btn-sun" href="{e(conf['register'])}" rel="noopener" target="_blank">Register as a delegate</a><a class="btn btn-ghost-light" href="{e(conf['volunteer'])}" rel="noopener" target="_blank">Volunteer</a><a class="btn btn-ghost-light" href="{e(conf['partner'])}" rel="noopener" target="_blank">Partner</a></p>
 <p class="muted" style="font-size:14px">Registration, volunteering and partnership are handled on the official conference website, cuttingedgeconference.co.ke.</p>
</div></section>
<section class="sec"><div class="wrap split">
 <div><span class="eyebrow">Programme</span><h2>Six days</h2>
 <table class="programme"><thead><tr><th scope="col">Day</th><th scope="col">Time</th><th scope="col">Focus</th></tr></thead><tbody>
 {''.join(f'<tr><td>{e(p["day"])}</td><td>{e(p["time"])}</td><td>{e(p["what"])}</td></tr>' for p in conf['programme'])}
 </tbody></table>
 <p class="muted mt2">Delegate options: {e(' · '.join(conf['options']))}. See the official site for fees and the full session list.</p></div>
 <div><span class="eyebrow">Speakers</span><h2>Ministering</h2>
 <div class="cards two">{''.join(f'<div class="card"><h3>{e(s["name"])}</h3><p class="muted">{e(s["from"])}</p></div>' for s in conf['speakers'])}</div></div>
</div></section>
<section class="sec band-night"><div class="wrap"><div class="sec-head"><div><span class="eyebrow">From past conferences</span><h2>Being on the cutting edge</h2></div></div>
<div class="videos">{''.join(video_card(v) for v in vids(conf['videos']))}</div></div></section>
<section class="sec"><div class="wrap prose"><span class="eyebrow">Questions</span><h2>Contact the conference team</h2>
<p>Email <a href="mailto:{e(conf['email'])}">{e(conf['email'])}</a> or call <a href="tel:+254722864864">{e(conf['phone'])}</a>.</p></div></section>
""", current="events.html", extra_ld=ev_ld[:1])

P["news.html"] = page("news.html", "News & stories", "News and stories from Life Celebration Centre (LCC) Nakuru.",
f"""
<div class="wrap"><header class="page-hero"><span class="eyebrow">News &amp; stories</span><h1>Stories of <em>life</em> together.</h1></header></div>
<section class="sec"><div class="wrap" data-cms="news">
{''.join(f'<article class="split wide-left" style="padding:32px 0;border-top:1px solid var(--line)" id="{e(n["slug"])}"><div><span class="eyebrow">{e(n["date"])}</span><h2 style="font-size:clamp(28px,3vw,40px)">{e(n["title"])}</h2><p class="muted">{e(n["summary"])}</p>' + (f'<a href="{e(n["link"])}">Read more →</a>' if n.get("link") else '') + '</div><div>' + (video_card(vids([n["video"]])[0]) if n.get("video") and vids([n["video"]]) else '') + '</div></article>' for n in C['news'])}
</div></section>
""", current=None)

P["give.html"] = page("give.html", "Give", "Give to Life Celebration Centre (LCC) Nakuru. Verified giving details are published after confirmation by the church office.",
f"""
<div class="wrap"><header class="page-hero"><span class="eyebrow">Give</span><h1>Generosity that <em>transforms.</em></h1><p class="lead">Your giving supports worship, outreach, discipleship and the work of transforming nations for Christ.</p></header></div>
<section class="sec"><div class="wrap">
 <h2 class="sr-only">Ways to give</h2>
 <div class="give-grid">
  <div class="give-card"><span class="eyebrow">In person</span><h3>During any service</h3><p class="muted">Give your tithes and offerings during our Sunday services.</p></div>
  <div class="give-card"><span class="eyebrow">M-Pesa</span><h3>Mobile giving</h3>{giving_html()}</div>
  <div class="give-card"><span class="eyebrow">Questions</span><h3>Talk to the office</h3><p class="muted">For pledges, projects or receipts, call <a href="tel:{e(CT['phone_intl'])}">{e(CT['phone'])}</a>.</p></div>
 </div>
 <div class="notice mt4"><b>Stay safe</b>LCC will only ever publish giving numbers on this page and from the church office. If someone sends you a different number claiming to be LCC, please call the office to confirm before sending money.</div>
</div></section>
""", current="give.html")

P["contact.html"] = page("contact.html", "Contact & prayer", "Contact Life Celebration Centre (LCC) Nakuru: phone 0722 864 864, General Kariba Street, Nakuru. Send a private prayer request.",
f"""
<div class="wrap"><header class="page-hero"><span class="eyebrow">Contact</span><h1>We're <em>here</em> for you.</h1></header></div>
<section class="sec"><div class="wrap split">
 <div>
  <span class="eyebrow">Church office</span><h2>Get in touch</h2>
  <p><b>Phone</b><br><a href="tel:{e(CT['phone_intl'])}">{e(CT['phone'])}</a></p>
  <p><b>Email</b><br><a href="mailto:{e(CT['email'])}">{e(CT['email'])}</a></p>
  <p><b>Visit</b><br>{e(CT['street'])}, {e(CT['city'])}<br>{e(CT['postal'])}</p>
  <p><b>Online</b><br><a href="{e(SO['facebook'])}" rel="noopener" target="_blank">Facebook</a> · <a href="{e(SO['youtube'])}" rel="noopener" target="_blank">YouTube</a> · <a href="{e(SO['instagram'])}" rel="noopener" target="_blank">Instagram</a></p>
 </div>
 <div>
  <div class="tabs" role="group" aria-label="Choose a form"><a class="chip" href="#message" style="display:inline-flex;align-items:center;text-decoration:none">Send a message</a><a class="chip" href="#prayer" style="display:inline-flex;align-items:center;text-decoration:none">Prayer request</a></div>
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
   <div class="field"><label for="p-reply">Email or phone <span class="muted">(optional, if you'd like a call back)</span></label><input id="p-reply" name="reply" maxlength="120"></div>
   <div class="field"><label for="p-msg">How can we pray for you?</label><textarea id="p-msg" name="message" required maxlength="3000"></textarea></div>
   <div class="check"><input type="checkbox" id="p-ok" name="consent" value="1" required><label for="p-ok">I agree that the LCC pastoral team may read this request and contact me if I gave my details.</label></div>
   <div class="hp" aria-hidden="true"><label for="p-web">Website</label><input id="p-web" name="website" tabindex="-1" autocomplete="off"></div>
   <button class="btn btn-clay" type="submit">Send prayer request</button>
   <div class="form-status" role="status" aria-live="polite"></div>
  </form>
 </div>
</div></section>
""", current="contact.html")

P["privacy.html"] = page("privacy.html", "Privacy notice", "How the LCC Nakuru website handles your information, prayer requests, cookies and YouTube embeds.",
f"""
<div class="wrap"><header class="page-hero"><span class="eyebrow">Privacy</span><h1>Your privacy.</h1></header></div>
<section class="sec"><div class="wrap prose">
<h2>What we collect</h2><p>We collect only what you send through our contact and prayer forms: your name (optional for prayer), how to reach you, and your message. Prayer requests are never published and are read only by the LCC pastoral team.</p>
<h2>Cookies and embeds</h2><p>This site sets no tracking cookies. Videos use YouTube's privacy-enhanced mode (youtube-nocookie.com) and only load after you press play. When you play a video, YouTube's own privacy policy applies. Video thumbnails are loaded from YouTube's image servers.</p>
<h2>Fonts</h2><p>Fonts are served from this website, not from a third party.</p>
<h2>Your rights</h2><p>Under Kenya's Data Protection Act, 2019, you may ask to see or delete information you sent us. Contact <a href="mailto:{e(CT['email'])}">{e(CT['email'])}</a> or call {e(CT['phone'])}.</p>
<p class="muted">Last updated {TODAY}.</p>
</div></section>
""")

P["404.html"] = page("404.html", "Page not found", "This page could not be found.",
"""<div class="wrap"><header class="page-hero"><span class="eyebrow">404</span><h1>This page has <em>wandered</em> off.</h1><p class="lead">Let's get you home.</p><p class="mt2"><a class="btn btn-solid" href="./">Go to the homepage</a></p></header></div>""")


def main():
    for name, src in P.items():
        src = re.sub(r'"uploadDate": null, ?', "", src)
        (ROOT / name).write_text(src, encoding="utf-8")
    urls = [n for n in P if n != "404.html"]
    sm = "".join(f"<url><loc>{BASE if u == 'index.html' else BASE + u}</loc><lastmod>{TODAY}</lastmod></url>" for u in urls)
    (ROOT / "sitemap.xml").write_text(f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{sm}</urlset>\n')
    (ROOT / "robots.txt").write_text(f"User-agent: *\nAllow: /\nDisallow: /admin/\nDisallow: /api/\nDisallow: /private/\n\nSitemap: {BASE}sitemap.xml\n")
    print("built", len(P), "pages")


if __name__ == "__main__":
    main()
