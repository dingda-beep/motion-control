"""动作接口测试：证明每一步变换的含义，而不只检查代码能否运行。"""

from __future__ import annotations

import math
import sys
import unittest
from pathlib import Path

# 测试直接从源码目录导入教学包，不要求读者先执行 pip install。
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from rl_deploy_lab import ActionProcessor, PolicyContract


# 所有测试共享同一份已校验契约，避免测试自己另造一套动作语义。
CONTRACT = PolicyContract.load(ROOT / "config" / "g1_29dof_policy_contract.example.json")


class ActionProcessorTests(unittest.TestCase):
    """覆盖 Actor 动作到 SDK 电机包的关键不变量。"""

    def test_zero_action_means_default_pose(self) -> None:
        """验证 a=0 时 q_des=q_default，而不是让所有关节去 0 rad。"""

        processed = ActionProcessor(CONTRACT).process([0.0] * 29)
        self.assertEqual(
            processed.policy_joint_targets_rad,
            CONTRACT.data["actions"]["default_joint_pos_rad"],
        )

    def test_scale_and_policy_to_sdk_mapping(self) -> None:
        """验证动作先按策略顺序缩放，再准确重排到 SDK 顺序。"""

        actor_output = [0.0] * 29
        # 策略第 1 号关节在 SDK 中是第 6 号；0.4×0.25 rad 抵消默认的 -0.1 rad。
        actor_output[1] = 0.4
        processed = ActionProcessor(CONTRACT).process(actor_output)
        self.assertAlmostEqual(processed.policy_joint_targets_rad[1], 0.0)
        self.assertAlmostEqual(processed.sdk_joint_targets_rad[6], 0.0)
        self.assertEqual(processed.sdk_joint_targets_rad[6], processed.policy_joint_targets_rad[1])

    def test_rejects_non_finite_action(self) -> None:
        """验证 NaN 不会穿过动作接口进入电机命令。"""

        with self.assertRaisesRegex(ValueError, "NaN"):
            ActionProcessor(CONTRACT).process([math.nan] + [0.0] * 28)

    def test_motor_packet_matches_reference_position_interface(self) -> None:
        """验证 dq_des、tau_ff、Kp、Kd 确实来自部署契约。"""

        processed = ActionProcessor(CONTRACT).process([0.0] * 29)
        self.assertEqual(processed.sdk_joint_velocity_targets_rad_s, [0.0] * 29)
        self.assertEqual(processed.sdk_feedforward_torque_nm, [0.0] * 29)
        self.assertEqual(processed.sdk_kp[:4], [100.0, 100.0, 100.0, 150.0])
        self.assertEqual(processed.sdk_kd[:4], [2.0, 2.0, 2.0, 4.0])

    def test_pd_equation_uses_feedback_and_desired_values(self) -> None:
        """制造 0.1 rad 位置误差，验证 Kp=100 时比例项给出 10 N·m。"""

        processor = ActionProcessor(CONTRACT)
        actor_output = [0.0] * 29
        actor_output[0] = 0.4
        processed = processor.process(actor_output)
        q_feedback = list(processed.sdk_joint_targets_rad)
        # 只让 SDK 第 0 号关节比目标少 0.1 rad，其余关节完全贴合目标。
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
