"""观测接口：按契约缩放、保存历史，并拼出 Actor 真正接收的一维数组。"""

from __future__ import annotations

import math
from collections import deque
from collections.abc import Mapping, Sequence

from .contract import PolicyContract, expand_scale


class ObservationHistory:
    """按“观测项优先、项内从旧到新”的规则维护历史。"""

    def __init__(self, contract: PolicyContract):
        # 观测顺序不能由字典遍历或部署者的记忆决定，必须以发布契约为唯一依据。
        self.contract = contract
        config = contract.data["observations"]
        self.history_length = int(config["history_length"])
        self.terms = list(config["terms"])
        self._history: dict[str, deque[list[float]]] = {
            term["name"]: deque(maxlen=self.history_length) for term in self.terms
        }

    def reset(self) -> None:
        """清空上一回合历史；机器人重置后不能继续携带旧动作和旧状态。"""

        for history in self._history.values():
            history.clear()

    def push(self, raw_frame: Mapping[str, Sequence[float]]) -> list[float]:
        """接收一个未缩放观测帧，返回可直接喂给 Actor 的完整历史观测。"""

        # 先逐项校验和缩放。这样报错会指出具体观测项，而不是只说“480 维不对”。
        scaled_frame: dict[str, list[float]] = {}
        for term in self.terms:
            name = term["name"]
            if name not in raw_frame:
                raise ValueError(f"缺少观测项 {name!r}")
            values = [float(value) for value in raw_frame[name]]
            if len(values) != term["size"]:
                raise ValueError(f"观测项 {name!r} 应为 {term['size']} 维，实际为 {len(values)} 维")
            if not all(math.isfinite(value) for value in values):
                raise ValueError(f"观测项 {name!r} 含 NaN 或 Inf")
            scales = expand_scale(term["scale"], term["size"])
            scaled_frame[name] = [value * scale for value, scale in zip(values, scales)]

        # 刚重置时还没有 5 帧历史，因此复制首帧填满；这也是部署契约的一部分。
        for term in self.terms:
            name = term["name"]
            history = self._history[name]
            if not history:
                for _ in range(self.history_length):
                    history.append(list(scaled_frame[name]))
            else:
                history.append(list(scaled_frame[name]))

        # 注意这里不是“第 1 帧所有项、第 2 帧所有项”，而是“某一项的全部历史，再到下一项”。
        flattened: list[float] = []
        for term in self.terms:
            for frame_values in self._history[term["name"]]:
                flattened.extend(frame_values)

        # 最后的总维度检查是保险丝，不能替代前面对每一项语义的检查。
        expected = self.contract.observation_dimension
        if len(flattened) != expected:
            raise RuntimeError(f"内部错误：构造出 {len(flattened)} 维观测，契约要求 {expected} 维")
        return flattened
