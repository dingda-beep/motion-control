# 附录 B：SLAM 缩写与符号速查

> 用法：正文遇到缩写或符号时来查。这里提供定位，不代替对应章节的因果解释。

## B.1 核心任务缩写

| 缩写 | 英文 | 中文与本质 |
|---|---|---|
| SLAM | Simultaneous Localization and Mapping | 同时定位与建图；联合估计轨迹和环境 |
| VO | Visual Odometry | 视觉里程计；主要由连续图像估短时相对运动 |
| VIO | Visual-Inertial Odometry | 视觉惯性里程计；相机与 IMU 联合估计 |
| LO | LiDAR Odometry | 激光里程计；由连续点云估相对运动 |
| LIO | LiDAR-Inertial Odometry | 激光惯性里程计；激光与 IMU 联合估计 |
| SfM | Structure from Motion | 从多张图像恢复相机运动和场景结构，常为离线问题 |
| MVS | Multi-View Stereo | 多视图立体；从多图像恢复稠密三维表面 |

## B.2 视觉几何与跟踪

| 缩写 | 英文 | 含义 |
|---|---|---|
| ORB | Oriented FAST and Rotated BRIEF | 一种带方向的角点与二进制描述子组合 |
| FAST | Features from Accelerated Segment Test | 快速角点检测器 |
| BRIEF | Binary Robust Independent Elementary Features | 二进制局部描述子 |
| LK | Lucas–Kanade | 常见稀疏光流方法 |
| KLT | Kanade–Lucas–Tomasi | 常指特征选择与 LK 跟踪组合 |
| F | Fundamental Matrix | 基础矩阵；像素坐标中的对极几何 |
| E | Essential Matrix | 本质矩阵；归一化相机坐标中的相对几何 |
| H | Homography | 单应矩阵；描述平面或纯旋转下的图像变换 |
| PnP | Perspective-n-Point | 由三维点到二维像素对应估相机位姿 |
| DLT | Direct Linear Transform | 直接线性变换；多种几何初值估计方法的框架 |
| RANSAC | Random Sample Consensus | 随机采样一致性；在外点中寻找受最多数据支持的模型 |

## B.3 优化与后端

| 缩写 | 英文 | 含义 |
|---|---|---|
| BA | Bundle Adjustment | 束调整；联合优化相机位姿和地图点 |
| GN | Gauss–Newton | 高斯–牛顿非线性最小二乘迭代 |
| LM | Levenberg–Marquardt | 带阻尼的非线性最小二乘方法 |
| MAP | Maximum A Posteriori | 最大后验估计；结合测量和先验找最可能状态 |
| MLE | Maximum Likelihood Estimation | 最大似然估计；找最能解释测量的参数 |
| EKF | Extended Kalman Filter | 扩展卡尔曼滤波；对非线性模型线性化的递推估计 |
| UKF | Unscented Kalman Filter | 无迹卡尔曼滤波；用采样点传播非线性不确定性 |
| iSAM | incremental Smoothing and Mapping | 增量平滑与建图 |
| PCM | Pairwise Consistency Maximization | 成对一致性最大化；可用于筛查回环等约束 |

## B.4 激光、深度与地图

| 缩写 | 英文 | 含义 |
|---|---|---|
| LiDAR | Light Detection and Ranging | 激光雷达；测方向与距离等信息 |
| ICP | Iterative Closest Point | 迭代最近点；交替建立点云对应与求位姿 |
| GICP | Generalized ICP | 广义 ICP；引入局部协方差/表面结构 |
| NDT | Normal Distributions Transform | 正态分布变换；用网格局部分布对齐点云 |
| RGB-D | Red Green Blue + Depth | 彩色图加深度 |
| ToF | Time of Flight | 飞行时间测距 |
| TSDF | Truncated Signed Distance Function | 截断有符号距离函数；常用于表面融合 |
| ESDF | Euclidean Signed Distance Field | 欧氏有符号距离场；常供规划查询障碍距离 |
| SDF | Signed Distance Function | 有符号距离函数 |
| Voxel | — | 体素；三维空间格子 |

## B.5 回环与地点识别

| 缩写 | 英文 | 含义 |
|---|---|---|
| LC | Loop Closure | 回环闭合；发现当前与旧地点相同并加入长程约束 |
| BoW | Bag of Words | 词袋；把局部描述子量化成可检索图像摘要 |
| DBoW | Database of Words | 常见视觉词袋数据库/实现家族名称 |
| PR | Place Recognition | 地点识别；提出历史地点候选 |
| Reloc | Relocalization | 重定位；跟踪丢失或启动到旧图时恢复位姿 |

## B.6 评估指标

| 缩写 | 英文 | 含义 |
|---|---|---|
| ATE | Absolute Trajectory Error | 对齐后估计轨迹与参考轨迹的全局误差 |
| RPE | Relative Pose Error | 固定间隔内相对运动误差 |
| RMSE | Root Mean Squared Error | 均方根误差 |
| MAE | Mean Absolute Error | 平均绝对误差 |
| FPS | Frames Per Second | 每秒处理帧数；不等于端到端低延迟 |

## B.7 常见坐标系下标

| 字母 | 常见含义 |
|---|---|
| `w` | world，世界坐标系 |
| `m` | map，地图坐标系；注意也可能用作地图变量 |
| `o` | odom，局部里程计坐标系 |
| `b` | body/base，机体坐标系 |
| `c` | camera，相机坐标系 |
| `i` | IMU 坐标系或索引；看上下文 |
| `l` | LiDAR，激光坐标系 |
| `g` | GNSS 或 gravity；看上下文 |

