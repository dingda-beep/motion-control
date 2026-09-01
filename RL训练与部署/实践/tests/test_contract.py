"""部署契约测试：故意制造“形状对、语义错”的常见 Sim2Real 故障。"""

from __future__ import annotations

import copy
import json
import sys
import unittest
from pathlib import Path

# 从实践根目录加载源码和示例配置。
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from rl_deploy_lab import ContractError, PolicyContract


CONTRACT_PATH = ROOT / "config" / "g1_29dof_policy_contract.example.json"


def load_data() -> dict:
    """每个破坏性测试重新读取 JSON，避免不同测试互相污染。"""

    return json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))


class PolicyContractTests(unittest.TestCase):
    """检查发布契约最重要的跨模块一致性。"""

    def test_reference_contract_is_consistent(self) -> None:
        """基准契约应得到 29 维动作和 480 维观测。"""

        contract = PolicyContract.load(CONTRACT_PATH)
        self.assertEqual(contract.joint_count, 29)
        self.assertEqual(contract.observation_dimension, 480)

    def test_rejects_wrong_declared_observation_dimension(self) -> None:
        """手写总维度与明细推导不一致时必须拒绝。"""

        data = load_data()
        data["observations"]["declared_dimension"] = 481
        with self.assertRaisesRegex(ContractError, "推导应为 480"):
            PolicyContract(data).validate()

    def test_rejects_duplicate_joint_mapping(self) -> None:
        """两个策略关节指向同一电机时，数组长度仍正确但语义已经损坏。"""

        data = load_data()
        data["robot"]["policy_to_sdk"][-1] = data["robot"]["policy_to_sdk"][-2]
        with self.assertRaisesRegex(ContractError, "双射"):
            PolicyContract(data).validate()

    def test_rejects_timing_mismatch(self) -> None:
        """策略周期必须等于物理步长乘以 decimation。"""

        data = load_data()
        data["timing"]["policy_period_s"] = 0.01
        with self.assertRaisesRegex(ContractError, "必须等于"):
            PolicyContract(data).validate()

    def test_rejects_joint_name_mapping_that_only_matches_shape(self) -> None:
        """关节名与映射不一致时，不能因为 29 对 29 就放行。"""

        data = copy.deepcopy(load_data())
        names = data["robot"]["policy_joint_names"]
        names[0], names[1] = names[1], names[0]
        with self.assertRaisesRegex(ContractError, "关节名称不一致"):
            PolicyContract(data).validate()


if __name__ == "__main__":
    unittest.main()
