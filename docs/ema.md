# EMA：指数移动平均

[算法索引与时间约定](overview.md)

## 原理

固定系数递推形式：

$$\hat x_0=x_0,\qquad \hat x_n=\alpha x_n+(1-\alpha)\hat x_{n-1},\quad 0<\alpha\le1.$$

展开后历史权重按指数衰减。α 越小，记忆越长、通常越平滑但越迟钝；α=1 时直接输出观测。原文“小 α 平滑不足”的描述不正确。

归一化历史权重形式为：

$$\hat x_n=\frac{\sum_{k=0}^{n}(1-\alpha)^k x_{n-k}}{\sum_{k=0}^{n}(1-\alpha)^k}.$$

两者主要区别是启动阶段对首个样本的权重处理，不是因果与非因果的区别。

## 优缺点、变体与时延

- 两种形式都只用当前和过去样本，首帧即可输出，无固定未来等待。
- 优点：计算简单；固定系数形式只需保存上一次估计，适合持续更新。
- 缺点：变化响应滞后、首值影响启动过程、不抗离群点。固定 α 下，斜坡的稳态等效滞后为 `(1−α)Δt/α`；不是任意信号的统一延迟。
- 可扩展双向指数平滑，但会用未来数据且改变滤波效果，项目尚未实现；不能把后向 EMA 直接改名为中心 EMA。

## 本项目实现与注意事项

[algorithms.py](../tslab/algorithms.py)：`pandas.Series(x).ewm(alpha=alpha, adjust=adjust).mean()`。A01 默认 α=0.1、`adjust=True`，即归一化形式；取消勾选后采用固定系数递推。

[realtime.py](../tslab/realtime.py)：手写固定系数递推，对应 `adjust=False`。A07 的 EMA 后差分同样使用固定系数形式，再接指定差分公式。

比较离线与模拟前要统一 `adjust`。α 无量纲；采样率改变而希望保持相同物理时间尺度时，可按时间常数 τ 选择 `α=1−exp(−Δt/τ)`，当前界面不自动换算。

接口依据：[pandas ewm](https://pandas.pydata.org/docs/reference/api/pandas.Series.ewm.html)。
