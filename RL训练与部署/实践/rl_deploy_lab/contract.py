"""部署契约：读取并校验策略输入、输出和低层接口的静态含义。"""

from __future__ import annotations

import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any


class ContractError(ValueError):
    """契约缺字段或内部矛盾时抛出；这类错误应在启动前解决。"""


@dataclass(frozen=True)
class PolicyContract:
    """JSON 策略契约的只读包装；`load` 返回前一定完成一致性校验。"""

    # data 仍保留原始层级，方便读者把代码字段与 JSON 逐项对照。
    data: dict[str, Any]

    @classmethod
    def load(cls, path: str | Path) -> "PolicyContract":
        """读取 UTF-8 JSON，并在任何下游模块使用它之前完成校验。"""

        with Path(path).open("r", encoding="utf-8") as stream:
            data = json.load(stream)
        contract = cls(data)
        contract.validate()
        return contract

    @property
    def joint_count(self) -> int:
        """策略控制的关节数量。"""

        return int(self.data["robot"]["joint_count"])

    @property
    def observation_dimension(self) -> int:
        """从每帧各观测项维度与历史长度推导 Actor 总输入维度。"""

        observations = self.data["observations"]
        one_history_slice = sum(int(term["size"]) for term in observations["terms"])
        return one_history_slice * int(observations["history_length"])

    def validate(self) -> None:
        """一次收集所有契约错误，避免修完一个字段后才看到下一个错误。"""

        errors: list[str] = []

        # schema_version 让未来格式升级时能够明确拒绝旧解释器无法理解的新契约。
        if self.data.get("schema_version") != 1:
            errors.append("schema_version 必须为 1")

        # 关节数量是动作、默认姿态、PD 参数和映射数组共同依赖的基准维度。
        robot = self.data.get("robot", {})
        count = robot.get("joint_count")
        if not isinstance(count, int) or count <= 0:
            errors.append("robot.joint_count 必须是正整数")
            count = 0

        for key in ("policy_joint_names", "sdk_joint_names", "policy_to_sdk"):
            value = robot.get(key)
            if not isinstance(value, list) or len(value) != count:
                errors.append(f"robot.{key} 的长度必须等于 joint_count")

        # 双射表示每个策略关节恰好落到一个 SDK 电机，并且没有电机被重复占用或遗漏。
        mapping = robot.get("policy_to_sdk", [])
        if len(mapping) == count:
            if sorted(mapping) != list(range(count)):
                errors.append("policy_to_sdk 必须是 0..joint_count-1 的双射")
            else:
                policy_names = robot.get("policy_joint_names", [])
                sdk_names = robot.get("sdk_joint_names", [])
                if len(policy_names) == count and len(sdk_names) == count:
                    for policy_index, sdk_index in enumerate(mapping):
                        if policy_names[policy_index] != sdk_names[sdk_index]:
                            errors.append(
                                "policy_to_sdk 与关节名称不一致："
                                f"policy[{policy_index}]={policy_names[policy_index]!r}, "
                                f"sdk[{sdk_index}]={sdk_names[sdk_index]!r}"
                            )
                            break

        # 策略不是每个物理步都推理：policy_period = physics_dt × decimation。
        # 训练和部署周期不一致，会让同一个动作对应完全不同的真实时间。
        timing = self.data.get("timing", {})
        physics_dt = timing.get("physics_dt_s")
        decimation = timing.get("decimation")
        policy_period = timing.get("policy_period_s")
        if not _positive_number(physics_dt):
            errors.append("timing.physics_dt_s 必须为正数")
        if not isinstance(decimation, int) or decimation <= 0:
            errors.append("timing.decimation 必须为正整数")
        if not _positive_number(policy_period):
            errors.append("timing.policy_period_s 必须为正数")
        if _positive_number(physics_dt) and isinstance(decimation, int) and decimation > 0:
            if _positive_number(policy_period) and not math.isclose(
                float(physics_dt) * decimation,
                float(policy_period),
                rel_tol=0.0,
                abs_tol=1e-12,
            ):
                errors.append("physics_dt_s × decimation 必须等于 policy_period_s")

        # 观测不仅检查总维度，还检查每项名称、大小、缩放、历史排列和重置方式。
        observations = self.data.get("observations", {})
        history_length = observations.get("history_length")
        terms = observations.get("terms")
        if not isinstance(history_length, int) or history_length <= 0:
            errors.append("observations.history_length 必须为正整数")
        if observations.get("history_layout") != "term_major_oldest_to_newest":
            errors.append("本示例只接受 term_major_oldest_to_newest 历史布局")
        if observations.get("reset_mode") != "repeat_first_frame":
            errors.append("本示例只接受 repeat_first_frame 历史初始化")
        if not isinstance(terms, list) or not terms:
            errors.append("observations.terms 不能为空")
        else:
            names: list[str] = []
            for term in terms:
                name = term.get("name")
                size = term.get("size")
                scale = term.get("scale")
                if not isinstance(name, str) or not name:
                    errors.append("每个观测项都必须有非空 name")
                else:
                    names.append(name)
                if not isinstance(size, int) or size <= 0:
                    errors.append(f"观测项 {name!r} 的 size 必须是正整数")
                if not _valid_scale(scale, size):
                    errors.append(f"观测项 {name!r} 的 scale 必须是数值或与 size 等长的数值数组")
            if len(names) != len(set(names)):
                errors.append("观测项名称不能重复")

        # declared_dimension 是发布者写下的预期；derived 是程序从明细重新算出的事实。
        declared = observations.get("declared_dimension")
        try:
            derived = self.observation_dimension
        except (KeyError, TypeError, ValueError):
            derived = None
        if derived is not None and declared != derived:
            errors.append(f"declared_dimension={declared!r}，但按观测项和历史推导应为 {derived}")

        # 本教学实现只讲“Actor 输出相对默认姿态的位置增量”这一种动作接口。
        actions = self.data.get("actions", {})
        if actions.get("type") != "joint_position_delta_from_default":
            errors.append("本示例只实现 joint_position_delta_from_default 动作")
        if actions.get("size") != count:
            errors.append("actions.size 必须等于 joint_count")
        if not _valid_scale(actions.get("scale_rad"), count):
            errors.append("actions.scale_rad 必须是数值或与关节数等长的数值数组")
        offsets = actions.get("default_joint_pos_rad")
        if not isinstance(offsets, list) or len(offsets) != count or not _all_finite(offsets):
            errors.append("actions.default_joint_pos_rad 必须是与关节数等长的有限数数组")
        clip = actions.get("normalized_clip")
        if clip is not None and (
            not isinstance(clip, list)
            or len(clip) != 2
            or not _all_finite(clip)
            or clip[0] > clip[1]
        ):
            errors.append("actions.normalized_clip 必须为 null 或 [lower, upper]")

        # 明确锁定电机控制律，防止训练按位置目标解释，部署却把动作当力矩发送。
        motor = self.data.get("motor_interface", {})
        expected_law = "tau_cmd = tau_ff + kp * (q_des - q) + kd * (dq_des - dq)"
        if motor.get("control_law") != expected_law:
            errors.append("motor_interface.control_law 与本示例实现不一致")
        for key in (
            "desired_joint_velocity_rad_s",
            "feedforward_torque_nm",
            "kp_sdk_order",
            "kd_sdk_order",
        ):
            if not _valid_scale(motor.get(key), count):
                errors.append(f"motor_interface.{key} 必须是数值或与关节数等长的有限数数组")

        # 当前上层接口只有 vx、vy、yaw_rate 三维速度命令，并限制在训练覆盖范围内。
        commands = self.data.get("commands", {}).get("base_velocity", {})
        lower = commands.get("lower")
        upper = commands.get("upper")
        if not _bounds_are_valid(lower, upper, 3):
            errors.append("base_velocity 命令上下界必须是 3 维有限数组，且 lower <= upper")

        # 教学文件默认禁止真机部署；任何示例脚本都不能悄悄把这一位改成允许。
        if self.data.get("artifact_kind") == "teaching_example_not_for_hardware":
            if self.data.get("deployment_authorized") is not False:
                errors.append("教学示例必须明确 deployment_authorized=false")

        if errors:
            raise ContractError("策略契约校验失败：\n- " + "\n- ".join(errors))


