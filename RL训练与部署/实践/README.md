# 实践：先把部署契约跑通

这个小项目不需要 Isaac Lab、PyTorch、ONNX Runtime 或机器人 SDK，只用 Python 标准库。它的目的不是假装训练 G1，而是先把最容易在 Sim2Real 中悄悄出错的接口变成可运行测试。

## 1. 它验证什么

示例契约记录了当前教程参考快照中的关键结构：

```text
29 个策略关节与 29 个 SDK 关节
policy index → SDK index 的双射
5 ms × 4 = 20 ms
单帧 96 维 × 5 帧 = 480 维
观测项优先、项内从旧到新的历史布局
动作：q_target = q_default + 0.25 × action
电机包：q_des、dq_des=0、Kp、Kd、tau_ff=0
命令范围、状态新鲜度和姿态检查
```

配置文件明确带有：

```jsonc
{
  // 声明这是教学快照，不能把里面的 G1 参数当作真机批准配置。
  "artifact_kind": "teaching_example_not_for_hardware",

  // 即使其他字段都通过检查，本文件也不授予发送真机命令的权限。
  "deployment_authorized": false
}
```

这里用 `jsonc` 只是为了在讲义中展示注释；磁盘上的实际配置仍是标准 JSON，不包含 `//` 注释，可被 Python `json` 模块直接读取。

它不会也不应连接任何机器人。真实项目必须从自己解析后的训练环境生成契约，并经过硬件团队审核。

当前官方参考中，Kp/Kd 来自导出的 `deploy.yaml`，而 `dq_des=0、tau_ff=0` 由部署 C++ 代码设置。本实践把二者合并进一个显式 `motor_interface`，正是为了说明：**接口事实可能散落在模型、配置和代码中，发布前必须收拢成一份能检查的契约。**

## 2. 运行

进入本目录：

```bash
# 后续相对路径都以这个实践目录为起点。
cd RL训练与部署/实践
```

校验契约：

```bash
# 输入：策略契约 JSON；输出：维度、周期、映射等一致性摘要或明确错误。
python3 scripts/validate_contract.py \
  config/g1_29dof_policy_contract.example.json
```

运行三个纯内存模拟周期：

```bash
# 用假状态走三次完整数据链；脚本不会加载 SDK，也不会发送电机命令。
python3 scripts/run_mock_deployment.py \
  config/g1_29dof_policy_contract.example.json
```

把四种行为的奖励逐项记账：

```bash
# 把四个假想行为的奖励逐项展开，观察原始指标、变换、权重和贡献。
python3 scripts/explain_reward.py \
  config/reward_scenarios.example.json
```

请先比较“要求前进但拒绝移动”和“速度跟上但脚在滑”：不要只看总分，要看速度收益、足滑和动作代价分别贡献了多少。随后复制配置，修改一个权重或 `sigma`，观察行为排序怎样改变。这个脚本是奖励尺度实验，不复刻官方任务的完整奖励。

运行全部测试：

```bash
# 自动验证契约、观测、动作、奖励和安全闸门的关键不变量。
python3 -m unittest discover -s tests -v
```

## 3. 建议故意破坏一次

复制 JSON 到临时文件，然后一次只改一项：

- 把 `declared_dimension` 改成 481；
- 把 `policy_period_s` 改成 0.01；
- 让 `policy_to_sdk` 出现重复索引；
- 交换两个策略关节名但不改映射；
- 把一个观测项大小从 29 改成 28。

重新运行校验器，观察为什么“数组还能装下”不等于语义正确。

## 4. 代码对应教程中的哪一段

| 文件 | 作用 | 对应章节 |
|---|---|---|
| `contract.py` | 检查维度、周期、关节名称与双射 | 03、04、13 |
| `observation.py` | 缩放并按明确布局维护历史 | 05 |
| `action.py` | 生成 q_des/dq_des/Kp/Kd/tau_ff 电机包，并按 PD 公式复算未限幅力矩 | 06 |
| `safety.py` | 在策略外拒绝旧状态、坏姿态、NaN 和越界命令 | 15、16 |
| `reward.py` | 展开每个奖励项的原始值、变换、权重和贡献 | 08 |
| `run_mock_deployment.py` | 串起三个不接硬件的控制周期 | 15 |

## 5. 怎样接入真实训练工程

下一步不是手工把这份 JSON 改成真机配置，而是：

1. 从已创建的 Isaac Lab 环境读取解析后的观测、动作、关节和 timing；
2. 自动导出契约；
3. 给契约增加训练 run、checkpoint、资源和哈希；
4. 保存一组原始状态、期望 480 维观测和期望 29 维动作；
5. 在 Python 训练端、ONNX Runtime 和 C++ 部署端共同跑 golden test；
6. 只有通过分级安全审查的独立发布包，才可能把 `deployment_authorized` 交由真实发布流程管理。

Unitree RL Lab 当前已经能够导出 `deploy.yaml` 的关节映射、周期、PD、默认姿态、动作和观测信息。本实践是在更小的环境里把其背后的工程原则拆开讲清，而不是取代官方部署代码。

准备好安装完整仿真栈后，继续做[训练实验手册](训练实验手册.md)。它把官方 G1 任务拆成短跑体检、站立、小范围前进、扩命令、鲁棒化、导出和 Sim2Sim 等逐级实验。

## 6. 它与成熟开源工程怎样对应

这套代码没有自己虚构一套“迷你框架”，而是把成熟项目中最容易被大工程掩盖的边界单独拆出来：

| 成熟工程中的职责 | 本实践中的教学替身 | 刻意没有实现什么 |
|---|---|---|
| Isaac Lab 的 Observation/Action/Reward/Termination 等任务组件 | `observation.py`、`action.py`、`reward.py`、`safety.py` | 并行物理环境、接触传感器和完整任务管理器 |
| RSL-RL 的 rollout、actor、critic 与 PPO 更新 | 奖励账本只展示会进入 rollout 的标量和明细 | 神经网络、反向传播、优势估计和 PPO 优化 |
| Unitree 部署程序的“状态 → 观测 → Actor → 关节目标 → 低层命令”循环 | `run_mock_deployment.py` | ONNX Runtime、DDS/SDK 通信和真实电机写入 |
| 发布前的观测/动作/周期/关节映射一致性 | `contract.py` 与单元测试 | 真实项目的自动配置导出、跨语言 golden test 与发布审批 |

因此，读代码时不要把 `run_mock_deployment.py` 当成训练程序：它故意用全零数组代替 Actor，只为了让你先看清 Actor 前后的数据接口。真正训练由 Isaac Lab 环境和 RSL-RL 完成；真正部署还必须接入经过审核的状态机、硬件 SDK 和安全流程。

继续对照源码时，建议按下面三个入口阅读：

- [Isaac Lab：创建 Manager-Based RL 环境](https://isaac-sim.github.io/IsaacLab/main/source/tutorials/03_envs/create_manager_rl_env.html)：看任务怎样拆成观测、动作、奖励、终止、事件、课程和命令；
- [RSL-RL 配置与观测组](https://leggedrobotics.github.io/rsl_rl/guide/configuration.html)：看 actor 为什么只能接收部署可得观测，而 critic 可以在训练期额外使用特权观测；
- [Unitree RL Gym](https://github.com/unitreerobotics/unitree_rl_gym)：看 `Train → Play → Sim2Sim → Sim2Real` 的完整路径，以及真机循环怎样把策略动作变成 `q/qd/kp/kd/tau` 电机包。
