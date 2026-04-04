# AB Outcome Explorer

Interactive data explorer for MLB batting outcomes by ball-strike count and batter/pitcher handedness.

**Live site:** https://kuod.github.io/ab-outcome/

## What it shows

**Outcomes Explorer tab** — pick batter hand (L/R) and pitcher hand (L/R), then browse all 12 ball-strike counts. Each count card shows a proportional breakdown of outcomes (hits, walk, strikeout, groundout, flyout). Click any card for a detailed bar chart.

**Platoon Advantage tab** — tests whether batters perform better against opposite-handed pitchers. Compares OBP (hits + walks) for opposite-handedness matchups (RHB vs LHP, LHB vs RHP) against same-handedness across all 12 counts.

## Data

555,995 plate appearances from MLB 2022–2024 Statcast via [pybaseball](https://github.com/jldbc/pybaseball). Outcomes are aggregated into 9 categories: single, double, triple, home run, walk, strikeout, ground out, fly out, other.

The pre-aggregated data lives in `docs/data.json` (48 records: 4 handedness combos × 12 counts). To regenerate it with updated seasons, edit `SEASONS` in `fetch_data.py` and run:

```bash
pip install pybaseball
python3 fetch_data.py
```

## Local development

```bash
cd docs && python3 -m http.server 8742
# open http://localhost:8742
```

The front-end is a single `docs/index.html` with no build step — Chart.js loaded from CDN.
