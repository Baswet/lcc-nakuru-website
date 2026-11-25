# Design Decisions Log

1. **Static-first build** (HTML/CSS/vanilla JS + `data/content.json`). It runs on GitHub Pages now and on any PHP host later. A Python build script (`tools/build.py`) renders every page from `content.json`, so SEO content is real HTML. On PHP hosting, `admin/` edits `content.json` and the pages re-hydrate their dynamic lists from it.
2. **No autoplay video; lite YouTube embeds.** Nakuru visitors are mostly on mobile data. A thumbnail costs about 20 KB versus about 1 MB for an iframe. The privacy-enhanced youtube-nocookie domain is used.
3. **Self-hosted fonts.** No third-party font requests.
4. **No borrowed photography.** LCC's Facebook photos are church-owned but not licensed to us. Art-directed placeholders say so plainly and can be swapped in admin.
5. **Unverified = labelled or withheld.** Service times are shown as "being confirmed". The M-Pesa paybill is withheld until confirmed. History is a placeholder.
6. **Prayer requests are never public.** On PHP hosting they are saved outside the web root (or in `private/`, which has `Deny from all`) and visible only to logged-in admins. On GitHub Pages the form tells the person to call or email, and nothing is sent anywhere.
7. **Accessibility target: WCAG 2.1 AA.** Contrast is checked in `colour-system.md`. Skip link, visible focus, reduced-motion support, 44px touch targets.
8. **Conference** links to official registration on cuttingedgeconference.co.ke rather than duplicating the forms.
