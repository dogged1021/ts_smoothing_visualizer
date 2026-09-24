# Kalman：基于状态模型的递推估计

[算法索引与时间约定](overview.md)

## 原理

本项目使用一维随机游走模型，不是通用运动模型：

$$z_n=z_{n-1}+w_n,\quad x_n=z_n+v_n,\quad \operatorname{Var}(w_n)=Q,\ \operatorname{Var}(v_n)=R.$$

z 为潜在真实状态，x 为观测。预测与更新：

$$m_n^-=m_{n-1},\quad P_n^-=P_{n-1}+Q,\quad K_n=\frac{P_n^-}{P_n^-+R},$$
$$m_n=m_n^-+K_n(x_n-m_n^-),\quad P_n=(1-K_n)P_n^-.$$

增益 K 决定相信新观测多少，类似“由不确定性决定系数的递推平均”。在线性高斯且模型正确的条件下，它给出相应的条件均值和协方差。

## 优缺点、变体与时延

- 当前滤波只使用当前与过去数据，无未来等待，首帧即可输出，但仍可能响应滞后。
- 优点：明确结合状态模型和观测可信度；可扩展到位置—速度、多个传感器等。
- 缺点：依赖模型与参数；普通 Kalman 不抗异常观测，估计协方差也不等于模型一定正确。
- 通常增大 Q 或减小 R 会更追随观测；反之更平滑。启动时初始协方差也影响结果，不应只看 Q/R。
- 离线 smoother、固定延迟 smoother、运动模型、EKF/UKF 都是扩展，项目当前未实现。

## 本项目实现与注意事项

[algorithms.py](../tslab/algorithms.py)：`pykalman.KalmanFilter`，状态转移和观测矩阵均为 1；`transition_covariance=Q`、`observation_covariance=R`，默认 Q=0.05、R=0.2。初始均值取第一个观测、初始方差为 1，调用 `.filter(x)`，只返回均值。

[realtime.py](../tslab/realtime.py)：手写相同标量递推。首帧直接用初始先验做观测更新，不先加 Q；后续帧才加过程方差，保持与库实现一致。

**Q、R 是方差，不是标准差。** Q 按每个采样步定义，修改 Δt 后应重新评估。当前模型没有速度或加速度状态，也没有缺失数据处理入口；不能因 Kalman 家族具备扩展能力就认为本项目已支持这些功能。

接口依据：[pykalman KalmanFilter](https://pykalman.readthedocs.io/en/latest/class_docs.html)。
