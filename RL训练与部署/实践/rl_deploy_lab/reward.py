"""A tiny reward ledger for inspecting per-term scale and failure trade-offs."""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class RewardContribution:
    name: str
    metric: float
    transformed: float
    weight: float
    contribution: float


@dataclass(frozen=True)
class RewardBreakdown:
    scenario: str
    contributions: tuple[RewardContribution, ...]

    @property
    def total(self) -> float:
        return sum(item.contribution for item in self.contributions)


class RewardLedger:
    """Evaluate deliberately simple scalar reward terms from a JSON-friendly config."""

    def __init__(self, terms: list[dict[str, Any]]):
        if not terms:
            raise ValueError("奖励项不能为空")
        self.terms = terms

    def evaluate(self, scenario: str, metrics: dict[str, Any]) -> RewardBreakdown:
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
