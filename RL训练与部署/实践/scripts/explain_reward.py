#!/usr/bin/env python3
"""打印每个奖励项的计算明细，避免总奖励掩盖策略钻空子的原因。"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# 直接运行脚本时，把实践根目录加入模块搜索路径。
PRACTICE_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PRACTICE_ROOT))

from rl_deploy_lab import RewardLedger  # noqa: E402


def main() -> int:
    """载入奖励场景，按场景输出“指标 → 变换 → 权重 → 贡献”。"""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("config", type=Path, help="奖励项与假想场景 JSON 文件")
    args = parser.parse_args()

    with args.config.open("r", encoding="utf-8") as stream:
        config = json.load(stream)
    ledger = RewardLedger(config["terms"])

    print(config["note"])
    for scenario in config["scenarios"]:
        # 同一组奖励权重放进多种典型失败场景，才能看出行为排序是否符合本意。
        result = ledger.evaluate(scenario["name"], scenario["metrics"])
        print(f"\n场景：{result.scenario}")
        print("  奖励项                      原始指标      变换后       权重       贡献")
        for item in result.contributions:
            print(
                f"  {item.name:<26} {item.metric:>10.4f} "
                f"{item.transformed:>10.4f} {item.weight:>10.4f} {item.contribution:>10.4f}"
            )
        print(f"  {'总计':<58} {result.total:>10.4f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
