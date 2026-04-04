# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

**Regenerate data** (takes ~5 min, downloads from Baseball Savant via pybaseball):
```bash
python3 fetch_data.py
```
Output goes to `docs/data.json`. Pybaseball caches downloads in `~/.pybaseball/cache/`.

**Run local dev server:**
```bash
cd docs && python3 -m http.server 8742
```

**Install dependency:**
```bash
pip install pybaseball
```

## Architecture

Two-file pipeline: a Python build script produces a static JSON file consumed by a self-contained single-page app.

### `fetch_data.py` (data build step)
- Downloads 3 seasons of MLB Statcast pitch-level data (2022–2024) via `pybaseball.statcast()`
- Filters to final pitch of each plate appearance (`events` column non-null)
- Maps Statcast event names → 9 simplified outcomes: `single`, `double`, `triple`, `home_run`, `walk`, `strikeout`, `groundout`, `flyout`, `other`
- Special case: `field_out` (the most common out event) requires `bb_type` column to disambiguate groundout vs flyout
- Groups by `stand` (batter hand L/R) × `p_throws` (pitcher hand L/R) × `balls` × `strikes` → 48 records
- Each record contains `props` (proportions) and `raw` (counts) for all 9 outcomes

### `docs/index.html` (the entire front-end)
Single HTML file with inline CSS and JS, no build step. Loads `data.json` at runtime via `fetch()`.

**Two tabs:**
1. **Outcomes Explorer** — filter by batter/pitcher hand, 4×3 grid of count cards, click for detail bar chart
2. **Platoon Advantage** — compares opposite-handedness matchups (RHB vs LHP + LHB vs RHP pooled) against same-handedness, OBP as the primary metric, delta shown per count

Key JS functions:
- `lookup(stand, p_throws, balls, strikes)` — finds a record from rawData
- `poolRecords(r1, r2)` — weighted-average props across two records (used for platoon pooling)
- `computeHypothesis(balls, strikes)` — returns `{ opposite, same, delta }` for the platoon tab
- `buildGrid()` / `buildHypothesisGrid()` — render the 4×3 count card grids
- `renderDetail()` / `renderHypothesisDetail()` — render Chart.js horizontal bar charts in the right panel

Charts use Chart.js 4.4 (CDN). Color scheme: hits = shades of blue, outs = shades of red, walk = green.

### `docs/` (GitHub Pages root)
Configured to serve from `/docs` on the `main` branch. `.nojekyll` disables Jekyll processing.
