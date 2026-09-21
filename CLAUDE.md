# Body Maintenance

A static, single-page reference site on evidence-based health and fitness. No build step, no framework, no dependencies to install.

## Architecture

Three moving parts:

- **`index.html`** — the entire application. Inline CSS and JS, plus a baked-in copy of all content. Loads `marked` and `highlight.js` from CDN, builds the sidebar nav from the manifest, then renders markdown into the content pane on click.
- **`build.py`** — bakes `manifest.json` and every markdown file into `index.html` so it runs from `file://`.
- **`manifest.json`** — the single source of truth for site structure. Nothing appears in the nav unless it's listed here.
- **`content/**/*.md`** — one markdown file per page.

Adding a page means writing the markdown file *and* registering it in `manifest.json`. Neither alone is enough.

## Navigation model (3 levels)

`manifest.json` has a `sections` array. A node's shape determines how it renders:

| Node shape | Renders as |
|---|---|
| `file`, no `children` | Top-level page (e.g. Overview) |
| `children`, no `file` | Collapsible top-level section with an icon (e.g. Diet) |
| `file` + `children` | Mid-level page that also expands to grandchildren (e.g. Mobility & Flexibility) |

Three levels is the maximum `index.html` supports. Sections carry an `icon` (a geometric glyph: ◎ ◈ ◇ ◉).

## Content conventions

Match these when writing or editing pages — they are load-bearing for how the site reads and renders.

- **Evidence tags.** Claims carry `[STRONG]`, `[MODERATE]`, or `[EMERGING]` in brackets. `index.html` post-processes these into styled badges, so the literal bracket syntax matters — and only those three exist. Any other bracketed word renders as plain text.
- **Citations.** Blockquote immediately after the claim: `> [Source: Author (Year) — description](https://pubmed.ncbi.nlm.nih.gov/PMID/)`. Do not invent PMIDs — if the exact ID isn't known, link a PubMed search URL instead.
- **Internal links.** Repo-root-relative paths, not URLs: `[Hips](content/exercise/mobility/hips.md)`. The click handler intercepts these and loads the page in-pane.
- **Structure.** H1 title, short framing paragraph, then `---`-separated sections. Tables for anything comparative. Deep-dive pages end with a `## See Also` list.
- Parent pages do not link down to their children — the nav handles that.

## Content is baked in — rebuild after editing

`index.html` normally can't read local files over `file://` (browsers block `fetch()` there). So `build.py` embeds `manifest.json` and every markdown page into a `<script id="siteData" type="application/json">` block, between the `BUILD:DATA:START` / `BUILD:DATA:END` markers.

**After editing any `.md` file or `manifest.json`, run:**

```
python3 build.py
```

Then just open `index.html` — double-click it, no server needed. The build reports any file listed in the manifest but missing from disk, and any markdown file on disk that no manifest entry points at.

The runtime prefers the embedded copy but falls back to `fetch()` when the page is served over `http://`. So `python3 -m http.server 8000` still works and picks up markdown edits live, without a rebuild — useful while writing. The baked copy is what makes the double-click path work.

The CDN `<script>` tags still need a network connection on first load; the browser caches them afterward.

## In-page links

`renderer.link` tags any href ending in `.md` with `class="internal-link"` and leaves off `target="_blank"`. A delegated click handler on `#contentInner` intercepts those, looks the path up in `PAGE_INDEX` (a flattened `file -> {item, sectionTitle, subsectionTitle}` map built from the manifest), and loads the page in-pane with a correct breadcrumb. A cross-reference only works if its target is registered in `manifest.json`.

## Sections

- **Exercise** — mobility, cardiovascular, strength, recovery (each with deep-dive children)
- **Diet** — longevity/anti-inflammatory, body composition, gut & metabolic health
- **Mind & Nervous System** — breathwork, emotional awareness

### Strength & Muscle subtree

The strength deep-dives are written around one specific goal: **relative strength** — getting stronger while staying lean, rather than hypertrophy. `content/exercise/strength/gym-program.md` is a 12-month, 2–3×/week plan for a returning lifter using commercial-gym equipment (Vasa). If editing these, keep the framing consistent: heavy loads, low-to-moderate volume, long rests, calories at maintenance. The parent `strength-muscle.md` remains general-purpose and does not assume that goal.

`content/exercise/strength/kettlebell-amrap.md` is the companion conditioning program: a 12-week, 3×/week plan built on 20-minute AMRAPs. Its load-bearing ideas are the three session intents (**Pace** = nasal-breathing aerobic, **Heavy** = one bell up with rest-as-needed, **Push** = beat the log), a fixed **Benchmark** session retested every 4 weeks, and the progression order *rounds → load → complexity*. Bell sizes are given by test ("20 clean swings fresh") rather than by prescribed weight, so the page works for any bell collection. The gym program and the kettlebell page cross-link in their See Also sections and share a "Combining With the Gym" scheduling table — if either program's weekly structure changes, check that table still matches.

### Cardiovascular subtree

`content/exercise/cardio/running-program.md` is a 12-week, 3×/week Zone 2 running plan. Its load-bearing ideas: sessions are prescribed in **minutes, never distance**; the **HR cap governor** (run until HR crosses the top of Zone 2, walk until it drops ~10 bpm, repeat) is what makes running a Zone 2 activity for a non-runner; volume grows ≤10%/week with every 4th week a step-back; intervals (4×4) appear only in Block 3. The benchmark is **pace at a fixed HR over 30 min**, not a time trial. It has its own "Combining With..." tables pairing it with the kettlebell and gym programs — the three programs' scheduling tables should agree with each other.
