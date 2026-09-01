# 输入输出总表：从上层命令到电机，再回到 PPO

如果你是程序员，可以把 RL 运控理解成两条相连但职责不同的调用链：

- 部署闭环：每 20 ms 调一次，真的影响机器人；
- 训练闭环：在仿真中批量制造经验，更新 actor 参数。

## 一、部署闭环

### 1. 上层产生目标

```text
# 上层可能是遥控器或导航器；运控只消费统一的三维速度接口。
command_3 = command_source()
command_3 = [
    vx_cmd,   # 前后速度目标，m/s
    vy_cmd,   # 左右速度目标，m/s
    vyaw_cmd  # 转向角速度目标，rad/s
]
```

| 问题 | 答案 |
|---|---|
| 谁调用 | 控制程序每周期读取 |
| 输入 | 遥控器摇杆、导航器或其他上层意图 |
| 输出 | 希望前后速度、左右速度、转向角速度 |
| 单位 | m/s、m/s、rad/s |
| 下一站 | 进入 actor 观测，也进入训练时的速度跟踪奖励 |

为什么必须进 actor？因为相同的直立反馈既可能要求站住，也可能要求前进。只给“现在怎样”，不给“希望怎样”，函数没有足够信息决定动作。

### 2. SDK 读取身体反馈

```text
# 这些都是机器人反馈；不要把 q、dq 误认为 Actor 生成的量。
q_29, dq_29, imu = sdk.read_state()
```

| 输出 | 来源 | 表示什么 |
|---|---|---|
| `q_29` | 电机状态中的位置反馈 | 当前 29 个关节角 |
| `dq_29` | 电机状态中的速度反馈 | 当前 29 个关节角速度 |
| `imu.gyroscope` | IMU | 机身角速度 |
| `imu.orientation` | IMU/姿态处理 | 机身朝向，用于计算投影重力 |

`q、dq` 可以粗略理解为“电机/驱动告诉控制程序的自己现在怎样”，但严谨说它们是 SDK 暴露的关节反馈，可能已经经过驱动器的估计、滤波和传动换算，不一定是最原始传感器电压。

### 3. 构造 480 维观测

```text
# 输入由“真实反馈 + 上层目标 + 控制器记忆”三类数据组成。
obs_480 = observation_builder(
    imu,            # 角速度与姿态，用来得到投影重力
    q_29,           # 当前关节角
    dq_29,          # 当前关节速度
    command_3,      # 希望速度，不是测得的实际水平速度
    last_action_29, # 上一策略动作
    history_5       # 最近 5 帧，按契约规定的顺序排列
)
# 输出必须严格为 480 维，下一站只有 Actor。
```

当前案例一帧：

```text
base_ang_vel 3
+ projected_gravity 3
+ command 3
+ joint_pos_relative 29
+ joint_velocity 29
+ last_action 29
= 96
```

再保留 5 帧，所以是 `96 × 5 = 480`。输出下一站只有一个：actor。

### 4. actor 产生 29 维原始动作

```text
# 网络只做数值映射：480 个有固定语义的输入 → 29 个无量纲动作。
raw_action_29 = actor(obs_480)
```

- 输入：480 维、顺序和缩放固定的观测；
- 输出：29 个无单位的策略动作；
- 还不是：关节角、速度或力矩；
- 下一站：动作处理器。

训练时 actor 会围绕网络输出进行随机采样以探索；部署通常使用确定性中心动作。

### 5. 动作处理器产生 `q_des`

```text
# 先在策略关节顺序中解释动作，再重排到 SDK 电机顺序。
q_des_policy_order = q_default + 0.25 × raw_action
q_des_sdk_order    = remap(q_des_policy_order, policy_to_sdk)
```

- `q_default`：训练默认姿态，单位 rad；
- `0.25`：当前案例动作比例，单位 rad；
- `policy_to_sdk`：把策略关节顺序改成电机数组顺序；
- 输出：29 个期望关节角 `q_des`。

### 6. 电机位置接口形成力矩

```text
# q_des/dq_des 是目标，q/dq 是驱动反馈；二者不能混为同一组量。
tau_cmd = tau_ff + Kp(q_des - q) + Kd(dq_des - dq)
```

当前参考部署发送：

```text
q_des   = RL 动作处理后的目标
dq_des  = 0
Kp, Kd  = deploy config 中按 SDK 顺序保存的增益
tau_ff  = 0
```

电机反馈提供：

```text
q, dq = 当前关节位置与速度
```

