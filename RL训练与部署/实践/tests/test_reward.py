from __future__ import annotations

import json
import math
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from rl_deploy_lab import RewardLedger


CONFIG_PATH = ROOT / "config" / "reward_scenarios.example.json"


class RewardLedgerTests(unittest.TestCase):
    def setUp(self) -> None:
        config = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
        self.ledger = RewardLedger(config["terms"])
        self.scenarios = config["scenarios"]

    def test_exact_tracking_has_unit_transformed_reward(self) -> None:
        result = self.ledger.evaluate(
            self.scenarios[0]["name"], self.scenarios[0]["metrics"]
        )
        tracking = result.contributions[0]
        self.assertEqual(tracking.transformed, 1.0)
        self.assertEqual(tracking.contribution, 1.0)

    def test_half_meter_error_with_half_meter_sigma_is_exp_minus_one(self) -> None:
        result = self.ledger.evaluate(
            self.scenarios[1]["name"], self.scenarios[1]["metrics"]
        )
        self.assertAlmostEqual(result.contributions[0].transformed, math.exp(-1.0))

    def test_missing_metric_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "缺少指标"):
            self.ledger.evaluate("bad", {})


if __name__ == "__main__":
    unittest.main()
