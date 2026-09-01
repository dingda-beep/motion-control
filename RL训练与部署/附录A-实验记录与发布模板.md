# 附录 A：实验记录与发布模板

## A.1 训练实验卡

```markdown
# 实验 <run_id>

## 问题
这次实验只想回答什么？

## 假设
为什么这项改动可能有效？预计改善哪些指标，可能损伤哪些指标？

## 相对基线的改动
- 主要改动：
- 其余保持不变：

## 复现信息
- 日期：
- Git commit / dirty diff：
- 机器人资源版本与哈希：
- Isaac Sim / Isaac Lab / RSL-RL：
- GPU / 驱动 / Python：
- 随机种子：
- 完整命令：
- resolved config 路径：

## 训练结果
- 仿真步数 / 迭代：
- 训练耗时：
- 异常：

## 固定评估
- 硬门槛：
- 任务指标：
- 质量指标：
- 鲁棒指标：
- 失败类型：

## 结论
- 支持假设 / 不支持 / 证据不足：
- 下一次只改什么：
```

## A.2 发布候选清单

```markdown
# Release Candidate <version>

## 身份
- robot hardware revision：
- policy SHA256：
- contract SHA256：
- training commit：
- checkpoint：
- parent release：

## 明确能力包络
- 命令范围：
- 地面：
- 载荷：
- 延迟：
- 持续时间：
- 环境限制：

## 自动检查
- schema：PASS/FAIL
- joint bijection：PASS/FAIL
- timing：PASS/FAIL
- observation golden：PASS/FAIL
- action golden：PASS/FAIL
- PyTorch ↔ ONNX：PASS/FAIL

## 仿真评估
- Isaac Lab：
- MuJoCo：
- 长时：
- 边界与扰动：

## 真机分级状态
- Level 0：
- Level 1：
- Level 2：
- Level 3：
- Level 4：
- Level 5：

## 已知限制
- （填写）

## 回退版本与触发条件
- （填写）

## 批准人、日期和证据链接
- （填写）
```

## A.3 事故记录

```markdown
# Incident <id>

- 时间与地点：
- 模型/契约/程序/机器人版本：
- 测试级别与批准命令包络：
- 触发前 10 秒命令与状态：
- 首个异常信号及其时间戳：
- 状态机与保护是否触发：
- 人员与设备后果：
- 原始日志/视频是否已只读归档：
- 初步分类：接口 / 估计 / 执行器 / 接触 / 分布 / 奖励 / 安全逻辑 / 未知
- 可复现步骤：
- 根因证据：
- 修正与回归范围：
- 新候选版本：
```
