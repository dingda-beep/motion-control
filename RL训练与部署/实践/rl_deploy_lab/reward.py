"""奖励账本：把总奖励拆回每一项，观察尺度与行为取舍。"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class RewardContribution:
    """一个奖励项从原始指标到最终贡献的完整计算痕迹。"""

    # 奖励项名称，例如速度跟踪或足端打滑。
    name: str
    # 从环境状态算出的原始物理指标，还没有做奖励变换。
    metric: float
    # 原始指标经过 identity、平方或指数核后的值。
    transformed: float
    # 配置给出的权重；负数通常表示惩罚。
    weight: float
    # contribution = weight × transformed，所有贡献相加才是总奖励。
    contribution: float


@dataclass(frozen=True)
class RewardBreakdown:
    """某个假想场景下的逐项奖励明细。"""

    scenario: str
    contributions: tuple[RewardContribution, ...]

    @property
    def total(self) -> float:
        """返回 PPO 最终会看到的标量奖励。"""

        return sum(item.contribution for item in self.contributions)


class RewardLedger:
    """计算一组故意简化的奖励项；它是诊断工具，不是完整机器人环境。"""

    def __init__(self, terms: list[dict[str, Any]]):
        if not terms:
            raise ValueError("奖励项不能为空")
        self.terms = terms

    def evaluate(self, scenario: str, metrics: dict[str, Any]) -> RewardBreakdown:
        """根据一个场景的物理指标，逐项计算并保留中间结果。"""

        contributions: list[RewardContribution] = []
        for term in self.terms:
            name = term["name"]
            metric_name = term["metric"]
            if metric_name not in metrics:
                raise ValueError(f"场景 {scenario!r} 缺少指标 {metric_name!r}")
            metric = float(metrics[metric_name])
            weight = float(term["weight"])
            if not math.isfinite(metric) or not math.isfinite(weight):
                raise ValueError(f"奖励项 {name!r} 含 NaN 或 Inf")

            # 变换决定“误差变化时，奖励怎样变化”；权重只负责整体缩放和正负方向。
            transform = term["transform"]
            if transform == "identity":
                transformed = metric
            elif transform == "square":
                transformed = metric * metric
            elif transform == "exp_negative_square":
                sigma = float(term["sigma"])
                if not math.isfinite(sigma) or sigma <= 0:
                    raise ValueError(f"奖励项 {name!r} 的 sigma 必须为正数")
                transformed = math.exp(-(metric * metric) / (sigma * sigma))
            else:
                raise ValueError(f"奖励项 {name!r} 使用未知 transform={transform!r}")

            # 不直接累加一个匿名数字，而是留下账目，便于发现某个惩罚压倒主任务。
            contributions.append(
                RewardContribution(
                    name=name,
                    metric=metric,
                    transformed=transformed,
                    weight=weight,
                    contribution=weight * transformed,
                )
            )
        return RewardBreakdown(scenario=scenario, contributions=tuple(contributions))
