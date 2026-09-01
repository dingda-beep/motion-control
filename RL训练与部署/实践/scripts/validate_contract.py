#!/usr/bin/env python3
"""校验并摘要显示策略部署契约，任何错误都在启动控制循环前暴露。"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# 让脚本无需安装 Python 包也能导入相邻的教学模块。
PRACTICE_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PRACTICE_ROOT))

from rl_deploy_lab import ContractError, PolicyContract  # noqa: E402


def main() -> int:
    """读取命令行中的契约路径，校验成功返回 0，失败返回 1。"""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("contract", type=Path, help="策略部署契约 JSON 文件")
    args = parser.parse_args()

    try:
        contract = PolicyContract.load(args.contract)
    except (OSError, ValueError, ContractError) as error:
        # 错误写到 stderr，自动化流水线可以凭返回码阻止错误发布包继续流转。
        print(f"FAIL: {error}", file=sys.stderr)
        return 1

    # 校验通过后再读取字段；下面的输出是给人看的摘要，不替代机器校验。
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
