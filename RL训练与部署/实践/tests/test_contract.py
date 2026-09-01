from __future__ import annotations

import copy
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from rl_deploy_lab import ContractError, PolicyContract


CONTRACT_PATH = ROOT / "config" / "g1_29dof_policy_contract.example.json"


def load_data() -> dict:
    return json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))


class PolicyContractTests(unittest.TestCase):
    def test_reference_contract_is_consistent(self) -> None:
        contract = PolicyContract.load(CONTRACT_PATH)
        self.assertEqual(contract.joint_count, 29)
        self.assertEqual(contract.observation_dimension, 480)

    def test_rejects_wrong_declared_observation_dimension(self) -> None:
        data = load_data()
        data["observations"]["declared_dimension"] = 481
        with self.assertRaisesRegex(ContractError, "推导应为 480"):
            PolicyContract(data).validate()

    def test_rejects_duplicate_joint_mapping(self) -> None:
        data = load_data()
        data["robot"]["policy_to_sdk"][-1] = data["robot"]["policy_to_sdk"][-2]
        with self.assertRaisesRegex(ContractError, "双射"):
            PolicyContract(data).validate()

    def test_rejects_timing_mismatch(self) -> None:
        data = load_data()
        data["timing"]["policy_period_s"] = 0.01
        with self.assertRaisesRegex(ContractError, "必须等于"):
            PolicyContract(data).validate()

    def test_rejects_joint_name_mapping_that_only_matches_shape(self) -> None:
        data = copy.deepcopy(load_data())
        names = data["robot"]["policy_joint_names"]
        names[0], names[1] = names[1], names[0]
        with self.assertRaisesRegex(ContractError, "关节名称不一致"):
            PolicyContract(data).validate()


if __name__ == "__main__":
    unittest.main()
