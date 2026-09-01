"""零第三方依赖的 RL 部署契约教学组件；这里只导出读者需要使用的公开接口。"""

from .action import ActionProcessor
from .contract import ContractError, PolicyContract
from .observation import ObservationHistory
from .reward import RewardBreakdown, RewardContribution, RewardLedger
from .safety import SafetyGate, SafetyResult

# 明确公开接口，避免示例脚本依赖模块内部的校验辅助函数。
__all__ = [
    "ActionProcessor",
    "ContractError",
    "ObservationHistory",
    "PolicyContract",
    "RewardBreakdown",
    "RewardContribution",
    "RewardLedger",
    "SafetyGate",
    "SafetyResult",
]
