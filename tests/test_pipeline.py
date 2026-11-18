from __future__ import annotations

import unittest
from pathlib import Path

import numpy as np
import pandas as pd

from src.data_preparation import (
    allocate_zip_demand_to_tracts,
    haversine_matrix_miles,
    prepare_model_data,
    municipal_operating_hours,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]


class DataPreparationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.data = prepare_model_data(
            PROJECT_ROOT, PROJECT_ROOT / "config" / "base_case.json"
        )

    def test_haversine_identity(self) -> None:
        distance = haversine_matrix_miles(
            np.array([40.75]), np.array([-73.99]), np.array([40.75]), np.array([-73.99])
        )
        self.assertAlmostEqual(float(distance[0, 0]), 0.0, places=10)

    def test_accessibility_pairs_respect_radius(self) -> None:
        self.assertLessEqual(
            float(self.data.accessible_pairs["distance_miles"].max()),
            float(self.data.config["service_radius_miles"]) + 1e-10,
        )

    def test_equity_score_bounds(self) -> None:
        score = self.data.demand["equity_shortage_score"]
        self.assertTrue(score.between(0.0, 1.0).all())

    def test_site_ids_are_unique(self) -> None:
        self.assertFalse(self.data.sites["site_id"].duplicated().any())

    def test_installation_limits_are_nonnegative_integers(self) -> None:
        limits = self.data.municipal["max_additional_ports"]
        self.assertTrue(limits.ge(0).all())
        self.assertTrue((limits == limits.astype(int)).all())

    def test_uniform_twenty_percent_installation_limits(self) -> None:
        m = self.data.municipal
        self.assertEqual(self.data.config["max_new_port_share_of_remaining_spaces"], 0.2)
        remaining = (m["Parking spaces"].astype(int) - m["existing_ports"]).clip(lower=0)
        expected = np.minimum(20, np.floor(remaining * 0.2).astype(int))
        np.testing.assert_array_equal(m["max_additional_ports"], expected)

    def test_hours_scale_existing_and_added_capacity(self) -> None:
        m = self.data.municipal.set_index("facility_id")
        self.assertAlmostEqual(m.at["belmont", "added_port_capacity_kwh"], 7.2 * 90 * .9)
        self.assertAlmostEqual(m.at["gunhill", "existing_capacity_kwh"],
                               m.at["gunhill", "existing_ports"] * 7.2 * 112 * .9)
        np.testing.assert_allclose(m["existing_capacity_kwh"],
                                   m["existing_ports"] * m["added_port_capacity_kwh"])
        other = self.data.sites.loc[self.data.sites["site_type"].eq("other")]
        self.assertTrue(other["operating_hours_per_week"].eq(168).all())

    def test_fixed_cost_absorbs_first_time_indicator(self) -> None:
        m = self.data.municipal
        expected = np.where(m["existing_ports"].eq(0),
                            self.data.config["fixed_first_time_install_cost_usd"], 0.0)
        np.testing.assert_array_equal(m["applicable_fixed_cost_usd"], expected)
        self.assertNotIn("first_time_install_indicator", m.columns)

    def test_missing_and_invalid_hours_fail_instead_of_defaulting(self) -> None:
        for value in [None, "unknown", -1, 169, float("inf")]:
            with self.subTest(value=value), self.assertRaises(ValueError):
                municipal_operating_hours(pd.DataFrame({
                    "Facility ID": ["test"], "Scheduled hours/week": [value]}))
        with self.assertRaises(ValueError):
            municipal_operating_hours(pd.DataFrame({"Facility ID": ["test"]}))
        self.assertEqual(municipal_operating_hours(pd.DataFrame({
            "Facility ID": ["closed"], "Scheduled hours/week": [0]})).iloc[0], 0)

    def test_hud_residential_ratio_allocation_conserves_matched_records(self) -> None:
        zip_demand = pd.DataFrame(
            {
                "zip": ["10001", "10002"],
                "electric_registration_records": [100.0, 40.0],
            }
        )
        crosswalk = pd.DataFrame(
            {
                "zip": ["10001", "10001", "10002", "99999"],
                "tract_geoid": [
                    "36061000100",
                    "36061000200",
                    "36061000200",
                    "34001000100",
                ],
                "res_ratio": [0.25, 0.75, 0.50, 1.0],
            }
        )
        tracts = pd.DataFrame(
            {
                "tract_geoid": ["36061000100", "36061000200"],
                "latitude": [40.7, 40.8],
                "longitude": [-74.0, -73.9],
            }
        )
        allocated, audit = allocate_zip_demand_to_tracts(zip_demand, crosswalk, tracts)
        by_tract = allocated.set_index("tract_geoid")["electric_registration_records"]
        self.assertAlmostEqual(float(by_tract["36061000100"]), 25.0)
        self.assertAlmostEqual(float(by_tract["36061000200"]), 115.0)
        self.assertAlmostEqual(float(by_tract.sum()), 140.0)
        self.assertAlmostEqual(float(audit["allocation_conservation_error_records"]), 0.0)


class CurbsideExtensionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.base = prepare_model_data(PROJECT_ROOT, PROJECT_ROOT / "config" / "tract_case.json")
        cls.curb = prepare_model_data(
            PROJECT_ROOT, PROJECT_ROOT / "config" / "tract_curbside_case.json"
        )

    def test_base_case_has_no_curbside_candidates(self) -> None:
        self.assertEqual(len(self.base.curbside), 0)
        self.assertFalse(self.base.sites["site_type"].eq("curbside").any())

    def test_curbside_candidates_are_unserved_demand_points(self) -> None:
        c = self.curb.curbside
        self.assertGreater(len(c), 0)
        unserved = self.curb.demand.loc[
            self.curb.demand["accessible_existing_supply_kwh"] <= 1e-9, "geography_id"
        ].astype(str)
        self.assertEqual(set(c["geography_id"].astype(str)), set(unserved))
        self.assertFalse(self.curb.sites["site_id"].duplicated().any())

    def test_curbside_capacity_and_cost_follow_config(self) -> None:
        cfg = self.curb.config
        c = self.curb.curbside
        per_port = (
            cfg["port_power_kw"]
            * cfg["curbside_weekly_operating_hours"]
            * cfg["curbside_availability_factor"]
        )
        np.testing.assert_allclose(c["site_capacity_kwh"], per_port * cfg["curbside_ports_per_site"])
        np.testing.assert_allclose(
            c["site_cost_usd"],
            cfg["curbside_fixed_cost_per_site_usd"]
            + cfg["curbside_ports_per_site"] * cfg["curbside_cost_per_port_usd"],
        )
        self.assertTrue(c["existing_capacity_kwh"].eq(0).all())

    def test_curbside_does_not_change_demand_or_equity(self) -> None:
        cols = ["demand_id", "projected_demand_kwh", "equity_shortage_score"]
        pd.testing.assert_frame_equal(
            self.base.demand[cols].reset_index(drop=True),
            self.curb.demand[cols].reset_index(drop=True),
        )

    def test_curbside_pairs_respect_radius(self) -> None:
        pairs = self.curb.accessible_pairs
        curb_pairs = pairs.loc[pairs["site_id"].str.startswith("C:")]
        self.assertGreater(len(curb_pairs), 0)
        self.assertLessEqual(
            float(curb_pairs["distance_miles"].max()),
            float(self.curb.config["service_radius_miles"]) + 1e-10,
        )
        base_pairs = pairs.loc[~pairs["site_id"].str.startswith("C:")]
        self.assertEqual(len(base_pairs), len(self.base.accessible_pairs))


if __name__ == "__main__":
    unittest.main()
