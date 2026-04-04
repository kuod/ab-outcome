"""
Fetch Statcast data and aggregate batting outcomes by count, batter hand, pitcher hand.
Each row in Statcast is a pitch; we keep only rows where `events` is non-null
(final pitch of each plate appearance).
"""

import json
import pandas as pd
from pybaseball import statcast
import warnings
warnings.filterwarnings("ignore")

# Enable caching to avoid re-downloading
from pybaseball import cache
cache.enable()

SEASONS = [
    ("2022-04-07", "2022-10-05"),
    ("2023-03-30", "2023-10-01"),
    ("2024-03-20", "2024-09-29"),
]

OUTCOME_MAP = {
    "single": "single",
    "double": "double",
    "triple": "triple",
    "home_run": "home_run",
    "walk": "walk",
    "intent_walk": "walk",
    "hit_by_pitch": "walk",            # batter reaches, treat like walk
    "strikeout": "strikeout",
    "strikeout_double_play": "strikeout",
    "grounded_into_double_play": "groundout",
    "ground_out": "groundout",
    "force_out": "groundout",
    "fielders_choice": "groundout",
    "fielders_choice_out": "groundout",
    "fly_out": "flyout",
    "pop_out": "flyout",
    "line_out": "flyout",
    "sac_fly": "flyout",
    "sac_fly_double_play": "flyout",
    "double_play": "flyout",           # air DPs; ground DPs covered by grounded_into_double_play
    "triple_play": "groundout",
    "sac_bunt": "other",
    "sac_bunt_double_play": "other",
    "catcher_interf": "other",
    "field_error": "other",
    "other_out": "other",
    # field_out handled separately via bb_type below
}

# For "field_out" (the most common out event in Statcast), use bb_type to disambiguate
BB_TYPE_GROUNDOUT = {"ground_ball"}
BB_TYPE_FLYOUT    = {"fly_ball", "line_drive", "popup"}

OUTCOME_ORDER = ["single", "double", "triple", "home_run", "walk", "strikeout", "groundout", "flyout", "other"]

def fetch_all():
    frames = []
    for start, end in SEASONS:
        print(f"Fetching {start} → {end} …")
        df = statcast(start_dt=start, end_dt=end)
        frames.append(df)
        print(f"  got {len(df):,} pitches")
    return pd.concat(frames, ignore_index=True)


def process(df):
    # Keep only final pitches of each PA (events is populated)
    pa = df[df["events"].notna()].copy()
    print(f"\nPlate appearances: {len(pa):,}")

    # Require known handedness and valid count
    pa = pa[pa["stand"].isin(["L", "R"]) & pa["p_throws"].isin(["L", "R"])]
    pa = pa[pa["balls"].between(0, 3) & pa["strikes"].between(0, 2)]

    # Map to simplified outcome
    pa["outcome"] = pa["events"].map(OUTCOME_MAP)

    # field_out: use bb_type to classify as groundout or flyout
    is_field_out = pa["events"] == "field_out"
    pa.loc[is_field_out & pa["bb_type"].isin(BB_TYPE_GROUNDOUT), "outcome"] = "groundout"
    pa.loc[is_field_out & pa["bb_type"].isin(BB_TYPE_FLYOUT),    "outcome"] = "flyout"
    pa.loc[is_field_out & ~pa["bb_type"].isin(BB_TYPE_GROUNDOUT | BB_TYPE_FLYOUT), "outcome"] = "other"

    # Any remaining NaN → other
    pa["outcome"] = pa["outcome"].fillna("other")

    # Count by group
    grp = (
        pa.groupby(["stand", "p_throws", "balls", "strikes", "outcome"])
        .size()
        .reset_index(name="n")
    )

    # Pivot to wide, compute proportions
    records = []
    for (stand, p_throws, balls, strikes), sub in grp.groupby(["stand", "p_throws", "balls", "strikes"]):
        total = sub["n"].sum()
        counts_dict = dict(zip(sub["outcome"], sub["n"]))
        props = {o: round(counts_dict.get(o, 0) / total, 5) for o in OUTCOME_ORDER}
        raw   = {o: int(counts_dict.get(o, 0)) for o in OUTCOME_ORDER}
        records.append({
            "stand": stand,
            "p_throws": p_throws,
            "balls": int(balls),
            "strikes": int(strikes),
            "total": int(total),
            "props": props,
            "raw": raw,
        })

    return records


if __name__ == "__main__":
    df = fetch_all()
    records = process(df)
    out_path = "/Users/david/git/ab-outcome/docs/data.json"
    with open(out_path, "w") as f:
        json.dump(records, f)
    print(f"\nWrote {len(records)} records to {out_path}")
    # Quick sanity check
    total_pa = sum(r["total"] for r in records) // 4  # each PA counted in multiple groups? no — groups are disjoint
    print(f"Total plate appearances in dataset: {sum(r['total'] for r in records):,}")
