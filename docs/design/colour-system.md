# Colour System

| Token | Hex | Use | Contrast |
|---|---|---|---|
| `--paper` | #F6F1E8 | Page background | — |
| `--paper-2` | #FFFCF6 | Cards, form fields | — |
| `--sand` | #EADFCC | Subtle panels, placeholders | — |
| `--line` | #DDD0BC | Hairlines | decorative |
| `--ink` | #1E1A16 | Body text, primary buttons | 15.6:1 on paper |
| `--muted` | #5F554B | Secondary text | 6.9:1 on paper (AA) |
| `--clay` | #A3442A | Accent, links, eyebrow | 5.6:1 on paper (AA) |
| `--clay-deep` | #7E321E | Link hover | 8.3:1 |
| `--ochre` | #D49A2F | Tiles, highlights (never body text on paper) | 2.3:1, decorative only |
| `--flamingo` | #EBAE97 | Tiles (Lake Nakuru nod) | decorative |
| `--night` | #15110E | Cinematic bands | — |
| `--night-2` | #221C17 | Cards on night | — |
| `--bone` | #F2EADF | Text on night | 15.9:1 |
| `--sun` | #F0C060 | Accent on night, live badge | 11.6:1 on night |

Rules:
- Text on ochre or flamingo tiles is always `--ink` (≥ 7:1).
- Focus ring: 3px `--clay` outline with a 2px paper offset. On night bands the ring is `--sun`.
- No gradients except on placeholder art and the hero glow on night bands.
