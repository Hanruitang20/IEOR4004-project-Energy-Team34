from __future__ import annotations
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
import pandas as pd

from src.data_preparation import ModelData, load_config, prepare_model_data
from src.optimization import solve_with_gurobi
from src.resident_candidates import load_resident_candidates

ROOT = Path(__file__).resolve().parents[1]


class ResidentCandidateTests(unittest.TestCase):
    def test_real_pins_replace_centroids_without_changing_demand_or_equity(self):
        base = prepare_model_data(ROOT, ROOT / "config/tract_case.json")
        new = prepare_model_data(ROOT, ROOT / "config/tract_resident_curbside_15m_cap150.json")
        source = pd.read_csv(ROOT / "data/resident_curbside_candidates_2026-11-18.csv")
        eligible = source.loc[source.candidate_eligible].set_index("location_id")
        result = new.curbside.set_index("location_id")
        self.assertEqual(set(eligible.index), set(result.index))
        self.assertEqual(len(result), 487)
        pd.testing.assert_frame_equal(eligible[["latitude", "longitude"]].sort_index(),
                                      result[["latitude", "longitude"]].sort_index())
        self.assertTrue(result.wanted_count.gt(0).all())
        self.assertTrue(result.borough_from_coordinates.notna().all())
        self.assertEqual(new.config["curbside_max_sites"], 150)
        self.assertEqual(new.config["planning_horizon_years"], 5)
        pd.testing.assert_frame_equal(base.demand[["demand_id", "projected_demand_kwh", "equity_shortage_score"]],
                                      new.demand[["demand_id", "projected_demand_kwh", "equity_shortage_score"]])
        self.assertEqual(new.audit["resident_source_locations"], 544)
        self.assertEqual(new.audit["resident_excluded_locations"], 57)

    def test_bad_ids_coordinates_or_support_are_rejected(self):
        source = pd.read_csv(ROOT / "data/resident_curbside_candidates_2026-11-18.csv")
        valid = source.loc[source.candidate_eligible].head(1).copy()
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "candidates.csv"
            for field, value in [("latitude", 100), ("longitude", float("inf")),
                                 ("wanted_count", 0), ("candidate_eligible", "unknown")]:
                bad = valid.copy(); bad[field] = value; bad.to_csv(path, index=False)
                with self.subTest(field=field), self.assertRaises(ValueError):
                    load_resident_candidates(path)
            pd.concat([valid, valid]).to_csv(path, index=False)
            with self.assertRaises(ValueError): load_resident_candidates(path)

    def test_site_cap_is_an_integer_and_never_silently_rounded(self):
        config = json.loads((ROOT / "config/tract_resident_curbside_15m_cap150.json").read_text())
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "config.json"
            for value in [-1, 2.5, float("inf")]:
                config["curbside_max_sites"] = value; path.write_text(json.dumps(config))
                with self.subTest(value=value), self.assertRaises(ValueError): load_config(path)


@unittest.skipUnless(importlib.util.find_spec("gurobipy"), "gurobipy is not installed")
class CurbsideSiteCapSolverTests(unittest.TestCase):
    def make_data(self, cap):
        cfg = dict(budget_usd=1000., mip_gap=0., time_limit_seconds=10,
                   equity_lambda=0., scenario_name="tiny_station_cap",
                   annual_demand_growth_rate=0., planning_horizon_years=5,
                   service_radius_miles=.5, curbside_max_sites=cap)
        municipal = pd.DataFrame([dict(site_id="M:j", facility_id="j", existing_ports=0,
            max_additional_ports=0, applicable_fixed_cost_usd=20., port_cost_usd=10.,
            added_port_capacity_kwh=10.)])
        curbside = pd.DataFrame([dict(site_id="C:"+x, existing_ports=0,
            ports_per_site=4, site_cost_usd=100., site_capacity_kwh=40.,
            added_port_capacity_kwh=10.) for x in ["a", "b"]])
        sites = pd.DataFrame([dict(site_id=s, existing_capacity_kwh=0.,
            added_port_capacity_kwh=10.) for s in ["M:j", "C:a", "C:b"]])
        demand = pd.DataFrame([dict(demand_id="i", baseline_demand_kwh=100.,
                                   projected_demand_kwh=100., equity_shortage_score=0.)])
        pairs = pd.DataFrame([dict(demand_id="i", site_id=s, distance_miles=.1)
                              for s in sites.site_id])
        return ModelData(cfg, demand, municipal, sites, pairs, pd.DataFrame(), {}, curbside)

    def test_cap_counts_stations_not_ports_and_zero_prevents_opening(self):
        for cap in [0, 1, 2]:
            with self.subTest(cap=cap):
                result = solve_with_gurobi(self.make_data(cap))
                self.assertEqual(result.summary["selected_curbside_sites"], cap)
                self.assertEqual(result.summary["curbside_ports"], 4*cap)
                self.assertAlmostEqual(result.summary["total_served_kwh"], 40*cap, places=3)
                self.assertTrue(result.sanity_checks["curbside_site_limit_holds"])
                self.assertTrue(result.sanity_checks["all_checks_pass"])


if __name__ == "__main__": unittest.main()
