from __future__ import annotations

import unittest
from pathlib import Path

import numpy as np
import pandas as pd

from src.data_preparation import (
    allocate_zip_demand_to_tracts,
    haversine_matrix_miles,
    prepare_model_data,
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


if __name__ == "__main__":
    unittest.main()
