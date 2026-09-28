# Butterworth 低通：单向滤波

[算法索引](overview.md) · [双向变体](butterworth_bidirectional.md)

## 原理与任务

低通保留较慢变化、削弱较快变化；Butterworth 的特点是通带幅度响应最大平坦。模拟原型的幅度平方为：

$$|H(j\Omega)|^2=\frac{1}{1+(\Omega/\Omega_c)^{2N}}.$$

N 为阶数，Ωc 为截止角频率。在截止处幅度为 1/√2（约 −3.01 dB），不是截止以上立即变成零。项目使用 SciPy 的数字滤波器设计，不能把模拟原型公式直接当成整个数字频轴的响应。

## 参数、效果与局限

- 页面阶数默认为 2，范围 1–8；截止频率单位为 Hz，初次默认取 Nyquist 的 20%，即采样率的 10%。默认 Δt=0.1 秒时为 1 Hz。
- 较低截止频率通常更平滑，但可能损失真实快速运动。较高阶数使过渡更陡，也可能增加瞬态、过冲及相位畸变。
- 单向实现只使用当前和过去数据，不等待未来帧；不同频率的相位延迟不同，不等于固定移动几帧。
- 不抗离群点，也不能自动区分目标高频与噪声。它不是频谱分析方法，不执行 FFT。

## 本项目实现

[algorithms.py](../tslab/algorithms.py) 的 `butterworth_lowpass`：

```python
sos = butter(order, cutoff, btype="lowpass", fs=1 / dt, output="sos")
y, state = sosfilt(sos, x, zi=sosfilt_zi(sos) * x[0])
```

使用 `scipy.signal` 的二阶节（SOS）表示，避免高阶直接多项式系数带来的数值敏感性。首值初始化假设滤波器此前处于该常值输入的稳态；这能避免从零启动的跳变，但不保证实际信号没有启动瞬态。

A01 离线的“仅使用当前及过去数据”组与模拟实时的“无需等待未来帧”组均可选择。模拟在 [realtime.py](../tslab/realtime.py) 中仅对已到达前缀执行同一因果函数，首帧可输出，新增数据不改写历史结果。当前没有 A07 低通求导入口。

截止频率必须满足 0<fc<fs/2。界面限制在 Nyquist 的 0.1%–99.9%；修改采样间隔使旧频率越界时重设为新 Nyquist 的 20%，仍有效时保留原 Hz 值。离线单向/双向共享参数；模拟使用独立参数键。

## 验证与注意事项

已验证常数保持、截止 −3 dB、已知正弦频率衰减、前缀结果稳定、非法参数和页面切换。启动区仍计入评价，不自动删掉人为指定的“稳定时间”。短数据也可单向计算，但不意味着已稳定。

示例：fs=100 Hz、fc=5 Hz、N=2 时，1 Hz 正弦保留较多，20 Hz 正弦明显削弱；具体增益应按数字滤波器频率响应计算。

官方接口：[butter](https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.butter.html)、[sosfilt_zi](https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.sosfilt_zi.html)。

A01 现已显示理论低频滞后，计算公式、适用范围与边界解释见 [时间说明](timing.md)。
