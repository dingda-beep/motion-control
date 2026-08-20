# 附录 B：缩写和符号速查

> **附录定位**：全书字典，不属于线性阅读主线。
>
> **使用方法**：遇到缩写、符号复用或单位不确定时查询；不要脱离当前章节定义背字母。

## 1. 机器人与控制缩写

| 缩写 | 英文 | 中文/含义 |
|---|---|---|
| AD | Automatic Differentiation | 自动微分 |
| BFM | Behavior Foundation Model | 行为基础模型 |
| CBF | Control Barrier Function | 控制障碍函数 |
| CD | Centroidal Dynamics | 质心动力学 |
| CLF | Control Lyapunov Function | 控制李雅普诺夫函数 |
| CMM | Centroidal Momentum Matrix | 质心动量矩阵 |
| COM | Center of Mass | 质心 |
| CoP | Center of Pressure | 压力中心 |
| CP | Capture Point | 捕获点 |
| DDP | Differential Dynamic Programming | 微分动态规划 |
| DLS | Damped Least Squares | 阻尼最小二乘 |
| DP | Dynamic Programming | 动态规划 |
| EKF | Extended Kalman Filter | 扩展卡尔曼滤波 |
| FD | Forward Dynamics | 正动力学 |
| FK | Forward Kinematics | 正运动学 |
| GRF | Ground Reaction Force | 地面反作用力 |
| HQP | Hierarchical Quadratic Programming | 层级二次规划 |
| ID | Inverse Dynamics | 逆动力学 |
| IK | Inverse Kinematics | 逆运动学 |
| IMU | Inertial Measurement Unit | 惯性测量单元 |
| KF | Kalman Filter | 卡尔曼滤波 |
| LIP | Linear Inverted Pendulum | 线性倒立摆 |
| LQR | Linear Quadratic Regulator | 线性二次调节器 |
| MPC | Model Predictive Control | 模型预测控制 |
| NLP | Nonlinear Programming | 非线性规划 |
| NMPC | Nonlinear Model Predictive Control | 非线性模型预测控制 |
| OCP | Optimal Control Problem | 最优控制问题 |
| QDD | Quasi-Direct Drive | 准直驱 |
| QP | Quadratic Programming | 二次规划 |
| SEA | Series Elastic Actuator | 串联弹性执行器 |
| SLIP | Spring-Loaded Inverted Pendulum | 弹簧负载倒立摆 |
| SQP | Sequential Quadratic Programming | 序列二次规划 |
| SRBD | Single Rigid Body Dynamics | 单刚体动力学 |
| TO | Trajectory Optimization | 轨迹优化 |
| TSID | Task-Space Inverse Dynamics | 任务空间逆动力学 |
| VMC | Virtual Model Control | 虚拟模型控制 |
| WBC | Whole-Body Control | 全身控制 |
| WBD | Whole-Body Dynamics | 全身动力学 |
| ZMP | Zero Moment Point | 零力矩点 |

## 2. 强化学习与模仿学习缩写

