"""观测测试：固定每个数字的位置，防止部署端悄悄改变 Actor 输入语义。"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

# 直接使用实践目录中的源码和契约。
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from rl_deploy_lab import ObservationHistory, PolicyContract


CONTRACT = PolicyContract.load(ROOT / "config" / "g1_29dof_policy_contract.example.json")


def frame(base_value: float) -> dict[str, list[float]]:
    """构造一帧易于手算缩放结果的假观测。"""

    return {
        "base_ang_vel": [base_value, 2.0, 3.0],
        "projected_gravity": [0.0, 0.0, -1.0],
        "velocity_commands": [0.2, 0.0, 0.0],
        "joint_pos_rel": [0.0] * 29,
        "joint_vel_rel": [10.0] * 29,
        "last_action": [0.0] * 29,
    }


class ObservationHistoryTests(unittest.TestCase):
    """覆盖维度、缩放、历史布局、重置填充和缺项拒绝。"""

    def test_builds_480_dimensions(self) -> None:
        """验证单帧 96 维乘 5 帧得到 Actor 所需 480 维。"""

        result = ObservationHistory(CONTRACT).push(frame(1.0))
        self.assertEqual(len(result), 480)

    def test_scales_values_and_repeats_first_frame(self) -> None:
        """验证首帧重复填满历史，并按各观测项独立缩放。"""

        result = ObservationHistory(CONTRACT).push(frame(1.0))
        # base_ang_vel 的 scale=0.2；前两组 3 维都应是同一个首帧。
        self.assertEqual(result[:3], [0.2, 0.4, 0.6000000000000001])
        self.assertEqual(result[3:6], [0.2, 0.4, 0.6000000000000001])

        # 跳过角速度、投影重力、命令和关节位置的全部历史，定位到关节速度。
        joint_velocity_start = (3 * 5) + (3 * 5) + (3 * 5) + (29 * 5)
        self.assertEqual(result[joint_velocity_start], 0.5)

    def test_layout_is_term_major_oldest_to_newest(self) -> None:
        """验证同一观测项的五帧历史相邻排列，且最新帧位于最后。"""

        history = ObservationHistory(CONTRACT)
        history.push(frame(1.0))
        result = history.push(frame(5.0))
        base_history = result[: 3 * 5]
        self.assertEqual(base_history[-3:], [1.0, 0.4, 0.6000000000000001])
        self.assertEqual(base_history[:3], [0.2, 0.4, 0.6000000000000001])

    def test_rejects_missing_term(self) -> None:
        """缺少 last_action 时必须指出缺项，不能用零值悄悄顶替。"""

        bad = frame(1.0)
        del bad["last_action"]
        with self.assertRaisesRegex(ValueError, "last_action"):
            ObservationHistory(CONTRACT).push(bad)


if __name__ == "__main__":
    unittest.main()
