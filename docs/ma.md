# MA：移动平均

[算法索引与时间约定](overview.md)

## 原理

W 个样本等权平均：后向形式为 $\hat x_n=\frac1W\sum_{k=0}^{W-1}x_{n-k}$；中心形式将求和范围改为 −R,…,R，W=2R+1。它等价于矩形核卷积。

## 变体、优缺点与时延

- 中心 MA：使用未来 R 帧；完整窗口内部保留线性趋势，但会压低峰、模糊阶跃。按目标时间绘图不整体右移。
- 后向 MA：无需未来帧，但对线性斜坡的等效滞后为 `(W−1)Δt/2`；首次完整输出需 W 帧。
- 优点：简单、直观、易解释；对独立同方差白噪声，平均后的噪声方差为原来的 1/W。
- 缺点：不抗离群点，尖峰容易被削弱；W 越大通常越平滑，但结构损失与响应滞后也更明显。它不是理想的频率选择滤波器。

## 本项目实现与注意事项

[algorithms.py](../tslab/algorithms.py) 调用 `pandas.Series(x).rolling(W, center=...).mean()`，默认 W=15；整数窗口默认要求完整 W 点。中心首尾各 R 点、后向前 W−1 点留 NaN，不用后面的值回填。

[realtime.py](../tslab/realtime.py) 只实现后向 MA，逐帧对完整历史窗口 `np.mean`，模拟默认共享窗口 W=5。中心 MA 尚未接入模拟，但可通过等待 R 帧扩展。

项目界面使用奇数窗口，输入要求均匀采样。NaN 表示无法计算，不是输出为零。窗口以样本计，修改 Δt 后同一窗口覆盖的物理时间会改变。

接口依据：[pandas rolling](https://pandas.pydata.org/docs/reference/api/pandas.Series.rolling.html)。