| 缩写 | 英文 | 中文/含义 |
|---|---|---|
| AC | Actor-Critic | 演员-评论家框架 |
| AE | Autoencoder | 自编码器 |
| AMP | Adversarial Motion Priors | 对抗运动先验 |
| BC | Behavior Cloning | 行为克隆 |
| CNN | Convolutional Neural Network | 卷积神经网络 |
| DAgger | Dataset Aggregation | 数据集聚合 |
| DR | Domain Randomization | 域随机化 |
| FB | Forward-Backward Representation | 前向-后向表征 |
| [FBCPR](https://arxiv.org/abs/2504.11054) | Forward-Backward Representations with Conditional-Policy Regularization | 带条件策略正则的前向—后向表征 |
| FOV | Field of View | 视场 |
| FSQ | Finite Scalar Quantization | 有限标量量化 |
| GAE | Generalized Advantage Estimation | 广义优势估计 |
| GAN | Generative Adversarial Network | 生成对抗网络 |
| GRU | Gated Recurrent Unit | 门控循环单元 |
| KL | Kullback–Leibler Divergence | KL 散度 |
| MDP | Markov Decision Process | 马尔可夫决策过程 |
| MHA | Multi-Head Attention | 多头注意力 |
| MLP | Multi-Layer Perceptron | 多层感知机；本书从输入、隐藏层到 Actor/Critic 的完整解释见[第 13 章](13-强化学习基础.md)第 6 节 |
| OOD | Out of Distribution | 分布外 |
| POMDP | Partially Observable MDP | 部分可观测 MDP |
| PIE | Parkour with Implicit-Explicit Learning Framework for Legged Robots | 面向腿足机器人跑酷的隐式—显式学习框架 |
| PPO | Proximal Policy Optimization | 近端策略优化 |
| RL | Reinforcement Learning | 强化学习 |
| RND | Random Network Distillation | 随机网络蒸馏/内在奖励方法 |
| RSI | Reference State Initialization | 参考状态初始化 |
| RNN | Recurrent Neural Network | 循环神经网络 |
| VAE | Variational Autoencoder | 变分自编码器 |

> FBCPR 是具体方法名，不是对“风格损失 + 物理惩罚”的通用简称。正文仍应回到论文所定义的条件策略正则、数据和部署方式理解。

## 3. 系统与数据缩写

| 缩写 | 英文 | 中文/含义 |
|---|---|---|
| API | Application Programming Interface | 应用程序接口 |
| CAN | Controller Area Network | 控制器局域网总线 |
| HIL | Hardware-in-the-Loop | 硬件在环 |
| LiDAR | Light Detection and Ranging | 激光雷达 |
| MJCF | MuJoCo XML Model Format | MuJoCo 模型格式 |
| mocap | Motion Capture | 动作捕捉 |
| ONNX | Open Neural Network Exchange | 神经网络交换格式 |
| RTI | Real-Time Iteration | 实时迭代 |
| SIL | Software-in-the-Loop | 软件在环 |
| SMPL | Skinned Multi-Person Linear Model | 参数化人体模型 |
| SysID | System Identification | 系统辨识 |
| URDF | Unified Robot Description Format | 统一机器人描述格式 |
| VLA | Vision-Language-Action | 视觉-语言-动作 |
| VLM | Vision-Language Model | 视觉语言模型 |
| VLN | Vision-Language Navigation | 视觉语言导航 |

## 4. 高频英文词

| 词 | 常见含义 |
|---|---|
| action | 动作/控制输入 |
| actuator | 执行器 |
| baseline | 基线方案 |
| bias | 偏差 |
| contact schedule | 接触时序 |
| cost/loss | 代价/损失 |
| curriculum | 课程学习 |
| desired/ref | 期望/参考 |
| dynamics | 动力学 |
| end effector | 末端执行器 |
| estimator | 状态估计器 |
| frame | 坐标系；也可指数据帧 |
| gait | 步态 |
| ground truth/GT | 真值，通常仅仿真或外部测量可得 |
| horizon | 预测时域 |
| ill-conditioned | 病态；输入或测量的小变化会在反求结果中被严重放大 |
| joint | 关节 |
| kinematics | 运动学 |
| latent | 潜变量/隐表示 |
| locomotion | 移动运动，腿足语境下常指行走奔跑能力 |
| observation/obs | 策略或估计器可见的观测 |
| Oracle | 某项诊断中临时获得理想信息、真值或理想选择规则的参照者；不是固定网络结构，也不自动等于 Teacher |
| policy | 策略 |
| proprioception | 本体感知 |
| rank | 秩；矩阵能独立产生或保留的方向数 |
| retarget | 动作重映射 |
| rollout | 用策略与环境交互采集的一段轨迹 |
| stance | 支撑相 |
| state | 状态 |
| swing | 摆动相 |
| torque | 力矩 |
| tracking | 跟踪 |
| wrench | 三维力与三维力矩组成的 6 维量 |

## 5. 常见符号

| 符号 | 常见含义 | 常见单位 |
|---|---|---|
| `t` | 连续时间 | s |
| `k` | 离散时刻编号 | 无 |
| `Δt` | 时间步长 | s |
| `x` | 状态；也可能指任务空间量 | 取决于分量 |
| `x_real` | 真实机器人当前状态，通常不能完整直接测得 | 取决于分量 |
| `x_hat` | 状态估计器给出的当前状态估计 | 取决于分量 |
| `x_model` | 模型沿时间预测的状态 | 取决于分量 |
| `y` | 传感器测量或系统输出 | 取决于传感器 |
| `u` | 控制程序发出的命令；在优化中也可表示候选控制输入 | 取决于接口 |
| `u_real` | 驱动器、电机和传动最终在现实中实现的输入；不保证等于命令 `u` | 取决于接口 |
| `f_model` | 控制器、规划器或估计器内部的状态转移模型 | 依模型 |
| `f_real` | 现实中的真实状态转移规律，通常未知且含未建模因素 | 依系统 |
| `h_model` | 估计器内部的测量模型：某个状态猜测应该产生怎样的传感器读数 | 依传感器 |
| `h_real` | 现实中的测量过程：真实状态实际上怎样形成传感器读数 | 依传感器 |
| `noise` | 混入测量的随机误差或未建模影响 | 取决于传感器 |
| `disturbance` | 外部扰动或未建模影响 | 依分量 |
| `q` | 广义配置/关节角 | m、rad、四元数混合 |
| `v` | 广义速度或线速度 | m/s、rad/s |
| `v_dot` | 广义加速度 | m/s²、rad/s² |
| `p` | 位置 | m |
| `R` | 旋转矩阵 | 无 |
| `T` | 齐次变换 | 旋转无单位、平移 m |
| `ω` | 角速度 | rad/s |
| `M` | 质量矩阵 | 混合单位 |
| `J` | 雅可比矩阵；有些论文也用它表示代价，本书正文尽量将代价写作 `Cost` | 取决于语境 |
| `τ` | 关节力矩 | N·m |
| `λ` | 接触力/wrench；RL 中也可能是 GAE 参数 | N、N·m 或无 |
| `f` | 力 | N |
| `m` | 质量 | kg |
| `g` | 重力加速度大小；有些优化资料也用它表示一次项或约束函数 | m/s² 或依语境 |
| `μ` | 摩擦系数；概率中也常表示均值 | 无或依语境 |
| `σ` | 标准差 | 与变量相同 |
| `γ` | RL 折扣因子 | 无 |
| `θ,φ,ψ` | 角度或网络参数 | 依语境 |
| `Q,R` | 控制代价权重；KF 中为噪声协方差 | 依语境 |
| `P` | 状态估计协方差；RL 的 MDP 中也常表示状态转移概率 | 状态单位的平方或无 |
| `𝔼` | 数学期望 | 与内部量相同 |
| `∇` | 梯度 | 依变量 |
| `∂` | 偏导符号 | 无 |
| `‖·‖_2` | 二范数 | 与内部向量相同 |
| `(·)ᵀ` | 转置 | 无 |
| `(·)⁻¹` | 逆 | 原单位的倒数/组合 |
| `(·)^†` | 伪逆 | 依矩阵 |
| `Σ` | 求和 | 与求和项相同 |
| `arg min` | 返回使目标最小的自变量 | 与自变量相同 |
| `arg max` | 返回使目标最大的自变量 | 与自变量相同 |

## 6. 读公式的六步法

1. 找等号左边：公式最终输出什么？
2. 标出每个变量是标量、向量还是矩阵；
3. 写出 shape；
4. 写出坐标系；
5. 检查单位；
6. 问公式依赖哪些假设，在哪些条件下会失效。

读控制公式时，再补七个贯穿全书的问题：

1. 这是人的目标、参考、测量、估计、预测、命令，还是现实结果？
2. 控制器此刻实际能看到哪些量？
3. 它输出的是候选命令，还是已经发生的结果？
4. 结论只保证几何可达，还是也检查了动力学、接触和电机限制？
5. 使用的是 `f_model` 还是来自 `f_real` 的测量证据？
6. 这是离线训练/设计过程，还是部署时的在线反馈过程？
7. 一次动作看起来合理，还是扰动后长期仍能恢复？

例如：

```text
τ=Jᵀf
```

若 `f∈ℝ³`、`J∈ℝ^(3×n)`，则 `Jᵀ∈ℝ^(n×3)`，输出 `τ∈ℝ^n`。这里若把 `f` 定义为环境施加在机器人末端上的力，`τ` 就是这股外力对各关节产生的广义力矩；若要求电机抵消它，命令通常还要取反号，并计入重力等其他作用。接着还要问 `f` 与 `J` 是否在一致坐标系表达。

## 7. 同一个字母为何反复复用

数学符号没有全局命名空间：

- `q` 可指关节角，也可指四元数；
- `λ` 可指接触力、拉格朗日乘子或 GAE 参数；
- `Q` 可指 OCP 权重或 KF 过程噪声；
- `r` 可指奖励、位置向量，许多 PPO 论文也用它表示概率比；本书将 PPO 概率比写成 `ratio`；
- `g` 可指重力、优化的一次项或约束函数；本书在 QP 例子中尽量把一次项写成 `c`。

不要按字母记含义，要按“本节定义 + 维度 + 单位”理解。

遇到 `A⁻¹` 或 `A†` 时还要额外问：矩阵是否保留了足够的独立方向？如果方向已经缺失，换一种求逆函数也不能凭空恢复信息；如果方向接近重合，反求结果还可能把小误差放得很大。
