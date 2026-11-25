# LCC Nakuru website v2: Final Report

**Date:** 25 November 2026
**Live preview:** https://baswet.github.io/lcc-nakuru-website/
**Repository:** github.com/Baswet/lcc-nakuru-website

This report covers all four briefs: Ultimate Website Upgrade; Logos, Photographs and Media Sourcing; Complete Digital Presence; and the About Us Special Project.

---

## 1. Research and sources consulted

| Source | What it confirmed |
|---|---|
| **YouTube @DeliveranceChurchLCC.** The /streams tab lists 267 live streams; video uploads are in `research/youtube-videos.tsv`. | A **First Service and a Second Service every Sunday**, streamed weekly (the oldest generic Sunday stream in the list is 10 months old). **Praise Express Service** about every 2–3 months (≈Mar, May, Jul and Oct 2026). **Crossover Kesha 2025–2026.** **Cutting Edge Conference 2026** (20 sessions, April 2026). **Leaders' Summit 2026** (guest Bishop Jimmy Kimani). **Pastors' and Spouses Conference** (≈June 2026). **InterVarsity Worship Experience 2025.** Sermon titles and speakers (Rev. Elijah Mwangi, Rev. Gabriel Ngugi). Vision and mission. |
| **cuttingedgeconference.co.ke** (home, /about, /speakers) | 2027 edition: 30 Mar – 4 Apr 2027, "Commissioning for the Global Mission", anchor scripture **John 4:35**, venue LCC Freehold along Kariba Road. Six-day programme. History: annual every April since **2018**, not held 2020–2022 (COVID-19); 2026 was the **6th edition**. **Core values.** **Official biography of Rev. Elijah Mwangi.** Full speaker list. Registration, volunteer and partner links. |
| **Facebook** (LifeCelebrationCentre / 164068594168996) | Name "Deliverance Church- LCC", 14K followers, vision, address (General Kariba Street, P.O. Box 2758-20100). Posts: #connectiontime fellowship; Leaders' Summit; "Expectation of a Believer" (Bishop Jimmy Kimani); a "Sunday Service – Second Service" stream. 42 photos catalogued. |
| Nation (local.nation.co.ke) | LCC regularly hosts intervarsity worship experiences. |
| famousnakuru.co.ke | Secondary account of Deliverance Church Nakuru's founding (Bishop Mark Kariuki; Freehold land 1991). **Not published** because it is unofficial. |
| Design: 20 live sites, the churchcreation.com list (50) and the reachrightstudios.com list (23), plus Pinterest | See `research/inspiration-board.md` and `research/competitor-analysis.md`. |

## 2. Verified church information

- **Name:** Deliverance Church International – Life Celebration Centre (LCC), Nakuru.
- **Vision:** "Transforming Nations for Christ."
- **Mission:** "Life Celebration Centre exists to reconcile people to God, equip them for Ministry to God and the people with a transformative agenda."
- **Core values:** Hospitality · Integrity · Servanthood · Fellowship · Commitment · Excellence. The official page lists the third value as "Servant hood".
- **Lead Pastor:** Rev. Elijah Mwangi, with the official biography (degrees, author, married to Mary Wambui Maina). The names of his children are on the source page but are left off the website for privacy.
- **Contact:** 0722 864 864 (two sources); lccnakuru@yahoo.com (Facebook); General Kariba Street, Freehold, Nakuru; P.O. Box 2758-20100.
- **Social:** YouTube @DeliveranceChurchLCC · Facebook /LifeCelebrationCentre · Instagram @lccnakuru.

## 3. Information awaiting confirmation (shown as "to be confirmed", or withheld)

| Item | Status |
|---|---|
| **Exact Sunday service times** | Both services are confirmed to exist, but no published timetable was found. Reading the stream start times from YouTube was blocked, so they could not be measured. The website says "time to be confirmed" and gives the office number. |
| **M-Pesa paybill 882784** | Single source (YouTube description). **Withheld.** It can be enabled in admin once the church office confirms it. |
| Extra phone and email numbers (0784 613 898; life.celebration18@gmail.com; TV 0722 48 71 21) | Single source. Not published. |
| **WhatsApp** | None published officially, so none is listed. |
| Founding date and early history | Not officially published. The timeline starts at documented 2018 milestones. |
| Pastoral team roles | Rev. Gabriel Ngugi preaches regularly; his role is not stated. He is listed under "Voices from our pulpit" with "role to be confirmed". |
| Children's, teens', women's and men's ministries; Daughters of Faith; Night Kesha schedule | Not documented as LCC-specific (Daughters of Faith appears as a denomination-wide event). Not listed; the page explains why. |
| Youth Ablaze, CityAnnex | Seen in Facebook highlights only. Youth Ablaze is marked "Reported"; CityAnnex is not listed. |
| Parking and children's arrangements on Sunday | The FAQ says these details are being confirmed. |
| Testimonies | None approved, so none are shown. The section invites people to share. |

