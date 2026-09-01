"""Turn normalized actor output into policy-order and SDK-order joint targets."""

from __future__ import annotations

import math
from collections.abc import Sequence
from dataclasses import dataclass

from .contract import PolicyContract, expand_scale


@dataclass(frozen=True)
class ProcessedAction:
    normalized: list[float]
    policy_joint_targets_rad: list[float]
    sdk_joint_targets_rad: list[float]
    sdk_joint_velocity_targets_rad_s: list[float]
    sdk_kp: list[float]
    sdk_kd: list[float]
    sdk_feedforward_torque_nm: list[float]


class ActionProcessor:
    def __init__(self, contract: PolicyContract):
        self.contract = contract

    def process(self, actor_output: Sequence[float]) -> ProcessedAction:
        config = self.contract.data["actions"]
        size = int(config["size"])
        normalized = [float(value) for value in actor_output]
        if len(normalized) != size:
            raise ValueError(f"actor 应输出 {size} 维，实际为 {len(normalized)} 维")
        if not all(math.isfinite(value) for value in normalized):
            raise ValueError("actor 输出含 NaN 或 Inf")

        clip = config.get("normalized_clip")
        if clip is not None:
            lower, upper = map(float, clip)
            normalized = [min(max(value, lower), upper) for value in normalized]

        scales = expand_scale(config["scale_rad"], size)
        offsets = [float(value) for value in config["default_joint_pos_rad"]]
        policy_targets = [
            offset + scale * action
            for offset, scale, action in zip(offsets, scales, normalized)
        ]

        mapping = self.contract.data["robot"]["policy_to_sdk"]
        sdk_targets = [0.0] * size
        for policy_index, sdk_index in enumerate(mapping):
            sdk_targets[sdk_index] = policy_targets[policy_index]

        motor = self.contract.data["motor_interface"]
        return ProcessedAction(
            normalized=normalized,
            policy_joint_targets_rad=policy_targets,
            sdk_joint_targets_rad=sdk_targets,
            sdk_joint_velocity_targets_rad_s=expand_scale(
                motor["desired_joint_velocity_rad_s"], size
            ),
            sdk_kp=expand_scale(motor["kp_sdk_order"], size),
            sdk_kd=expand_scale(motor["kd_sdk_order"], size),
            sdk_feedforward_torque_nm=expand_scale(motor["feedforward_torque_nm"], size),
        )

    def compute_unclipped_pd_torque(
        self,
        processed: ProcessedAction,
        q_feedback_sdk_rad: Sequence[float],
        dq_feedback_sdk_rad_s: Sequence[float],
    ) -> list[float]:
        """Evaluate the contract's PD equation without modeling hardware saturation."""

        count = self.contract.joint_count
        q = [float(value) for value in q_feedback_sdk_rad]
        dq = [float(value) for value in dq_feedback_sdk_rad_s]
        if len(q) != count or len(dq) != count:
            raise ValueError(f"q 和 dq 反馈都必须是 {count} 维 SDK 顺序数组")
        if not all(math.isfinite(value) for value in q + dq):
            raise ValueError("q 或 dq 反馈含 NaN/Inf")

        return [
            tau_ff + kp * (q_des - q_now) + kd * (dq_des - dq_now)
            for tau_ff, kp, q_des, q_now, kd, dq_des, dq_now in zip(
                processed.sdk_feedforward_torque_nm,
                processed.sdk_kp,
                processed.sdk_joint_targets_rad,
                q,
                processed.sdk_kd,
                processed.sdk_joint_velocity_targets_rad_s,
                dq,
            )
        ]
