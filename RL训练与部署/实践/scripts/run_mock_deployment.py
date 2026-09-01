#!/usr/bin/env python3
"""运行三个纯内存部署周期；不连接机器人，也不发送任何电机命令。"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# 允许直接从 scripts/ 运行，同时仍导入同一实践目录中的 rl_deploy_lab 包。
PRACTICE_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PRACTICE_ROOT))

from rl_deploy_lab import ActionProcessor, ObservationHistory, PolicyContract, SafetyGate  # noqa: E402


def make_frame(joint_count: int, command: list[float], phase: float) -> dict[str, list[float]]:
    """制造一帧可预测的假传感器数据，用来演示观测拼接而不是模拟物理。"""

    return {
        # 这些键名、维度与契约 observations.terms 一一对应。
        "base_ang_vel": [0.01 * phase, -0.02 * phase, 0.0],
        "projected_gravity": [0.0, 0.0, -1.0],
        "velocity_commands": command,
        "joint_pos_rel": [0.001 * phase] * joint_count,
        "joint_vel_rel": [0.01 * phase] * joint_count,
        "last_action": [0.0] * joint_count,
    }


def main() -> int:
    """串起“读契约 → 构造观测 → 安全检查 → 动作处理 → PD 估算”。"""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("contract", type=Path)
    args = parser.parse_args()

    contract = PolicyContract.load(args.contract)
    history = ObservationHistory(contract)
    actions = ActionProcessor(contract)
    gate = SafetyGate(contract)
    command = [0.2, 0.0, 0.0]

    # 双保险：即使有人传入其他契约，这个教学脚本也拒绝接近真机授权路径。
    if contract.data.get("deployment_authorized") is not False:
        raise RuntimeError("本脚本只允许运行明确禁止真机部署的教学契约")

    print("MOCK ONLY：不连接 SDK，不发送电机命令")
    for cycle in range(3):
        # 真实部署在这里读取 IMU、编码器和上层速度命令；本例只生成假数据。
        frame = make_frame(contract.joint_count, command, float(cycle))
        observation = history.push(frame)

        # 安全闸门位于策略外：即使 Actor 正常，也可能因为状态过旧而拒绝运行。
        safety = gate.check(
            state_age_s=0.005,
            roll_rad=0.01,
            pitch_rad=-0.02,
            command=command,
            state_values=observation,
        )
        if not safety.allowed:
            print(f"cycle={cycle}: REJECT {safety.reasons}")
            return 2

        # 用全零动作代替神经网络推理。按本契约，它表示“保持默认姿态”。
        actor_output = [0.0] * contract.joint_count
        processed = actions.process(actor_output)

        # 假设反馈刚好等于目标，PD 位置和速度误差都为零，因此估算力矩应为零。
        estimated_torque = actions.compute_unclipped_pd_torque(
            processed,
            q_feedback_sdk_rad=processed.sdk_joint_targets_rad,
            dq_feedback_sdk_rad_s=[0.0] * contract.joint_count,
        )
        # 打印每一层的维度和前三个值，让读者看见数据确实走完整条链路。
        print(
            f"cycle={cycle}: obs={len(observation)} action={len(actor_output)} "
            f"safe={safety.allowed} sdk_target_first3={processed.sdk_joint_targets_rad[:3]} "
            f"pd_tau_first3={estimated_torque[:3]}"
        )
    return 0


if __name__ == "__main__":
    # 把 main 的返回值交给 shell，便于脚本被自动化检查调用。
    raise SystemExit(main())
