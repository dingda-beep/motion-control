#!/usr/bin/env python3
"""Validate and summarize a policy deployment contract."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

PRACTICE_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PRACTICE_ROOT))

from rl_deploy_lab import ContractError, PolicyContract  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("contract", type=Path, help="policy contract JSON")
    args = parser.parse_args()

    try:
        contract = PolicyContract.load(args.contract)
    except (OSError, ValueError, ContractError) as error:
        print(f"FAIL: {error}", file=sys.stderr)
        return 1

    data = contract.data
    timing = data["timing"]
    one_frame = sum(term["size"] for term in data["observations"]["terms"])
    print("PASS: 策略契约内部一致")
    print(f"机器人: {data['robot']['name']}")
    print(f"关节: {contract.joint_count}")
    print(
        "观测: "
        f"{one_frame} 维/帧 × {data['observations']['history_length']} 帧 "
        f"= {contract.observation_dimension} 维"
    )
    print(f"动作: {data['actions']['size']} 维，类型={data['actions']['type']}")
    motor = data["motor_interface"]
    print(
        "电机接口: "
        f"q_des=策略目标, dq_des={motor['desired_joint_velocity_rad_s']}, "
        f"tau_ff={motor['feedforward_torque_nm']}"
    )
    print(
        "周期: "
        f"{timing['physics_dt_s']}s × {timing['decimation']} "
        f"= {timing['policy_period_s']}s"
    )
    print(f"真机部署授权: {data['deployment_authorized']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
