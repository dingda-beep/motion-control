"""策略外安全闸门：任一关键检查失败，都拒绝进入运动状态。"""

from __future__ import annotations

import math
from collections.abc import Sequence
from dataclasses import dataclass

from .contract import PolicyContract


@dataclass(frozen=True)
class SafetyResult:
    """安全检查结果；失败原因全部保留，便于定位而不是只返回 False。"""

    allowed: bool
    reasons: tuple[str, ...]


class SafetyGate:
    """检查状态新鲜度、姿态、数值有效性和命令训练边界。"""

    def __init__(self, contract: PolicyContract):
        self.contract = contract

    def check(
        self,
        *,
        state_age_s: float,
        roll_rad: float,
        pitch_rad: float,
        command: Sequence[float],
        state_values: Sequence[float],
    ) -> SafetyResult:
        """执行一次无副作用检查；本函数不会发命令，也不会自动恢复。"""

        reasons: list[str] = []
        timing = self.contract.data["timing"]
        safety = self.contract.data["safety"]

        # NaN 参与比较时可能让普通阈值判断失效，因此必须先单独拦截非有限数。
        scalar_values = [state_age_s, roll_rad, pitch_rad]
        if not all(math.isfinite(value) for value in scalar_values):
            reasons.append("时间或姿态含 NaN/Inf")
        if safety.get("require_finite_values", True) and not all(
            math.isfinite(float(value)) for value in state_values
        ):
            reasons.append("状态数组含 NaN/Inf")

        # 状态太旧时，控制器是在用过去的机器人控制现在的机器人。
        if math.isfinite(state_age_s) and (state_age_s < 0 or state_age_s > timing["max_state_age_s"]):
            reasons.append(
                f"状态年龄 {state_age_s:.6f}s 超过允许值 {timing['max_state_age_s']:.6f}s"
            )

        # roll/pitch 超界通常意味着机器人已接近倾倒，不应继续信任行走策略。
        tilt_limit = float(safety["max_abs_roll_pitch_rad"])
        if math.isfinite(roll_rad) and abs(roll_rad) > tilt_limit:
            reasons.append(f"roll={roll_rad:.6f}rad 超过 ±{tilt_limit:.6f}rad")
        if math.isfinite(pitch_rad) and abs(pitch_rad) > tilt_limit:
            reasons.append(f"pitch={pitch_rad:.6f}rad 超过 ±{tilt_limit:.6f}rad")

        # 命令也要受训练能力包络约束；策略没见过的命令不应直接拿真机试。
        command_values = [float(value) for value in command]
        bounds = self.contract.data["commands"]["base_velocity"]
        if len(command_values) != 3:
            reasons.append(f"速度命令应为 3 维，实际为 {len(command_values)} 维")
        elif not all(math.isfinite(value) for value in command_values):
            reasons.append("速度命令含 NaN/Inf")
        else:
            for index, (value, lower, upper) in enumerate(
                zip(command_values, bounds["lower"], bounds["upper"])
            ):
                if not lower <= value <= upper:
                    reasons.append(f"命令第 {index} 维 {value} 超出 [{lower}, {upper}]")

        # fail-closed：只有 reasons 为空才放行，漏掉一次检查不会默认“安全”。
        return SafetyResult(allowed=not reasons, reasons=tuple(reasons))
