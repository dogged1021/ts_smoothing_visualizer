# Butterworth 低通：双向离线变体

[单向原理与参数](butterworth.md) · [算法索引](overview.md)

## 原理与差别

对同一记录先正向、再反向滤波。对于实系数滤波器，在忽略有限记录边界影响的频率响应模型下：

$$H_{\mathrm{fb}}(e^{j\omega})=H(e^{j\omega})H(e^{-j\omega})=|H(e^{j\omega})|^2.$$

相位抵消，幅度响应变为单向的平方。因此单向截止处约 −3 dB，双向约 −6 dB；并非保持幅度不变只移除延迟。页面阶数 N 指每次滤波的阶数，双向组合的有效阶数为 2N；不要将其理解为同截止频率的普通 2N 阶 Butterworth。

## 效果、时间语义与限制

优点是离线比较时减少相位偏移，同时抑制高频。代价是依赖未来数据，具有边界效应，可能出现变化发生之前的响应及过冲。不是实时零延迟算法，也不提供固定未来等待帧数；模拟实时不显示此选项。

频率选择不会保证运动学一致性。当前仅平滑信号，速度、加速度需要另行定义求导规则。

## 本项目实现

[algorithms.py](../tslab/algorithms.py) 的 `butterworth_lowpass(..., zero_phase=True)` 使用与单向相同的 `butter(..., output="sos")`，再调用：

```python
sosfiltfilt(sos, x, padtype="odd", padlen=3 * (order + 1))
```

使用奇对称端点延拓，长度规则对应当前低通设计。数据长度必须大于 padlen；不满足时页面提示增加样本或降低阶数，跳过该方法，不自动缩短延拓或退化为单向。

A01 离线“使用未来数据”组提供此项。与单向共用截止频率与阶数，默认值见单向文档。边界结果仍计入 A01 指标，应结合局部曲线判断，不能只看总体 RMSE。

已验证常数保持、正弦幅度对应单向增益平方、短序列提示和双向方法不会进入模拟列表。

官方接口：[sosfiltfilt](https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.sosfiltfilt.html)。

A01 现已显示理论低频滞后，计算公式、适用范围与边界解释见 [时间说明](timing.md)。