## 4. Service timetable (`services.html`)

| Programme | When | Status | Source |
|---|---|---|---|
| First Service | Sunday morning (time TBC) | Confirmed | YouTube streams, weekly |
| Second Service | Sunday late morning (time TBC) | Confirmed | YouTube streams, weekly |
| Connection Time | After service | Confirmed | Facebook post |
| Praise Express Service | Periodic Sundays (latest Oct 2026) | Confirmed | YouTube streams |
| Kesha / Crossover Kesha | Special nights; 31 Dec | Confirmed | YouTube stream |
| Youth Ablaze | Youth nights | Reported | Facebook highlights |

## 5. Ministries published (each with a section on `ministries.html#…`)

Praise & Worship (One Accord Ministers) · Youth & Students (Youth Ablaze, InterVarsity Worship) · Prayer (Kesha) · Leadership Development (Leaders' Summit, Pastors' and Spouses Conference) · Fellowship (Connection Time) · Cutting Edge Conference.

## 6. Visual assets and permission status

The full inventory is in `research/lcc-photography/asset-inventory.md`.

- **Official logo:** only the Deliverance Church International emblem (Facebook profile image) was found. There is **no LCC-specific logo file**. The site uses a temporary text wordmark, **marked for approval**.
- **LCC photographs:** 42 Facebook photos were catalogued by ID with intended placements. They are **awaiting approval and not republished**: your briefs say public visibility is not permission.
- **Videos:** **65 official LCC videos** are used through privacy-enhanced YouTube embeds.
- **Photography from LCC's own streams:** YouTube automatically captures real frames inside each video (maxres1–3, 1280×720): congregations worshipping, worship teams, Praise Express, Kesha, conference worship. These are used wherever the design needs photography (About slideshow, story, collage, LCC Moments, ministry and event cards, invitations), each linked to its source video. Video cards keep the channel's own thumbnails.
- **Stock images:** **none used.**
- **Approval-ready:** every photo slot (About slideshow, story images) reads from `content.json → photos[]`. In admin, upload a photo, choose it for the slot, tick "Approved" and rebuild. The real image then replaces the YouTube still with no redesign.

## 7. Pages completed (23)

Home · About (13 sections) · Leadership · Services · Plan Your Visit · Ministries · Sermons & Media · Watch Online · Events · Cutting Edge Conference · 7 event detail pages (past events) · Gallery ("LCC Moments") · Announcements · Give · Contact & Prayer · Privacy · 404.

## 8. Features implemented

- **About:** cinematic slideshow (crossfade, slow zoom, dots, prev/next, pause, reduced-motion paused, mobile-safe); sticky "Discover LCC" section navigator; layered editorial story with "Read our story"; sourced timeline (horizontal on desktop, vertical on mobile); oversized vision and mission; values composition; church-family masonry collage with a video lightbox; leadership; ministry discovery; worship experience; upcoming vs past events; conference feature with its own identity; stories invitation (no fabricated testimonies); "Come and experience LCC" invitation.
- **This Sunday at LCC:** in person / online / catch up.
- **Message of the Week.**
- **Streaming-style sermon rows:** Latest Sunday Services, Praise Express, CEC 2026, Special services and nights, Worship, Archive. Search, category filter and **speaker filter**.
- **Watch Online page:** no false "live" badge, because the site cannot check live status without an API key. The latest service is shown instead.
- **Events:** featured conference with a **live countdown**; recurring programmes; filterable past-events archive with an individual page per event. Past events are never shown as upcoming.
- **Cutting Edge Conference universe:** giant "2027" numerals, countdown, John 4:35 in the King James Version (public domain), programme, 2027 speakers, all-time featured speakers, 2026 and earlier archive rows.
- **Gallery:** "LCC Moments" with category filters and a lightbox.
- **Plan Your Visit:** 4-step first-time journey, click-to-load Google Map (privacy), FAQ, visitor enquiry form.
- **Prayer:** private prayer form, stored outside public view and visible only to admins.
- **Share buttons:** native share sheet or copy link, on every page footer, conference, sermons and events.
- **Original linework divider:** kiondo/kitenge-inspired SVG.
- **Admin:** notice, services (with status, watch link and source), giving (verification gate), videos, events, past events, news, ministries, contact details, photo-slot approvals, image upload (re-encoded), and private submissions including the new visitor enquiries.

