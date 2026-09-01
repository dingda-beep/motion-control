from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from rl_deploy_lab import ObservationHistory, PolicyContract


CONTRACT = PolicyContract.load(ROOT / "config" / "g1_29dof_policy_contract.example.json")


def frame(base_value: float) -> dict[str, list[float]]:
    return {
        "base_ang_vel": [base_value, 2.0, 3.0],
        "projected_gravity": [0.0, 0.0, -1.0],
        "velocity_commands": [0.2, 0.0, 0.0],
        "joint_pos_rel": [0.0] * 29,
        "joint_vel_rel": [10.0] * 29,
        "last_action": [0.0] * 29,
    }


class ObservationHistoryTests(unittest.TestCase):
    def test_builds_480_dimensions(self) -> None:
        result = ObservationHistory(CONTRACT).push(frame(1.0))
        self.assertEqual(len(result), 480)

    def test_scales_values_and_repeats_first_frame(self) -> None:
        result = ObservationHistory(CONTRACT).push(frame(1.0))
        self.assertEqual(result[:3], [0.2, 0.4, 0.6000000000000001])
        self.assertEqual(result[3:6], [0.2, 0.4, 0.6000000000000001])

        joint_velocity_start = (3 * 5) + (3 * 5) + (3 * 5) + (29 * 5)
        self.assertEqual(result[joint_velocity_start], 0.5)

    def test_layout_is_term_major_oldest_to_newest(self) -> None:
        history = ObservationHistory(CONTRACT)
        history.push(frame(1.0))
        result = history.push(frame(5.0))
        base_history = result[: 3 * 5]
        self.assertEqual(base_history[-3:], [1.0, 0.4, 0.6000000000000001])
        self.assertEqual(base_history[:3], [0.2, 0.4, 0.6000000000000001])

    def test_rejects_missing_term(self) -> None:
        bad = frame(1.0)
        del bad["last_action"]
        with self.assertRaisesRegex(ValueError, "last_action"):
            ObservationHistory(CONTRACT).push(bad)


if __name__ == "__main__":
    unittest.main()
