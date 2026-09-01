"""动作接口：把 Actor 输出变成电机位置式 PD 接口需要的完整命令。"""

from __future__ import annotations

import math
from collections.abc import Sequence
from dataclasses import dataclass

from .contract import PolicyContract, expand_scale


@dataclass(frozen=True)
class ProcessedAction:
    """一次动作处理的全部中间结果，便于逐层检查，而不是只留下最终数组。"""

    # 裁剪后的 Actor 原始动作；它没有单位，也还不是关节角度。
    normalized: list[float]
    # 按训练策略关节顺序排列的 q_des，单位 rad。
    policy_joint_targets_rad: list[float]
    # 同一组 q_des 改排为机器人 SDK 的电机顺序，单位 rad。
    sdk_joint_targets_rad: list[float]
    # 位置式 PD 的 dq_des；本示例为 0，但接口必须显式携带。
    sdk_joint_velocity_targets_rad_s: list[float]
    # 下面三项与 SDK 电机顺序一致，不能再按策略顺序解释。
    sdk_kp: list[float]
    sdk_kd: list[float]
    sdk_feedforward_torque_nm: list[float]


class ActionProcessor:
    """实现部署端的动作后处理，不负责 Actor 推理，也不直接发送电机命令。"""

    def __init__(self, contract: PolicyContract):
        # 契约集中保存训练端与部署端必须完全一致的动作语义。
        self.contract = contract

    def process(self, actor_output: Sequence[float]) -> ProcessedAction:
        """把一维 Actor 输出依次做校验、裁剪、缩放、偏置和关节重排。"""

        config = self.contract.data["actions"]
        size = int(config["size"])

        # 第一层防线：维度正确不代表数据正确，NaN/Inf 也必须在发命令前拒绝。
        normalized = [float(value) for value in actor_output]
        if len(normalized) != size:
            raise ValueError(f"actor 应输出 {size} 维，实际为 {len(normalized)} 维")
        if not all(math.isfinite(value) for value in normalized):
            raise ValueError("actor 输出含 NaN 或 Inf")

        clip = config.get("normalized_clip")
        if clip is not None:
            lower, upper = map(float, clip)
            normalized = [min(max(value, lower), upper) for value in normalized]

        # Actor 输出 a 没有 rad 单位。这里落实教程主线：q_des = q_default + scale × a。
        scales = expand_scale(config["scale_rad"], size)
        offsets = [float(value) for value in config["default_joint_pos_rad"]]
        policy_targets = [
            offset + scale * action
            for offset, scale, action in zip(offsets, scales, normalized)
        ]

        # 训练环境和 SDK 往往使用不同关节顺序。只按数组长度复制会让命令发错电机。
        mapping = self.contract.data["robot"]["policy_to_sdk"]
        sdk_targets = [0.0] * size
        for policy_index, sdk_index in enumerate(mapping):
            sdk_targets[sdk_index] = policy_targets[policy_index]

        # Actor 在本例只决定 q_des；dq_des、Kp、Kd、tau_ff 来自部署契约。
        # 这与成熟部署程序把网络输出再组装为低层电机包的做法一致。
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
        """按 PD 公式估算未限幅力矩；用于讲解和测试，不冒充真实驱动器。"""

        count = self.contract.joint_count
        # q、dq 必须来自编码器/驱动反馈，并且必须与命令采用相同的 SDK 顺序。
        q = [float(value) for value in q_feedback_sdk_rad]
        dq = [float(value) for value in dq_feedback_sdk_rad_s]
        if len(q) != count or len(dq) != count:
            raise ValueError(f"q 和 dq 反馈都必须是 {count} 维 SDK 顺序数组")
        if not all(math.isfinite(value) for value in q + dq):
            raise ValueError("q 或 dq 反馈含 NaN/Inf")

        # 真实硬件还会有限流、力矩饱和、温度保护和驱动器内部动态；这里故意不模拟。
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
