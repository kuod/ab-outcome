# AB Outcome Explorer

Interactive data explorer for MLB batting outcomes by ball-strike count and batter/pitcher handedness.

**Live site:** https://kuod.github.io/ab-outcome/

## What it shows

**Outcomes Explorer tab** — pick batter hand (L/R) and pitcher hand (L/R), then browse all 12 ball-strike counts. Each count card shows a proportional breakdown of outcomes (hits, walk, strikeout, groundout, flyout). Click any card for a detailed bar chart.

**Platoon Advantage tab** — tests whether batters perform better against opposite-handed pitchers. Compares OBP (hits + walks) for opposite-handedness matchups (RHB vs LHP, LHB vs RHP) against same-handedness across all 12 counts.

### Hypothesis & findings

**Hypothesis:** batters have a meaningful OBP advantage when facing a pitcher of the opposite hand — the classic platoon split.

**Result: largely confirmed, but count-dependent and smaller than conventional wisdom suggests.**

The advantage holds in 11 of 12 counts, but the effect size varies significantly:

| When it's largest | When it's negligible |
|---|---|
| 3-0: **+1.7 pts** | 1-1: +0.0 pts |
| 3-2: **+1.4 pts** | 0-1: −0.1 pts (only exception) |
| 0-2: **+1.2 pts** | 1-0, 2-1: +0.1 pts |

The pattern points to **pitcher behavior under pressure**, not just batter skill. The biggest edges appear at the counts where pitchers most need to throw strikes (3-0, 3-2) or most want to expand the zone (0-2, 1-2) — situations where the platoon matchup affects pitch selection and location more than it does in neutral counts. In the middle of at-bats (1-1, 2-1), pitchers have more flexibility and the advantage nearly disappears.

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
