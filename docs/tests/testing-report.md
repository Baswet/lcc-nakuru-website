# Testing Report: LCC Nakuru website (v2 results first, v1 below)

## v2: 25 Nov 2026
- 23 pages × 8 widths: 0 overflow, 0 JS errors, 0 small touch targets, 0 broken links.
- axe WCAG 2.1 AA: 0 violations (fixed: dark-panel contrast, values grid at 320–390, heading order, slideshow dots).
- Interactions: 20/20 pass (`interactions.py`, `interaction-results.txt`).
- Admin v2: photo-slot path traversal blocked, non-https links rejected, visitor enquiry form saved privately.

---

## v1

**Date:** 25 November 2026 · **Build:** `tools/build.py` from `data/content.json`
**Tools:** Playwright + Google Chrome (headless), axe-core 4.x, PHP 8.3 built-in server, curl. The script is `tests/qa.py`; raw results are in `tests/qa-results.json`.

## 1. Responsive layout — 13 pages × 8 widths (104 renders)
Widths tested: 320, 360, 375, 390, 430, 768, 1024 and 1440 px.

| Check | Result |
|---|---|
| Horizontal overflow (scrollWidth > viewport) | **0 failures** |
| JavaScript runtime errors | **0** |
| Touch targets under 44 × 44 px (buttons, chips, CTAs at 390 px) | **0** |
| Mobile menu: opens, focus moves into the menu, Tab is trapped, Esc closes and returns focus, closes at ≥1100 px | **Pass** |

Screenshots: `tests/screenshots/` (full-page at 390 and 1440 for every page; all 8 widths for Home).

## 2. Accessibility — axe-core (WCAG 2.0/2.1 A + AA + best practice) at 390 and 1440
- First run: 26 findings, none serious or critical. They were: the notice bar outside a landmark (moderate), `role=img` on `<figure>` (minor), and heading-order gaps on Events, Give and Ministries (moderate).
- All were fixed. **Re-run: 0 violations on all 13 pages.**
- Colour contrast is covered by axe. Token ratios are in `design/colour-system.md`.
- Other checks: skip link, visible focus rings, `prefers-reduced-motion` honoured, language `en-KE`, labelled form fields, `aria-live` status messages, and video buttons named "Play video: <title>".

## 3. Links
All internal `href`s resolve to files (**0 broken**). External links (YouTube, Facebook, Instagram, the conference site, Google Maps) open in a new tab with `rel="noopener"` and screen-reader text.

## 4. Forms and backend security (PHP hosting)
| Test | Expected | Result |
|---|---|---|
| POST without CSRF token | 403 | ✅ |
| Valid contact form | 200; saved to `private/submissions` | ✅ |
| Prayer form without consent | 422 | ✅ |
| GET on submit endpoint | 405 | ✅ |
| 6th submission in one hour from the same IP | 429 rate-limited | ✅ |
| Honeypot filled | silently dropped | ✅ (code path) |
| Admin wrong password | rejected, with delay and throttle | ✅ |
| Admin correct password | 302; session ID regenerated | ✅ |
| Stored XSS (`<script>` in a name, `"><img>` in a title) shown in admin | escaped | ✅ |
| Admin POST without CSRF | 403 | ✅ |
| Upload `evil.php.jpg` (GIF header + PHP) | rejected | ✅ |
| Upload a real PNG | re-encoded with GD, random name | ✅ |
| content.json backup before every save | file in `private/backups` | ✅ |
| Headers: X-Frame-Options DENY, CSP, nosniff; session cookie HttpOnly + SameSite=Strict | present | ✅ |
| `private/` and `assets/uploads/` script execution | denied by `.htaccess` (Apache/LiteSpeed) | Config shipped; verify on the real host |

On **GitHub Pages** the forms never send data. They show the church phone and email instead, so no prayer request can leak.

## 5. SEO
- Every page has a unique `<title>`, meta description, canonical URL, Open Graph and Twitter tags, and a 1200 × 630 OG image.
- JSON-LD: `Church`/`PlaceOfWorship` on every page; `Event` on Events and Conference; `FAQPage` on Visit; `ItemList` of `VideoObject` on Sermons.
- `sitemap.xml` (12 URLs) and `robots.txt` (disallows /admin, /api, /private).
- Images lazy-load. Fonts are self-hosted and preloaded. No autoplay video.

## 6. Performance (local, before YouTube thumbnails)
Home HTML is about 22 KB, CSS about 20 KB, JS about 7 KB, and the two preloaded fonts about 80 KB. There are no third-party requests until a thumbnail loads or someone presses play.

## 7. Content integrity
- No invented facts. Unverified items (service times, history, giving numbers) are labelled "to be confirmed" or withheld.
- The M-Pesa paybill found on YouTube (one source) is **not published** until the church office confirms it.
- No LCC photos or logos are used without permission; placeholders are labelled.

## 8. Known limitations
- YouTube thumbnails could not load in the sandboxed test browser (network allowlist); they are checked on the live GitHub Pages site.
- `.htaccess` protections need Apache or LiteSpeed. On nginx, deny `/private` in the server config.
- Real-device testing (Android Chrome, iOS Safari) is recommended before launch.