本教程约定：

```text
T_ab：把 b 坐标系中的坐标变到 a 坐标系
p_a = T_ab p_b
```

外部代码可能采用其他命名，必须用实际等式判断。

## B.8 常见状态符号

| 符号 | 含义 |
|---|---|
| `x_real` | 现实中的真实状态或轨迹，真机通常未知 |
| `x_hat` | 算法当前状态估计 |
| `m_real` | 现实环境 |
| `m_hat` | 算法当前地图估计 |
| `z` | 传感器实际测量 |
| `z_hat` | 当前状态/地图预测的测量 |
| `r` | 残差，通常是实际测量与预测测量之差 |
| `p` | 位置或三维点；坐标系由下标说明 |
| `v` | 线速度 |
| `a` | 线加速度；IMU 上下文要区分比力 |
| `ω` | 角速度，希腊字母 omega |
| `g` | 重力向量 |
| `b_g` | 陀螺仪零偏 |
| `b_a` | 加速度计零偏 |
| `Δt` | 时间间隔 |

## B.9 几何符号

| 符号 | 含义 |
|---|---|
| `R_ab` | 从 `b` 方向表达旋转到 `a` 的旋转矩阵 |
| `t_ab` | 与变换 `b → a` 配套的平移 |
| `T_ab` | 从 `b` 到 `a` 的齐次刚体变换 |
| `K` | 相机内参矩阵 |
| `f_x,f_y` | 像素单位横纵焦距 |
| `c_x,c_y` | 主点像素坐标 |
| `u,v` | 像素横纵坐标 |
| `X,Y,Z` | 点在相机坐标系的三维坐标；`Z` 常为光学深度 |
| `B` | 双目基线 |
| `d` | 双目视差；也可能泛指距离，需看上下文 |
| `n` | 单位法向量或数量；看上下文 |
| `ρ` | 常表示逆深度或鲁棒核函数；看自变量判断 |

## B.10 线性代数与优化符号

| 符号 | 含义 |
|---|---|
| `Aᵀ` | 矩阵 `A` 的转置 |
| `A⁻¹` | 矩阵 `A` 的逆；不一定存在 |
| `||x||` | 向量范数/长度 |
| `Σ` | 大写时可能表示求和符号或协方差矩阵，按排版判断 |
| `σ` | 标准差；`σ²` 为方差 |
| `W` | 权重或信息矩阵 |
| `J` | 雅可比矩阵；残差对状态的变化率 |
| `H` | 优化中的 Hessian 近似；几何中也可能指单应矩阵 |
| `g` | 优化中的梯度向量；物理中也可能是重力 |
| `Δx` | 本轮状态小增量 |
| `λ` | LM 阻尼、射线深度比例或其他标量；按上下文 |
| `I` | 单位矩阵；图像上下文也可能表示亮度函数 |
| `argmin` | 返回让目标函数最小的自变量 |
| `∼` | 齐次坐标中相差非零比例仍代表同一点 |
| `≈` | 近似等于 |

同一个字母在不同子领域可能复用。好文档应在局部解释，不能只靠字母猜。

## B.11 群与旋转

| 符号 | 含义 |
|---|---|
| `SO(2)` | 二维旋转集合 |
| `SO(3)` | 三维旋转集合 |
| `SE(2)` | 二维刚体位姿集合 |
| `SE(3)` | 三维刚体位姿集合 |
| `Sim(3)` | 三维相似变换：尺度 + 旋转 + 平移 |
| `Exp(δ)` | 把局部小向量映射为合法旋转/位姿变换 |
| `Log(T)` | 把旋转/位姿差映射回局部向量 |
| `q` | 四元数；注意库中的分量顺序 |

## B.12 传感器误差词汇

| 中文 | 英文 | 区别 |
|---|---|---|
| 随机噪声 | Noise | 重复测量中短时抖动 |
| 零偏 | Bias | 整体持续偏向某个方向，可随时间缓慢变 |
| 漂移 | Drift | 相对误差沿积分或轨迹累计后的长期偏离 |
| 离群值 | Outlier | 不服从正常小噪声的异常观测或错关联 |
| 延迟 | Latency | 测量/结果产生到被使用的时间差 |
| 时间偏移 | Time offset | 两设备时钟或采样语义之间的系统性错位 |
| 退化 | Degeneracy | 当前几何对某些状态方向约束太弱 |
| 不可观 | Unobservable | 不同状态在现有测量中无法被区分 |

## B.13 地图关系词汇

| 词 | 含义 |
|---|---|
| Landmark | 地标/地图点；可被重复观测的环境元素 |
| Keyframe | 关键帧；长期保留并参与地图/后端的代表帧 |
| Local map | 局部地图；当前跟踪附近最相关的地图子集 |
| Submap | 子地图；内部局部一致、整体位姿可在全局图中调整的地图块 |
| Covisibility graph | 共视图；关键帧因共享地图点而连接 |
| Pose graph | 位姿图；节点为位姿，边为相对位姿约束 |
| Factor graph | 因子图；变量节点与测量因子组成的估计图 |
| Marginalization | 边缘化；消去旧变量并把其信息浓缩为剩余变量先验 |

返回[SLAM 教程目录](README.md)。
