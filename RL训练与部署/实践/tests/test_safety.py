"""安全闸门测试：证明放行采用 fail-closed，而不是策略自己判断安全。"""

from __future__ import annotations

import math
import sys
import unittest
from pathlib import Path

# 直接导入实践源码，测试不依赖安装步骤。
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from rl_deploy_lab import PolicyContract, SafetyGate


CONTRACT = PolicyContract.load(ROOT / "config" / "g1_29dof_policy_contract.example.json")


class SafetyGateTests(unittest.TestCase):
    """覆盖正常放行和四类必须拒绝的边界。"""

    def setUp(self) -> None:
        """为每个测试创建独立闸门。"""

        self.gate = SafetyGate(CONTRACT)

    def test_accepts_fresh_finite_state_in_command_bounds(self) -> None:
        """状态新鲜、姿态正常、命令在训练范围内时才允许通过。"""

        result = self.gate.check(
            state_age_s=0.01,
            roll_rad=0.1,
            pitch_rad=-0.2,
            command=[0.2, 0.0, 0.0],
            state_values=[0.0] * 480,
        )
        self.assertTrue(result.allowed)

    def test_rejects_stale_state(self) -> None:
        """状态年龄超过 0.1 秒时拒绝继续使用旧反馈控制现在。"""

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
        """姿态越界与 NaN 同时出现时，两项原因都应被保留。"""

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
        """上层命令超出训练能力包络时，不允许直接交给策略。"""

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
