# FABERLOOM — Brand Identity & Logo System
**For:** Claude Design
**Date:** 2026-04-18
**From:** Álvaro, FaberLoom (product architect)
**Goal:** Design the FaberLoom brand identity — explore 3 directions for the symbol/isotipo, recommend one, then produce a full system of variants (horizontal wordmark, vertical wordmark, isotipo standalone, combined lockup, favicon, app icon) in the confirmed coral warm palette, working in both light and dark modes.

---

## 0. Context (read first)

FaberLoom is a **control plane for AI agents in LatAm SMBs** (5–50 employees). Non-technical founders wire up AI agents that read email, consult a knowledge base, draft responses, quote prices, and update CRM — but **never send anything external without human approval** unless autonomy has been explicitly unlocked with evidence. The product is editorial, audited, draft-first. It is not a chatbot. It is not marketing-SaaS. It is where a small company controls AI operations without losing human oversight.

The wedge v1 is **B2B industrial safety footwear quoting** for Marluvas/Tecmater distributors across LatAm — concrete and niche, not a generic "AI employee" pitch.

The existing product UI uses an editorial palette (cream + coral + warm dark, Georgia + Inter) and has already been designed. The **brand identity must live in the same visual world** as the product — no disconnect between app and marque.

---

## 1. Name — fixed decisions

- **Name:** `FaberLoom` — camelCase capitalization (capital F + capital L). Never `Faberloom` flat. Never `FABERLOOM` all-caps except in wordmark lockups with deliberate letter-spacing.
- **Etymology (optional narrative you can lean on):**
  - *faber* (Latin: maker, artisan, craftsman)
  - *loom* (English: weaving frame; also "to emerge / to come into view")
  - Combined narrative: **"a loom of agents"** — where human and AI are warp and weft, weaving structured work together. This narrative can inform the symbol but should never appear as a tagline on the mark itself.

---

## 2. Brand tone — fixed

**Editorial Classic — Warm.**

Reference feel: *NYT / The Atlantic / Stripe-press*, not Silicon-Valley-SaaS. Think of a well-printed book spine, a careful serif, a candle-lit warmth — not neon, not tech-bro gradient, not chatbot-purple.

Attributes (ordered by weight):
1. **Editorial** — serif, considered, literate.
2. **Warm** — coral and cream pull toward human, away from cold-blue enterprise.
3. **Auditable** — restrained, not flashy. Disciplined craft.
4. **LatAm-ready** — warmth reads as hospitality without being folkloric.
5. **Timeless** — should not look like "2026 startup trend". Should read as durable in 2030.

---

## 3. What to explore — three directions for the symbol

Before producing the full system, explore **three distinct directions** for the isotipo (symbol/monogram) in low-fidelity black-on-cream sketches. All three must feel cohesive with the wordmark `FaberLoom` in Georgia (or close serif).

### Direction A — Monogram FL (woven)
The letters **F** and **L** interlocked or overlapping as if threaded, suggesting warp/weft of a loom. Georgia italic as starting point (a pre-existing draft sketch uses `F` in dark + `L` in coral at 140px serif italic — you can honor that lineage or break from it).
Feel: intimate, literate, monogrammatic. Reads as a bookplate or imprint mark.

### Direction B — Abstract loom grid
A minimal grid or lattice glyph — 3 vertical lines + 3 horizontal lines crossing, or an abstract cross-hatch — evoking the warp and weft of a loom without using letterforms. Could be stylized as a single continuous line that crosses itself, or as discrete strokes meeting.
Feel: abstract, symbolic, wordless. Reads at any size including favicon.

### Direction C — Closed loop (infinite loom)
A single continuous stroke tracing a closed loop — suggesting cycle, recurring process, the human-in-the-loop itself as the design principle. Can reference Möbius, an unbroken ribbon, or a serif ampersand-like glyph.
Feel: conceptual, philosophical. Reads as a process mark.

