#!/usr/bin/env python3
"""Run three dependency-free mock policy cycles without contacting any robot."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

PRACTICE_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PRACTICE_ROOT))

from rl_deploy_lab import ActionProcessor, ObservationHistory, PolicyContract, SafetyGate  # noqa: E402


def make_frame(joint_count: int, command: list[float], phase: float) -> dict[str, list[float]]:
    return {
        "base_ang_vel": [0.01 * phase, -0.02 * phase, 0.0],
        "projected_gravity": [0.0, 0.0, -1.0],
        "velocity_commands": command,
        "joint_pos_rel": [0.001 * phase] * joint_count,
        "joint_vel_rel": [0.01 * phase] * joint_count,
        "last_action": [0.0] * joint_count,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("contract", type=Path)
    args = parser.parse_args()

    contract = PolicyContract.load(args.contract)
    history = ObservationHistory(contract)
    actions = ActionProcessor(contract)
    gate = SafetyGate(contract)
    command = [0.2, 0.0, 0.0]

    if contract.data.get("deployment_authorized") is not False:
        raise RuntimeError("本脚本只允许运行明确禁止真机部署的教学契约")

    print("MOCK ONLY：不连接 SDK，不发送电机命令")
    for cycle in range(3):
        frame = make_frame(contract.joint_count, command, float(cycle))
        observation = history.push(frame)
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

        actor_output = [0.0] * contract.joint_count
        processed = actions.process(actor_output)
        estimated_torque = actions.compute_unclipped_pd_torque(
            processed,
            q_feedback_sdk_rad=processed.sdk_joint_targets_rad,
            dq_feedback_sdk_rad_s=[0.0] * contract.joint_count,
        )
        print(
            f"cycle={cycle}: obs={len(observation)} action={len(actor_output)} "
            f"safe={safety.allowed} sdk_target_first3={processed.sdk_joint_targets_rad[:3]} "
            f"pd_tau_first3={estimated_torque[:3]}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