def expand_scale(scale: float | list[float], size: int) -> list[float]:
    """把一个全局标量扩成逐关节数组；已有逐关节数组则只转换数值类型。"""

    if isinstance(scale, (int, float)) and not isinstance(scale, bool):
        return [float(scale)] * size
    return [float(value) for value in scale]


def _positive_number(value: Any) -> bool:
    """判断值是否为有限正数；Python 的 bool 是 int 子类，因此要显式排除。"""

    return (
        isinstance(value, (int, float))
        and not isinstance(value, bool)
        and math.isfinite(value)
        and value > 0
    )


def _all_finite(values: list[Any]) -> bool:
    """检查数组中的每一项都是有限数，拒绝 bool、NaN 和 Inf。"""

    return all(
        isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)
        for value in values
    )


def _valid_scale(value: Any, size: Any) -> bool:
    """缩放既可写一个标量，也可写成与目标维度等长的数组。"""

    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return math.isfinite(value)
    return (
        isinstance(value, list)
        and isinstance(size, int)
        and len(value) == size
        and _all_finite(value)
    )


def _bounds_are_valid(lower: Any, upper: Any, size: int) -> bool:
    """检查上下界维度、数值有效性，并确保每一维下界都不大于上界。"""

    return (
        isinstance(lower, list)
        and isinstance(upper, list)
        and len(lower) == size
        and len(upper) == size
        and _all_finite(lower)
        and _all_finite(upper)
        and all(low <= high for low, high in zip(lower, upper))
    )