### What to deliver for this exploration step (before the full system)
- 3 rough sketches (SVG inline), each ~160×160px, black on cream `#F4F1ED`.
- For each: one sentence on the rationale and one sentence on what might go wrong with it.
- A recommendation of which one to carry forward, with reason.

**If you cannot reach Álvaro for confirmation, default to Direction A** and proceed. It honors the existing visual lineage and carries least risk.

---

## 4. Color tokens (already fixed — do not propose alternatives)

### Light mode
```
--bg-primary:     #F4F1ED   /* cream off-white — main background */
--bg-surface:     #FFFFFF   /* elevated — cards, modals */
--bg-subtle:      #EDE8DF   /* hover, subtle fills */
--text-primary:   #1F1E1C   /* warm near-black */
--text-secondary: #5A544C
--text-muted:     #8A8278
--border-subtle:  #D8D0C0

--coral-primary:  #C96442   /* accent — CTAs, active, brand symbol */
--coral-hover:    #A84F33
--coral-tint:     rgba(201, 100, 66, 0.10)
```

### Dark mode
```
--bg-primary-dark:    #1F1E1C
--bg-surface-dark:    #2A2824
--bg-subtle-dark:     #34312C
--text-primary-dark:  #F4F1ED
--text-secondary-dark: #B8B0A4
--text-muted-dark:    #8A8278
--border-subtle-dark: #3D3A34

--coral-primary-dark: #C96442   /* same coral works in both */
--coral-hover-dark:   #D97757   /* slightly lighter hover in dark */
```

### Accepted color pairings for the logo
- Primary: `coral #C96442` on `cream #F4F1ED`
- Dark: `cream #F4F1ED` or `coral #C96442` on `dark warm #1F1E1C`
- Mono black: `#1F1E1C` on cream or white (for single-ink print)
- Mono white/cream: on coral or dark warm (for one-ink inverse)
- Never: coral on white (washes out), black on coral (muddy), any blue or purple.

---

## 5. Typography for the wordmark

- **Primary display face:** Georgia, weight 500 (medium) or 400 (regular). Italic is allowed and encouraged in the wordmark — it carries editorial warmth.
- **Acceptable alternatives if Georgia feels off:** Adobe Caslon, Source Serif, EB Garamond. Avoid geometric serifs (Didone, Bodoni) — too cold.
- **Never:** sans-serif wordmark. That would break the editorial tone.
- **Letter-spacing:** tight (default Georgia spacing) for the primary wordmark. Wide letter-spacing (+80 to +200) is reserved for all-caps treatments in secondary lockups or tagline contexts.

---

## 6. Required variants (full system, after direction is confirmed)

Deliver each variant in **SVG inline** (optimized, no rasterization), on the specified background:

| Variant | Purpose | Format notes |
|---|---|---|
| **1. Wordmark horizontal — primary** | Sidebar of the app, email signatures, headers | `FaberLoom` in Georgia italic (or selected serif), single line, coral on cream. ~220×44px baseline. |
| **2. Wordmark horizontal — dark** | Sidebar dark mode, inverse backgrounds | Same wordmark, cream on dark warm. |
| **3. Wordmark vertical — stacked** | Pitch deck title slides, posters, covers | Isotipo centered above `FaberLoom` wordmark. ~200×240px. |
| **4. Isotipo (symbol only)** | Favicon, app icon, avatar, loading indicator | Standalone, square-safe bounding box, scalable from 512×512 down to 16×16. |
| **5. Combined lockup (symbol + wordmark)** | Homepage header, social avatars with text, press | Isotipo + wordmark side-by-side, correct optical spacing. ~300×64px. |
| **6. Lockup monochrome dark** | Single-color print, watermarks | Black on white version of #5. |
| **7. Lockup monochrome inverse** | On coral or on dark warm background | Cream/white version of #5. |
| **8. Favicon 32×32 and 16×16** | Browser tab | Simplified version of isotipo if needed for pixel clarity at 16px. |
| **9. App icon 512×512 with background** | iOS/Android/PWA install | Isotipo centered on a solid coral or dark warm rounded square, 22% corner radius. |

