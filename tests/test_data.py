import json
import unittest
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
import sys
sys.path.insert(0, str(ROOT))
import fetch_data  # noqa: E402


def _pa(events, stand="R", p_throws="R", balls=0, strikes=0, bb_type=None):
    return dict(events=events, stand=stand, p_throws=p_throws,
                balls=balls, strikes=strikes, bb_type=bb_type)


class ProcessTests(unittest.TestCase):
    def run_process(self, rows):
        return fetch_data.process(pd.DataFrame(rows))

    def test_field_out_uses_bb_type(self):
        recs = self.run_process([
            _pa("field_out", bb_type="ground_ball"),
            _pa("field_out", bb_type="fly_ball"),
            _pa("field_out", bb_type="popup"),
            _pa("field_out", bb_type=None),
        ])
        raw = recs[0]["raw"]
        self.assertEqual((raw["groundout"], raw["flyout"], raw["other"]), (1, 2, 1))

    def test_filters_non_plate_appearances_and_invalid_counts(self):
        recs = self.run_process([
            _pa(None),
            _pa("single", balls=4),
            _pa("single", strikes=3),
            _pa("single", stand="S"),
            _pa("single"),
        ])
        self.assertEqual(sum(r["total"] for r in recs), 1)

    def test_hbp_and_intent_walk_count_as_walk(self):
        recs = self.run_process([_pa("hit_by_pitch"), _pa("intent_walk")])
        self.assertEqual(recs[0]["raw"]["walk"], 2)

    def test_props_sum_to_one(self):
        recs = self.run_process([_pa("single"), _pa("strikeout", strikes=2)])
        for r in recs:
            self.assertAlmostEqual(sum(r["props"].values()), 1, places=3)


class DataJsonTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open(ROOT / "docs" / "data.json") as f:
            cls.data = json.load(f)

    def test_has_48_unique_records(self):
        keys = {(r["stand"], r["p_throws"], r["balls"], r["strikes"]) for r in self.data}
        self.assertEqual(len(self.data), 48)
        self.assertEqual(len(keys), 48)

    def test_raw_sums_to_total_and_props_sum_to_one(self):
        for r in self.data:
            self.assertEqual(sum(r["raw"].values()), r["total"])
            self.assertAlmostEqual(sum(r["props"].values()), 1, places=3)
            self.assertEqual(list(r["raw"]), fetch_data.OUTCOME_ORDER)


if __name__ == "__main__":
    unittest.main()
