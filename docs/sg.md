# Savitzky–Golay（SG）：局部多项式拟合

[算法索引与时间约定](overview.md) · [对照 Gaussian](gf.md)

## 原理

SG 假设一个短窗口内的干净信号可以用低阶多项式近似。对窗口样本 `(u_i, x_i)` 解最小二乘问题：

$$
\min_{a_0,\ldots,a_p}\sum_i\left[x_i-\sum_{j=0}^{p}a_j(u_i-u_*)^j\right]^2.
$$

`u_*` 是要估计的位置，坐标以样本为单位。拟合后，信号估计为 $a_0$；第 d 阶导数为 $d!a_d/\Delta t^d$。这是“找一条尽量贴合窗口数据的曲线，然后在指定位置读值或斜率”。

固定窗口、阶数和求值位置后，最小二乘可化为固定加权和，不需要每次重新求解。**权重由多项式拟合约束决定，可为负数，并非按距离直接指定。**

### 与高斯的具体区别

五点二阶中心 SG 的权重（从左到右）为 `[-3, 12, 17, 12, -3] / 35`。输入无噪声抛物线 `[4, 1, 0, 1, 4]`，中心输出恰为 `0`；Gaussian 的正权平均会大于 `0`。SG 用负权重抵消曲率造成的平均偏差，高斯只按距离平均。

因此，SG 能在完整窗口、无噪声且阶数足够时精确保留局部多项式；这不是“所有峰形都不失真”的保证。

## 变体与时延

设奇数窗口 W=2R+1，拟合阶数 p<W：

| 变体 | 求值位置 | 未来等待 | 启动与边界 |
|---|---|---|---|
| 中心 SG | 窗口中点 | R 帧 | 完整窗口后输出；结果标在中心时刻 |
| SG-endpoint | 窗口右端 | 0 帧 | 收齐 W 帧才首次输出当前时刻估计 |
| 固定延迟 SG | 本项目就是中心 SG 的逐帧执行 | R 帧 | 第 n 帧到达，发布第 n−R 帧结果 |

endpoint 仍拟合整个历史窗口，不是截掉中心 SG 的一半权重。它能跟随匹配的多项式趋势，但任意信号仍可能存在响应失真或滞后；不能概括为“实时零时延”。

## 优缺点与参数

- 优点：保留局部多项式趋势；同一拟合能直接给出信号与导数。
- 缺点：可能产生过冲、振铃；对异常点不稳健；端点估计通常比中心估计更易受噪声影响，求二阶导数时尤其明显。
- 加大窗口通常增强降噪，但可能跨越局部结构；提高阶数增加拟合灵活性，也可能保留更多噪声。p=W−1 时拟合可穿过全部窗口点，零阶输出失去降噪作用。

## 本项目实现

源码：[algorithms.py](../tslab/algorithms.py)、[realtime.py](../tslab/realtime.py)。

- 离线信号：`scipy.signal.savgol_filter(x, window_length=W, polyorder=p, mode="interp")`。A01 默认 W=15、p=2。
- 离线导数：同一接口设置 `deriv=1/2, delta=dt`；A07 默认 W=15、p=3。`interp` 在首尾窗口拟合多项式以计算边界输出，不是零填充。
- 模拟：`savgol_coeffs(W, p, pos=..., deriv=d, delta=dt, use="dot")`。endpoint 用 `pos=W−1`，中心用 `pos=W//2`；系数与按时间递增排列的窗口做点积。零阶可省略 `delta`。
- 模拟默认 W=5、p=2；启动前及中心方法未发布的尾部为 NaN，不做边界外推，也不回写已发布值。

注意：项目要求均匀采样；导数必须使用真实 Δt。当前中心估计按目标时间绘图，所以看不到整体右移，但实时发布必须等待 RΔt 秒。

接口依据：[SciPy savgol_coeffs](https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.savgol_coeffs.html)、[savgol_filter](https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.savgol_filter.html)。
