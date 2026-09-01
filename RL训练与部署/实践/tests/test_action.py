from __future__ import annotations

import math
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from rl_deploy_lab import ActionProcessor, PolicyContract


CONTRACT = PolicyContract.load(ROOT / "config" / "g1_29dof_policy_contract.example.json")


class ActionProcessorTests(unittest.TestCase):
    def test_zero_action_means_default_pose(self) -> None:
        processed = ActionProcessor(CONTRACT).process([0.0] * 29)
        self.assertEqual(
            processed.policy_joint_targets_rad,
            CONTRACT.data["actions"]["default_joint_pos_rad"],
        )

    def test_scale_and_policy_to_sdk_mapping(self) -> None:
        actor_output = [0.0] * 29
        actor_output[1] = 0.4
        processed = ActionProcessor(CONTRACT).process(actor_output)
        self.assertAlmostEqual(processed.policy_joint_targets_rad[1], 0.0)
        self.assertAlmostEqual(processed.sdk_joint_targets_rad[6], 0.0)
        self.assertEqual(processed.sdk_joint_targets_rad[6], processed.policy_joint_targets_rad[1])

    def test_rejects_non_finite_action(self) -> None:
        with self.assertRaisesRegex(ValueError, "NaN"):
            ActionProcessor(CONTRACT).process([math.nan] + [0.0] * 28)

    def test_motor_packet_matches_reference_position_interface(self) -> None:
        processed = ActionProcessor(CONTRACT).process([0.0] * 29)
        self.assertEqual(processed.sdk_joint_velocity_targets_rad_s, [0.0] * 29)
        self.assertEqual(processed.sdk_feedforward_torque_nm, [0.0] * 29)
        self.assertEqual(processed.sdk_kp[:4], [100.0, 100.0, 100.0, 150.0])
        self.assertEqual(processed.sdk_kd[:4], [2.0, 2.0, 2.0, 4.0])

    def test_pd_equation_uses_feedback_and_desired_values(self) -> None:
        processor = ActionProcessor(CONTRACT)
        actor_output = [0.0] * 29
        actor_output[0] = 0.4
        processed = processor.process(actor_output)
        q_feedback = list(processed.sdk_joint_targets_rad)
        q_feedback[0] -= 0.1
        torque = processor.compute_unclipped_pd_torque(
            processed,
            q_feedback_sdk_rad=q_feedback,
            dq_feedback_sdk_rad_s=[0.0] * 29,
        )
        self.assertAlmostEqual(torque[0], 10.0)
        self.assertEqual(torque[1:], [0.0] * 28)


if __name__ == "__main__":
    unittest.main()
