# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

**Regenerate data** (takes ~5 min, downloads from Baseball Savant via pybaseball):
```bash
python3 fetch_data.py
```
Output goes to `docs/data.json` (path is relative to the script). Pybaseball caches downloads in `~/.pybaseball/cache/`.

**Run local dev server:**
```bash
cd docs && python3 -m http.server 8742
```

**Install dependency:**
```bash
pip install -r requirements.txt
```

## Architecture

Two-file pipeline: a Python build script produces a static JSON file consumed by a self-contained single-page app.

### `fetch_data.py` (data build step)
- Downloads 3 seasons of MLB Statcast pitch-level data (2022–2024) via `pybaseball.statcast()`
- Filters to final pitch of each plate appearance (`events` column non-null)
- Note: `walk` also includes `intent_walk`; `hit_by_pitch` is its own `hbp` outcome; `double_play`/`triple_play` are classified by `bb_type` like `field_out`; sac bunts/errors/catcher interference are `other`
- Each record also has `excluded`: PAs outside the standard OBP denominator (`sac_bunt`, `sac_bunt_double_play`, `catcher_interf`, `truncated_pa`); `sac_fly` and `field_error` are not excluded
- `load_cache()` / `python3 fetch_data.py --from-cache` rebuild from the local pybaseball cache with no network
- Maps Statcast event names → 10 simplified outcomes: `single`, `double`, `triple`, `home_run`, `walk`, `hbp`, `strikeout`, `groundout`, `flyout`, `other`
- Special case: `field_out` (the most common out event) requires `bb_type` column to disambiguate groundout vs flyout
- Groups by `stand` (batter hand L/R) × `p_throws` (pitcher hand L/R) × `balls` × `strikes` → 48 records
- Each record contains `props` (proportions) and `raw` (counts) for all 10 outcomes, plus `total` and `excluded`

### `docs/index.html` (the entire front-end)
Single HTML file with inline CSS and JS, no build step. Loads `data.json` at runtime via `fetch()`.

**Six tabs** (home, explorer, hypothesis, alluvial/Count Flow, count-paths, simulator). The two core ones:
1. **Outcomes Explorer** — filter by batter/pitcher hand, 4×3 grid of count cards, click for detail bar chart
2. **Platoon Advantage** — compares opposite-handedness matchups (RHB vs LHP + LHB vs RHP pooled) against same-handedness, standard OBP ((H+BB+HBP)/(AB+BB+HBP+SF), computed from `raw` and `total - excluded`) as the primary metric, delta shown per count

Key JS functions:
- `lookup(stand, p_throws, balls, strikes)` — finds a record from rawData
- `poolRecords(r1, r2)` — weighted-average props across two records (used for platoon pooling)
- `computeHypothesis(balls, strikes)` — returns `{ opposite, same, delta }` for the platoon tab
- `buildGrid()` / `buildHypothesisGrid()` — render the 4×3 count card grids
- `renderDetail()` / `renderHypothesisDetail()` — render Chart.js horizontal bar charts in the right panel

Charts use Chart.js 4.4 (CDN). Color scheme: hits = shades of blue, outs = shades of red, walk = green, hbp = teal.

**Tests:** `python3 -m unittest discover -s tests` (no network or pybaseball needed).

### `docs/` (GitHub Pages root)
Configured to serve from `/docs` on the `main` branch. `.nojekyll` disables Jekyll processing.