## 9. Performance

- Home HTML is about 21 KB; CSS about 38 KB; JS about 17 KB; 2 preloaded fonts about 80 KB; no frameworks.
- Videos load only on click (lite embed). Stills are lazy-loaded except the hero.
- The map is click-to-load. There is no autoplaying audio or video.
- `prefers-reduced-motion` is respected: the slideshow starts paused and zoom and reveal animations are off.

## 10. Testing results (`tests/`)

- **Layout:** 23 pages × 8 widths (320–1440) = 184 renders, with **0 overflow, 0 JS errors and 0 touch targets under 44 px**.
- **Accessibility:** axe WCAG 2.1 AA plus best practice at 390 and 1440 px gives **0 violations** after fixes. The fixes were dark-panel contrast, the values grid on small screens, heading order, and slideshow dot size.
- **Links:** 0 broken internal links.
- **Interactions** (`tests/interactions.py`): **20/20 pass**. Covered: slideshow, pause, reduced motion, lightbox (open, arrow keys, Esc), rows, countdown, sermon and speaker filters, lite video, past-events filter, "no past event as upcoming", click-to-load map, form validation, gallery filter, mobile menu.
- **Backend:** CSRF, honeypot, rate limit, XSS escaping, upload validation, path traversal in photo slots blocked, non-https links rejected, and the new "visit" form type. All pass.
- **Screenshots:** `tests/screenshots/` (v2). Before-and-after screenshots are in `research/before-v1-screenshots/`.

## 11. Outstanding issues

1. Exact service times: the church office needs to confirm them.
2. Photo permission, official logo and Lead Pastor portrait: the church office needs to provide them.
3. Instagram not reviewed (login required). Facebook post dates and poster text could not be read automatically.
4. `.htaccess` protections need Apache or LiteSpeed when the site moves to PHP hosting.
5. Real-device testing (Android Chrome, iOS Safari) is recommended.

## 12. Additional ideas (15+)

| # | Idea | Benefit | Look | Approval? | When |
|---|---|---|---|---|---|
| 1 | Sermon series pages | Group multi-week series | Series artwork row + episode list | Yes (series names and art) | Later |
| 2 | Church calendar (ICS feed) | Add events to phone calendars | "Add to calendar" button on event cards | Yes (dates) | Now-ready once dates are confirmed |
| 3 | WhatsApp channel link | Kenya's main messaging app | Green pill in the footer and Contact | Yes (official number) | When provided |
| 4 | New believer pathway | Next steps after salvation | 4-step journey like Plan Your Visit | Yes (content) | Later |
| 5 | Bible reading plan | Daily engagement | Card with day's reading (public-domain text) | Yes | Later |
| 6 | Kesha and Praise Express landing pages | Recurring campaigns with their own identity | Night-band campaign page + countdown | Yes (dates and posters) | When dates are announced |
| 7 | Conference archive by year | History of all editions since 2018 | Year tabs with sessions and photos | Partly | Later |
| 8 | Volunteer sign-up form | Serve-team recruitment | Form with ministry checkboxes → admin | Yes | Now-ready (reuses forms) |
| 9 | Newsletter (email) | Weekly reach | Footer signup → office mailbox or provider | Yes (provider) | Later |
| 10 | Visitor follow-up | Welcome new people | Enquiry form → office follow-up checklist in admin | Yes (process) | Now (form exists) |
| 11 | Testimony submission + moderation | Authentic stories | "Share your story" form → admin approve/publish | Yes (each story) | Later |
| 12 | Downloadable resources (sermon notes, conference programme PDF) | Take-home content | Resource cards with file size | Yes | Later |
| 13 | Swahili toggle for key pages | Wider reach in Nakuru | EN/SW switch in header | Yes (translation) | Later |
| 14 | Live-status check via YouTube API | A real "Live now" badge | Pulsing badge only when live | Yes (API key, server-side) | On PHP hosting |
| 15 | Ministry leaders' contact cards | Direct connection | Portrait + role + office contact | Yes | When provided |
| 16 | Prayer-team follow-up dashboard | Pastoral care | Admin status per request (prayed / called) | Yes | Later |
| 17 | Anniversary or history exhibition page | Celebrate milestones | Photo timeline with archive images | Yes (history and photos) | Later |

## 13. Backup and rollback

- **Backup of v1:** `lcc-v1-backup-20261125.zip`, plus GitHub history (the v1 commits before "v2 upgrade").
- **Rollback on GitHub:** open the repo, go to Commits, open the last v1 commit and choose "Browse files", or revert the v2 commits. Pages redeploys automatically.
- **Rollback locally:** unzip the v1 backup over the site folder.
