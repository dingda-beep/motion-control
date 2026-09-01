"""Build the actor observation with explicit term order and history semantics."""

from __future__ import annotations

import math
from collections import deque
from collections.abc import Mapping, Sequence

from .contract import PolicyContract, expand_scale


class ObservationHistory:
    """Term-major history buffer: each term stores frames from oldest to newest."""

    def __init__(self, contract: PolicyContract):
        self.contract = contract
        config = contract.data["observations"]
        self.history_length = int(config["history_length"])
        self.terms = list(config["terms"])
        self._history: dict[str, deque[list[float]]] = {
            term["name"]: deque(maxlen=self.history_length) for term in self.terms
        }

    def reset(self) -> None:
        for history in self._history.values():
            history.clear()

    def push(self, raw_frame: Mapping[str, Sequence[float]]) -> list[float]:
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

        for term in self.terms:
            name = term["name"]
            history = self._history[name]
            if not history:
                for _ in range(self.history_length):
                    history.append(list(scaled_frame[name]))
            else:
                history.append(list(scaled_frame[name]))

        flattened: list[float] = []
        for term in self.terms:
            for frame_values in self._history[term["name"]]:
                flattened.extend(frame_values)

        expected = self.contract.observation_dimension
        if len(flattened) != expected:
            raise RuntimeError(f"内部错误：构造出 {len(flattened)} 维观测，契约要求 {expected} 维")
        return flattened
