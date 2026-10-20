# AB Outcome Explorer

Interactive data explorer for MLB batting outcomes by ball-strike count and batter/pitcher handedness.

**Live site:** https://kuod.github.io/ab-outcome/

## What it shows

**Outcomes Explorer** — pick batter hand (L/R) and pitcher hand (L/R), then browse all 12 ball-strike counts. Each count card shows a proportional breakdown of outcomes (hits, walk, hit by pitch, strikeout, groundout, flyout). Click any card for a detailed bar chart.

**Platoon Advantage** — tests whether batters perform better against opposite-handed pitchers. Compares standard OBP, (H + BB + HBP) / (AB + BB + HBP + SF), for opposite-handedness matchups (RHB vs LHP, LHB vs RHP) against same-handedness across all 12 counts.

**Count Flow** — alluvial (Sankey) diagram connecting each ball-strike count to its plate appearance outcomes by raw volume. Hover a count or outcome node to highlight its flows; click to filter. Flow tooltips show both the percentage of the count's total *and* the percentage of that outcome's total.

**Count Paths** — Sankey diagram of how at-bats travel through the count, from 0-0 to the final pitch. Green flows are balls advancing the ball count; red flows are strikes. Nodes are colored by count advantage (blue = batter-ahead, gray = even, red = pitcher-ahead) and sized by estimated PA visits. Hover for estimated visit counts and flow percentages.

**Simulator** — build a count pitch-by-pitch and watch outcome probabilities update live. Select batter and pitcher handedness, then add balls and strikes. The most likely outcome is highlighted with a glowing border keyed to outcome type (blue for hits, green for walk, red for outs).

### Platoon Advantage hypothesis & findings

**Hypothesis:** batters have a meaningful OBP advantage when facing a pitcher of the opposite hand — the classic platoon split.

**Result: largely confirmed, but count-dependent and smaller than conventional wisdom suggests.**

The advantage holds in 10 of 12 counts (1-1 is a dead heat at −0.0 pts and 0-1 is slightly negative), but the effect size varies significantly:

| When it's largest | When it's negligible |
|---|---|
| 3-0: **+1.8 pts** | 1-1: −0.0 pts |
| 3-2: **+1.4 pts** | 0-1: −0.1 pts |
| 0-2: **+1.2 pts** | 2-1: +0.1 pts, 1-0: +0.2 pts |

The pattern points to **pitcher behavior under pressure**, not just batter skill. The biggest edges appear at the counts where pitchers most need to throw strikes (3-0, 3-2) or most want to expand the zone (0-2) — situations where the platoon matchup affects pitch selection and location more than it does in neutral counts. In the middle of at-bats (1-1, 2-1), pitchers have more flexibility and the advantage nearly disappears.

## Data

555,995 plate appearances from MLB 2022–2024 Statcast via [pybaseball](https://github.com/jldbc/pybaseball). Outcomes are aggregated into 10 categories: single, double, triple, home run, walk, hit by pitch, strikeout, ground out, fly out, other. Note that "walk" also includes intentional walks. Double and triple plays are classified by batted-ball type (ground ball = ground out; line drive, fly ball, popup = fly out). The OBP on the Platoon tab is standard OBP, (H + BB + HBP) / (AB + BB + HBP + SF): sacrifice bunts, catcher interference and truncated PAs are excluded from the denominator (stored as `excluded` per record); sacrifice flies stay in the denominator and reached-on-error PAs count as at-bats. Overall OBP is .3147.

The pre-aggregated data lives in `docs/data.json` (48 records: 4 handedness combos × 12 counts). To regenerate it with updated seasons, edit `SEASONS` in `fetch_data.py` and run:

```bash
pip install -r requirements.txt
python3 fetch_data.py
```

Run the tests with `python3 -m unittest discover -s tests`.

## Local development

```bash
cd docs && python3 -m http.server 8742
# open http://localhost:8742
```

The front-end is a single `docs/index.html` with no build step — Chart.js and D3 loaded from CDN. Includes a light/dark mode toggle.
