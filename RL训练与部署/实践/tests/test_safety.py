from __future__ import annotations

import math
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from rl_deploy_lab import PolicyContract, SafetyGate


CONTRACT = PolicyContract.load(ROOT / "config" / "g1_29dof_policy_contract.example.json")


class SafetyGateTests(unittest.TestCase):
    def setUp(self) -> None:
        self.gate = SafetyGate(CONTRACT)

    def test_accepts_fresh_finite_state_in_command_bounds(self) -> None:
        result = self.gate.check(
            state_age_s=0.01,
            roll_rad=0.1,
            pitch_rad=-0.2,
            command=[0.2, 0.0, 0.0],
            state_values=[0.0] * 480,
        )
        self.assertTrue(result.allowed)

    def test_rejects_stale_state(self) -> None:
        result = self.gate.check(
            state_age_s=0.101,
            roll_rad=0.0,
            pitch_rad=0.0,
            command=[0.0, 0.0, 0.0],
            state_values=[0.0] * 480,
        )
        self.assertFalse(result.allowed)
        self.assertIn("状态年龄", result.reasons[0])

    def test_rejects_bad_orientation_and_nan(self) -> None:
        result = self.gate.check(
            state_age_s=0.0,
            roll_rad=0.81,
            pitch_rad=0.0,
            command=[0.0, 0.0, 0.0],
            state_values=[math.nan],
        )
        self.assertFalse(result.allowed)
        self.assertGreaterEqual(len(result.reasons), 2)

    def test_rejects_command_outside_training_envelope(self) -> None:
        result = self.gate.check(
            state_age_s=0.0,
            roll_rad=0.0,
            pitch_rad=0.0,
            command=[1.1, 0.0, 0.0],
            state_values=[0.0],
        )
        self.assertFalse(result.allowed)
        self.assertTrue(any("命令第 0 维" in reason for reason in result.reasons))


if __name__ == "__main__":
    unittest.main()
