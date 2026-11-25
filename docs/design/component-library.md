# Component Library

All components live in `website/assets/css/site.css`; class names are in brackets.

- **Header** (`.site-header`): wordmark + 7 primary links + "Plan your visit" pill. Under 1024px, a disclosure menu (`button[aria-expanded]`), full-screen sheet, focus kept inside the sheet, Esc closes.
- **Live pill** (`.live-pill`): links to YouTube /live. Shown as "Watch online", never claims "LIVE NOW" (we cannot detect live status without the API).
- **Hero** (`.hero`): eyebrow, display H1, lead, two CTAs, art panel.
- **Placeholder art** (`.ph`): warm gradient with an SVG contour (Menengai or Rift lines) and a caption "Awaiting LCC-approved photo". Never presented as a real photo.
- **Facts strip** (`.facts`): 3–4 cells (Sundays / Where / Watch / Next event).
- **Intent tiles** (`.intents`): "I want to…" cards in ochre, flamingo, paper and sand.
- **Night band** (`.band-night`): dark section for video and the conference.
- **Video card** (`.video`): YouTube thumbnail + play button. Click loads a youtube-nocookie iframe (lite embed). Keyboard accessible, with the title as the accessible name.
- **Sermon filter** (`.filters`): All / Sermons / Worship / Conference, plus a text search. Client-side.
- **Event card** (`.event`): date block, title, meta, CTA.
- **Notice** (`.notice`): "To be confirmed" callout for unverified items.
- **Forms** (`.form`): labelled inputs, hint text, error summary, honeypot, consent checkbox for prayer requests.
- **Footer**: contact, socials, quick links, vision line, admin-free.
