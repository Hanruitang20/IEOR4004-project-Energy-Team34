from __future__ import annotations

import unittest
from pathlib import Path

import numpy as np

from src.data_preparation import haversine_matrix_miles, prepare_model_data


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


if __name__ == "__main__":
    unittest.main()
