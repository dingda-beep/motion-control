#!/usr/bin/env python3
"""Print every reward contribution instead of hiding behavior behind one total."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PRACTICE_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PRACTICE_ROOT))

from rl_deploy_lab import RewardLedger  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("config", type=Path)
    args = parser.parse_args()

    with args.config.open("r", encoding="utf-8") as stream:
        config = json.load(stream)
    ledger = RewardLedger(config["terms"])

    print(config["note"])
    for scenario in config["scenarios"]:
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
