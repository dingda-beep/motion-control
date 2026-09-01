"""奖励账本测试：用可手算场景固定奖励变换的真实含义。"""

from __future__ import annotations

import json
import math
import sys
import unittest
from pathlib import Path

# 从实践根目录读取源码和奖励场景。
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from rl_deploy_lab import RewardLedger


CONFIG_PATH = ROOT / "config" / "reward_scenarios.example.json"


class RewardLedgerTests(unittest.TestCase):
    """检查奖励项变换、加权以及坏配置拒绝。"""

    def setUp(self) -> None:
        """每个测试重新创建账本，保证测试互不影响。"""

        config = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
        self.ledger = RewardLedger(config["terms"])
        self.scenarios = config["scenarios"]

    def test_exact_tracking_has_unit_transformed_reward(self) -> None:
        """速度误差为零时，指数跟踪奖励 exp(0) 应等于 1。"""

        result = self.ledger.evaluate(
            self.scenarios[0]["name"], self.scenarios[0]["metrics"]
        )
        tracking = result.contributions[0]
        self.assertEqual(tracking.transformed, 1.0)
        self.assertEqual(tracking.contribution, 1.0)

    def test_half_meter_error_with_half_meter_sigma_is_exp_minus_one(self) -> None:
        """误差恰好等于 sigma 时，指数核应得到 exp(-1)。"""

        result = self.ledger.evaluate(
            self.scenarios[1]["name"], self.scenarios[1]["metrics"]
        )
        self.assertAlmostEqual(result.contributions[0].transformed, math.exp(-1.0))

    def test_missing_metric_is_rejected(self) -> None:
        """奖励配置引用了环境未提供的指标时必须立即报错。"""

        with self.assertRaisesRegex(ValueError, "缺少指标"):
            self.ledger.evaluate("bad", {})


if __name__ == "__main__":
    unittest.main()
