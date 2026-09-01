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

```json
"artifact_kind": "teaching_example_not_for_hardware",
"deployment_authorized": false
```

它不会也不应连接任何机器人。真实项目必须从自己解析后的训练环境生成契约，并经过硬件团队审核。

当前官方参考中，Kp/Kd 来自导出的 `deploy.yaml`，而 `dq_des=0、tau_ff=0` 由部署 C++ 代码设置。本实践把二者合并进一个显式 `motor_interface`，正是为了说明：**接口事实可能散落在模型、配置和代码中，发布前必须收拢成一份能检查的契约。**

## 2. 运行

进入本目录：

```bash
cd RL训练与部署/实践
```

校验契约：

```bash
python3 scripts/validate_contract.py \
  config/g1_29dof_policy_contract.example.json
```

运行三个纯内存模拟周期：

```bash
python3 scripts/run_mock_deployment.py \
  config/g1_29dof_policy_contract.example.json
```

把四种行为的奖励逐项记账：

```bash
python3 scripts/explain_reward.py \
  config/reward_scenarios.example.json
```

请先比较“要求前进但拒绝移动”和“速度跟上但脚在滑”：不要只看总分，要看速度收益、足滑和动作代价分别贡献了多少。随后复制配置，修改一个权重或 `sigma`，观察行为排序怎样改变。这个脚本是奖励尺度实验，不复刻官方任务的完整奖励。

运行全部测试：

```bash
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