---

## 7. Construction guidelines

- **Grid:** build on an 8px base grid with optical corrections as needed. Isotipo should fit in a square canvas (width = height).
- **Clearspace:** minimum clearspace around any variant = the x-height of the wordmark's "a". Never crop tighter.
- **Minimum sizes:**
  - Wordmark: 96px wide minimum (anything smaller, use isotipo only).
  - Isotipo: 16px square minimum for favicon use; design accordingly.
- **Stroke weight (for Direction B or C):** never thinner than 1.5px at 32px display size — should hold up at favicon scale.
- **Optical alignment:** Georgia italic slants right; if combining with a geometric isotipo, balance visual weight, not mathematical center.

---

## 8. Usage rules — examples of correct and incorrect use

Include in your deliverable a 1-page usage guide showing:

### Do
- Coral `#C96442` symbol on cream `#F4F1ED` (primary)
- Cream symbol on dark warm `#1F1E1C` (dark mode)
- Adequate clearspace
- Use on flat color backgrounds only

### Don't
- Do not stretch or distort
- Do not recolor to any non-approved color
- Do not outline or add drop shadows
- Do not place on busy photographic backgrounds
- Do not rotate
- Do not combine with other typography inside the lockup
- Do not add taglines inside the lockup

Show 3–4 "do" examples and 3–4 "don't" examples with red X overlays on the wrong ones.

---

## 9. Narrative / brand doc (short)

Alongside the SVGs, deliver a **`FABERLOOM_BRAND.md`** file (max 400 words) covering:

1. **Essence** — one paragraph: who FaberLoom is and how the mark expresses it.
2. **Rationale for chosen direction** — one paragraph on why the selected isotipo direction (A, B, or C) won out.
3. **Construction notes** — how the mark is built (proportions, grid, key angles).
4. **Tone of voice (brief)** — 3 adjectives + 2 words to avoid. This informs future copy, even though not part of this deliverable.
5. **Future extensions** — suggestions for how the mark could extend into patterns, animations, or merchandise if the brand grows.

---

## 10. Deliverables summary

1. **Exploration SVG** — one HTML file with the 3 direction sketches (`FABERLOOM_EXPLORATION.html`), with rationale for each and a recommended direction.
2. **Full system SVG** — one HTML file with all 9 variants cleanly organized and labeled (`FABERLOOM_BRAND_SYSTEM.html`).
3. **Individual isotipo SVG files** — for direct use (`faberloom_isotipo.svg`, `faberloom_isotipo_dark.svg`, `faberloom_isotipo_mono.svg`).
4. **Favicon set** — 16×16 and 32×32 PNG exports (inline base64 in the HTML or as separate files).
5. **App icon** — 512×512 PNG (inline base64 or separate file).
6. **Brand doc** — `FABERLOOM_BRAND.md` per Section 9.

If anything in this brief is ambiguous, default to the safer editorial choice and leave a short note in the brand doc explaining what you interpreted and why.

---

## 11. Principles when in doubt

1. Editorial restraint over Silicon Valley flash — **always**.
2. Warmth over coolness — **always**.
3. Timelessness over trend — **always**.
4. Works at 16px favicon size? If no, simplify.
5. Works in light AND dark without a second design? If no, rework.
6. Would this mark look out of place on a book spine? If yes, it's too techy.

---

## 12. Out of scope (do NOT produce)

- Marketing landing page
- Full brand book (50+ pages)
- Animated intro video
- Merchandise mockups (unless you want to include a single optional reference image)
- Secondary sub-brands or agent avatars (future work)
- Any photography direction

Build the mark. Build the system. Keep it disciplined.