所以 RL 的直接输出不是 `tau_cmd`。它通过每 20 ms 改变 `q_des`，让 PD 根据不断变化的误差产生任务所需力矩。

“前馈被 RL 内化”可以作如下精确表述：**策略把许多预见性动态效果编码进 `q_des` 的时间序列，但显式 `tau_ff` 输入仍为零。**直接输出前馈力矩的策略会使用另一份动作契约。

### 7. 现实给出下一次反馈

```text
# 输入是已经形成的力矩和现实物理条件；这里不是一个可在真机上直接调用的软件函数。
next_real_state = real_world(
    tau_cmd,      # 电机在本段时间里实际施加的作用
    robot_body,   # 真实质量、惯量、柔性、传动等
    contact,      # 足底与地面的真实接触
    disturbances, # 外力、地面变化和未建模影响
    elapsed_time  # 从本状态向未来演化的时间
)
# 输出再被传感器测量，成为下一个控制周期的新反馈。
```

传感器再读取 `next_real_state`，闭环回到第 2 步。神经网络没有单独“让机器人走”；完整环路共同产生了走路。

## 二、训练闭环

### 8. 仿真器替代现实产生下一状态

```text
# 训练时由仿真器预测动作后果，同时返回奖励/终止需要的接触信息。
next_state, contacts = simulator.step(motor_command)
```

训练时仍走同样的观测、actor、动作处理和 PD 语义，只是“现实世界”暂时由物理引擎预测。仿真与真机越一致，接口迁移越自然；差异部分由建模、实测和随机化处理。

### 9. 奖励函数给这次转移记分

```text
# 这些输入描述“刚才做了什么、世界怎样变化”；奖励只服务训练。
reward = reward_fn(
    state,      # 动作前状态
    action,     # Actor 本步动作
    next_state, # 推进物理后的状态
    command,    # 本步要求跟随的目标
    contacts    # 足部和非期望身体接触
)
```

输入是仿真真值与本步事件，输出是一个奖励标量和用于日志的分项。奖励进入训练数据，不进入部署 actor。

### 10. 终止函数决定这段经验是否结束

```text
# done 决定这段 rollout 是否在此结束；reason 用来区分失败和正常截断。
done, reason = termination_fn(next_state, contacts, elapsed_time)
```

输出告诉训练器这是摔倒、坏姿态还是正常超时。随后重置函数产生新初始状态。

### 11. rollout 收集一批接口调用记录

```text
# 保存动作发生当时的数据；PPO 更新时必须知道它来自哪一个旧策略分布。
rollout.add(obs, action, reward, done, value, action_probability)
```

当前参考配置每轮收集 `4096 × 24 = 98,304` 条转移。

### 12. PPO 更新网络参数

```text
# 输入是刚采集的一批经验；输出是下一轮采样要使用的新网络参数。
new_actor, new_critic = ppo_update(rollout)
```

- 输入：当前策略刚产生的一批 rollout；
- 输出：更新后的 actor 与 critic 参数；
- actor 的部署接口仍然是 `480 → 29`，不会因为 PPO 内部计算复杂就改变。

critic 可以在训练时额外看仿真真值，输出当前局面的价值估计；它帮助 actor 学习，最终通常不进入真机控制循环。

### 13. 导出把训练结果冻结成部署输入

```text
# checkpoint 给参数，resolved_environment 给这些参数两端的现实含义。
policy.onnx, deploy_config = export(
    selected_checkpoint, # 通过固定评估选中的参数快照
    resolved_environment # 实际生效的观测、动作、周期、关节与归一化配置
)
```

`policy.onnx` 保存 `obs → raw_action`；`deploy_config` 保存前后两端怎样解释这些数，包括观测、动作、关节映射、PD 与周期。两者共同回到部署闭环第 3～6 步。

## 三、用接口一眼看出错误属于哪一层

| 现象 | 先查哪个接口 |
|---|---|
| 给前进命令却转弯 | command 三维顺序、符号和坐标 |
| 一接管就猛跳 | raw action → q_des 的 scale、default、joint map |
| 姿态输入看似合理却总向一侧倒 | SDK/IMU → observation 的轴、符号、历史顺序 |
| 同样 q_des，真机比仿真硬很多 | Kp/Kd、执行器、力矩限制与周期 |
| 奖励很高但跪着走 | state/contact → reward 的计分漏洞 |
| PyTorch 会走，ONNX 不会 | obs → actor 的归一化、导出和运行时 |

这就是全书的核心学习方法：**先找到出错函数，再核对它的输入输出；不要跨过接口去盲调另一个模块。**
